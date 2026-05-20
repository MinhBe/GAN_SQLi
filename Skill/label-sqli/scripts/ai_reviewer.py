"""
ai_reviewer.py -- Chat-based AI reviewer (NO API required)

Workflow:
  1. Pipeline writes prompt files to  <work_dir>/prompts/batch_NNN.txt
  2. User opens each prompt file, pastes into any chat AI
     (Claude.ai, ChatGPT, Gemini, Copilot, etc.)
  3. User copies AI response, saves to  <work_dir>/responses/batch_NNN.txt
  4. Pipeline reads response, parses JSON, continues

No API key needed. Works with any chat AI that can read/write text.

Returns: {payload_index: {sqli_type, db_engine, confidence, reasoning}}
"""

import json
import random
import time
from pathlib import Path

VALID_TYPES   = ['time_blind', 'boolean_blind', 'union_based', 'error_based', 'benign']
VALID_ENGINES = ['mysql', 'postgres', 'oracle', 'mssql', 'sqlite', 'unknown']
BUDGET_CAP    = 50_000
BATCH_SIZE    = 50   # 50 payloads per chat session (fits in most chat AI context windows)

REVIEW_PROMPT_TEMPLATE = """You are a SQL injection expert. Classify each payload below.

For each payload, output ONLY a JSON object on one line (no markdown, no explanation):
{{"idx": <index>, "sqli_type": "<type>", "db_engine": "<engine>", "confidence": <0.0-1.0>}}

Valid sqli_type values: time_blind, boolean_blind, union_based, error_based, benign
Valid db_engine values: mysql, postgres, oracle, mssql, sqlite, unknown

Rules:
- time_blind: uses SLEEP(), BENCHMARK(), WAITFOR, pg_sleep() to cause delays
- boolean_blind: uses OR/AND true/false conditions (OR 1=1, AND 1=2, substring comparisons)
- union_based: uses UNION SELECT to append extra result sets
- error_based: triggers DB errors to leak info (extractvalue, xmltype, floor(rand()))
- benign: not an injection attempt

Payloads to classify:
{payloads_block}

Output one JSON per line, NO other text, NO markdown code blocks:"""


def _format_payload_block(indexed_payloads: list) -> str:
    return "\n".join(f"[{idx}] {str(p)[:300]}" for idx, p in indexed_payloads)


def _parse_response(response_text: str, expected_indices: set) -> dict:
    """Parse JSON lines from chat AI response. Tolerant of extra text."""
    results = {}
    for line in response_text.strip().split('\n'):
        line = line.strip()
        # Strip markdown code fences if chat AI added them
        if line.startswith('```'):
            continue
        if not line or not line.startswith('{'):
            continue
        try:
            obj = json.loads(line)
            idx = int(obj.get('idx', -1))
            sqli_type  = obj.get('sqli_type', 'benign')
            db_engine  = obj.get('db_engine', 'unknown')
            confidence = float(obj.get('confidence', 0.70))
            if idx in expected_indices:
                results[idx] = {
                    'sqli_type':  sqli_type if sqli_type in VALID_TYPES else 'benign',
                    'db_engine':  db_engine if db_engine in VALID_ENGINES else 'unknown',
                    'confidence': max(0.0, min(1.0, confidence)),
                    'reasoning':  obj.get('reasoning', ''),
                }
        except (json.JSONDecodeError, ValueError, KeyError):
            continue
    return results


def _stratified_sample(disagreement_indices: list, cap: int, seed: int = 42) -> list:
    if len(disagreement_indices) <= cap:
        return disagreement_indices
    print(f"[WARN] {len(disagreement_indices):,} disagreements > cap {cap:,}")
    print(f"[INFO] Sampling {cap:,} rows; rest get fallback labels")
    random.seed(seed)
    return random.sample(disagreement_indices, cap)


# ===========================================================================
# CHAT MODE — file-based, no API
# ===========================================================================

def review_batch(payloads: list,
                 disagreement_indices: list,
                 work_dir: str = None,
                 batch_size: int = BATCH_SIZE,
                 budget_cap: int = BUDGET_CAP,
                 dry_run: bool = False,
                 # kept for backward compat — ignored in chat mode
                 api_key: str = None,
                 model: str = None) -> dict:
    """
    Chat-based review. No API. User pastes prompts into any chat AI manually.

    Args:
        payloads:              Full list of all payloads (indexed by position)
        disagreement_indices:  Indices needing AI review
        work_dir:              Directory for prompt/response files.
                               Default: same folder as this script / chat_review/
        batch_size:            Payloads per chat session (default 50)
        budget_cap:            Max rows to review (rest get fallback labels)
        dry_run:               Skip all interaction, return mock labels

    Folder structure created:
        <work_dir>/
          prompts/   batch_000.txt  batch_001.txt  ...
          responses/ batch_000.txt  batch_001.txt  ...  (user fills these)
    """
    if not disagreement_indices:
        print("[INFO] No disagreement rows — skipping chat review")
        return {}

    sample_indices = _stratified_sample(disagreement_indices, budget_cap)

    if dry_run:
        print("[INFO] DRY RUN — mock labels, no chat interaction")
        return {
            idx: {'sqli_type': 'boolean_blind', 'db_engine': 'unknown',
                  'confidence': 0.72, 'reasoning': 'dry_run_mock'}
            for idx in sample_indices
        }

    # Setup directories
    base = Path(work_dir) if work_dir else Path(__file__).resolve().parent / "chat_review"
    prompts_dir   = base / "prompts"
    responses_dir = base / "responses"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)

    batches = [sample_indices[i:i+batch_size]
               for i in range(0, len(sample_indices), batch_size)]

    total_batches = len(batches)
    print(f"\n[INFO] Chat review mode: {len(sample_indices):,} rows, {total_batches} batches of {batch_size}")
    print(f"[INFO] Prompt files  -> {prompts_dir}")
    print(f"[INFO] Response files-> {responses_dir}")
    print(f"[INFO] Writing all prompt files first...\n")

    # Write ALL prompt files upfront so user can work through them
    for batch_num, batch_indices in enumerate(batches):
        indexed_payloads = [(idx, payloads[idx]) for idx in batch_indices]
        payload_block = _format_payload_block(indexed_payloads)
        prompt = REVIEW_PROMPT_TEMPLATE.format(payloads_block=payload_block)
        prompt_file = prompts_dir / f"batch_{batch_num:03d}.txt"
        prompt_file.write_text(prompt, encoding='utf-8')

    print(f"[OK] {total_batches} prompt files written to: {prompts_dir}\n")
    print("=" * 65)
    print("  INSTRUCTIONS — for each batch:")
    print("  1. Open prompts/batch_NNN.txt")
    print("  2. Copy ALL content -> paste into chat AI")
    print("     (Claude.ai, ChatGPT, Gemini, Copilot, etc.)")
    print("  3. Copy AI response -> save as responses/batch_NNN.txt")
    print("  4. Come back here and press Enter to continue")
    print("=" * 65)

    all_results = {}

    for batch_num, batch_indices in enumerate(batches):
        prompt_file   = prompts_dir   / f"batch_{batch_num:03d}.txt"
        response_file = responses_dir / f"batch_{batch_num:03d}.txt"
        expected      = set(batch_indices)

        # Skip if response already exists (resumable)
        if response_file.exists():
            print(f"[SKIP] Batch {batch_num:03d} — response already exists, loading...")
            response_text = response_file.read_text(encoding='utf-8')
            batch_results = _parse_response(response_text, expected)
            all_results.update(batch_results)
            _fill_fallback(all_results, batch_indices)
            continue

        # Prompt user
        print(f"\n[ACTION] Batch {batch_num+1}/{total_batches} "
              f"({len(batch_indices)} payloads)")
        print(f"  Prompt : {prompt_file}")
        print(f"  Save response to: {response_file}")

        while True:
            try:
                input("  Press Enter when response file is ready (or Ctrl+C to skip batch)...")
            except KeyboardInterrupt:
                print(f"\n[SKIP] Batch {batch_num:03d} skipped — applying fallback labels")
                _fill_fallback(all_results, batch_indices)
                break

            if response_file.exists():
                response_text = response_file.read_text(encoding='utf-8')
                batch_results = _parse_response(response_text, expected)
                if batch_results:
                    all_results.update(batch_results)
                    _fill_fallback(all_results, batch_indices)
                    parsed = len(batch_results)
                    total  = len(batch_indices)
                    print(f"  [OK] Parsed {parsed}/{total} responses "
                          f"({'OK' if parsed == total else 'WARN: some missing, fallback applied'})")
                    break
                else:
                    print("  [WARN] Response file exists but no valid JSON found.")
                    print("  Check format: each line must be a JSON object starting with {")
                    print("  Try again or Ctrl+C to skip.")
            else:
                print(f"  [WARN] File not found: {response_file}")
                print("  Save the AI response there and press Enter again.")

        if (batch_num + 1) % 5 == 0 or (batch_num + 1) == total_batches:
            print(f"\n[INFO] Progress: {batch_num+1}/{total_batches} batches, "
                  f"{len(all_results):,}/{len(sample_indices):,} rows labeled")

    print(f"\n[OK] Chat review complete: {len(all_results):,} rows labeled")

    type_dist = {}
    for r in all_results.values():
        t = r.get('sqli_type', 'unknown')
        type_dist[t] = type_dist.get(t, 0) + 1
    for t, cnt in sorted(type_dist.items(), key=lambda x: -x[1]):
        print(f"  {t}: {cnt:,} ({cnt/max(len(all_results),1)*100:.1f}%)")

    return all_results


def _fill_fallback(results: dict, batch_indices: list) -> None:
    """Apply fallback label for any index not yet in results."""
    for idx in batch_indices:
        if idx not in results:
            results[idx] = {
                'sqli_type': 'boolean_blind',
                'db_engine': 'unknown',
                'confidence': 0.50,
                'reasoning': 'chat_review_fallback',
            }

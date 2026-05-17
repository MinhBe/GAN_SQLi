"""chat_label_coordinator.py — Chia chat_queue.csv thành chunks + emit subagent prompts.

Output:
  - {temp_dir}/chunk_001.csv, chunk_002.csv, ... (N chunks of chunk_size rows)
  - {temp_dir}/prompts.json (list of subagent invocation specs)

Main Claude Code session đọc prompts.json và spawn subagents song song
(parallel ~10 mỗi đợt) qua tool Agent (subagent_type=general-purpose).

Mỗi subagent task:
  1. Đọc Skill/sqli-data-curator/SKILL.md, taxonomy.md, function_whitelist.md
  2. Đọc chunk CSV
  3. Label từng row với reasoning ≥ 50 chars
  4. Ghi chunk_NNN_labeled.csv với schema chuẩn

Sau khi tất cả subagents xong → chạy merge_chunks.py.
"""
import argparse
import json
import os
from pathlib import Path

import pandas as pd


# Subagent prompt template — KHÔNG sửa free-form, cố định cho consistency
SUBAGENT_PROMPT_TEMPLATE = """Bạn là chuyên gia phân loại SQL injection cho dataset GAN training.

# BƯỚC 1: Đọc taxonomy (BẮT BUỘC, đọc đầy đủ trước khi label)

Đọc 3 file sau bằng tool Read:
1. {skill_md_path}
2. {taxonomy_md_path}
3. {function_whitelist_md_path}

# BƯỚC 2: Đọc chunk CSV

Đọc file: {chunk_path}

Schema columns: id, payload_norm, payload_inner, a_type, a_db, a_signals, c_type, c_db, c_signals
(số rows: {n_rows})

# BƯỚC 3: Phân loại từng row

Cho mỗi row, gán nhãn cuối cùng:
- sqli_type ∈ {{benign, error_based, boolean_blind, time_blind, union_based, auth_bypass, heavy_query, out_of_band, stacked_queries, polyglot}}
- db_engine ∈ {{oracle, mysql, postgresql, mssql, firebird, sqlite, db2, generic}}
- confidence ∈ [0.5, 1.0]
- reasoning ≥ 50 chars TRÍCH TOKEN cụ thể từ payload_inner

QUY TẮC:
1. Tham khảo a_type/c_type nhưng KHÔNG bắt buộc theo. Tin payload thật, không tin hint.
2. Nếu payload có nhiều signals: dùng priority table trong taxonomy.md (lower = stronger)
3. Reasoning PHẢI quote token cụ thể, ví dụ:
   ✓ ĐÚNG: "pg_sleep(N) is PostgreSQL time-based; 'OR' boolean context makes it true-branch sleep"
   ✗ SAI:  "time blind" (quá ngắn, không có evidence)
4. Nếu unsure: confidence=0.5, reasoning bắt đầu với "UNCERTAIN:"

# BƯỚC 4: Tính sources_agree
- 3: sqli_type == a_type AND sqli_type == c_type
- 2: sqli_type khớp 1 trong (a_type, c_type)
- 1: sqli_type khác cả a_type và c_type
- 0: confidence < 0.5

# BƯỚC 5: Ghi output (BẮT BUỘC)

Dùng Write tool để ghi file: {output_path}

CSV schema (chính xác 7 cột, theo thứ tự):
  id, payload_inner, sqli_type, db_engine, confidence, reasoning, sources_agree

# BƯỚC 6: Báo cáo (≤ 100 từ)

In ra:
- Số rows đã label
- Type distribution top 5
- Số rows có confidence < 0.7
- Số rows reasoning < 50 chars (lý tưởng = 0)

KHÔNG paste CSV content trong message. KHÔNG diễn giải dài. CHỈ thống kê.
"""


def split_chunks(input_csv: str, chunk_size: int, temp_dir: str) -> list[dict]:
    """Split input CSV into chunks, save each as chunk_NNN.csv.

    Returns list of chunk metadata: [{path, n_rows, chunk_id}, ...]
    """
    df = pd.read_csv(input_csv)
    n_total = len(df)
    n_chunks = (n_total + chunk_size - 1) // chunk_size

    os.makedirs(temp_dir, exist_ok=True)
    chunks = []
    for i in range(n_chunks):
        start = i * chunk_size
        end = min(start + chunk_size, n_total)
        chunk_df = df.iloc[start:end].copy()
        chunk_id = i + 1
        filename = f"chunk_{chunk_id:03d}.csv"
        chunk_path = os.path.join(temp_dir, filename)
        chunk_df.to_csv(chunk_path, index=False)
        chunks.append({
            "chunk_id": chunk_id,
            "path": os.path.abspath(chunk_path),
            "n_rows": len(chunk_df),
            "output_path": os.path.abspath(
                os.path.join(temp_dir, f"chunk_{chunk_id:03d}_labeled.csv")
            ),
        })

    return chunks


def generate_subagent_prompt(chunk: dict, skill_root: str) -> str:
    """Generate the labeling prompt for one subagent given a chunk."""
    return SUBAGENT_PROMPT_TEMPLATE.format(
        skill_md_path=os.path.join(skill_root, "SKILL.md"),
        taxonomy_md_path=os.path.join(skill_root, "references", "taxonomy.md"),
        function_whitelist_md_path=os.path.join(skill_root, "references", "function_whitelist.md"),
        chunk_path=chunk["path"],
        output_path=chunk["output_path"],
        n_rows=chunk["n_rows"],
    )


def emit_orchestration_plan(chunks: list[dict], skill_root: str, prompts_path: str):
    """Write prompts.json with subagent specs for main chat to orchestrate."""
    plan = {
        "n_subagents": len(chunks),
        "subagent_type": "general-purpose",
        "parallel_limit": 10,
        "skill_root": skill_root,
        "subagents": [
            {
                "id": f"sub_{c['chunk_id']:03d}",
                "description": f"Label SQLi chunk {c['chunk_id']} ({c['n_rows']} rows)",
                "chunk_path": c["path"],
                "output_path": c["output_path"],
                "n_rows": c["n_rows"],
                "prompt": generate_subagent_prompt(c, skill_root),
            }
            for c in chunks
        ],
    }
    with open(prompts_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    return plan


def main():
    parser = argparse.ArgumentParser(description="Chunk chat_queue + emit subagent prompts")
    parser.add_argument("--input", required=True, help="chat_queue.csv path")
    parser.add_argument("--chunk_size", type=int, default=200, help="Rows per chunk")
    parser.add_argument("--temp_dir", required=True, help="Directory for chunks output")
    parser.add_argument("--emit_prompts", default=None,
                        help="Path for prompts.json (default: <temp_dir>/prompts.json)")
    parser.add_argument("--skill_root", default=None,
                        help="Path to sqli-data-curator skill folder "
                             "(default: auto-detect from script location)")
    args = parser.parse_args()

    # Auto-detect skill root
    if not args.skill_root:
        script_dir = Path(__file__).resolve().parent  # .../scripts/
        skill_root = str(script_dir.parent)            # .../sqli-data-curator/
    else:
        skill_root = args.skill_root

    if not args.emit_prompts:
        args.emit_prompts = os.path.join(args.temp_dir, "prompts.json")

    print(f"Skill root: {skill_root}")
    print(f"Splitting {args.input} into chunks of {args.chunk_size}...")
    chunks = split_chunks(args.input, args.chunk_size, args.temp_dir)
    print(f"Created {len(chunks)} chunks in {args.temp_dir}")

    plan = emit_orchestration_plan(chunks, skill_root, args.emit_prompts)
    print(f"Wrote orchestration plan to {args.emit_prompts}")
    print(f"\n=== SUBAGENT PLAN ===")
    print(f"Total subagents      : {plan['n_subagents']}")
    print(f"Parallel limit       : {plan['parallel_limit']}")
    print(f"Estimated rounds     : {(plan['n_subagents'] + plan['parallel_limit'] - 1) // plan['parallel_limit']}")
    print(f"\n=== NEXT STEPS ===")
    print(f"Main Claude session: read {args.emit_prompts} and spawn subagents")
    print(f"via Agent tool (subagent_type=general-purpose), parallel {plan['parallel_limit']}.")
    print(f"After all done, run:")
    print(f"  python merge_chunks.py --temp_dir {args.temp_dir} --output relabeled_chat.csv")


if __name__ == "__main__":
    main()

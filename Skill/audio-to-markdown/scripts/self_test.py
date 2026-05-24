#!/usr/bin/env python3
"""Offline checks for audio-to-markdown behavior."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "audio_to_markdown.py"
FIXTURES = REPO_ROOT / "Asset" / "Record_Transcript"


def run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="atm_selftest_") as temp:
        temp_dir = Path(temp)

        fail_out = temp_dir / "voice_008.md"
        proc = run_cli(
            [
                "--input",
                "missing-audio.m4a",
                "--transcript",
                str(FIXTURES / "Voice 008_sd.md"),
                "--output",
                str(fail_out),
                "--language",
                "vi",
            ]
        )
        assert_true(proc.returncode == 2, "Voice 008 fixture should fail quality gate.")
        fail_text = fail_out.read_text(encoding="utf-8")
        assert_true("failed_stt_quality_gate" in fail_text, "Failure report should include failed status.")
        assert_true("## Action Items" not in fail_text, "Failure report must not render full action items.")

        meeting_out = temp_dir / "thay_lam.md"
        proc = run_cli(
            [
                "--input",
                "missing-audio.m4a",
                "--transcript",
                str(FIXTURES / "Thầy lâm 2.md"),
                "--output",
                str(meeting_out),
                "--profile",
                "research_meeting",
                "--language",
                "vi",
                "--emit-analysis",
            ]
        )
        assert_true(proc.returncode == 0, f"Research fixture should render successfully: {proc.stderr}")
        meeting_text = meeting_out.read_text(encoding="utf-8")
        analysis_text = meeting_out.with_name("thay_lam_analysis.md").read_text(encoding="utf-8")
        for heading in ["Advisor Questions", "Required Revisions", "Weak Points Raised", "Next Meeting Checklist"]:
            assert_true(heading in meeting_text, f"Missing research section: {heading}")
        assert_true("| Student |" in meeting_text or "| Unclear |" in meeting_text, "Action table should have owner evidence.")
        assert_true("Evidence-Based Action Items" in analysis_text, "Analysis file should be emitted.")

        second_out = temp_dir / "record_thay_lam_2.md"
        proc = run_cli(
            [
                "--input",
                "missing-audio.m4a",
                "--transcript",
                str(FIXTURES / "Record thầy Lâm (2).md"),
                "--output",
                str(second_out),
                "--profile",
                "research_meeting",
                "--language",
                "vi",
            ]
        )
        assert_true(proc.returncode == 0, f"Second research fixture should render successfully: {proc.stderr}")
        second_text = second_out.read_text(encoding="utf-8")
        assert_true("Weak Points Raised" in second_text, "Second fixture should include research weakness section.")
        assert_true("không kiểm soát" in second_text, "Second fixture should preserve readable Vietnamese text.")

        sys.path.insert(0, str(SKILL_ROOT / "scripts"))
        from audio_markdown.quality import assess_quality
        from audio_markdown.repair import repair_vietnamese_segments
        from audio_markdown.render import extract_action_items

        mojibake = [{"start": 0, "text": "H\u00c3\u00a3y subscribe cho k\u00c3\u00aAnh."}]
        repaired = repair_vietnamese_segments(mojibake)
        assert_true(repaired["repair_applied"], "Mojibake repair should apply.")
        assert_true("Hãy" in repaired["segments"][0]["text"], "Mojibake sample should become readable Vietnamese.")

        normal = [{"start": 0, "text": "Em phải bổ sung bảng kết quả và giải thích rõ dữ liệu."}]
        assert_true(assess_quality(normal).status != "failed_stt_quality_gate", "Short normal transcript should not fail.")
        actions = extract_action_items(normal)
        assert_true(actions and actions[0]["owner"] == "Student", "Action extraction should infer Student owner.")

        json.load((SKILL_ROOT / "evals" / "evals.json").open(encoding="utf-8"))

    print("audio-to-markdown self-test ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

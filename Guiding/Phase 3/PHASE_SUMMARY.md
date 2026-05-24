# Phase 3 - Decision Gate Summary

## Mục tiêu

Phase 3 không train mô hình. Nó đọc artifact Phase 2 và áp gate đã đăng ký để quyết định hướng chính: tiếp tục GAN hay chọn MLE làm main path.

## Chuyện gì đã xảy ra

Report chính `reports/03_decision_gate_report.md` kết luận:

- Decision: `MLE_MAIN`.
- Gate passed: `false`.
- Lý do: GAN fail 4/6 gate.
- Tie-break/default path: Conditional MLE + evaluator-guided search.

Các gate fail:

- `G1_unique_ratio`: GAN `0.497` <= MLE `0.803`.
- `G2_self_bleu3`: GAN `0.037` >= MLE `0.012`.
- `G5_no_collapse`: collapsed 3/3 seeds.
- `G6_frontier_dominance`: không có dominating pair.

Các gate pass:

- `G3_syntax_guard`: GAN syntax seed tốt nhất vượt threshold.
- `G4_D_shortcut`: không thấy D shortcut rõ.

## Kiến trúc/logic

Không có model training. Đây là statistical decision layer:

1. Load `Phase 2/eval/mle_frontier.json`.
2. Load `Phase 2/eval/gan_results.json`.
3. Tính mean/std/CI và collapse status.
4. Kiểm tra gate theo protocol.
5. Xuất decision JSON, statistical summary, frontier plot, report.

## File trong Phase 3

| File/thư mục | Tác dụng |
|---|---|
| `03_preregistered_protocol.md` | Protocol/gate đăng ký cho Phase 3. |
| `phase03_decision_gate.py` | Script gate-only; đọc Phase 2 artifacts, không train. |
| `reports/03_decision_gate_report.md` | Report kết luận chính của Phase 3. |
| `eval/phase03/decision.json` | Quyết định máy đọc được: `MLE_MAIN`. |
| `eval/phase03/statistical_summary.json` | Summary thống kê/CI/collapse. |
| `eval/phase03/mle_vs_gan_frontier.png` | Plot frontier MLE vs GAN. |

## Vai trò trong toàn dự án

Phase 3 là điểm rẽ: nếu chỉ tối ưu chất lượng mô hình, MLE là đường chính. Nhưng vì đề tài cần GAN, Phase 3 trở thành bằng chứng nền để nói rằng GAN full-sequence cũ thất bại có kiểm chứng, từ đó biện minh cho việc đổi sang GAN constrained/surgery ở Phase 8.

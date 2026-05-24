# Guiding - Phase Summary Index

File này là bản đồ đọc nhanh cho thư mục `Guiding`. Mục tiêu là làm rõ thư mục đang lộn xộn mà không xóa, di chuyển, hoặc đổi tên bất cứ artifact nào.

## Cách đọc nhanh

| Khu vực | Vai trò hiện tại | File tóm tắt |
|---|---|---|
| `Phase 1` | Data reality check trên dữ liệu gốc | `Guiding/Phase 1/PHASE_SUMMARY.md` |
| `Phase 2` | Vertical slice: MLE vs mini Gumbel-SeqGAN | `Guiding/Phase 2/PHASE_SUMMARY.md` |
| `Phase 3` | Decision gate, không train | `Guiding/Phase 3/PHASE_SUMMARY.md` |
| `Phase 3.5` | Nhánh retry/diagnostic, hiện không còn artifact chính trong thư mục | `Guiding/Phase 3.5/PHASE_SUMMARY.md` |
| `Phase 4` | Full data foundation, delex, dedup, cluster-safe split | `Guiding/Phase 4/PHASE_SUMMARY.md` |
| `Phase 5` | Full detector-only labeling system | `Guiding/Phase 5/PHASE_SUMMARY.md` |
| `Phase 6` | GPU training: token shards, MLE, Gumbel smoke, condition audits | `Guiding/Phase 6/PHASE_SUMMARY.md` |
| `Phase 8` | Reopened GAN path: evaluator, surgery baselines, H5' paired surgery GAN | `Guiding/Phase 8/PHASE_SUMMARY.md` |

## Trạng thái khoa học ngắn gọn

- Phase 1-5 tạo nền dữ liệu: hiểu thực trạng dữ liệu, delex, dedup, split an toàn, gán nhãn detector-only.
- Phase 2-3 chứng minh full-sequence mini Gumbel-SeqGAN trên vertical slice không vượt MLE và có collapse.
- Phase 6 chứng minh pipeline GPU chạy được trên RTX 3050 6GB: MLE baseline, attack-only branch, Gumbel smoke/balanced. Gumbel có thể chạy nhưng condition/evaluator còn yếu.
- Phase 8 đổi hướng từ full-sequence GAN sang constrained GAN: paired masked payload-surgery GAN. GAN hiện chạy ổn, không OOM, nhưng novelty vẫn chưa thắng mutation-engine và evasion/WAF axis còn thiếu.

## Những thư mục/file không nên coi là nguồn chính

- `checkpoints/`, `outputs/`, `cache/`, `logs/`: artifact chạy thử hoặc kết quả chạy. Không xóa khi chưa backup, nhưng không đọc đầu tiên.
- `__pycache__/`: artifact Python runtime, không có giá trị khoa học.
- Nhiều report cũ vẫn giữ để truy vết. Khi viết luận văn, ưu tiên đọc `PHASE_SUMMARY.md` của từng phase rồi mở report được dẫn trong đó.

## Phase chưa có thư mục riêng

- `Phase 7` và `Phase 9` chưa có thư mục triển khai riêng trong `Guiding` tại thời điểm lập bản đồ này.
- Kế hoạch/ý tưởng của các phase này nằm trong `Guiding/Mục lục/` và timeline, không phải artifact chạy chính.

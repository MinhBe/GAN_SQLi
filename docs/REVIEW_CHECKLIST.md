# Review Checklist

## Protocol
- [ ] Research question đã freeze.
- [ ] Dataset có source/lineage.
- [ ] Train/test không trùng lineage.
- [ ] Accuracy không phải metric headline.

## Code
- [ ] SeqGAN output chỉ là candidate.
- [ ] Không có scanner/request tới hệ thống thật.
- [ ] Không có hard-coded payload list.
- [ ] Generated/quality_passed/selected được báo riêng.

## Kaggle
- [ ] Dataset path đúng.
- [ ] GPU bật nếu chạy SeqGAN lớn.
- [ ] Output được lưu trong `/kaggle/working`.

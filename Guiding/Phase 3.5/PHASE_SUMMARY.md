# Phase 3.5 - Disciplined GAN Retry Summary

## Mục tiêu

Phase 3.5 là nhánh retry/diagnostic sau khi Phase 3 gate chọn `MLE_MAIN`. Ý tưởng là cho GAN full-sequence một cơ hội kỹ thuật công bằng hơn trước khi đóng hướng này:

- Straight-through/Gumbel variants.
- SpectralNorm/TTUR.
- WGAN-GP/token-level variants.

## Trạng thái thư mục hiện tại

Trong `Guiding/Phase 3.5` hiện chỉ còn `__pycache__/`. Không có script/report chính còn nằm trực tiếp trong thư mục này tại thời điểm lập bản đồ.

Tuy vậy, nội dung Phase 3.5 đã được ghi lại trong timeline:

- `Guiding/timeline/Kết luận 210526.md`
- `Guiding/timeline/Kết luận 220526.md`

## Chuyện gì đã xảy ra theo timeline

Các biến thể GAN full-sequence tiếp tục không tạo frontier tốt hơn MLE:

- SpectralNorm/TTUR collapse ở screening.
- WGAN-GP collapse ở screening.
- Straight-through Gumbel sống hơn nhưng đổi syntax quality lấy diversity.
- D có xu hướng bão hòa, G loss tăng mạnh, generator trôi khỏi cú pháp hợp lệ.

Nhận định kỹ thuật:

- Vấn đề không chỉ là thiếu tuning.
- Đơn vị sinh full-sequence token là không phù hợp với SQLi payload trong dữ liệu này.
- Cần đổi đơn vị sinh từ toàn chuỗi sang slot/action/surgery có ràng buộc.

## File trong Phase 3.5

| File/thư mục | Tác dụng |
|---|---|
| `__pycache__/` | Cache Python runtime. Không phải artifact khoa học, không cần đọc. |

## Vai trò trong toàn dự án

Phase 3.5 là cầu nối lập luận: không chỉ mini GAN Phase 2 fail, mà cả các retry full-sequence có kỷ luật cũng không đủ. Điều này mở đường cho Phase 8: `Paired Masked Payload-Surgery GAN`, tức GAN vẫn là trung tâm nhưng không còn sinh toàn chuỗi.

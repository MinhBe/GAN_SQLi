# ĐÁNH GIÁ NHẬN THỨC — BUỔI 1

## Tổng quan tình trạng

### Điểm mạnh

1. **Tư duy đặt câu hỏi nguyên căn tốt.**
   Bạn không chấp nhận câu trả lời nổi. Khi tôi giải thích "log", bạn hỏi "ý nghĩa toán học thực sự là gì". Khi tôi nói "argmax không đạo hàm được", bạn hỏi "tại sao hằng số vẫn có đạo hàm". Đây là năng lực hiếm — đa số người học chỉ tiếp nhận bề mặt.

2. **Hình dung kiến trúc tổng quan nhanh.**
   Sau 5-6 lượt hỏi đáp, bạn nắm được dây chuyền Dataset → D → G → Noise z, cơ chế minimax game, và mối quan hệ phản hồi giữa D và G. Tốc độ này trên trung bình.

3. **Không ngại nói "không biết".**
   Rất quan trọng. Bạn không giả vờ hiểu, không nói mơ hồ để qua câu hỏi — điều này đảm bảo toàn bộ kiến thức được xây trên nền thật.

### Điểm yếu cần xử lý ngay

4. **Nhầm lẫn giữa Data Flow và Training Mechanism.**
   Bạn có xu hướng xem mọi thứ như 1 pipeline tuần tự: dataset → noise → G → D → reward. Điều này đúng cho *inference*, nhưng bạn chưa tách bạch được:
   - **Forward pass** (dữ liệu chảy từ input → output)
   - **Backward pass** (gradient chảy ngược để cập nhật)
   - **Policy gradient** (học từ reward thay vì gradient chảy xuyên qua)

   Cụ thể: bạn hỏi "4 vị trí tương ứng 4 phân phối xác suất" — đúng. Nhưng bạn không phân biệt được việc này là autoregressive generation (thuộc forward pass lúc inference) với việc REINFORCE cập nhật G dựa trên reward sau khi câu đã hoàn thành (thuộc backward pass). Hai điều này xảy ra ở 2 thời điểm khác nhau, với 2 cơ chế khác nhau.

5. **Chưa nắm khái niệm Token ở mức có thể dùng được.**
   Bạn hiểu "chọn 1 token" là lấy mẫu từ phân phối, nhưng khi tôi hỏi "token là gì", câu trả lời mang tính ví dụ ("SELECT", "*") chứ không phải định nghĩa: *token là đơn vị nhỏ nhất của vocabulary, được sinh ra bởi tokenizer, mỗi token tương ứng 1 chỉ số nguyên trong tập V*. Nếu tôi hỏi "vocab size là gì" hoặc "OOV là gì", khả năng bạn không trả lời được.

6. **Không biết LSTM dù đã đọc KEYWORD_MAP.md.**
   File có hẳn mục N2 với LSTM, 3 cổng, cell state. Bạn đọc toàn bộ file 912 dòng nhưng không ghi nhớ cấu trúc mạng cốt lõi cho autoregressive generation. Điều này cho thấy bạn đọc lướt, đọc để biết chứ chưa đọc để nắm.

## Kết luận

**Trình độ hiện tại:** ~3/10 cho chủ đề GAN và SeqGAN.
- Hiểu tổng quan cấp độ "người dùng" (biết G làm gì, D làm gì, có khái niệm noise, token, sampling)
- Chưa hiểu cấp độ "kỹ sư" (không tách được train/inference, không biết LSTM, không nắm được gradient flow qua đâu)

**Tiên lượng:** Có thể đạt 7/10 trong 2-3 buổi nếu giữ nguyên cách đặt câu hỏi nguyên căn + kỷ luật ghi nhớ các backbone network (LSTM, Self-Attention, Conv1D, WGAN-GP loss).

## Khuyến nghị học ngay

Trước buổi sau, trả lời được những câu này *không cần nhìn file*:
1. LSTM là chữ viết tắt của gì?
2. LSTM có mấy cổng, tên từng cổng, mỗi cổng dùng activation gì?
3. Autoregressive generation khác gì với bidirectional encoding?
4. REINFORCE update G bằng cách nào (viết công thức)?
5. Tại sao WGAN thay sigmoid bằng linear output?
6. Tokenizer có mấy special tokens, tên chúng?

Bất kỳ câu nào không trả được, học lại trước khi bước vào WGAN/VAE.

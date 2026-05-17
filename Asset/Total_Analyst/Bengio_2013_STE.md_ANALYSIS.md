# Phân Tích Paper: Estimating or Propagating Gradients Through Stochastic Neurons for Conditional Computation

## Phần A: Thông Tin Cơ Bản & Phân Loại
- **Tiêu đề:** Estimating or Propagating Gradients Through Stochastic Neurons for Conditional Computation
- **Tác giả:** Yoshua Bengio, Nicholas Léonard, Aaron Courville
- **Năm xuất bản:** 2013
- **Phân loại:** Gradient Estimation, Stochastic Neurons, Conditional Computation.
- **Từ khóa:** Back-propagation, REINFORCE, Straight-through estimator (STE), Stochastic Binary Neurons.

## Phần B: Dữ Liệu
- **Tập dữ liệu:** MNIST.
- **Đặc điểm:** Chữ số viết tay đen trắng 28x28.
- **Mục tiêu:** Sử dụng các đơn vị gating ngẫu nhiên (stochastic gating units) để tắt/mở các phần của mạng nơ-ron nhằm giảm chi phí tính toán.

## Phần C: Kiến Trúc Mô Hình
- **Gating Path:** 400 đơn vị tanh, sau đó là 2000 đơn vị gating ngẫu nhiên.
- **Main Path:** 2000 đơn vị ẩn.
- **Cơ chế:** Đầu ra của đơn vị gating ($h_i \in \{0, 1\}$) được nhân với đơn vị tương ứng trên đường chính ($H_i$). Chỉ các $H_i$ có $h_i=1$ mới cần tính toán.

## Phần D: Training Configuration
- **Optimizer:** Momentum (cho STS), không dùng cho SBN.
- **Learning rate:** 0.1 cho toàn bộ mạng, ngoại trừ SBN (gating path dùng lr nhỏ hơn 100 lần).
- **Constraints:** Max-norm của trọng số được giới hạn bằng 2.
- **Sparsity target:** 10% (sử dụng KL-divergence hoặc L1-norm).

## Phần E: Beyond Baselines
- Đề xuất các phương pháp để lan truyền gradient qua các hàm không khả vi (như hàm ngưỡng).
- Giới thiệu **Straight-through estimator (STE)**: giả định hàm ngưỡng là hàm đồng nhất trong quá trình back-prop.
- Giới thiệu **STS (Stochastic Times Smooth)**: kết hợp phần ngẫu nhiên và phần trơn để ước lượng gradient.

## Phần F: Ablation & Experiments
- So sánh 4 phương pháp: Noisy Rectifier, Straight-through, STS, Stochastic Binary Neuron (REINFORCE).
- So sánh với các baseline: Non-noisy rectifier, Sigmoid + Noise, Sigmoid truyền thống.
- Kết quả: Straight-through đạt lỗi thấp nhất trên tập validation (1.42%) và test (1.39%).

## Phần G: Stability & Mode Collapse
- **Stability:** REINFORCE có phương sai gradient cao, cần baseline để ổn định. STE dù thiên kiến (biased) nhưng thực tế lại hoạt động rất tốt và ổn định.
- **Mode Collapse:** Không áp dụng trực tiếp vì đây không phải mô hình sinh đối kháng, nhưng đề cập đến việc điều chỉnh bias để tránh các unit bị "chết" (luôn bằng 0).

## Phần H: Kết Quả & Đánh Giá
- Chứng minh rằng có thể huấn luyện mạng có các quyết định ngẫu nhiên bằng gradient descent.
- Tiết kiệm đáng kể tài nguyên tính toán (chỉ tính 10% mạng) mà vẫn giữ được độ chính xác tương đương mạng đầy đủ.

## Phần I: Đánh Giá Cá Nhân
- **Ưu điểm:** Cung cấp nền tảng lý thuyết và thực nghiệm cho các kỹ thuật như Straight-through estimator, hiện đang được dùng rộng rãi trong Quantization và VQ-VAE.
- **Hạn chế:** Các thí nghiệm chỉ ở quy mô nhỏ (MNIST).

## Trích xuất kiến thức (Skill-style)
- **Core Question:** Làm thế nào để lan truyền gradient qua các hàm "cứng" (như chọn 0 hoặc 1)?
- **3-tier explanation:**
    - **Child:** Giống như khi bạn muốn dạy một robot bấm nút, nhưng nó chỉ biết làm hoặc không. Bạn giả vờ như nó đã làm "một chút" để chỉ cho nó biết nếu làm nhiều hơn thì kết quả sẽ tốt hơn.
    - **Student:** Paper đề xuất các bộ ước lượng gradient. Straight-through estimator đơn giản là bỏ qua đạo hàm của hàm ngưỡng (coi như bằng 1) khi tính back-prop. REINFORCE sử dụng xác suất để ước lượng gradient không thiên kiến nhưng có phương sai cao.
    - **Expert:** Bài báo khám phá các kỹ thuật lan truyền gradient qua stochastic neurons. Đặc biệt, STS unit sử dụng Taylor expansion để xấp xỉ kỳ vọng của hàm mất mát. STE được chứng minh là hiệu quả nhất dù về mặt lý thuyết là thiên kiến, đóng vai trò quan trọng trong tối ưu hóa mạng nơ-ron rời rạc.
- **Misconception Seeds:** Nghĩ rằng không thể back-prop qua hàm ngưỡng; nghĩ rằng REINFORCE luôn tốt hơn vì nó không thiên kiến.
- **Transfer Question:** Làm thế nào để kết hợp STE vào việc nén mô hình (model compression) cho các thiết bị nhúng?

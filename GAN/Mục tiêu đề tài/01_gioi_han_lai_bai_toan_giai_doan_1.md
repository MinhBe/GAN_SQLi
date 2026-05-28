# Giới hạn lại bài toán giai đoạn 1

Ngày lập: 2026-05-28

## 1. Kết luận định vị

Bài toán không nên được trình bày là:

> Dùng GAN sinh payload SQL Injection.

Cách đặt này quá rộng, dễ bị đánh giá là triển khai kỹ thuật, và chưa trả lời được các câu hỏi tối thiểu: sinh để làm gì, đo bằng gì, so với cái gì, dữ liệu từ đâu, kết quả chứng minh điều gì.

Bài toán giai đoạn 1 nên được giới hạn lại thành:

> Xây dựng và kiểm chứng một protocol đánh giá an toàn, tái lập được cho các phương pháp sinh payload SQL Injection, thông qua việc tái triển khai các mô hình/paper lõi và so sánh chúng với baseline rule/mutation trên cùng bộ dữ liệu, cùng evaluator và cùng WAF testbed local.

Trong giai đoạn 1, GAN là một đối tượng được khảo sát và tái triển khai, không phải toàn bộ đóng góp của đề tài.

## 2. Một câu bài toán

> Làm thế nào để đánh giá công bằng, an toàn và tái lập được việc sinh payload SQL Injection bằng generative models, và các mô hình được thầy chỉ hoặc từ paper có thực sự tốt hơn baseline rule/mutation ở validity, novelty, diversity và khả năng kiểm thử WAF hay không?

## 3. Phạm vi được giữ lại

Giai đoạn 1 chỉ tập trung vào 5 việc:

1. Phân loại toàn bộ paper OCR hiện có.
2. Chọn paper lõi cần chạy hoặc tái triển khai.
3. Lập paper card và dataset/source card.
4. Xây evaluator chung: validity, duplicate, novelty, diversity, WAF allow/block.
5. Chạy baseline và ít nhất một mô hình/pipeline từ paper hoặc code thầy chỉ.

Đối tượng nghiên cứu là payload SQL Injection và biến thể của payload, không phải khai thác hệ thống thật.

## 4. Phạm vi loại bỏ khỏi giai đoạn 1

Không đưa vào mục tiêu chính của giai đoạn 1:

- Cloud WAF hoặc website thật.
- Diffusion model.
- Nhiều WAF cùng lúc.
- Nhiều biến thể GAN nâng cao nếu chưa có baseline.
- Defense recommendation đầy đủ.
- Tuyên bố có mô hình mới trước khi có reproduction và ablation.
- Trộn tùy tiện dataset IDS như CIC-IDS2017, UNSW-NB15, NSL-KDD vào bài toán payload SQLi.

Các mục này chỉ để future work hoặc phụ lục nếu còn thời gian.

## 5. Đóng góp chính nên chốt

Đóng góp chính phù hợp nhất hiện tại là:

> Protocol đánh giá payload SQLi sinh bởi generative models trong WAF testbed an toàn.

Lý do:

- Phù hợp với tiêu chuẩn của thầy: có vấn đề, căn cứ, phương pháp, metric, baseline, giới hạn.
- Không phụ thuộc vào việc GAN phải thắng mọi baseline.
- Nếu GAN tốt, có thể mở rộng thành model contribution.
- Nếu GAN fail, kết quả vẫn có giá trị vì chỉ ra giới hạn, failure mode và điều kiện đánh giá.

## 6. Câu hỏi nghiên cứu giai đoạn 1

RQ1. Các paper hiện có đang sinh hoặc augment SQLi payload bằng cách nào?

RQ2. Paper nào có đủ thông tin để tái triển khai: dataset, code, mô hình, metric, testbed?

RQ3. Baseline rule/mutation đạt kết quả thế nào trên evaluator chung?

RQ4. Mô hình từ paper hoặc code thầy chỉ có tái lập được claim không?

RQ5. Phương pháp nào tốt hơn baseline ở tiêu chí nào: validity, ASR, uniqueness, novelty, diversity, hoặc runtime?

## 7. Metric tối thiểu

Không dùng một metric chung chung như accuracy để kết luận toàn bộ bài toán. Giai đoạn 1 cần tối thiểu các metric sau:

| Metric | Ý nghĩa |
|---|---|
| Validity rate | Payload hợp lệ về cú pháp/định dạng theo evaluator. |
| ASR / WAF allow rate | Tỷ lệ payload đi qua WAF local trong môi trường được phép. |
| Uniqueness | Tỷ lệ payload không trùng lặp trong output. |
| Novelty | Mức khác biệt với seed/train payload. |
| Diversity | Độ phủ nhiều dạng biến thể SQLi. |
| Duplicate rate | Mức sinh lặp hoặc mode collapse. |
| Failure distribution | Fail vì syntax, semantic, duplicate, blocked, timeout hay evaluator error. |

## 8. Baseline bắt buộc

Trước khi chạy hoặc bảo vệ mô hình GAN, cần có ít nhất 2 baseline:

| Baseline | Vai trò |
|---|---|
| Template/rule baseline | Mốc đơn giản, dễ tái lập, cho biết seed/template cơ bản đạt được gì. |
| Mutation baseline | Mốc mạnh hơn, gần với WAF evasion thực tế, bắt buộc để so với GAN sinh mutation. |

Nếu chưa có baseline, mọi kết luận kiểu "GAN tốt" đều chưa đủ căn cứ.

## 9. Testbed an toàn

Testbed chính:

- ModSecurity + OWASP Core Rule Set local.

Testbed phụ nếu kịp:

- Coraza.

Ranh giới:

- Chỉ chạy local/lab/sandbox.
- Không gửi payload vào website thật.
- Không test cloud WAF khi chưa có quyền.
- Báo cáo public chỉ dùng thống kê, taxonomy và phân tích; không trình bày payload bypass theo hướng hướng dẫn khai thác.

## 10. Tiêu chí đạt giai đoạn 1

Giai đoạn 1 được xem là đạt nếu có đủ:

- 100% paper OCR được phân loại.
- Ít nhất 5 paper card lõi.
- Danh sách paper cần chạy trước, kèm lý do.
- Dataset/source inventory có trạng thái rõ.
- Evaluator chung chạy được trên sample nhỏ.
- 2 baseline có bảng metric.
- Ít nhất 1 mô hình/pipeline từ paper hoặc code thầy được smoke test hoặc tái triển khai.
- Một bảng so sánh chung giữa baseline và model.
- Một phần failure analysis nói rõ kết quả chưa chứng minh được gì.

## 11. Câu trình bày ngắn với thầy

> Em thu hẹp đề tài về giai đoạn 1 thành bài toán xây dựng protocol đánh giá an toàn và tái lập cho các phương pháp sinh payload SQL Injection. Em sẽ phân loại paper, chọn các mô hình thầy chỉ và paper lõi để tái triển khai, chạy ít nhất hai baseline rule/mutation, rồi đo tất cả bằng cùng evaluator và WAF local. Kết quả giai đoạn này không nhằm tuyên bố ngay một mô hình mới, mà nhằm trả lời bằng số liệu: mô hình nào tái lập được, tốt hơn baseline ở đâu, fail ở đâu, và hướng nào đủ căn cứ để phát triển tiếp.

# Đánh giá hướng đi đề tài theo tiêu chuẩn nghiên cứu chung

Đối tượng đánh giá:

- `Ke_hoach_trien_khai_GAN_SQLi_theo_gop_y_thay.md`
- `Ke_hoach_nghien_cuu_hai_huong.md`

Tiêu chuẩn dùng để đánh giá:

- Vấn đề rõ.
- Lý do rõ.
- Căn cứ rõ.
- Phương pháp rõ.
- Thước đo rõ.
- So sánh rõ.
- Đóng góp rõ.
- Giới hạn rõ.
- Bước tiếp theo rõ.

## 1. Kết luận ngắn

Hướng đi hiện tại đã đáp ứng phần lớn tiêu chuẩn nghiên cứu ở mức kế hoạch, nhưng chưa đáp ứng đầy đủ ở mức bằng chứng thực nghiệm.

Nói cách khác, đề tài hiện tại đã có khung tư duy đúng: biết đặt vấn đề, biết cần baseline, biết cần metric, biết cần dữ liệu có nguồn, biết cần evaluator/WAF, biết cần phân tích failure. Tuy nhiên, phần lớn nội dung vẫn đang ở dạng kế hoạch và thiết kế, chưa có đủ kết quả chạy thật để chứng minh giá trị.

Đánh giá tổng quan:

- Nếu xem như **kế hoạch nghiên cứu**: khoảng `7/10`.
- Nếu xem như **đề tài đã sẵn sàng bảo vệ bằng kết quả**: khoảng `4/10`.

Mức hiện tại:

> Đề tài đang ở giữa mức “kế hoạch luận văn tốt” và “khung nghiên cứu sinh vững”, nhưng chưa phải một nghiên cứu hoàn chỉnh.

## 2. Đánh giá theo từng tiêu chuẩn

| Tiêu chí | Mức đáp ứng | Nhận xét |
|---|---:|---|
| Vấn đề rõ | Tốt | Đề tài đã xác định khá rõ: sinh payload SQL Injection để kiểm thử WAF trong môi trường an toàn. |
| Lý do rõ | Khá tốt | Có nêu vì sao rule/template/mutation chưa đủ và vì sao cần generative models. |
| Căn cứ rõ | Trung bình | Có ý thức về dataset, paper, source card, data card, nhưng chưa có bảng dữ liệu thật đã kiểm kê. |
| Phương pháp rõ | Khá tốt | Pipeline đã rõ: paper/dataset -> seed -> baseline -> generative model -> evaluator/WAF -> metric. |
| Thước đo rõ | Tốt | Metric hợp lý: validity, semantic preservation, ASR, novelty, diversity, transferability, collapse. |
| So sánh rõ | Khá tốt | Đã xác định baseline: rule, mutation, tree-transform, MLE/Transformer, paper baseline. Nhưng chưa có kết quả baseline. |
| Đóng góp rõ | Trung bình | Có nhiều khả năng đóng góp, nhưng chưa chốt một đóng góp chính. |
| Giới hạn rõ | Tốt | Ranh giới an toàn, lab/local testbed, không test hệ thống thật được nêu rõ. |
| Bước tiếp theo rõ | Khá tốt | Có phase, output, tiêu chí nghiệm thu. Nhưng cần thu hẹp và gắn với kết quả cụ thể hơn. |

## 3. So sánh hai tài liệu

### 3.1. `Ke_hoach_trien_khai_GAN_SQLi_theo_gop_y_thay.md`

Tài liệu này mạnh ở vai trò roadmap triển khai.

Điểm mạnh:

- Có pipeline tổng thể rõ.
- Có danh sách phase từ tài liệu, baseline, mô hình, testbed, phân tích đến artifact.
- Có metric khá đầy đủ.
- Có nhận diện rủi ro: dual-use, data leakage, mode collapse, WAF feedback sparse.
- Có checklist nghiệm thu trước khi trình bày.

Điểm yếu:

- Phạm vi còn rộng: GAN, LLM, diffusion, nhiều WAF, nhiều baseline, nhiều artifact.
- Có nguy cơ trở thành kế hoạch lớn nhưng khó hoàn thành.
- Một số phần vẫn là “nên có”, chưa biến thành việc đã làm.
- Đóng góp chính chưa được chốt.

Đánh giá:

> Tốt cho triển khai và quản lý công việc, nhưng cần thu hẹp để trở thành một đề tài nghiên cứu có trọng tâm.

### 3.2. `Ke_hoach_nghien_cuu_hai_huong.md`

Tài liệu này mạnh hơn về mặt nghiên cứu.

Điểm mạnh:

- Đặt lại đề tài từ đầu, không phụ thuộc pipeline cũ.
- Chia thành hai trục hợp lý:
  - Trục paper: người ta đã làm gì, tái hiện được gì, claim nào đúng/sai.
  - Trục theo yêu cầu thầy: bài toán, dữ liệu, nhãn, evaluator, metric, baseline, failure.
- Có câu hỏi nghiên cứu rõ.
- Có ranh giới an toàn tốt.
- Có hướng đề xuất đóng góp sau khi tái hiện paper.
- Có khuyến nghị hợp lý: ưu tiên `Protocol contribution`.

Điểm yếu:

- Vẫn chưa có kết quả tái hiện paper.
- Chưa có paper card thật đã hoàn thiện.
- Chưa có dataset card thật với số liệu cụ thể.
- Chưa có baseline result table.
- Chưa chốt cuối cùng giữa protocol contribution, model contribution và defense contribution.

Đánh giá:

> Đây là tài liệu tốt hơn để làm nền học thuật cho đề tài. Nó thể hiện tư duy nghiên cứu trưởng thành hơn vì bắt đầu từ paper, reproduction, gap và proposal.

## 4. Hướng đi đã đáp ứng những gì?

### 4.1. Đã đặt được bài toán

Đề tài không còn dừng ở câu “dùng GAN sinh SQL Injection”.

Cách đặt hiện tại tốt hơn:

> Đánh giá xem generative models có thể sinh payload SQL Injection hợp lệ, có tính mới, có ý nghĩa và hữu ích cho kiểm thử WAF tốt hơn các baseline rule/mutation truyền thống hay không.

Đây là cách đặt vấn đề có thể nghiên cứu được vì có:

- Đối tượng rõ: payload SQL Injection.
- Môi trường rõ: WAF/testbed an toàn.
- Mục tiêu rõ: kiểm thử WAF.
- Tiêu chí rõ: hợp lệ, mới, đa dạng, semantic, bypass/evasion.

### 4.2. Đã có tư duy so sánh

Bạn không còn đặt GAN là trung tâm tuyệt đối.

Hướng hiện tại đã đặt GAN bên cạnh:

- Rule/template.
- Mutation.
- Tree-transform.
- RL.
- MLE/Transformer.
- LLM.
- Paper baseline.

Đây là điểm mạnh vì một đề tài nghiên cứu không được chứng minh bằng việc “mô hình chạy được”, mà bằng việc “mô hình tốt hơn hoặc khác baseline ở tiêu chí nào”.

### 4.3. Đã có metric đúng hướng

Các metric được chọn là hợp lý:

- `Validity rate`: payload có hợp lệ không.
- `Semantic preservation`: payload có giữ ý định tấn công không.
- `ASR`: payload có qua WAF/testbed không.
- `Uniqueness`: có bị lặp không.
- `Novelty`: có khác seed/train không.
- `Diversity`: có phủ nhiều dạng không.
- `Transferability`: có qua nhiều WAF không.
- `Failure distribution`: fail vì syntax, semantic, duplicate, blocked hay timeout.

Đây là bộ metric tốt hơn nhiều so với việc chỉ báo “accuracy” hoặc chỉ đưa vài payload ví dụ.

### 4.4. Đã có ranh giới an toàn

Hai tài liệu đều nêu rõ:

- Chỉ chạy trong local lab/testbed.
- Không test hệ thống thật.
- Không test cloud WAF nếu không có quyền.
- Không công bố payload bypass chi tiết.
- Tập trung vào thống kê, taxonomy, metric, defense recommendation.

Đây là điểm rất quan trọng vì đề tài thuộc nhóm dual-use.

### 4.5. Đã có nhận thức về failure

Bạn đã đưa vào các rủi ro nghiên cứu quan trọng:

- Mode collapse.
- Reward sparsity.
- Semantic break.
- Data leakage.
- Label noise.
- WAF feedback sparse.
- Compute limitation.

Điều này thể hiện tư duy nghiên cứu tốt: không né thất bại, mà chuẩn bị cách đo và phân tích thất bại.

## 5. Những điểm chưa đáp ứng

### 5.1. Dữ liệu chưa được chứng minh bằng số thật

Hiện tại đã có mẫu:

- Dataset card.
- Source card.
- Payload source card.
- Seed corpus manifest.
- Safe split rule.

Nhưng còn thiếu bảng thật:

| Cần có | Trạng thái hiện tại |
|---|---|
| Nguồn dữ liệu cụ thể | Mới liệt kê, chưa kiểm kê đầy đủ |
| Raw rows | Chưa có số liệu cuối |
| Usable rows | Chưa có số liệu cuối |
| Duplicate rows | Chưa có thống kê |
| Invalid rows | Chưa có thống kê |
| License | Chưa xác minh đầy đủ |
| Label source | Mới định nghĩa, chưa kiểm chứng |
| Split rule | Đã có ý tưởng, chưa có file split thật |

Đây là khoảng trống lớn nhất nếu chuẩn bị trình bày với thầy.

### 5.2. Baseline chưa có kết quả

Kế hoạch baseline đã tốt, nhưng chưa đủ nếu chưa chạy.

Cần có ít nhất:

- Template/rule baseline.
- Random hoặc rule-based mutation baseline.
- Cùng testbed.
- Cùng số lượng payload.
- Cùng metric.

Khi chưa có baseline result, chưa thể kết luận generative model tốt hơn cái gì.

### 5.3. Đóng góp chưa chốt

Hiện có ba hướng đóng góp:

1. Protocol contribution.
2. Model/loss contribution.
3. Defense contribution.

Cả ba đều hợp lý, nhưng không nên ôm cả ba làm đóng góp chính.

Đánh giá khả thi:

| Hướng đóng góp | Mức phù hợp hiện tại | Nhận xét |
|---|---:|---|
| Protocol contribution | Cao | Phù hợp nhất, ít phụ thuộc vào việc GAN thắng lớn. |
| Model/loss contribution | Trung bình | Cần kết quả train ổn định và ablation. Rủi ro cao hơn. |
| Defense contribution | Trung bình | Cần phân tích failure đủ sâu từ WAF/testbed. |

Khuyến nghị:

> Nên chốt đóng góp chính là protocol đánh giá payload SQLi sinh bởi generative models trong WAF testbed an toàn.

### 5.4. Phạm vi còn rộng

Các thành phần đang xuất hiện trong kế hoạch:

- GAN.
- SeqGAN.
- Gumbel GAN.
- RelGAN.
- MaskGAN.
- LLM.
- Diffusion.
- ModSecurity CRS.
- Coraza.
- WAF-ML.
- Cloud WAF.
- Defense recommendation.
- Docker/CI/artifact.

Đây là quá rộng nếu xem là mục tiêu chính.

Nên thu hẹp:

- 1 testbed chính: ModSecurity + OWASP CRS.
- 1 testbed phụ nếu kịp: Coraza.
- 2 baseline: template/rule và mutation.
- 1 generative method chính.
- 1 contribution chính: protocol.

### 5.5. Chưa có ngưỡng nghiệm thu định lượng

Bạn đã có metric, nhưng chưa có ngưỡng để biết thế nào là đạt.

Ví dụ cần bổ sung:

| Metric | Ngưỡng nghiệm thu gợi ý |
|---|---|
| Validity rate | Cao hơn baseline hoặc đạt mức tối thiểu đã định |
| Duplicate rate | Thấp hơn baseline/template |
| Novelty rate | Không chỉ near-copy từ seed/train |
| ASR | So sánh công bằng với mutation baseline |
| Runtime | Chạy được trong giới hạn tài nguyên hiện có |
| Reproducibility | Có seed/config/log để chạy lại |

Không nhất thiết phải đặt ngưỡng quá cao ngay, nhưng phải có tiêu chí để biết kết quả đủ tốt hay chưa.

## 6. Mức độ đáp ứng hiện tại

| Cấp độ | Trạng thái |
|---|---|
| Demo kỹ thuật | Đã vượt qua về mặt tư duy |
| Kế hoạch luận văn | Đạt khá |
| Nghiên cứu sinh vững | Đang tiến gần |
| Hướng bài báo | Chưa đạt |
| Đề tài trưởng thành | Chưa đạt |

Giải thích:

- Đã vượt mức demo vì đề tài không chỉ mô tả model, mà đã có câu hỏi nghiên cứu, metric, baseline, evaluator và risk.
- Đạt mức kế hoạch luận văn vì đã có cấu trúc triển khai và tiêu chí nghiệm thu.
- Chưa đạt mức bài báo vì chưa có kết quả thực nghiệm, chưa có reproduction, chưa có ablation, chưa có contribution đã được chứng minh.

## 7. Hướng đi nên chọn

Hướng nên chốt:

> Xây dựng và kiểm chứng một protocol đánh giá payload SQL Injection sinh bởi generative models trong WAF testbed an toàn.

Lý do:

- Phù hợp với tiêu chuẩn của thầy.
- Ít rủi ro hơn việc tuyên bố thuật toán GAN mới.
- Vẫn cho phép dùng GAN/LLM/mutation như đối tượng so sánh.
- Nếu GAN tốt, có thể mở rộng thành model contribution.
- Nếu GAN fail, vẫn có giá trị ở protocol, metric, baseline và failure analysis.

Định vị đề tài nên là:

> Đề tài không chỉ hỏi “GAN có sinh được payload không”, mà hỏi “làm thế nào để đánh giá công bằng, an toàn và tái lập các phương pháp sinh payload SQLi, và phương pháp nào thật sự tạo giá trị so với baseline”.

## 8. Ba việc cần làm ngay

### Việc 1: Tạo dataset inventory thật

Output cần có:

- `dataset_inventory.md`
- `seed_corpus_manifest.csv`
- `split_rule.md`

Cột tối thiểu:

| Field | Ý nghĩa |
|---|---|
| source | Nguồn dữ liệu |
| file | File local |
| raw rows | Số dòng ban đầu |
| usable rows | Số dòng dùng được |
| duplicate rows | Số dòng trùng |
| invalid rows | Số dòng không dùng được |
| label source | Nguồn nhãn |
| license | Giấy phép |
| split group | Nhóm dùng để split an toàn |

### Việc 2: Chạy hai baseline đầu tiên

Baseline tối thiểu:

- Template/rule baseline.
- Mutation baseline.

Testbed tối thiểu:

- ModSecurity + OWASP CRS local.

Metric tối thiểu:

- Validity.
- ASR.
- Uniqueness.
- Novelty.
- Duplicate rate.
- Failure distribution.

### Việc 3: Lập bảng kết quả đầu tiên

Bảng tối thiểu:

| Method | Validity | ASR | Uniqueness | Novelty | Duplicate rate | Main failure |
|---|---:|---:|---:|---:|---:|---|
| Template/rule | TBD | TBD | TBD | TBD | TBD | TBD |
| Mutation | TBD | TBD | TBD | TBD | TBD | TBD |
| Generative v0 | TBD | TBD | TBD | TBD | TBD | TBD |

Khi có bảng này, đề tài sẽ chuyển từ “kế hoạch tốt” sang “nghiên cứu có bằng chứng ban đầu”.

## 9. Kết luận cuối

Hướng đi của bạn là đúng, nhưng cần chuyển nhanh từ kế hoạch sang bằng chứng.

Điểm mạnh hiện tại:

- Bài toán đã rõ.
- Tư duy nghiên cứu đúng.
- Metric tốt.
- Baseline đã được nhận diện.
- Ranh giới an toàn rõ.
- Có ý thức về failure và reproducibility.

Điểm yếu chính:

- Chưa có dataset inventory thật.
- Chưa có baseline result.
- Chưa có reproduction result.
- Chưa chốt contribution chính.
- Scope còn rộng.

Khuyến nghị cuối:

> Chốt hướng chính là protocol đánh giá. Thu hẹp phạm vi. Làm dataset inventory thật. Chạy baseline thật. Tạo bảng kết quả đầu tiên. Sau đó mới quyết định GAN, LLM hay model nào xứng đáng trở thành phần đóng góp tiếp theo.


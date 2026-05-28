# Phân tích yêu cầu thầy cho phần thuyết trình GAN

Nguồn: `Asset/Record_Transcript/Voice 008_sd.md`

Ghi chú: transcript đã được chỉnh thủ công nhưng vẫn có nhiều đoạn `[nghe không rõ]`. Phân tích dưới đây dựa trên các đoạn có ý nghĩa ổn định, đặc biệt quanh phần GAN `00:22:47-01:08:39` và đoạn cuối `02:39:03-02:44:57`.

## 1. Kết luận ngắn

Thầy không chỉ muốn nghe em nói "em dùng GAN để sinh payload SQL Injection". Thầy muốn thấy em có năng lực nghiên cứu: biết đặt vấn đề, biết vì sao cần làm, biết dữ liệu đến từ đâu, biết nhãn đúng sai thế nào, biết kiến trúc vận hành ra sao, biết loss/đánh giá gắn vào mục tiêu nào, biết điểm nghẽn hiện tại là gì, và biết bước tiếp theo để biến một demo thành luận văn/bài báo.

Với phần của em, trọng tâm thầy đang yêu cầu là:

- Làm rõ pipeline tổng thể: dữ liệu đầu vào -> tiền xử lý/template/split an toàn -> Generator -> Discriminator/Evaluator -> tường lửa thực tế -> tiêu chí chọn payload.
- Làm rõ vai trò của tường lửa: dùng để đánh nhãn, đánh giá khả năng bypass, hay feedback vào Generator.
- Làm rõ hàm loss: loss gồm những thành phần nào, mỗi thành phần tối ưu mục tiêu gì, trọng số ra sao, có dùng phản hồi từ tường lửa hay không.
- Làm rõ dữ liệu: nguồn, số dòng, trạng thái tải, số dòng dùng được, trùng lặp, template, nhãn, cách đảm bảo nhãn.
- Làm rõ vấn đề nghiên cứu: tại sao GAN là cần thiết, có bài nào làm chưa, khoảng trống là gì, đóng góp nằm ở dữ liệu hay thuật toán.
- Làm rõ failure hiện tại: mode collapse sau khoảng 500 lần lặp, Discriminator quá mạnh, chưa có bước đánh giá/loss hoàn chỉnh.

## 2. Những tín hiệu chính từ thầy

### 2.1. Thầy muốn tư duy what/how/why

Ở `00:15:17-00:16:18`, thầy nhấn mạnh phải xem đã có bài báo nào làm tương tự chưa, phải hiểu tại sao, và mọi vấn đề phải có logic. Câu then chốt là phải trả lời được `what`, `how`, `why`.

Diễn giải cho phần GAN:

- What: Em đang sinh loại payload nào, đầu vào/đầu ra là gì, tiêu chí thành công là gì.
- How: GAN sinh thế nào, Discriminator học gì, tường lửa tham gia ở đâu, loss tính thế nào.
- Why: Vì sao cần GAN thay vì template/rule/random mutation; vì sao kiến trúc này tốt hơn cách cũ.

### 2.2. Thầy muốn dữ liệu có căn cứ

Ở `00:24:02-00:24:50`, thầy hỏi về tên dataset, nguồn, số dòng, trạng thái, tên file, tải thành công hay chưa. Ở `00:30:03-00:32:29`, thầy hỏi "split an toàn là gì", tiền xử lý để làm gì, từ 14 triệu dòng ra template như thế nào.

Diễn giải cho phần GAN:

- Không được chỉ nói "em có 14 triệu dữ liệu".
- Phải nói rõ 14 triệu đến từ đâu, bao nhiêu dòng dùng được, bao nhiêu bị loại, vì sao loại.
- Phải có ví dụ cụ thể cho từng bước xử lý, không chỉ vẽ pipeline.
- Các con số trên slide phải ăn khớp với quy trình.

### 2.3. Thầy muốn nhãn/chất lượng được kiểm chứng

Ở `00:18:01-00:19:24`, thầy nói dữ liệu có thể sai, gán nhãn không phải 100% đúng, nếu nhãn sai thì mô hình sai. Thầy gợi ý dùng VirusTotal/hệ thống chuyên gia để tham chiếu, không tự gán nhãn tùy tiện.

Diễn giải cho phần GAN:

- Payload "đúng cú pháp SQL" chưa đủ.
- Payload "được Discriminator cho là thật" chưa đủ.
- Payload cần được kiểm tra bằng evaluator/tường lửa/rule/parser/benchmark có căn cứ.
- Cần phân biệt nhãn: malicious/benign, valid/invalid, bypass/non-bypass, realistic/non-realistic.

### 2.4. Thầy muốn thấy mô hình tổng thể trước khi xem kết quả

Ở `00:52:38-00:53:46`, thầy yêu cầu đi vào mô hình tổng thể, hỏi vị trí Generator, Discriminator, tường lửa thực tế, dữ liệu sinh ra chạy vào đâu. Đây là điểm rất quan trọng.

Diễn giải cho phần GAN:

- Slide kết quả không nên đứng trước slide kiến trúc.
- Mỗi mũi tên trong sơ đồ phải có nghĩa: dữ liệu gì đi qua, output là gì, dùng để train hay chỉ đánh giá.
- Nếu tường lửa vừa đánh nhãn vừa đánh giá bypass, phải tách rõ hai vai trò.

### 2.5. Thầy muốn loss và cơ chế học, không chỉ kiến trúc

Ở `00:55:12-00:55:24`, thầy hỏi hàm loss tính như thế nào và dùng khối đánh giá ra sao. Em trả lời là chưa tới bước đó vì mô hình đang mode collapse ở khoảng 500 lần lặp.

Diễn giải cho phần GAN:

- Đây là lỗ hổng lớn nhất của phần thuyết trình hiện tại.
- Nếu chưa có loss hoàn chỉnh, phải trình bày rõ "current status" và "planned loss".
- Phải có phương án xử lý mode collapse: balancing G/D, label smoothing, gradient penalty, entropy/diversity reward, pretraining, curriculum, sampling temperature, hoặc chuyển sang objective khác.

### 2.6. Đoạn cuối: thầy muốn cơ chế có tính học được, tổng quát hóa và hợp lý về chi phí

Ở `02:39:03-02:44:57`, thầy nói một cơ chế nếu chỉ khô cứng thì chưa đủ; nếu học trong quá trình mới thì khó nhưng mới xứng đáng. Thầy nhắc tới việc mô hình phải tự xác định, phải nghĩ đến tổng quát hóa, chi phí khi chạy thêm nhiều lần qua Transformer, phân biệt training/inference, và cơ chế kết hợp Temporal/Spatial thay vì tách rời.

Diễn giải cho phần GAN:

- Với em, tương đương là không chỉ hard-code rule/template rồi gọi là GAN.
- Cần chứng minh cơ chế sinh có khả năng học phân phối payload và tổng quát hóa ra biến thể mới.
- Cần nói rõ chi phí huấn luyện và suy diễn: sinh payload có nhanh không, dùng tường lửa thật trong loop có quá chậm không, nếu chậm thì dùng proxy/evaluator thế nào.
- Cần có cơ chế kết hợp các tín hiệu: syntactic validity, semantic attack intent, discriminator realism, WAF bypass, diversity.

## 3. Thầy mong muốn gì ở một phần thuyết trình nghiên cứu

Đây là bộ tiêu chí rút ra từ toàn cuộc họp, không chỉ phần GAN.

### Tiêu chí 1: Vấn đề phải sắc

- Nói rõ bài toán một câu: "Sinh payload SQL Injection có khả năng hợp lệ, đa dạng, realistic và có khả năng bypass/evasion".
- Nói rõ vì sao bài toán khó: cú pháp SQL, ngữ cảnh payload, nhãn, bypass WAF, mode collapse, đánh giá không đơn giản.
- Nói rõ đối tượng nghiên cứu: payload, không phải toàn bộ request/web app nếu em chưa làm tới.
- Nói rõ giới hạn: loại SQLi nào, dataset nào, WAF/evaluator nào.
- Nói rõ câu hỏi nghiên cứu: "GAN có sinh được payload tốt hơn template/mutation không?"

### Tiêu chí 2: Related work phải là nền cho khoảng trống

- Có bảng so sánh các nhóm phương pháp: rule/template, mutation/fuzzing, ML/NLP generation, GAN/SeqGAN, LLM-based generation nếu có.
- Mỗi nhóm cần nêu data, method, metric, limitation.
- Không chỉ liệt kê bài báo; phải nói bài đó thiếu gì so với mục tiêu của em.
- Chỉ ra khoảng trống: thiếu đánh giá với WAF thật, thiếu kiểm chứng nhãn, thiếu diversity/validity trade-off, thiếu phân tích mode collapse.
- Kết luận rõ contribution của em nằm ở đâu: dữ liệu, kiến trúc, loss, evaluator, hay protocol đánh giá.

### Tiêu chí 3: Dữ liệu phải truy vết được

- Mỗi dataset có tên, nguồn, file, số dòng raw, số dòng sau lọc, trạng thái tải.
- Có bảng lỗi/loại bỏ: duplicate, invalid SQL, không phải payload, thiếu nhãn, encoding lỗi.
- Có ví dụ trước/sau tiền xử lý.
- Có cách chia train/dev/test tránh leakage.
- Có tiêu chí "split an toàn" được định nghĩa bằng quy tắc và ví dụ.

### Tiêu chí 4: Kiến trúc phải giải thích được

- Sơ đồ tổng thể phải có input/output rõ.
- Mỗi khối phải trả lời: nhận gì, làm gì, trả gì, train hay inference.
- Generator, Discriminator, Evaluator/WAF không được vẽ nhập nhằng.
- Nếu WAF dùng trong training, phải nói rõ feedback đi vào loss thế nào.
- Nếu WAF chỉ dùng evaluation, phải tách khỏi loop huấn luyện.

### Tiêu chí 5: Loss/metric phải gắn mục tiêu

- Loss của Generator tối ưu điều gì: realism, validity, bypass, diversity.
- Loss của Discriminator phân biệt cái gì: real/fake, class, validity, attack type.
- Metric phải gồm ít nhất: validity rate, uniqueness/diversity, bypass rate, detection/evasion score, similarity/novelty, collapse indicator.
- Có baseline để so: template, random mutation, MLE/Transformer, SeqGAN/Gumbel-SeqGAN nếu liên quan.
- Có ablation: bỏ WAF feedback, bỏ diversity penalty, bỏ pretraining, đổi temperature.

### Tiêu chí 6: Kết quả phải biết tự phê bình

- Không chỉ đưa số tốt nhất; cần best/mean/std qua nhiều seed.
- Nếu mode collapse, phải có dấu hiệu đo được: unique ratio giảm, entropy giảm, lặp payload, discriminator overpower.
- Nếu chưa xong, nói rõ hiện trạng và kế hoạch xử lý.
- Biết chỉ ra điểm yếu của chính mô hình.
- Biết nói kết quả hiện tại đủ cho mức nào: demo, luận văn, hay bài báo.

## 4. Em cần làm gì ngay cho phần GAN

1. Viết lại slide đầu của phần GAN thành một câu bài toán, một câu khoảng trống, một câu đóng góp.
2. Làm bảng dataset: `name`, `source`, `raw rows`, `usable rows`, `file`, `status`, `notes`.
3. Tạo slide "Data pipeline" có ví dụ payload qua từng bước: raw -> clean -> template -> tokenized -> train split.
4. Tạo slide "Model overview" trước slide kết quả: Generator, Discriminator, Evaluator/WAF, output.
5. Tạo slide "Training objective" dù chưa xong: current loss, planned loss, WAF feedback/proxy.
6. Tạo slide "Mode collapse diagnosis": hiện tượng, bằng chứng, giả thuyết nguyên nhân, cách xử lý.
7. Tạo slide "Evaluation protocol": validity, diversity, bypass, novelty, comparison baseline.
8. Tạo slide "What is new": em mới ở dữ liệu, evaluator, loss, hay architecture?
9. Tạo slide "Next experiment": 3 thí nghiệm gần nhất và điều kiện để thầy nói "OK".

## 5. Kiến trúc thuyết trình đạt tiêu chí của thầy

### Tầng 0: Một câu định vị

Mục tiêu: trong 30 giây, người nghe biết em làm gì và vì sao đáng nghe.

Khung nói:

> Em nghiên cứu mô hình sinh payload SQL Injection bằng GAN, với mục tiêu sinh ra payload hợp lệ, đa dạng, có tính thực tế, và được đánh giá bằng cả Discriminator lẫn tường lửa/evaluator thực tế.

### Tầng 1: Bài toán và khoảng trống

Slide cần có:

- Problem statement.
- Why hard.
- Existing approaches.
- Gap.
- Research questions.

Quan điểm cải thiện:

1. Đừng mở đầu bằng "em có dataset 14 triệu"; hãy mở đầu bằng bài toán.
2. Nói rõ payload sinh ra dùng để làm gì: augmentation, adversarial testing, evasion research, hay benchmark.
3. Phân biệt "sinh giống dữ liệu thật" với "sinh có khả năng tấn công/bypass".
4. Đưa 3 câu hỏi nghiên cứu lên slide: validity, diversity, bypass.
5. Chỉ nêu phạm vi làm được trong luận văn, không ôm toàn bộ SQLi/WAF.
6. Dùng bảng related work để dẫn tới khoảng trống, không dùng danh sách bài báo rời rạc.
7. Định nghĩa "thành công" trước khi trình bày mô hình.

### Tầng 2: Dữ liệu và nhãn

Slide cần có:

- Dataset inventory.
- Data flow.
- Filtering/safe split.
- Labeling/verification.
- Examples.

Quan điểm cải thiện:

1. Mỗi con số phải có mẫu số: 14 triệu raw, bao nhiêu usable, bao nhiêu train/dev/test.
2. Nếu nói 268 template, phải có ví dụ 2-3 template và cách rút ra template.
3. Nếu có "split an toàn", định nghĩa bằng rule cụ thể và ví dụ.
4. Nói rõ duplicate/near-duplicate xử lý thế nào.
5. Nói rõ nhãn đến từ đâu: dataset gốc, rule, parser, WAF, VirusTotal/evaluator, hay human review.
6. Tách nhãn cú pháp và nhãn bảo mật: valid SQL payload khác với malicious/bypass.
7. Có một slide "data risk": nguồn ngoài có thể sai, nhãn có thể nhiễu, cách giảm rủi ro.
8. Đưa trạng thái file/tải thành công vào phụ lục hoặc bảng nhỏ.

### Tầng 3: Kiến trúc mô hình

Slide cần có:

- Generator input/output.
- Discriminator input/output.
- Evaluator/WAF role.
- Training loop.
- Inference loop.

Quan điểm cải thiện:

1. Vẽ lại sơ đồ theo hai màu: training path và evaluation path.
2. Không để WAF vừa là labeler vừa là evaluator nếu chưa giải thích rõ.
3. Với mỗi mũi tên, ghi loại dữ liệu: token sequence, payload string, score, label, reward.
4. Nêu rõ Generator sinh từ noise `z`, condition, template, hay prefix.
5. Nêu rõ Discriminator phân biệt real/fake hay còn phân loại valid/invalid.
6. Nếu dùng tường lửa trong loop, giải thích feedback: score, binary pass/fail, reward shaping.
7. Nếu chưa dùng được tường lửa trong training, nói rõ hiện tại chỉ dùng ở evaluation.
8. Tách model overview khỏi implementation detail.

### Tầng 4: Objective, loss và tiêu chí đánh giá

Slide cần có:

- Generator loss.
- Discriminator loss.
- Auxiliary/evaluator reward.
- Diversity/collapse control.
- Metrics.

Quan điểm cải thiện:

1. Đây là điểm thầy hỏi trực tiếp; phải có slide riêng.
2. Nếu chưa có công thức hoàn chỉnh, đưa bản v0 và kế hoạch v1.
3. Loss phải ánh xạ sang mục tiêu: validity, realism, bypass, diversity.
4. Có bảng `objective -> signal -> metric -> expected effect`.
5. Đưa mode collapse thành rủi ro chính, không né.
6. Đo collapse bằng unique ratio, entropy, duplicate rate, top-k repetition.
7. Có baseline để biết mô hình hơn cái gì.
8. Có ablation tối thiểu: không WAF reward, không diversity penalty, đổi cân bằng G/D.
9. Nói rõ chi phí: WAF thật chậm thì dùng proxy/evaluator nào.

### Tầng 5: Kết quả hiện tại và chẩn đoán

Slide cần có:

- Current results.
- Failure cases.
- Diagnosis.
- Next fixes.
- Evidence examples.

Quan điểm cải thiện:

1. Đừng chỉ nói "bị mode collapse"; đưa ví dụ payload lặp.
2. Chỉ ra collapse xảy ra sau khoảng bao nhiêu step/epoch và metric nào đổi.
3. Nêu giả thuyết: Discriminator quá mạnh, reward sparse, data imbalance, tokenization, learning rate.
4. Đưa 3 hướng sửa có thứ tự ưu tiên.
5. Phân biệt kết quả đã chạy và ý tưởng chưa chạy.
6. Khi kết quả chưa tốt, chuyển thành năng lực nghiên cứu bằng cách phân tích nguyên nhân.
7. Có bảng "experiment log" ngắn: config, outcome, lesson.

### Tầng 6: Tính mới và đóng góp

Slide cần có:

- Contribution 1: data/protocol.
- Contribution 2: model/loss.
- Contribution 3: evaluator/benchmark.
- Boundary.

Quan điểm cải thiện:

1. Đừng tuyên bố tính mới chung chung.
2. Nói rõ tính mới nằm ở dữ liệu, loss, evaluator, hay cách kết hợp GAN-WAF.
3. Nếu đóng góp dữ liệu: phải có protocol kiểm chứng và benchmark.
4. Nếu đóng góp thuật toán: phải có loss/architecture khác baseline.
5. Nếu đóng góp hệ thống: phải có pipeline end-to-end và metric vận hành.
6. So với người trình bày ở đẳng cấp cao hơn, điểm khác biệt là họ luôn gắn idea với evidence, metric, ablation và limitation.
7. Với luận văn, 2 đóng góp rõ còn hơn 5 đóng góp mơ hồ.

### Tầng 7: Kế hoạch tiếp theo

Slide cần có:

- Next 2 weeks.
- Next 1 month.
- Acceptance criteria.
- Risks.

Quan điểm cải thiện:

1. Chuyển góp ý của thầy thành task đo được.
2. Ví dụ: "giảm duplicate rate dưới X", "validity trên Y", "bypass rate trên baseline Z".
3. Có thứ tự: data cleanup trước, loss sau, WAF evaluation sau.
4. Không hứa mô hình quá lớn nếu chưa có compute.
5. Mỗi task cần output: bảng, biểu đồ, code, experiment, slide.
6. Có điều kiện dừng: khi nào đủ để báo cáo tiếp.
7. Có rủi ro và phương án thay thế: nếu GAN collapse, dùng MLE/Transformer baseline hoặc Gumbel-SeqGAN smoke.

## 6. Cấp độ nghiên cứu sinh và tiêu chí cải thiện

### Cấp 1: Người làm demo

Đặc điểm: có code, có pipeline, có vài kết quả, nhưng giải thích chưa sâu.

Cần cải thiện:

1. Mọi slide có một thông điệp chính.
2. Không đưa số liệu nếu chưa giải thích nguồn.
3. Luôn có ví dụ input/output.
4. Biết nói mô hình đang fail ở đâu.
5. Biết phân biệt cái đã làm và cái dự định làm.
6. Có bảng việc cần làm sau góp ý.
7. Tránh dùng thuật ngữ nếu chưa định nghĩa.

### Cấp 2: Người làm luận văn

Đặc điểm: có bài toán, có phương pháp, có đánh giá, có so sánh.

Cần cải thiện:

1. Mỗi phần trả lời what/how/why.
2. Có related work dẫn tới khoảng trống.
3. Có protocol đánh giá ổn định.
4. Có baseline tối thiểu.
5. Có metric đúng với mục tiêu.
6. Có phân tích lỗi.
7. Có giới hạn phạm vi rõ.
8. Có kế hoạch thí nghiệm tiếp theo.

### Cấp 3: Nghiên cứu sinh vững

Đặc điểm: biến vấn đề thành câu hỏi nghiên cứu, biết tự phê bình và kiểm chứng.

Cần cải thiện:

1. Đưa ra research question sắc và kiểm chứng được.
2. Chứng minh vì sao phương pháp hiện tại chưa đủ.
3. Thiết kế ablation để bảo vệ từng thành phần.
4. Có thống kê nhiều seed, mean/std, confidence nếu cần.
5. Biết liên hệ failure với lý thuyết: mode collapse, reward sparsity, data leakage.
6. Biết chọn metric phản ánh đúng hiện tượng.
7. Biết nói contribution nhỏ nhưng chắc.
8. Biết dùng limitation như định hướng nghiên cứu tiếp.
9. Có khả năng trả lời phản biện tại chỗ.

### Cấp 4: Nghiên cứu sinh hướng bài báo

Đặc điểm: đóng góp rõ, thực nghiệm đủ mạnh, câu chuyện có thể publish.

Cần cải thiện:

1. Đóng góp phải viết được thành 2-3 bullet cụ thể.
2. Related work phải đặt mình vào bản đồ nghiên cứu.
3. Method phải có phần mới đủ phân biệt baseline.
4. Evaluation phải công bằng và tái lập được.
5. Result phải có ablation, robustness, failure case.
6. Có novelty/validity/diversity/bypass trade-off.
7. Có bảng so sánh với SOTA hoặc baseline hợp lý.
8. Có threat to validity.
9. Có artifact rõ: dataset/protocol/code/model.
10. Có narrative: vì sao vấn đề quan trọng, vì sao cách này hợp lý, vì sao kết quả đáng tin.

### Cấp 5: Nghiên cứu sinh trưởng thành

Đặc điểm: nhìn được hệ thống, chi phí, tổng quát hóa và tác động dài hạn.

Cần cải thiện:

1. Không chỉ tối ưu một chỉ số; nhìn trade-off toàn hệ thống.
2. Biết khi nào dùng WAF thật, khi nào dùng proxy.
3. Biết phân biệt training-time và inference-time cost.
4. Biết thiết kế mô hình tổng quát hóa, không hard-code theo dataset.
5. Biết biến góp ý của thầy thành tiêu chí nghiệm thu.
6. Biết chọn phạm vi đủ hẹp để làm sâu.
7. Biết nói "chưa làm" nhưng kèm kế hoạch kiểm chứng.
8. Biết so sánh với người giỏi hơn bằng cấu trúc lập luận, không phải bằng độ phức tạp mô hình.
9. Biết chuẩn bị câu trả lời cho phản biện về dữ liệu, nhãn, loss, metric, novelty.
10. Biết kết nối luận văn với bài báo: dữ liệu riêng, thuật toán riêng, hoặc protocol riêng.

## 7. Bản slide đề xuất cho lần trình bày tiếp theo

1. Title: GAN-based SQL Injection Payload Generation.
2. Problem: cần sinh payload hợp lệ, đa dạng, realistic, có khả năng bypass/evasion.
3. Why hard: syntax, semantics, WAF behavior, noisy labels, mode collapse.
4. Related work map: template/mutation/ML/GAN/LLM, gap.
5. Dataset inventory: nguồn, số dòng, trạng thái.
6. Data pipeline: raw -> clean -> template -> split an toàn -> tokenization.
7. Label/verification: parser/rule/WAF/VirusTotal/evaluator, risk of wrong labels.
8. Model overview: Generator, Discriminator, Evaluator/WAF.
9. Training loop vs evaluation loop.
10. Loss/objective: current and planned.
11. Metrics: validity, diversity, bypass, novelty, collapse.
12. Current result: những gì đã chạy.
13. Failure analysis: mode collapse sau khoảng 500 lần lặp.
14. Fix plan: 3 thí nghiệm gần nhất.
15. Contribution and next milestone.

## 8. Checklist trước khi gặp thầy

- [ ] Em có thể nói bài toán trong 1 câu.
- [ ] Em có bảng dataset đầy đủ.
- [ ] Em có ví dụ payload qua từng bước tiền xử lý.
- [ ] Em có sơ đồ mô hình tổng thể rõ training/evaluation path.
- [ ] Em có slide loss, dù là bản kế hoạch.
- [ ] Em có metric đo mode collapse.
- [ ] Em có baseline.
- [ ] Em có related work trả lời "người ta đã làm chưa".
- [ ] Em có 3 việc tiếp theo đo được.
- [ ] Em có câu trả lời cho câu hỏi: "tại sao GAN, không phải template/mutation?"


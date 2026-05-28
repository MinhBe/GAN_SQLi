# Danh mục paper cần dùng trong giai đoạn 1

Ngày lập: 2026-05-28

Nguồn kiểm kê:

```text
C:\Users\Admin\Documents\GAN_SQLi\GAN\Paper\OCR
```

Trạng thái OCR theo `OCR_QUALITY_REPORT.md`: 14/14 PDF canonical đã OCR thành markdown, phần lớn đọc được. Một số file có title không khớp chủ đề và phải loại hoặc đánh dấu nghi ngờ.

## 1. Nhóm paper lõi phải ưu tiên

| Ưu tiên | File OCR | Tình trạng | Vai trò | Mô hình/phương pháp | Dữ liệu/testbed | Việc cần làm |
|---:|---|---|---|---|---|---|
| 1 | `Le_2024_GSQLi.md` | OCR tốt, rất liên quan | Paper lõi trực tiếp cho SQLi payload mutation chống WAF/detector | Customized conditional GAN sinh mutation actions từ noise + mutation vector; có Token Parser, Payload Transformer, Attack Classifier | HttpParams, SSHS/Kaggle; Libinjection; classifier RNN/GRU/BiLSTM; ModSecurity + OWASP CRS | Tạo paper card, tái triển khai hoặc mô phỏng pipeline GSQLi trước tiên |
| 2 | `Lu_2022_GAN_SQLi.md` | OCR tốt, rất liên quan | Paper lõi về sinh SQLi bằng GA + GAN/DCGAN/WGAN ý tưởng | Genetic algorithm chọn gene SQLi, improved DCGAN/Wasserstein distance, biến đổi bằng tamper operators | Payload từ CVE/CNVD/exploit-db, hơn 2.000 payload sau cleaning; SQLParse; sqli-lab; SafeDog V4.0 | Tạo paper card, tái triển khai conceptual nếu không có code/data gốc |
| 3 | `Research+on+SQL+injection+attacks+detection+method+based+on+BERT-GAN.md` | OCR tốt, tiếng Trung/Anh | Paper phụ-lõi về detection, không phải generation để test WAF | BERT-GAN bán giám sát; BERT feature extractor + conditional/semi-supervised GAN | sqli, sqliv2, sqli-extend; metric accuracy/precision/recall/F1 | Dùng làm related work detection/augmentation, không chọn làm model chính giai đoạn 1 |
| 4 | `2502.04786v1.md` | OCR tốt, preprint 2025 | Paper phụ-lõi về generative augmentation cho SQLi detection | VAE, U-Net, CWGAN-GP sinh synthetic SQL queries; XGBoost/classifier trên hybrid dataset | Kaggle `sqli.csv`, `Modified SQL Dataset.csv`; pseudo-label, clustering | Dùng làm related work về synthetic data; chỉ tái triển khai nếu giai đoạn 1 còn thời gian |
| 5 | `2212.11119v1.md` | OCR tốt | Nền tảng text GAN | Survey text generation bằng GAN; nhóm Gumbel-Softmax, RL, modified objectives | Survey, không có testbed SQLi | Dùng để giải thích vì sao GAN cho SQLi text rời rạc khó train |

## 2. Nhóm nền tảng GAN cần trích dẫn

| File OCR | Tình trạng | Paper đã làm gì | Kiến trúc/tài liệu | Vai trò trong đề tài |
|---|---|---|---|---|
| `Goodfellow_2014_GAN.md` | OCR tốt | Đề xuất GAN gốc: Generator học phân phối dữ liệu, Discriminator phân biệt real/fake, tối ưu minimax | MLP Generator/Discriminator; noise prior; adversarial loss | Dùng để giải thích GAN cơ bản, không tái triển khai cho SQLi |
| `Gulrajani_2017_WGAN_GP.md` | OCR tốt | Cải thiện training WGAN bằng gradient penalty thay weight clipping | Critic thay Discriminator; Wasserstein loss; gradient penalty | Dùng khi giải thích ổn định train, mode collapse, và nếu dùng WGAN-GP/CWGAN-GP |
| `Radford_2015_DCGAN.md` | OCR tốt | DCGAN cho ảnh, convolution/deconvolution, batch norm, kiến trúc ổn định hơn GAN gốc | Generator deconv, Discriminator conv | Chỉ là nền kiến trúc; không phải SQLi/text. Dùng khi Lu 2022 nói improved DCGAN |

## 3. Nhóm paper phụ về synthetic/security data

| File OCR | Tình trạng | Nội dung tổng quan | Vai trò |
|---|---|---|---|
| `Agrawal_2024_GenAI_Synthetic.md` | OCR tốt | Synthetic/genAI data trong bối cảnh bảo mật hoặc dữ liệu tổng hợp | Bối cảnh phụ, không ưu tiên tái triển khai |
| `CTGAN_IDS_Rare_Attacks_2025_Menssouri.md` | OCR tốt | CTGAN cho dữ liệu IDS/rare attacks | Chỉ dùng khi nói generative model cho dữ liệu an ninh mạng, không trộn vào SQLi payload |
| `Xu_2023_S2CGAN_IDS_possible_IE_GAN.md` | OCR tốt | Intrusion detection trên dữ liệu mất cân bằng, có yếu tố CGAN/IDS | Paper phụ, không phải SQLi payload generation |

## 4. Nhóm cần loại hoặc xác minh trước khi dùng

| File OCR | Lý do |
|---|---|
| `GSQLi_2025_uncertain_from_old_notes.md` | OCR quality report ghi title là `Active Deep Kernel Learning of Molecular Properties from Structural Embeddings`, không liên quan SQLi. Không dùng làm bằng chứng chính. |
| `Nawaz_2025_CTGAN_Web_Attacks.md` | OCR quality report ghi title là `Improving Credit Card Fraud Detection through Transformer-Enhanced GAN Oversampling`, không khớp tên file web attacks. Cần xác minh PDF gốc trước khi dùng. |
| `Lu_2022_GA_WGAN_SQLi.md` | Nội dung OCR hiện tại là bài tiếng Việt về GAN sinh ảnh Pokemon, không phải SQLi; có thể do đặt nhầm file hoặc OCR từ PDF khác. Không dùng làm paper SQLi. |

## 5. Paper card rút gọn cho các bài quan trọng

### 5.1. Le 2024 - GSQLi

Vị trí:

```text
C:\Users\Admin\Documents\GAN_SQLi\GAN\Paper\OCR\Le_2024_GSQLi.md
```

Tình trạng: dùng được, liên quan trực tiếp nhất.

Bài toán: sinh/mutate payload SQLi để đánh lừa ML-based detector và ModSecurity.

Phương pháp:

- Token Parser tách payload thành token.
- Tạo Mutation Vector gồm các đặc trưng như số lượng UNION, WHERE, LIKE, khoảng trắng, true/false expression, AND/OR, comment, function, bareword.
- Generator nhận noise + mutation vector, sinh mutation actions.
- Payload Transformer áp dụng mutation actions lên payload gốc.
- Attack Classifier gán nhãn cho payload mutated để hỗ trợ Discriminator.
- Discriminator học từ mutation vector, mutation actions và nhãn classifier.

Dữ liệu:

- HttpParams: 19.304 normal, 5.557 SQLi.
- SSHS/Kaggle: 19.573 normal, 6.217 SQLi.
- Chỉ chọn SQLi payload ngắn hơn 100 ký tự do giới hạn Libinjection.

Testbed/metric:

- Classifier RNN, GRU, BiLSTM.
- ModSecurity + OWASP rule set.
- Metric chính trong paper: TPR, FNR.

Hạn chế khi dùng cho đề tài:

- Paper tập trung vào evasion/detection, chưa đủ metric novelty/diversity/semantic theo tiêu chuẩn của thầy.
- Cần bổ sung evaluator chung: validity, uniqueness, novelty, duplicate, failure distribution.

Vai trò giai đoạn 1: ứng viên số 1 để tái triển khai hoặc smoke test.

### 5.2. Lu 2022 - A GAN-based Method for Generating SQL Injection Attack Samples

Vị trí:

```text
C:\Users\Admin\Documents\GAN_SQLi\GAN\Paper\OCR\Lu_2022_GAN_SQLi.md
```

Tình trạng: dùng được, liên quan trực tiếp.

Bài toán: augment/generate SQLi attack samples để giải quyết thiếu mẫu SQLi cho detection.

Phương pháp:

- Thu thập payload từ CVE, CNVD, exploit-db.
- Làm sạch và generalize payload.
- Dùng genetic algorithm sinh cá thể từ gene list SQLi.
- Dùng SQLParse đánh giá tính parse/syntax.
- Dùng improved DCGAN/Wasserstein distance để sinh mẫu.
- Dùng tamper/variation operators như base64, keyword case confusion, space comment, UTF8, apostrophe full-width, unicode-url, interface comment, MySQL versioned comment.

Dữ liệu/testbed:

- Hơn 2.000 payload sau cleaning.
- SQLParse.
- phpstudy2018, sqli-lab Range, SafeDog V4.0.

Metric/kết quả:

- Kiểm tra parsability và usability trên sqli-lab/SafeDog theo các dạng injection.
- Metric chưa đủ mạnh theo chuẩn giai đoạn 1, cần bổ sung evaluator chung.

Hạn chế:

- Dữ liệu gốc có thể không công khai đầy đủ.
- Có thể phải tái triển khai conceptual version.

Vai trò giai đoạn 1: paper lõi thứ 2, tốt để tạo mutation/tree/rule baseline và so với GSQLi.

### 5.3. BERT-GAN SQLi Detection 2024

Vị trí:

```text
C:\Users\Admin\Documents\GAN_SQLi\GAN\Paper\OCR\Research+on+SQL+injection+attacks+detection+method+based+on+BERT-GAN.md
```

Tình trạng: dùng được, nhưng trọng tâm là detection.

Bài toán: phát hiện SQLi khi dữ liệu thật khó thu thập và model truyền thống chưa chính xác.

Phương pháp:

- BERT fine-tuning để học representation của input.
- GAN bán giám sát để phân biệt real/adversarial và benign/malicious.
- So sánh với CNN, LSTM, BERT-Base, GAN-Base.

Dữ liệu:

- sqli.
- sqliv2.
- sqli-extend tự xây dựng.

Metric:

- Accuracy, precision, recall, F1.

Vai trò giai đoạn 1:

- Related work cho detection và semi-supervised GAN.
- Không chọn làm model sinh payload chính vì đầu ra là detector, không phải WAF testing payload generator.

### 5.4. Dasari 2025 - Enhancing SQL Injection Detection and Prevention Using Generative Models

Vị trí:

```text
C:\Users\Admin\Documents\GAN_SQLi\GAN\Paper\OCR\2502.04786v1.md
```

Tình trạng: dùng được, preprint 2025.

Bài toán: tăng dữ liệu SQLi để cải thiện detection/prevention.

Phương pháp:

- VAE encode SQL queries sang latent representation.
- U-Net adapted cho dữ liệu sequence 1D.
- CWGAN-GP sinh synthetic SQL queries có điều kiện.
- Pseudo-labeling, clustering, hybrid dataset.
- XGBoost/classifier đánh giá dữ liệu augmented.

Dữ liệu:

- Kaggle `sqli.csv`.
- `Modified SQL Dataset.csv`.

Metric:

- Detection metric cho classifier.
- Synthetic quality metric như MSE, R2, PCA/visual checks.

Vai trò giai đoạn 1:

- Related work mạnh cho synthetic augmentation.
- Không ưu tiên tái triển khai trước GSQLi vì mục tiêu là detection augmentation, không trực tiếp WAF evasion protocol.

### 5.5. Survey Text GAN 2022

Vị trí:

```text
C:\Users\Admin\Documents\GAN_SQLi\GAN\Paper\OCR\2212.11119v1.md
```

Tình trạng: dùng được.

Bài toán: khảo sát sinh văn bản bằng GAN.

Nội dung chính:

- GAN ban đầu thiết kế cho dữ liệu liên tục, còn text/payload là chuỗi rời rạc.
- Ba hướng xử lý chính: Gumbel-Softmax, Reinforcement Learning, modified training objectives.

Vai trò:

- Là cơ sở để giải thích vì sao SQLi payload generation bằng GAN khó.
- Dùng để biện minh nếu chọn GSQLi mutation-action thay vì sinh raw text trực tiếp.

## 6. Thứ tự chạy/tái triển khai đề xuất

1. Tạo paper card cho `Le_2024_GSQLi.md`, `Lu_2022_GAN_SQLi.md`, `BERT-GAN`, `2502.04786v1.md`, `Goodfellow_2014_GAN.md`, `Gulrajani_2017_WGAN_GP.md`, `2212.11119v1.md`.
2. Chọn `Le_2024_GSQLi.md` làm paper tái triển khai chính.
3. Dùng `Lu_2022_GAN_SQLi.md` để thiết kế mutation baseline/conceptual baseline.
4. Dùng `BERT-GAN` và `2502.04786v1.md` làm related work detection/augmentation, chưa chạy trước.
5. Loại khỏi paper lõi các file không khớp title/chủ đề.

## 7. Bảng quyết định nhanh

| Paper | Có nên đưa vào báo cáo chính? | Có nên chạy giai đoạn 1? | Lý do |
|---|---|---|---|
| Le 2024 GSQLi | Có | Có | Trực tiếp nhất với SQLi payload mutation và WAF/detector evasion. |
| Lu 2022 GAN SQLi | Có | Có thể, ưu tiên baseline/conceptual | Có pipeline SQLi generation nhưng dữ liệu/code cần kiểm tra. |
| BERT-GAN SQLi Detection | Có | Chưa | Liên quan detection, không phải generator chính. |
| Dasari 2025 VAE/U-Net/CWGAN-GP | Có | Chưa | Hữu ích về synthetic data, nhưng không ưu tiên hơn GSQLi. |
| Goodfellow 2014 | Có | Không | Nền lý thuyết GAN. |
| Gulrajani 2017 | Có | Không | Nền ổn định training WGAN-GP. |
| Text GAN Survey 2022 | Có | Không | Nền cho text discrete GAN. |
| GSQLi 2025 uncertain | Không | Không | Không liên quan theo title OCR. |
| Nawaz 2025 CTGAN Web Attacks | Không cho đến khi xác minh | Không | Title OCR không khớp. |
| Lu_2022_GA_WGAN_SQLi | Không như SQLi paper | Không | Nội dung OCR là GAN Pokemon. |

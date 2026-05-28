# SQL Injection Hiện Tại: Biến Thể, Cập Nhật, Khảo Sát Và Lý Do Vẫn Phổ Biến

Date: 2026-05-25

## Phạm Vi

Chủ đề: SQL injection trong các năm gần đây, gồm biến thể tấn công, bề mặt tấn công hiện đại, cập nhật phòng thủ, survey/systematic review, AI/LLM/Text-to-SQL, WAF/evasion, dataset/benchmark, và nguyên nhân SQLi vẫn xuất hiện nhiều.

Giai đoạn crawl học thuật: 2020-2026.

Nguồn scholarly metadata:

- OpenAlex
- Crossref

Không tải PDF, không crawl HTML publisher, không bypass paywall/CAPTCHA.

## Corpus

- Query đã chạy: 60
- Full normalized corpus sau deduplicate: 4,602 bản ghi
- Filtered corpus liên quan trực tiếp SQLi: 1,102 bản ghi
- Nguồn trong filtered corpus:
  - OpenAlex: 689
  - Crossref: 413

File chính:

- `sqli_current.normalized.jsonl`
- `sqli_current.csv`
- `sqli_current.md`
- `sqli_current.bib`
- `sqli_current.filtered.jsonl`
- `sqli_current.filtered.csv`
- `sqli_current.filtered.md`
- `sqli_current.filtered.bib`
- `queries.json`
- `crawl_stats.json`

## Topic Buckets Trong Filtered Corpus

Một paper có thể thuộc nhiều bucket.

- Modern surfaces: 743
- ML/DL detection: 699
- Surveys/root causes: 372
- Defense/secure coding: 351
- Datasets/benchmarks: 288
- Evasion/WAF/adversarial: 168
- AI/LLM/Text-to-SQL: 82
- General recent SQLi: 82
- Attack variants: 42

## Phân Bố Năm

- 2026: 101
- 2025: 264
- 2024: 230
- 2023: 161
- 2022: 139
- 2021: 116
- 2020: 91

## Quốc Gia/Affiliation Nổi Bật

Metadata quốc gia chủ yếu đến từ OpenAlex; Crossref thường thiếu country-level affiliation.

- IN: 100
- CN: 76
- ID: 62
- US: 52
- GB: 30
- SA: 24
- MY: 21
- PK: 19
- IQ: 14
- JO: 13
- TR: 13
- NG: 11
- BD: 11
- DE: 11
- AE: 10
- CA: 10

## Biến Thể SQLi Cần Chú Ý

Các biến thể truyền thống vẫn xuất hiện trong tài liệu và công cụ kiểm thử:

- Error-based SQLi: khai thác thông báo lỗi DB/application.
- Union-based SQLi: dùng `UNION` để trích xuất dữ liệu từ bảng khác.
- Boolean-based blind SQLi: suy luận qua true/false response.
- Time-based blind SQLi: suy luận qua độ trễ response.
- Second-order/stored SQLi: payload được lưu trước, kích hoạt ở luồng xử lý sau.
- Out-of-band SQLi: dữ liệu rò qua kênh phụ như DNS/HTTP callback.
- Stacked/batched queries: nối nhiều câu lệnh khi DB/driver cho phép.
- ORM/search parameter injection: dữ liệu thù địch đi vào query builder/ORM sai cách.
- NoSQL injection: cùng nguyên lý injection nhưng ở MongoDB/NoSQL query object.

## Cập Nhật/Bề Mặt Hiện Đại

Các bề mặt hiện tại đáng chú ý hơn so với mô hình web form cổ điển:

- API/REST/GraphQL: nhiều tham số JSON/header/path/query string hơn; parser và gateway có thể xử lý khác nhau.
- Microservices/cloud/serverless: dữ liệu đi qua nhiều service, queue, function, log pipeline; validation bị phân tán.
- CMS/plugin ecosystem: lỗi nằm ở plugin/theme/extension, không chỉ ở core app.
- Mobile/backend/API gateway: client mobile không đáng tin; backend vẫn phải validate và bind parameter đúng.
- IoT/admin portals/security appliances: giao diện quản trị và embedded web app vẫn phát sinh SQLi.
- Text-to-SQL/LLM-integrated apps: model sinh SQL hoặc chuyển ngôn ngữ tự nhiên sang query, tạo rủi ro mới nếu không có policy, sandbox, allowlist schema, parameterization, và kiểm soát execution.
- AI-generated code: code mẫu sinh ra có thể dùng string concatenation hoặc bỏ qua prepared statements nếu prompt/guardrail yếu.

## Vì Sao Hiện Tại Vẫn Nhiều SQLi

Từ corpus và các nguồn chính thức, nguyên nhân lặp lại là:

- Dynamic query vẫn bị nối chuỗi ở các lớp legacy, plugin, script nội bộ, dashboard quản trị.
- Prepared statements có từ lâu nhưng không được dùng nhất quán, đặc biệt khi truy vấn động nhiều điều kiện, search/filter/sort.
- ORM không tự động an toàn nếu dùng raw query, dynamic fragments, hoặc hostile data trong search parameters.
- Validation bị phân tán trong kiến trúc API/microservice; mỗi service giả định service trước đã làm sạch dữ liệu.
- CI/CD dùng SAST/DAST/WAF nhưng thiếu coverage hoặc false positive/false negative làm đội ngũ bỏ qua cảnh báo.
- WAF/signature bị bypass bằng encoding, comment, case mutation, DB-specific syntax, timing, hoặc payload biến thể.
- Dữ liệu benchmark thiếu đa dạng, model ML/DL detection dễ học dataset thay vì học semantics của SQLi.
- Vendor/plugin ecosystem tạo long tail: nhiều maintainer, chất lượng secure coding không đồng đều, patch adoption chậm.
- SQLi là class lỗi thiết kế/coding, không phải chỉ là lỗi cấu hình; nếu quy trình phát triển không tách data khỏi command, lỗi quay lại.

## Hướng Phòng Thủ/Cập Nhật Thực Tế

- Bắt buộc parameterized queries/prepared statements ở tất cả code path.
- Không dùng string concatenation cho SQL fragments; với dynamic sort/filter/table/column, dùng allowlist cứng.
- Giới hạn quyền DB theo least privilege; tách user đọc/ghi/admin.
- Dùng migration/query builder an toàn nhưng audit raw SQL escape hatch.
- SAST + DAST + IAST trong CI/CD, nhưng cần rule phù hợp framework và review false negative.
- Test fuzzing cho API parameters, headers, cookies, JSON/XML/SOAP bodies.
- Với Text-to-SQL/LLM: không cho model trực tiếp execute SQL; dùng AST/parser, schema allowlist, prepared statements, read-only role, query budget, result redaction, và human approval cho write operations.
- Dùng WAF/RASP như lớp phòng thủ bổ sung, không thay thế sửa code.
- Theo dõi CVE/KEV cho sản phẩm gateway, CMS, file-transfer, appliance, plugin.

## Nguồn Chính Thức Để Đặt Bối Cảnh

- OWASP Top 10:2021 xếp Injection ở A03; SQL Injection/CWE-89 là một CWE tiêu biểu trong nhóm này. OWASP nêu nguyên nhân chính là dữ liệu user không được validate/filter/sanitize, dynamic query/non-parameterized call, ORM parameter bị lạm dụng, và dữ liệu thù địch bị nối trực tiếp vào command/query. URL: https://owasp.org/Top10/2021/A03_2021-Injection/
- OWASP Developer Guide ghi nhận OWASP Top 10 web app mới nhất là bản 2021 và injection là nhóm rủi ro đã xuất hiện liên tục từ bản đầu năm 2003. URL: https://devguide.owasp.org/en/02-foundations/05-top-ten/
- OWASP API Security Top 10 2023 cho thấy bối cảnh API đã tách riêng thành một top 10; bản 2019 có API8 Injection, còn bản 2023 chuyển trọng tâm sang các rủi ro API-specific như Broken Object Level Authorization, SSRF, Security Misconfiguration, Inventory và Unsafe Consumption of APIs. URL: https://owasp.org/API-Security/editions/2023/en/0x00-header/
- MITRE CWE-89 định nghĩa SQL Injection là improper neutralization of special elements in SQL command; trang CWE-89 cũng liệt kê ví dụ gần đây như SQLi trong AI chatbot qua conversation message, SQLite/e-mail agent, security dashboard, file-transfer system và firewall/admin interface. URL: https://cwe.mitre.org/data/definitions/89.html
- CISA/FBI Secure by Design Alert 2024 kêu gọi loại bỏ SQL Injection như một class defect, thay vì chỉ vá từng CVE. URL: https://www.cisa.gov/resources-tools/resources/secure-design-alert-eliminating-sql-injection-vulnerabilities-software

## Ghi Chú Chất Lượng

Corpus này ưu tiên recall cao. `sqli_current.filtered.*` đã loại bớt nhiễu nhưng vẫn cần screening thủ công trước khi dùng làm systematic review. Một số paper cyber-security rộng có thể được giữ lại nếu metadata chứa SQLi trong abstract/keywords/concepts.

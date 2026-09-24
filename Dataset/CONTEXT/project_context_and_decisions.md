# Project context & decision log — handoff to another AI agent

## Mục tiêu
- Người dùng đang nghiên cứu ML/generative modeling để nâng cao tính tổng quát hóa của Boolean SQLi detector nhẹ.
- SeqGAN char-level là generator offline; thử RF hoặc char-n-gram TF-IDF+LR làm detector rẻ, advanced transformer/LLM chỉ cho các case uncertain sau WAF.
- Người dùng tránh "OR 1=1" nhân số lượng vô nghĩa; đặt trọng tâm grammar, typed slots, semantic diversity và SQL dialect/query-language representation.
- Đề xuất sau phản biện từ sếp: đánh giá usefulness/downstream detector, bằng chứng exploit trong lab (khác WAF bypass), dữ liệu có nguồn, false positive, và hiệu năng theo lượng request thực; không dựa trên sơ đồ/thống kê tự khẳng định.
- ABCD hiện tại A=boolean-like mechanism; B=Y1 Simple Y2 Variation Y3 Basic Transformation Y4 Basic Obfuscation; C=Z1 No Context; D=18 database/query systems/5 category. Trục C mở rộng tương lai single-stage context/multi-stage context; Second-order không phải payload complexity.
- Số lượng chính xác 28.800 A, 27.600 B, 56.400 rows. 1.400 unsupported CQL coverage slots; 55.000 nonempty records.
- B controls synthetic designed, not observed benign; A/B share abstract grammar and therefore cannot be treated as independent source split.
- D3/D4/D5 require appropriate non-SQL query representations. "Boolean-style" overarching concept does not make every sample SQL injection.

## Phạm vi KHÔNG có ở gói này
No packet captures; no production logs; no tracked IP/session; no response/time/OAST; no real attack labels; no confirmed bypass; no engine validation beyond in-memory SQLite parse test by packaging step; no ORM/config context; no multi-stage.

## Next gates before paper/product claims
(1) curated real/independent controls, (2) licensed observed corpus provenance, (3) parser+engine validation per supported dialect, (4) vulnerable app-lab outcome, (5) lineage/source-heldout benchmarking, (6) latency and escalation measurements, (7) eliminate grammar/data leakage, (8) security privacy/license review for any live logs.

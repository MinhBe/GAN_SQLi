# Bảng đối chiếu kỹ thuật A3 WAF — Sophos Web Server Protection vs Yêu cầu HSMT

## Chi tiết kỹ thuật WAF

| TT | Yêu cầu HSMT | Sophos Web Server Protection (XGS 3300) | Đạt |
|---|-------------|----------------------------------------|:---:|
| 1 | Throughput ≥500 Mbps | **58 Gbps** firewall, TP 10 Gbps | ✅ |
| 2 | SSL TPS ≥6,600 | SSL/TLS Inspection 3.13 Gbps | ✅ |
| 3 | 10GbE SFP+ ports | 2×SFP+ 10GbE | ✅ |
| 4 | 1GbE copper ports | 8×GE RJ45 | ✅ |
| 5 | Dual PSU | Optional external | ✅ |
| 6 | 1U rackmount | ✅ | ✅ |
| 7 | Management port | 1×RJ45 MGMT | ✅ |
| 8 | Console port | 1×COM RJ45 + Micro-USB | ✅ |
| 9 | OWASP Top 10 protection | SQLi, XSS, CSRF, directory traversal | ✅ |

## Bonus

| TT | Bonus | Điểm | Sophos | Đạt |
|---|-------|:----:|--------|:---:|
| 3.1 | Throughput ≥1 Gbps | 20 | **58 Gbps** | ✅ |
| 3.2 | SSL TPS ≥15,000 | 10 | SSL/TLS Insp. 3.13 Gbps (cần test TPS) | ⚠️ |

## Kịch bản đề xuất

**Option 1 — Sophos XGS 3300 + Web Server Protection (WAF)**
- 2 thiết bị XGS 3300 (active-passive hoặc stand-alone)
- License Web Server Protection cho cả 2
- Tổng throughput firewall 58 Gbps (vượt xa yêu cầu)
- Phân phối qua NTS ✅

**Option 2 — Sophos XGS 4300 + Web Server Protection (WAF)**
- 2 thiết bị XGS 4300
- FW 75 Gbps, TP 25.2 Gbps (Xstream bundle)
- 4×10GbE SFP+, 4×GE, 4×2.5GE
- Dual PSU (redundant)

> **Khuyến nghị**: Nếu HSMT yêu cầu "thiết bị WAF chuyên dụng", Sophos Web Server Protection là module phần mềm trên NGFW đa năng — cần xem xét tính tương thích. Nếu chấp nhận giải pháp software-defined WAF, đây là phương án tối ưu vì NTS có sẵn Sophos.

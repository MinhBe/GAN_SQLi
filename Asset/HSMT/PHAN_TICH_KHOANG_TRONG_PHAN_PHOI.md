# Phân tích khoảng trống phân phối — BID BP2500701601

## 1. Hạng mục A3: WAF

### Vấn đề
HSMT yêu cầu **02 thiết bị tường lửa ứng dụng Web (WAF)** với thông số kỹ thuật:
- Throughput ≥500 Mbps (bonus: >1 Gbps)
- SSL TPS ≥6,600 (bonus: >15,000)
- ≥4×10GbE SFP+
- OWASP Top 10, Bot protection, API protection
- Dual PSU, 03 năm bảo hành + bản quyền

### NTS không phân phối F5 BIG-IP
**Phương án A — F5 BIG-IP WAF qua nhà phân phối khác**
- Nhà phân phối F5 tại VN: **VTI**, **VST**, **NetPro**
- Liên hệ báo giá: cần xác nhận
- F5 i5800: Throughput 10 Gbps L7, SSL TPS 48,000 — đáp ứng vượt bonus
- ⚠ Rủi ro: phải hợp tác với NTS + nhà phân phối F5, tăng độ phức tạp

**Phương án B — Barracuda WAF qua NTS** (trong danh mục NTS)
- NTS phân phối Barracuda (xác nhận tại ntshanoi.com.vn)
- Cần kiểm tra thông số Barracuda WAF cụ thể
- ⚠ Chưa có datasheet Barracuda WAF — cần crawl

**Phương án C — Sophos XGS + Web Server Protection qua NTS**
- NTS phân phối Sophos
- Sophos Web Server Protection: license add-on trên XGS Firewall
- Tính năng: reverse proxy WAF, SQLi/XSS, 350+ attack patterns, dual AV
- ⚠ Không phải thiết bị WAF chuyên dụng — cần đánh giá tính tương thích HSMT
- ⚠ SSL TPS cần xác nhận (SSL/TLS inspection 3.13–8 Gbps trên XGS)

---

## 2. Hạng mục A6: Patch Management

### Vấn đề
HSMT yêu cầu:
- **Bảo hành mở rộng** Dell PowerEdge R430 — 03 năm
- **Gia hạn bản quyền** HCL BigFix Patch Management — 03 năm
- Bonus: ≥4 năm (+10 điểm)

### NTS không phân phối HCL BigFix
- HCL BigFix là phần mềm quản lý bản vá **UBCKNN đang sử dụng**
- HSMT yêu cầu gia hạn bản quyền **hiện tại**, không phải thay thế
- Có thể mua trực tiếp từ **HCL Software** hoặc distributor được ủy quyền tại VN

### Phương án
1. **Liên hệ HCL Việt Nam** (HCL Technologies Vietnam) để được báo giá gia hạn
2. Hoặc qua **đại lý ủy quyền của HCL BigFix tại VN**
3. Phần cứng Dell R430: mua bảo hành mở rộng qua Dell hoặc NTS (nếu NTS phân phối Dell)

---

## 3. Tổng hợp phương án phân phối

| STT | Hạng mục | Vendor | Phân phối | Ghi chú |
|:---:|----------|--------|:----------:|---------|
| 1 | DDoS | NETSCOUT Arbor | ✅ **NTS** | AED có sẵn |
| 2 | Firewall Core | Fortinet | ⚠️ **Cần xác nhận** | NTS có Fortinet? Nếu không → tìm VST/VTI |
| 3 | WAF | F5 / Barracuda / Sophos | ❌ NTS không có F5 | Cần quyết định phương án |
| 4 | SIEM | Splunk / IBM QRadar | ⚠️ **Cần xác nhận** | NTS có OpenText → tương thích |
| 5 | PAM | Delinea | ✅ **NTS** | Secret Server + Privilege Manager |
| 6 | Patch Mgmt | HCL BigFix | ❌ NTS không có | Mua trực tiếp HCL |
| 7 | Mail Gateway | Barracuda | ✅ **NTS** | Email Security Gateway |
| 8 | Firewall Trụ sở | Fortinet / Sophos | ✅ **NTS (Sophos)** | XGS 4300 |
| 9 | Web Content | Fortinet / Sophos | ✅ **NTS (Sophos)** | Tích hợp firewall |
| 10 | Anti-Malware | Kaspersky | ✅ **NTS** | Exclusive distributor VN |

### Các hạng mục cần xác nhận thêm
- **Fortinet phân phối**: NTS có Fortinet không? (không thấy trong danh sách). Nếu không → cần tìm VST, VTI, hoặc VNPT
- **SIEM phân phối**: NTS có OpenText, nhưng HSMT có thể chấp nhận Splunk/QRadar không?

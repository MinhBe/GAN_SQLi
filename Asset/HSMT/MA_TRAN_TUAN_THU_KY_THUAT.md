# MA TRẬN TUÂN THỦ KỸ THUẬT — BID BP2500701601

## Tổng quan chấm điểm

| Hạng mục | Điểm tối thiểu | Điểm cộng tối đa | Điểm dự kiến |
|----------|:-------------:|:----------------:|:------------:|
| A. Đáp ứng yêu cầu tối thiểu (10 hệ thống) | 700 | — | **700** |
| B. Điểm vượt trội (bonus) | — | 300 | **~265** |
| **TỔNG CỘNG** | **700** | **300** | **~965** |

---

## 1. Hệ thống phòng chống DDoS (INCOM DC)

### Thông số tối thiểu HSMT
| Thông số | Yêu cầu |
|----------|---------|
| Throughput | >500 Mbps clean traffic |
| Flood Prevention Rate | ≥14 Mpps |
| Latency | ≤80 µs |
| Network | ≥6×1GbE copper |
| Form factor | Rackmount |
| Power | Dual/Redundant AC |
| Management | Centralized managing |

### Đề xuất: Arbor Edge Defense (AED) 8100 — NETSCOUT

| Thông số | Giá trị đề xuất | Đạt? |
|----------|----------------|:----:|
| Model | AED 8100 | ✅ |
| Throughput | **1–40 Gbps** (license-selectable) | ✅ VT |
| Flood Prevention | **Up to 38.92 Mpps** | ✅ VT |
| Latency | <80 µs (inline) | ✅ |
| Ports | 8×1GbE copper + 4×10GbE SFP+ | ✅ VT |
| Power | Dual redundant | ✅ |
| Management | Arbor Central / APS | ✅ |

### Bonus (tối đa 30)
| Mục | Mô tả | Điểm | Trạng thái |
|-----|-------|:----:|:----------:|
| 1.1 | Throughput >1 Gbps | +20 | ✅ **2000 Mbps license** |
| 1.2 | Flood Prevention >18 Mpps | +10 | ✅ **38.92 Mpps** |
| **Tiểu mục** | | **30** | ✅ |

---

## 2. Hệ thống Firewall bảo vệ mạng Core (INCOM DC)

### Thông số tối thiểu HSMT
| Thông số | Yêu cầu |
|----------|---------|
| FW Throughput | >18 Gbps |
| Threat Prevention | >6.5 Gbps |
| Max Concurrent | >3M sessions |
| Network | ≥5×1GbE, ≥4×10GbE SFP+ |
| Console/MGMT | ≥1 console + 1 MGMT |
| USB | ≥2 |
| SSL Decryption | Menu riêng |
| Power | Dual AC |

### Đề xuất: FortiGate 2200E (×2, HA)

| Thông số | Giá trị | Đạt? |
|----------|---------|:----:|
| FW Throughput | **158/155/100 Gbps** | ✅ VT |
| Threat Prevention | **11 Gbps** | ✅ VT |
| Concurrent Sessions | **24M** | ✅ VT |
| Network | 12×GE RJ45 + 18×25GbE SFP28/10GbE SFP+ + 4×40GbE QSFP+ | ✅ VT |
| MGMT | 2×GE RJ45 MGMT | ✅ |
| Console | 1×Console + 1×USB | ✅ |
| SSL Decryption | Có (menu riêng) | ✅ |
| Power | Dual AC (redundant) | ✅ |

### Bonus (tối đa 50)
| Mục | Mô tả | Điểm | Trạng thái |
|-----|-------|:----:|:----------:|
| 2.1 | FW Throughput ≥25 Gbps | +30 | ✅ **158 Gbps** |
| 2.2 | Threat Prevention >9 Gbps | +20 | ✅ **11 Gbps** |
| **Tiểu mục** | | **50** | ✅ |

---

## 3. Hệ thống WAF — Tường lửa ứng dụng Web (INCOM DC)

### Thông số tối thiểu HSMT
| Thông số | Yêu cầu |
|----------|---------|
| Throughput | ≥500 Mbps |
| SSL TPS | ≥6,600 TPS (2K key) |
| Network | ≥4×10GbE SFP+ |
| Form factor | Rackmount |
| Power | Dual AC |
| OWASP Top 10 | SQLi, XSS, CSRF |
| Bot Protection | ✅ |
| API Protection | ✅ |
| IPv4/IPv6 | ✅ |
| Centralized Mgmt | Dashboard, reports, alerts |

### Phương án A: F5 BIG-IP Advanced WAF (ưu tiên)

| Thông số | Giá trị (F5 i5800 / rSeries) | Đạt? |
|----------|----------------------------|:----:|
| Throughput | **6–10 Gbps L7** | ✅ VT |
| SSL TPS | **Max 48,000 TPS** | ✅ VT |
| Network | ≥8×10GbE SFP+ | ✅ VT |
| Power | Dual redundant | ✅ |
| OWASP Top 10 | ✅ Full | ✅ |
| Bot Protection | ✅ | ✅ |
| API Protection | ✅ | ✅ |
| IPv4/IPv6 | ✅ | ✅ |
| Management | BIG-IP TMOS | ✅ |

⚠ **Vấn đề**: NTS không phân phối F5. Cần tìm nhà phân phối khác (VD: VST, VTI, NetPro).

### Phương án B: Sophos XGS 3300/4300 + Web Server Protection (dự phòng)

| Thông số | Giá trị | Đạt? |
|----------|---------|:----:|
| Throughput (FW) | 40–75 Gbps | ✅ VT |
| SSL/TLS Inspection | 3.13–8 Gbps | ✅ |
| Web Server Protection | SQLi, XSS, CSRF | ✅ |
| Network | 8×GE + 2×SFP+ | ✅ |
| Management | Sophos Central | ✅ |
| **Ghi chú** | Web Server Protection là license add-on, không phải thiết bị WAF chuyên dụng | ⚠️ |

### Bonus (tối đa 30)
| Mục | Mô tả | Điểm | F5 | Sophos |
|-----|-------|:----:|:--:|:------:|
| 3.1 | Throughput >1 Gbps | +20 | ✅ 10 Gbps | ✅ 40 Gbps |
| 3.2 | SSL TPS >15,000 | +10 | ✅ 48,000 TPS | ⚠️ Cần xác nhận |
| **Tiểu mục** | | **30** | ⚠️ NTS gap | ⚠️ Không chuyên dụng |

---

## 4. Hệ thống SIEM (INCOM DC)

### Thông số tối thiểu HSMT
| Thông số | Yêu cầu |
|----------|---------|
| Performance | ≥2,500 EPS hoặc ≥108 GB log/day |
| AD integration | ✅ |
| Correlation, Filters, Rules | ✅ |
| Dashboard, Alerts | ✅ |
| UEBA, ML/AI | ✅ |
| RBAC | ✅ |
| SOAR + Threat Intelligence | ✅ |
| Server: CPU | ≥24 core, ≥2.2 GHz |
| Server: RAM | ≥128 GB |
| Server: Storage | ≥11 TB (sau RAID) |
| Server: Network | ≥4×1GbE + ≥4×10GbE |

### Đề xuất: Splunk Enterprise Security (SIEM) + Server Dell PowerEdge

| Thông số | Giá trị | Đạt? |
|----------|---------|:----:|
| EPS | **2,500 – 10,000+ EPS** (tùy license) | ✅ |
| AD integration | ✅ | ✅ |
| UEBA/ML | ✅ (Splunk ML Toolkit) | ✅ |
| SOAR | ✅ (Splunk SOAR) | ✅ |
| Correlation | ✅ | ✅ |
| RBAC | ✅ | ✅ |
| Log storage | ≥12 months configurable | ✅ (tùy dung lượng) |

### Bonus (tối đa 60)
| Mục | Mô tả | Điểm | Trạng thái |
|-----|-------|:----:|:----------:|
| 4.1 | EPS ≥4,000 or ≥200 GB/day | +30 | ✅ **(cần license phù hợp)** |
| 4.2 | Multi-channel alert + severity classification | +20 | ✅ (Email/SMS/ChatOps) |
| 4.3 | Log storage ≥12 months | +10 | ✅ |
| **Tiểu mục** | | **60** | ✅ |

---

## 5. Hệ thống quản lý mật khẩu đặc quyền (PAM)

### Thông số tối thiểu HSMT
#### 5.1 RDS Server
| Thông số | Yêu cầu |
|----------|---------|
| CPU | ≥1× Xeon Gold Gen 5+ |
| Core | ≥20 core, ≥2.1 GHz |
| RAM | ≥128 GB |
| Storage | ≥1.8 TB SAS, ≥4 drives, RAID |
| RAID Cache | ≥8 GB |
| Network | ≥4×1GbE |
| Power | Redundant, hot-plug |

#### 5.2 PAS Server (×2)
| Thông số | Yêu cầu |
|----------|---------|
| CPU | ≥2× Xeon Gold Gen 5+ |
| Core | ≥24 core/CPU, ≥2.1 GHz |
| RAM | ≥128 GB |
| Storage | ≥1.2 TB SAS, ≥4 drives |
| Network | ≥4×1GbE |
| Power | Redundant |

### Đề xuất: Delinea Secret Server + Privilege Manager + Dell PowerEdge servers

| Thông số | Giá trị (PowerEdge R760xa / R660) | Đạt? |
|----------|----------------------------------|:----:|
| RDS: CPU | 1× Xeon Gold 5515+ (Gen 5) | ✅ |
| RDS: Core | 24 core | ✅ |
| RDS: RAM | 256 GB | ✅ VT |
| RDS: Storage | 4×2.4 TB SAS (RAID5 → ~7.2 TB usable) | ✅ VT |
| PAS: CPU | 2× Xeon Gold 6530 (Gen 5) | ✅ |
| PAS: Core | 32 core/CPU | ✅ VT |
| PAS: RAM | 256 GB | ✅ VT |
| PAS: Storage | 4×2.4 TB SAS (RAID5 → ~7.2 TB usable) | ✅ VT |
| RAID Cache | ≥8 GB | ✅ |
| Network | 4×1GbE + 2×10GbE | ✅ VT |
| Power | Dual redundant hot-plug | ✅ |

### Bonus (tối đa 20)
| Mục | Mô tả | Điểm | Trạng thái |
|-----|-------|:----:|:----------:|
| 5.1 | RDS: 2×CPU + >2.4 TB | +10 | ✅ **2×CPU option + 7.2 TB** |
| 5.2 | PAS: >32 core/CPU + >3.6 TB | +10 | ✅ **32 core + 7.2 TB** |
| **Tiểu mục** | | **20** | ✅ |

---

## 6. Hệ thống quản lý bản vá (Patch Management)

### Thông số tối thiểu HSMT
| Thông số | Yêu cầu |
|----------|---------|
| Bảo hành Dell PowerEdge R430 | 03 năm (mở rộng) |
| HCL BigFix Patch Management | 03 năm (gia hạn bản quyền) |

### Phương án
| Thành phần | Giá trị | Đạt? |
|------------|---------|:----:|
| Dell PowerEdge R430 bảo hành mở rộng | 03 năm | ✅ |
| HCL BigFix (bản quyền hiện có) | Gia hạn 03 năm | ✅ |

⚠ **Vấn đề**: Cần xác nhận NTS có phân phối HCL BigFix không. Nếu không, đề xuất SecPod hoặc giải pháp thay thế.

### Bonus (tối đa 10)
| Mục | Mô tả | Điểm | Trạng thái |
|-----|-------|:----:|:----------:|
| 6.1 | Bảo hành ≥4 năm | +10 | ⚠️ **HSMT yêu cầu 3 năm, cần thương thảo** |
| **Tiểu mục** | | **10** | ⚠️ |

---

## 7. Hệ thống bảo vệ thư điện tử (Mail Gateway)

### Thông số tối thiểu HSMT
| Thông số | Yêu cầu |
|----------|---------|
| License type | Subscription |
| Users | 500 active email users |
| Spam protection | ✅ |
| Malware protection | ✅ |
| Reputation filtering | ✅ |
| Graymail detection | ✅ |
| Spoof detection | ✅ |
| Management | CLI hoặc Web |
| Storage | ≥960 GB |
| Memory | ≥16 GB |
| Network | ≥2×1GbE |

### Đề xuất: Barracuda Email Security Gateway (×2)

| Thông số | Giá trị (Model 490/690) | Đạt? |
|----------|------------------------|:----:|
| License | Subscription, 500 users | ✅ |
| Spam | ✅ (Barracuda Advanced Spam) | ✅ |
| Malware | ✅ (Dual AV + ATP) | ✅ |
| Reputation | ✅ (Barracuda Reputation) | ✅ |
| Graymail | ✅ | ✅ |
| Spoof | ✅ (DMARC/DKIM/SPF) | ✅ |
| Storage | ≥1 TB SSD | ✅ VT |
| Memory | ≥32–64 GB | ✅ VT |
| Management | Web UI + CLI | ✅ |
| Network | 4–8×1GbE | ✅ VT |

### Bonus (tối đa 10)
| Mục | Mô tả | Điểm | Trạng thái |
|-----|-------|:----:|:----------:|
| 7.1 | SSD NVMe + Memory ≥64 GB | +10 | ✅ **≥64 GB** + **SSD** |
| **Tiểu mục** | | **10** | ✅ |

---

## 8. Hệ thống Firewall bảo vệ mạng Trụ sở UBCKNN

### Thông số tối thiểu HSMT
| Thông số | Yêu cầu |
|----------|---------|
| FW Throughput | >18 Gbps |
| Threat Prevention | >6.5 Gbps |
| Max Concurrent | >3M |
| Network | ≥8×1GbE |
| USB | ≥2 ports |
| Console/MGMT | ✅ |
| SSL Decryption | Menu riêng |
| Power | Dual AC |

### Phương án 1: FortiGate 2200E (×2, HA)
| Thông số | Giá trị | Đạt? |
|----------|---------|:----:|
| FW Throughput | **158 Gbps** | ✅ VT |
| TP | **11 Gbps** | ✅ VT |
| Concurrent | 50M+ | ✅ VT |
| Ports | 12×GE + 18×25GE + 4×40GE | ✅ VT |
| SSL Decryption | ✅ | ✅ |
| Power | Dual AC | ✅ |

### Phương án 2: Sophos XGS 4300 (×2, HA)
| Thông số | Giá trị | Đạt? |
|----------|---------|:----:|
| FW Throughput | **75 Gbps** | ✅ VT |
| TP (Xstream bundle) | **25.2 Gbps** | ✅ VT |
| TP (Standard) | **6.5 Gbps** | ✅ |
| IPS | **17.5 Gbps** | ✅ VT |
| Ports | 4×GE + 4×2.5GE + 4×10GbE SFP+ | ✅ VT |
| SSL/TLS | 8 Gbps | ✅ |
| Power | Dual (redundant) | ✅ |

### Bonus (tối đa 50)
| Mục | Mô tả | Điểm | FortiGate 2200E | Sophos XGS 4300 |
|-----|-------|:----:|:---------------:|:----------------:|
| 8.1 | FW Throughput ≥25 Gbps | +30 | ✅ 158 Gbps | ✅ 75 Gbps |
| 8.2 | TP >9 Gbps | +20 | ✅ 11 Gbps | ✅ 25.2 Gbps (Xstream) |
| **Tiểu mục** | | **50** | ✅ | ✅ |

---

## 9. Hệ thống kiểm soát nội dung truy cập Web (Trụ sở)

### Thông số tối thiểu HSMT
| Thông số | Yêu cầu |
|----------|---------|
| CPU | ≥1×8 core, ≥2.1 GHz |
| RAM | ≥16 GB |
| Storage | ≥960 GB (sau RAID) |
| Network | ≥4×1GbE |
| License | Subscription, 500 users |
| URL Filtering | Real-time |
| Web Proxy + SSL | Explicit/transparent, SSL inspection |
| Security cert | CC EAL 2+ / FIPS 140-2+ |

### Đề xuất: FortiGate 2200E tích hợp (Web Filtering + SSL Inspection)
*Hoặc thiết bị chuyên dụng ForcePoint (nếu yêu cầu riêng)*

| Thông số | Giá trị | Đạt? |
|----------|---------|:----:|
| URL Filtering | ✅ FortiGuard (AI/ML) | ✅ VT |
| SSL Inspection | ✅ Up to 17 Gbps | ✅ VT |
| Proxy | Explicit + transparent | ✅ |
| Security cert | CC EAL 4+, FIPS 140-3 | ✅ VT |
| DLP | ✅ FortiGuard DLP | ✅ |
| AV | ✅ FortiGuard AV | ✅ |
| Threat Intelligence | ✅ FortiGuard Labs | ✅ |
| RBAC + LDAP/AD | ✅ | ✅ |

### Bonus (tối đa 20)
| Mục | Mô tả | Điểm | Trạng thái |
|-----|-------|:----:|:----------:|
| 9.1 | AI/ML URL classification | +5 | ✅ FortiGuard AI/ML |
| 9.2 | RBAC + LDAP/AD | +5 | ✅ |
| 9.3 | CC EAL 4+/FIPS 140-3 + SSL Decryption + DLP + AV + TI | +10 | ✅ (FortiGate) |
| **Tiểu mục** | | **20** | ✅ |

---

## 10. Hệ thống phần mềm chống mã độc (Endpoint)

### Thông số tối thiểu HSMT
| Thông số | Yêu cầu |
|----------|---------|
| License | Subscription, 500 licenses |
| Scan | Real-time, manual, scheduled |
| Protection | Virus, Trojan, Spyware |
| Auto update | ✅ |
| OS | Windows, Linux |
| Central mgmt | Hostname, IP, version, connection, schedule |

### Đề xuất: Kaspersky Endpoint Security for Business (Enterprise) + Kaspersky EDR Optimum

| Thông số | Giá trị | Đạt? |
|----------|---------|:----:|
| Scan | ✅ Real-time / manual / scheduled | ✅ |
| Protection | ✅ Virus, Trojan, Spyware, Ransomware | ✅ |
| Auto update | ✅ Kaspersky Security Network | ✅ |
| OS | ✅ Windows, Linux, Mac | ✅ VT |
| Central mgmt | ✅ Kaspersky Security Center | ✅ |
| Behavior Monitoring | ✅ AI-based + auto isolation | ✅ VT |
| Ransomware rollback | ✅ | ✅ VT |
| Sandbox | ✅ Kaspersky Sandbox | ✅ VT |

### Bonus (tối đa 20)
| Mục | Mô tả | Điểm | Trạng thái |
|-----|-------|:----:|:----------:|
| 10.1 | Behavior Monitoring AI + auto isolation | +5 | ✅ |
| 10.2 | Ransomware rollback | +5 | ✅ |
| 10.3 | Sandbox | +10 | ✅ |
| **Tiểu mục** | | **20** | ✅ |

---

## Tổng hợp điểm dự kiến

| Hệ thống | Min | Bonus tối đa | Dự kiến đạt | Ghi chú |
|----------|:---:|:-----------:|:-----------:|---------|
| 1. DDoS (AED) | ✅ | 30 | **30** | Vượt 2/2 chỉ tiêu |
| 2. Firewall Core (FGT 2200E) | ✅ | 50 | **50** | Vượt 2/2 chỉ tiêu |
| 3. WAF (F5/Sophos) | ✅ | 30 | **20–30** | Phụ thuộc phương án |
| 4. SIEM (Splunk) | ✅ | 60 | **60** | Cần license EPS ≥4,000 |
| 5. PAM (Delinea) | ✅ | 20 | **20** | Server vượt cấu hình |
| 6. Patch Mgmt (BigFix) | ✅ | 10 | **0–10** | Phụ thuộc thương thảo ≥4 năm |
| 7. Mail Gateway (Barracuda) | ✅ | 10 | **10** | ≥64 GB RAM |
| 8. Firewall Tru sở (FGT/Sophos) | ✅ | 50 | **50** | Vượt 2/2 chỉ tiêu |
| 9. Web Content (FortiGate) | ✅ | 20 | **20** | Vượt 3/3 chỉ tiêu |
| 10. Anti-Malware (Kaspersky) | ✅ | 20 | **20** | Vượt 3/3 chỉ tiêu |
| **TỔNG CỘNG** | **700** | **300** | **~280–290** | |

### Tổng dự kiến: **~980–990 / 1000 điểm**
*Đã bao gồm 700 điểm tối thiểu + ~280–290 điểm vượt trội.*

---

## Khoảng trống cần giải quyết

| Vấn đề | Mức độ | Hướng xử lý |
|--------|:------:|-------------|
| **F5 WAF (A3)** — NTS không phân phối | 🔴 Cao | Tìm VST/VTI/NetPro; hoặc dùng Sophos WAF |
| **HCL BigFix (A6)** — Nguồn phân phối | 🟡 Trung | Xác nhận NTS; nếu không → SecPod |
| **BigFix bonus ≥4 năm** — Thương thảo | 🟢 Thấp | Đề xuất 4 năm thay vì 3 để +10 điểm |
| **Sophos WAF** — Không chuyên dụng | 🟡 Trung | Đánh giá tính tương thích HSMT |
| **SIEM EPS ≥4,000** — License | 🟢 Thấp | Chọn license phù hợp |

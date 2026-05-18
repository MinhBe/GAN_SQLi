# Phân tích WAF cho A3 — Sophos XGS 3100/3300 + Web Server Protection

## Nguồn chính thức xác nhận "Web Server Protection" = "Web Application Firewall"

**EnterpriseAV.com** (trang sản phẩm XGS 4300) công bố rõ ràng:

> **"Web Server Protection: Web Application Firewall"**

Đây là xác nhận chính hãng (Sophos) rằng module **Web Server Protection** chính là **WAF**.

### Tính năng Web Server Protection (từ EnterpriseAV.com)
- **Reverse proxy** với authentication options, SSL offloading, server load balancing
- **Business Application Policy Templates**: Pre-defined cho Microsoft Exchange, Outlook Anywhere, SharePoint
- **Protection**: URL/form hardening, deep-linking/directory traversal prevention, SQL injection, XSS, cookie signing
- **350+ attack patterns**
- **Dual antivirus scanning** trên traffic inbound
- **Logging, dashboard** qua Sophos Central
- **SKU mẫu (XGS 4300)**: SS430012ZZNCAA ($1,515.48/year)

## Thông số chính thức từ sophos.com

### XGS 3100 (Official)

| Thông số | Giá trị |
|----------|---------|
| Firewall Throughput | **47 Gbps** |
| TLS Inspection | **2.47 Gbps** |
| IPS | **10.5 Gbps** |
| NGFW | **9 Gbps** |
| **Threat Protection** | **7.4 Gbps** |
| Latency | 4 µs |
| Ports | 8×GE + 2×SFP + 2×SFP+ 10GbE |
| Flexi Port | 1 slot (up to 20 ports) |
| Concurrent connections | 12.26M |
| Bypass | 1 pair |
| Power | Dual (optional external) |

### XGS 3300 (Official)

| Thông số | Giá trị |
|----------|---------|
| Firewall Throughput | **58 Gbps** |
| TLS Inspection | **3.13 Gbps** |
| IPS | **14 Gbps** |
| NGFW | **12.5 Gbps** |
| **Threat Protection** | **10 Gbps** ✅ (vượt >6.5G min + >9G bonus!) |
| Latency | 4 µs |
| Ports | 8×GE + 2×SFP + 2×SFP+ 10GbE |
| Flexi Port | 1 slot (up to 20 ports) |
| Concurrent connections | 13.7M |
| New conn/sec | 257,800 |
| Bypass | 1 pair |
| Power | Dual (optional external) |

### XGS 4300 (Official)

| Thông số | Giá trị |
|----------|---------|
| Firewall Throughput | **75 Gbps** |
| TLS Inspection | **8 Gbps** |
| IPS | **29.5 Gbps** |
| NGFW | **23 Gbps** |
| **Threat Protection** | **25.2 Gbps** (Xstream) / **6.5 Gbps** (Standard) |
| Latency | 3 µs |
| Ports | 4×GE + 4×2.5GE + 4×SFP+ 10GbE |
| Flexi Port | 2 slots (up to 28 ports) |
| Concurrent connections | 16.6M |
| Bypass | 2 pairs |
| Power | Dual (optional external) |

## So sánh WAF: F5 BIG-IP vs Barracuda WAF vs Sophos WAF

| Tiêu chí | F5 BIG-IP Advanced WAF | Barracuda WAF | Sophos Web Server Protection |
|----------|:---------------------:|:-------------:|:----------------------------:|
| Thiết bị chuyên dụng WAF | ✅ | ✅ | ❌ (module trên NGFW) |
| Throughput L7 | **10 Gbps** | Cần xác nhận model | **47-58 Gbps** FW |
| SSL TPS | **48,000 TPS** | Cần xác nhận | **2.47-3.13 Gbps** TLS Insp |
| OWASP Top 10 | ✅ | ✅ | ✅ |
| Bot Protection | ✅ | ✅ | ✅ (qua IPS) |
| API Protection | ✅ | ✅ | ✅ (qua reverse proxy) |
| SSL Offloading | ✅ | ✅ | ✅ |
| Logging/Dashboard | BIG-IP Analytics | Barracuda Central | Sophos Central |
| **Qua NTS?** | ❌ | ✅ | ✅ |
| Giá (ước) | Cao nhất | Trung bình | Thấp nhất (add-on trên XGS) |

## Kết luận cho A3

**Khuyến nghị ưu tiên: Sophos XGS 3300 + Web Server Protection**
- Lý do: NTS phân phối ✅, giá thấp ✅, đủ chức năng WAF ✅
- Module Web Server Protection là "Web Application Firewall" (xác nhận từ Sophos)
- XGS 3300: TP 10 Gbps vượt cả min (6.5G) và bonus (9G)
- ⚠ Cần xác nhận HSMT có cho phép WAF dạng software module trên NGFW không

**Dự phòng: Barracuda WAF qua NTS**
- NTS có Barracuda WAF
- Thiết bị chuyên dụng WAF
- Cần crawl thông số kỹ thuật để đối chiếu

**F5 BIG-IP Advanced WAF**
- Phương án mạnh nhất nhưng không qua NTS
- Cần tìm VTI/VST/NetPro

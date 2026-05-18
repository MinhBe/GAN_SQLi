# Sophos Web Server Protection (WAF) — Phân tích cho HSMT A3

## Giới thiệu

Sophos **không có** thiết bị WAF chuyên dụng riêng. Thay vào đó, Sophos cung cấp **Web Server Protection** như một license add-on trên nền tảng XGS Firewall, biến XGS thành reverse proxy WAF.

## Web Server Protection License (gói WAF)

Theo documentation từ firewalls.com (bị 403) và enterpriseav.com (đã crawl), gói Web Server Protection bao gồm:

### Tính năng chính
- **Reverse proxy** với authentication options, SSL offloading, server load balancing
- **Business Application Policy Templates**: Pre-defined cho MS Exchange, Outlook Anywhere, SharePoint
- **Protection khỏi các tấn công web**:
  - SQL injection
  - Cross-Site Scripting (XSS)
  - Directory traversal
  - Deep-linking prevention
  - Cookie signing
  - URL and form hardening
  - 350+ attack patterns
- **Dual antivirus scanning** trên traffic inbound
- **Logging & dashboard** qua Sophos Central

### License SKUs (từ enterpriseav.com)

| Product | Term | SKU |
|---------|------|-----|
| XGS 4300 Web Server Protection | 1 Year | SS430012ZZNCAA |
| XGS 4300 Web Server Protection | 3 Year | SS430036ZZNCAA |

> Tương tự áp dụng cho XGS 3100/3300 với SKU theo model.

## Cách hoạt động

```
Client → Internet → XGS Firewall (Reverse Proxy WAF)
                        ↓
                Web Server Protection inspection
                  - TLS termination
                  - SQLi/XSS detection
                  - AV scanning
                  - Policy enforcement
                        ↓
                Internal Web Server
```

## So sánh với F5 BIG-IP WAF (đề xuất gốc)

| Tiêu chí | Sophos Web Server Protection | F5 BIG-IP WAF |
|----------|-----------------------------|---------------|
| Loại | License add-on trên XGS Firewall | Thiết bị chuyên dụng |
| OWASP Top 10 | ✅ | ✅ |
| SSL offloading | ✅ | ✅ |
| Reverse proxy | ✅ | ✅ |
| API protection | ✅ (qua reverse proxy) | ✅ |
| Bot detection | ✅ (qua IPS + WAF) | ✅ |
| Logging | Sophos Central | F5 Analytics |
| **Phù hợp NTS?** | ✅ (NTS phân phối Sophos) | ❌ (NTS không có F5) |
| Giá | Thấp hơn (shared platform) | Cao hơn (dedicated HW) |

## Đánh giá cho HSMT — Hạng mục A3 (WAF)

### Yêu cầu tối thiểu

| Yêu cầu | Sophos Web Server Protection trên XGS 3300/4300 |
|---------|------------------------------------------------|
| Throughput ≥500 Mbps | ✅ **38-75 Gbps FW** >> 500 Mbps |
| SSL TPS ≥6,600 | ✅ **2,470-8,000 Mbps SSL/TLS inspection** |
| OWASP Top 10 protection | ✅ (SQLi, XSS, CSRF, directory traversal) |
| 10GbE SFP+ ports | ✅ 2-4 ports |
| 1GbE ports | ✅ 8 ports |
| Logging & dashboard | ✅ Sophos Central |

### Bonus

| Bonus | Khả năng |
|-------|----------|
| Throughput ≥1 Gbps (+20) | ✅ **(38-75 Gbps FW)** |
| SSL TPS ≥15,000 (+10) | **Cần kiểm tra** — XGS 4300 có 8 Gbps SSL/TLS |

## Kết luận cho HSMT A3

**Có 2 hướng cho A3 WAF:**

1. **F5 BIG-IP WAF** (theo kế hoạch gốc) — cần tìm nhà phân phối khác ngoài NTS
2. **Sophos XGS + Web Server Protection** — có thể phân phối qua NTS, chi phí thấp hơn, nhưng cần chứng minh đây là giải pháp WAF tương đương

> ⚠ Sophos không có thiết bị WAF vật lý chuyên dụng. Web Server Protection là module phần mềm chạy trên nền tảng firewall đa năng. Cần đánh giá xem có phù hợp yêu cầu "thiết bị WAF chuyên dụng" trong HSMT hay không.

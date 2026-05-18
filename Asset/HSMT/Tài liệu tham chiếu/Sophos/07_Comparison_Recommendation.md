# So sánh & Khuyến nghị XGS cho HSMT

## Ma trận chọn model

| Hạng mục | Yêu cầu tối thiểu | Bonus target | Model đề xuất | Tối thiểu | Bonus |
|----------|------------------|-------------|---------------|-----------|-------|
| **A2. Firewall Core** (2×) | FW >18 Gbps, TP >6.5 Gbps | FW ≥25 (+30), TP ≥9 (+20) | **XGS 4300** | ✅ 75G/6.5G | ✅ 75G/25.2G* |
| **B1. Firewall Trụ sở** (2×) | FW >18 Gbps, TP >6.5 Gbps | FW ≥25 (+30), TP ≥9 (+20) | **XGS 4300** | ✅ | ✅ |
| **B2. Web Filtering** (2×) | URL filtering, SSL inspect | AI/ML URL (+5), RBAC (+5), CC EAL4+ (+10) | XGS 3300 hoặc 4300 | ✅ | ✅ |

## XGS 3300 vs XGS 4300

| Tiêu chí | XGS 3300 | XGS 4300 |
|----------|----------|----------|
| **FW Throughput** | 58 Gbps ✅ | **75 Gbps ✅** |
| **Threat Protection** | **3 Gbps ❌** | **6.5-25.2 Gbps ✅*** |
| IPsec VPN | 31.1 Gbps | **62.5 Gbps** |
| Concurrent sessions | 13.7M | 16.6M |
| 10GbE SFP+ | 2 | **4** |
| Bypass pairs | 1 | **2** |
| Flexi Port slots | 1 | **2** |
| Giá (ước lượng) | Thấp hơn | Cao hơn |
| **Đạt ≥25 FW + ≥9 TP bonus** | **❌** (TP=3G) | **✅** (TP=6.5-25.2G*) |

## Kết luận

- **XGS 3300**: Không đủ Threat Prevention (>6.5 Gbps) cho yêu cầu tối thiểu — chỉ đạt 3 Gbps
- **XGS 4300**: Đạt tất cả yêu cầu tối thiểu, có thể đạt bonus FW ≥25 và TP ≥9 nếu dùng **Xstream Protection bundle** (TP=25.2 Gbps)
- **XGS 4500**: Cao hơn nữa (80G FW, 31.85G TP) nhưng có thể overkill

> **Khuyến nghị: Dùng XGS 4300 cho cả A2 và B1** (4 thiết bị: 2 core + 2 trụ sở)
> 
> \* *Cần xác nhận Threat Protection throughput theo license bundle: Base/Standard cho 6.5 Gbps, Xstream Protection cho 25.2 Gbps.*

## Liên kết datasheet đã tải

| File | Nguồn |
|------|-------|
| `Sophos_Firewall_Brochure.pdf` | sophos.com (đã tải) |
| `Sophos_XGS_Data_Sheet.pdf` | sophos.com (đã tải) |
| `Sophos_XGS_Series_Datasheet.pdf` | sophos.com (đã tải) |
| `Sophos_XGS_4300_4500_Operating_Instructions.pdf` | docs.sophos.com (đã tải) |

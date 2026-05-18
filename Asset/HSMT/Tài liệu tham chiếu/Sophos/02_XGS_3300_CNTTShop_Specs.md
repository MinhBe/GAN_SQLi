# Sophos XGS 3300 HW — Thông số kỹ thuật (CNTTShop.vn)

Nguồn: https://cnttshop.vn/firewall-sophos-xgs-3300-hw-appliance

---

## Thông tin cơ bản

- **Model**: XGS-3300-HW
- **Phân khúc**: Enterprise, 750-1000 thiết bị
- **License**: Base license (mặc định)

## Physical Interfaces

| Interface | Số lượng |
|-----------|----------|
| GE copper (RJ45) | 8 |
| SFP fiber | 2 |
| SFP+ 10 GbE fiber | 2 |
| Bypass port pairs | 1 |
| RJ45 MGMT | 1 |
| COM RJ45 | 1 |
| Micro-USB (cable incl.) | 1 |
| USB 3.0 (front) | 2 |
| USB 2.0 (rear) | 1 |
| Flexi Port slots | 1 |

## Performance

| Metric | Value |
|--------|-------|
| **Firewall throughput** | **58,000 Mbps (58 Gbps)** |
| Firewall IMIX | 27,000 Mbps |
| Firewall Latency (64 byte UDP) | 4 µs |
| **IPS throughput** | **14,000 Mbps (14 Gbps)** |
| **Threat Protection throughput** | **3,000 Mbps (3 Gbps)** ⚠ |
| Concurrent connections | 13,700,000 |
| New connections/sec | 257,800 |
| Xstream SSL/TLS Inspection | 3,130 Mbps |
| Xstream SSL/TLS Concurrent connections | 102,400 |

## Tính năng bảo mật

- Xstream TLS và DPI engine
- IPS (Intrusion Prevention)
- ATP (Advanced Threat Protection)
- Security Heartbeat (Synchronized Security)
- SD-RED VPN
- Web Security and Control
- Application Control
- DKIM, BATV (chống giả mạo email)

## Đánh giá cho HSMT

| Tiêu chí | Yêu cầu | XGS 3300 |
|----------|---------|----------|
| FW throughput >18 Gbps | ✅ | **58 Gbps** ✅ |
| FW ≥25 Gbps (+30đ) | ✅ | **58 Gbps** ✅ |
| Threat Prevention >6.5 Gbps | ✅ | **3 Gbps** ❌ (cần XGS 4300) |
| TP ≥9 Gbps (+20đ) | ✅ | **3 Gbps** ❌ |
| Concurrent ≥3M | ✅ | 13.7M ✅ |
| ≥5×1GbE | ✅ | 8×GE ✅ |
| 10GbE SFP+ | ✅ | 2×SFP+ ✅ |

> ⚠ Lưu ý: Threat Protection throughput của XGS 3300 chỉ 3 Gbps — **không đạt** yêu cầu tối thiểu >6.5 Gbps cho Firewall Core. Cần dùng **XGS 4300** (Threat Protection 6.5-25.2 Gbps) hoặc **XGS 4500** (8.65-31.85 Gbps) để đạt bonus.

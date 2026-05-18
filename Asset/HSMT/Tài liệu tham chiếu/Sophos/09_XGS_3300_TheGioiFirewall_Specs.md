# Sophos XGS 3300 — Thông số kỹ thuật (TheGioiFirewall)

Nguồn: https://thegioifirewall.com/san-pham/sophos-xgs-3300/

---

## System Performance

| Metric | Value |
|--------|-------|
| **Firewall throughput** | **40,000 Mbps (40 Gbps)** |
| Firewall IMIX | 24,500 Mbps |
| Firewall Latency | 4 µs |
| Concurrent connections | **13,700,000** |
| New connections/sec | 257,800 |
| **IPS throughput** | **13,440 Mbps (13.44 Gbps)** |
| **NGFW Throughput** | **12,500 Mbps** |
| **Threat Protection Throughput** | **2,770 Mbps** |
| IPsec VPN throughput | 6,500 Mbps |
| **Xstream SSL/TLS Inspection** | **3,130 Mbps** |
| Xstream SSL/TLS Concurrent connections | 102,400 |

> ⚠ Lưu ý: Số liệu trên thegioifirewall.com có thể thấp hơn số liệu chính thức từ sophos.com (FW 58G, TP 10G) do license bundle khác nhau.

## Physical Interfaces

| Interface | Số lượng |
|-----------|----------|
| GE RJ45 (copper) | 8 |
| SFP fiber | 2 |
| SFP+ 10 GbE fiber | 2 |
| Max total interfaces | 20 (1 Flexi Port slot) |
| RJ45 MGMT | 1 |
| Micro-USB | 1 |
| COM RJ45 | 1 |
| USB 3.0 (front) | 2 |
| USB 2.0 (rear) | 1 |
| Storage | min. 240 GB SATA-III SSD |
| Display | Multi-function LCD module |

## Dimensions & Environment

| Spec | Value |
|------|-------|
| Mounting | 1U rackmount |
| Dimensions | 438 × 44 × 405 mm |
| Weight | 4.7 kg (unpacked) / 7 kg (packed) |
| PSU | Internal auto-ranging DC |
| Power Consumption | 50W idle / 201W max |
| Operating Temp | 0°C to 40°C |

## Comparing Spec Sources

| Metric | Sophos.com (official) | TheGioiFirewall | Chênh lệch |
|--------|----------------------|----------------|-----------|
| FW throughput | 58 Gbps | 40 Gbps | -18G |
| IPS | 14 Gbps | 13.44 Gbps | ~same |
| TP | 10 Gbps | 2.77 Gbps | -7.23G ⚠ |
| NGFW | 12.5 Gbps | 12.5 Gbps | ~same |
| IPsec VPN | 31.1 Gbps | 6.5 Gbps | -24.6G ⚠ |
| SSL/TLS | 3.13 Gbps | 3.13 Gbps | ~same |

> Kết luận: Luôn dùng số liệu từ **sophos.com** (nguồn chính thức) thay vì reseller.

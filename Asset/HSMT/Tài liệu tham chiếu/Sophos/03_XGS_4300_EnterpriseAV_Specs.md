# Sophos XGS 4300 — Thông số kỹ thuật chi tiết (EnterpriseAV.com)

Nguồn: https://www.enterpriseav.com/XGS-4300.asp

---

## Performance

| Metric | Value |
|--------|-------|
| **Firewall throughput** | **75,000 Mbps (75 Gbps)** |
| Firewall IMIX | 33,000 Mbps |
| Firewall Latency (64 byte UDP) | **3 µs** |
| **IPS throughput** | **29,500 Mbps (29.5 Gbps)** |
| **Threat Protection throughput** | **6,500 Mbps (6.5 Gbps)** |
| NGFW | 23,000 Mbps |
| Concurrent connections | **16,600,000** |
| New connections/sec | 368,000 |
| **IPsec VPN throughput** | **62,500 Mbps** |
| IPsec VPN concurrent tunnels | 8,500 |
| SSL VPN concurrent tunnels | 7,500 |
| **Xstream SSL/TLS Inspection** | **8,000 Mbps** |
| Xstream SSL/TLS Concurrent connections | 276,480 |

## Physical Specifications

| Spec | Value |
|------|-------|
| Mounting | 1U rackmount (sliding rails incl.) |
| Dimensions (W×H×D) | 438 × 44 × 510 mm |
| Weight | 8.7 kg unpacked / 14.9 kg packed |

## Power

| Spec | Value |
|------|-------|
| PSU | Internal Hot Swappable AC-DC 100-240VAC, 3.7-7.4A@50-60 Hz, **Redundant PSU option** |
| Power consumption | 131 W / 447.43 BTU/hr (idle), 268.35 W / 916.56 BTU/hr (max) |
| PoE addition enabled | 152 W / 519 BTU/hr |

## Operating Environment

| Spec | Value |
|------|-------|
| Operating temperature | 0°C to 40°C |
| Storage temperature | -20°C to +70°C |
| Humidity | 10% to 90%, non-condensing |

## Certifications

CB, CE, UKCA, UL, FCC, ISED, VCCI, KC, RCM, NOM, Anatel, CCC, BSMI, TEC, SDPPI

## Physical Interfaces

| Interface | Số lượng |
|-----------|----------|
| Storage (local quarantine/logs) | 1× min. 240 GB SATA-III SSD |
| **GbE copper** | **4** |
| **2.5 GbE copper** | **4** |
| **SFP+ 10 GbE fiber** | **4** |
| Bypass port pairs | **2** |
| RJ45 MGMT | 1 |
| COM RJ45 | 1 |
| Micro-USB (cable incl.) | 1 |
| USB 3.0 (front) | 2 |
| Flexi Port slots | **2** |
| Max total port density | **28** |
| Max PoE (Flexi Port) | 2 modules: 4 ports, 60W max. each |
| Display | Multi-function LCD module |

## Licensing Options

### Bundles
- **Xstream Protection Bundle**: Base + Network Protection + Web Protection + Zero-Day Protection + Central Orchestration + Enhanced Support
- **Standard Protection Bundle**: Base + Network Protection + Web Protection + Enhanced Support
- **Base License**: Stateful FW, VPN, Wireless (perpetual)

### Individual Subscriptions
- Network Protection: IPS, ATP, Security Heartbeat, SD-RED
- Web Protection: Web Control, App Control
- Zero-Day Protection: ML + Cloud Sandboxing
- Central Orchestration: SD-WAN VPN Orchestration, CFR Advanced
- Email Protection: Anti-spam, AV, DLP, Encryption
- Web Server Protection: WAF

## Key Features

- **Xstream Architecture**: Network Flow FastPath, TLS 1.3 inspection, DPI
- **SD-WAN**: Performance-based link selection, load balancing, zero-impact transitions
- **Synchronized Security**: Security Heartbeat with Sophos endpoints
- **Synchronized App Control**: Auto-identify unknown applications
- **Zero-Day Protection**: ML (deep learning) + Cloud Sandboxing (SophosLabs Intelix)
- **Central Management**: Sophos Central (multi-firewall, zero-touch deployment)
- **Deployment**: Hardware, AWS/Azure, VMware/Hyper-V/KVM, Software (x86)

## Đánh giá cho HSMT

| Tiêu chí | Yêu cầu HSMT | XGS 4300 | Điểm |
|----------|-------------|----------|------|
| FW Throughput >18 Gbps | Tối thiểu | **75 Gbps ✅** | Đạt |
| FW Throughput ≥25 Gbps | **Bonus +30** | **75 Gbps ✅** | **+30** |
| Threat Prevention >6.5 Gbps | Tối thiểu | 6.5 Gbps ✅ (sát ngưỡng) | Đạt |
| TP ≥9 Gbps | **Bonus +20** | 6.5 Gbps ❌ (cần Xstream Protection + license) | Cần xác nhận |
| Concurrent sessions ≥3M | Tối thiểu | 16.6M ✅ | Đạt |
| ≥5×1GbE ports | Tối thiểu | 4×GE + 4×2.5GE ✅ | Đạt |
| ≥4×10GbE SFP+ | Yêu cầu | 4×SFP+ ✅ | Đạt |
| Dual PSU | Yêu cầu | Optional ✅ | Đạt |
| 1U Rackmount | Yêu cầu | ✅ | Đạt |

> ⚠ Ghi chú: Threat Protection throughput trên EnterpriseAV ghi 6,500 Mbps — đúng bằng ngưỡng tối thiểu >6.5 Gbps. Tuy nhiên trên Sophos.com ghi XGS 4300 Threat Protection là **25.2 Gbps** (có thể khác nhau do license bundle: Base vs. Xstream Protection). Cần kiểm tra license bundle để đạt 25.2 Gbps cho bonus +20.

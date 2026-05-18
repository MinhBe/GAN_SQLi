# URL Crawl Status Report - Arbor APS DDoS Datasheets

**Date:** May 18, 2026
**Target Directory:** C:\Users\Admin\Documents\GAN_SQLi\Asset\HSMT\Tài liệu tham chiếu\DDoS

---

## Crawl Results Summary

| # | URL | Status | Result |
|---|---|---|---|
| 1 | https://www.netscout.com/products/ddos-mitigation/pravail-aps | **404 Not Found** | Page no longer exists on NETSCOUT site (Pravail APS product page discontinued) |
| 2 | https://www.netscout.com/resources/data-sheets/arbor-managed-availability-protection-system | **Fetched (No Datasheet)** | Returns resource center listing page; the specific datasheet for Arbor Managed Availability Protection System is behind a content gate / PDF viewer. No extractable spec content. |
| 3 | https://www.al-jammaz.com/uploads/5/0/7/1/50711957/01-arbor_datasheet.pdf | **404 Not Found** | PDF no longer available on al-jammaz.com |
| 4 | https://www.commoncriteriaportal.org/files/epfiles/Arbor%20Networks%20ST%20V2%200%20Mar%2010-2014.pdf | **Success (PDF)** | Common Criteria Security Target for Pravail APS 2100 Series - **Full specs extracted** |
| 5 | https://www.arbornetworks.com/ddos-protection-products/arbor-aps | **Redirected** | Domain now redirects to NETSCOUT TMS product page. No original Arbor APS product page available. |
| 6 | https://fr.scribd.com/document/431007619/Arbor-APS-STT-Unit-01-Design-Basics-25-Jan2018 | **Fetched (Login Required)** | Scribd page shows metadata only; full document requires login/subscription. Title: "Arbor APS STT Unit 01 Design Basics 25 Jan2018" - 31 pages |
| 7 | https://www.ncsi.com/wp-content/uploads/2021/04/Arbor-DDoS-Attack-Protection-Solutions.pdf | **Success (PDF)** | Arbor DDoS Attack Protection Solutions Solution Brief - **Specs extracted** |
| 8 | https://www.esecurityplanet.com/products/arbor-ddos-protection | **403 Forbidden** | Blocked by esecurityplanet.com (access denied) |

---

## Files Created

| File | Source URL | Content |
|---|---|---|
| Arbor_APS_2100_Series_Security_Target.md | URL #4 (Common Criteria Portal) | Full detailed specs: throughput, port counts, form factor, deployment modes, CC EAL2 certification, management features |
| Arbor_DDoS_Attack_Protection_Solutions.md | URL #7 (NCSI) | Product portfolio overview: APS (sub 100Mbps-40Gbps), TMS (400Gbps), Arbor Cloud (7Tbps), threat intelligence |
| Arbor_Threat_Mitigation_System.md | URL #5 (NETSCOUT) | TMS specs: 500 Gbps per appliance, 50 Tbps total, virtualization support, deployment options |

---

## Consolidated Specs Table (Extracted)

| Spec | APS 2104 | APS 2105 | APS 2107 | APS 2108 | TMS |
|---|---|---|---|---|---|
| **Throughput (Clean Traffic)** | Up to 2 Gbps | Up to 4 Gbps | Up to 8 Gbps | Up to 10 Gbps | Up to 500 Gbps per appliance |
| **Total Deployment Capacity** | - | - | - | - | Up to 50 Tbps |
| **HTTP(s) Connections/sec** | 368K/613K | 368K/613K | 368K/613K | 368K/613K | - |
| **Memory** | 24 GB | 24 GB | 24 GB | 24 GB | - |
| **Processor** | 2x Xeon | 2x Xeon | 2x Xeon | 2x Xeon | - |
| **1GbE Ports** | 12 (various) | 12 (various) | 12 (various) | 12 (various) | - |
| **10GbE Ports** | 4 (SR/LR) | 4 (SR/LR) | 4 (SR/LR) | 4 (SR/LR) | - |
| **Form Factor** | 2U | 2U | 2U | 2U | 2U/6U/Virtual |
| **Deployment** | Inline / Monitor | Inline / Monitor | Inline / Monitor | Inline / Monitor | Out-of-path / Inline |
| **Certification** | CC EAL2 | CC EAL2 | CC EAL2 | CC EAL2 | - |
| **Bypass** | HW + SW | HW + SW | HW + SW | HW + SW | - |

---

## Notes

- **Pravail APS** is the product line also known as Arbor APS (Availability Protection System). The 2100 series was the hardware appliance line.
- **Arbor APS** is also referenced as detecting/mitigating attacks from sub-100 Mbps to 40 Gbps (per the Solution Brief).
- **Arbor TMS** is a higher-end mitigation platform for service providers, with significantly higher throughput (500 Gbps per appliance, 50 Tbps total).
- **Arbor Cloud** provides over 7 Tbps of global scrubbing capacity.
- The Scribd document (URL #6) titled "Arbor APS STT Unit 01 Design Basics" likely contains additional design details but requires authentication.

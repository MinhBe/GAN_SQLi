# Arbor Pravail APS 2100 Series - Security Target (Common Criteria)

**Source:** Common Criteria Portal - Security Target Document
**URL:** https://www.commoncriteriaportal.org/files/epfiles/Arbor%20Networks%20ST%20V2%200%20Mar%2010-2014.pdf
**Document:** Pravail APS 2100 Series Appliances, Version 5.4 Security Target, Version 2.0, March 10, 2014
**Prepared By:** CygnaCom Solutions for Arbor Networks, Inc.

---

## 1. Product Overview

| Attribute | Detail |
|---|---|
| **Product Name** | Arbor Networks Pravail Availability Protection System (APS) 2100 Series |
| **TOE Type** | Distributed Denial of Service (DDoS) Detection and Mitigation Appliance |
| **Vendor** | Arbor Networks, Inc. (now part of NETSCOUT) |
| **Software Version** | Pravail APS Version 5.4 |
| **Certification** | Common Criteria EAL2 (Evaluation Assurance Level 2) |

---

## 2. Models and Performance Specifications

| Specification | APS 2104 | APS 2105 | APS 2107 | APS 2108 |
|---|---|---|---|---|
| **Memory** | 24 GB | 24 GB | 24 GB | 24 GB |
| **Inspected Throughput** | Up to 2 Gbps | Up to 4 Gbps | Up to 8 Gbps | Up to 10 Gbps |
| **HTTP(s) Connections/sec (Recommended Protection)** | 368K | 368K | 368K | 368K |
| **HTTP(s) Connections/sec (Filter List Only)** | 613K | 613K | 613K | 613K |
| **Processor** | 2 Intel Xeon CPU | 2 Intel Xeon CPU | 2 Intel Xeon CPU | 2 Intel Xeon CPU |

---

## 3. Interface Options / Port Counts

All models support the following protection interface options:

| Interface Option | Port Configuration |
|---|---|
| **Option 1 - Copper** | 12 x 10/100/1000 BaseT Copper |
| **Option 2 - Mixed Copper/Fiber** | 4 x 10/100/1000 BaseT Copper + 4 x GE SX Fiber + 4 x GE LX Fiber |
| **Option 3 - SX Fiber** | 12 x GE SX Fiber |
| **Option 4 - LX Fiber** | 12 x GE LX Fiber |
| **Option 5 - 10GE SR Fiber** | 4 x 10 GE SR Fiber |
| **Option 6 - 10GE LR Fiber** | 4 x 10 GE LR Fiber |

**Management Interfaces:**
- Management port 0 (mgt0): GbE NIC 1
- Management port 1 (mgt1): GbE NIC 2
- RJ45 Serial console port (Cisco pinouts)
- VGA connector
- USB ports (USB0, USB1, USB2, USB3)

---

## 4. Form Factor

| Specification | Detail |
|---|---|
| **Chassis** | 2U rack height |
| **Height** | 3.45 in (8.76 cm) |
| **Width** | 17.4 in (43.53 cm) |
| **Depth** | 24 in (61 cm) |
| **Weight** | 41 lbs (18.5 kg) |
| **Power** | 600W AC or DC hot-swap, redundant power supplies with PMBus support |
| **AC Input** | 100-127 VAC, 50-60 Hz, 6A max / 200-240 VAC, 50-60 Hz, 3A max |
| **DC Input** | -48 to -60 VDC, 13A max |

---

## 5. Environmental Specifications

| Parameter | Operating | Non-Operating |
|---|---|---|
| **Temperature** | 50 to 95 F (10 to 35 C) | -40 to 158 F (-40 to 70 C) |
| **Humidity** | 5% to 85% | 95%, non-condensing at 73-104 F (23-40 C) |

---

## 6. Deployment Modes

| Mode | Description |
|---|---|
| **Inline Mode (Active Protection)** | Pravail APS acts as a physical cable between Internet and protected network. All traffic flows through the appliance. Analyzes, detects, and mitigates attacks before forwarding. |
| **Inline Mode (Inactive/Monitoring)** | Analyzes traffic and detects attacks without performing mitigations. Used to set/customize policies before going active. |
| **Monitor Mode (Out-of-Line)** | Deployed via SPAN port or network tap. Traffic is mirrored to the appliance for analysis. No traffic forwarding; no mitigation takes place. Used primarily for trial/evaluation. |
| **Cloud Signaling** | When thresholds for volumetric/rate-based attacks are met, the TOE signals the ISP or MSSP (via trusted channel) for cloud-based mitigation. Cleaned traffic is then routed back. |

**Bypass Capabilities:**
- Integrated hardware bypass
- Internal "software" bypass to pass traffic without inspection
- Bypass-capable: if power failures, hardware failures, or software issues occur, network traffic can pass through the appliance unaffected.

---

## 7. Certifications

- **Common Criteria:** EAL2 (Evaluation Assurance Level 2)
- **Protection Profile:** Consistent with commercially reasonable security practices
- **Assurance Components:** ADV_ARC.1, ADV_FSP.2, ADV_TDS.1, AGD_OPE.1, AGD_PRE.1, ALC_CMC.2, ALC_CMS.2, ALC_DEL.1, ASE_CCL.1, ASE_ECD.1, ASE_INT.1, ASE_OBJ.2, ASE_REQ.2, ASE_SPD.1, ASE_TSS.1, ATE_COV.1, ATE_FUN.1, ATE_IND.2, AVA_VAN.2

---

## 8. Management Features

| Feature | Detail |
|---|---|
| **Web UI** | HTTPS-based graphical user interface. Menus: Summary, Explore, Protection Groups, Administration |
| **CLI** | Command Line Interface via serial console, SSH (Telnet disabled by default) |
| **Authentication** | Local password authentication, RADIUS, TACACS+ |
| **User Roles** | system_admin (full read/write), system_user (read-only), system_none (no access) |
| **Audit** | Security audit generation, user identity association, audit review, protected audit trail storage |
| **SNMP** | SNMP v2 or SNMP v3 (traps for alerts) |
| **Syslog** | Configurable syslog server for event notifications |
| **Email Alerts** | Email notifications for configurable events |
| **NTP** | Network Time Protocol support |
| **Cloud Signaling** | Automatic notification to ISP/MSSP for volumetric attack mitigation |
| **ATLAS Intelligence Feed (AIF)** | Subscription-based threat intelligence feed |
| **Browser Compatibility** | Firefox ESR 17/21, IE 9/10, Safari 6, Google Chrome 27 |

---

## 9. Security Functions

- **DDoS Defense (DDoS_DEF_EXT.1):** Identification and mitigation of DDoS attacks via filtering, whitelists, blacklists, TCP SYN rate monitoring
- **Security Audit (FAU):** Audit data generation, review, selectable audit, protected audit trail storage, reliable time stamps
- **Identification & Authentication (FIA):** User identification, authentication, password policy, RADIUS/TACACS+ support
- **Security Management (FMT):** Management of TSF data, specification of management functions, security roles
- **Protection of TSF (FPT):** Failure with preservation of secure state (bypass)
- **Trusted Path/Channels (FTP):** HTTPS (SSL/TLS) for Web UI, SSH for CLI, trusted channels for authentication and Cloud Signaling

---

## 10. Data Captured

- **TSF Data:** System parameters, admin settings, security attributes, authentication data, traffic control attributes, audit logging parameters
- **User Data:** Data created by external and internal IT entities. Information flows created by Clients and Servers.

---

*Extracted from Common Criteria Security Target Document - Arbor Networks Pravail APS Series 2100 (Version 5.4), ST Version 2.0, March 10, 2014*

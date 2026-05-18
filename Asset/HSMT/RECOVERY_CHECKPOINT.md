# RECOVERY CHECKPOINT — HSMT UBCKNN Bid Analysis

*Tạo lúc: 2026-05-18. Cập nhật mỗi khi có thay đổi lớn.*

---

## 1. MỤC TIÊU (GOAL)

Đối chiếu thông số kỹ thuật của **10 hạng mục** trong gói thầu **UBCKNN (Ủy ban Chứng khoán Nhà nước)** với tài liệu datasheet từ các hãng (Fortinet, F5, Sophos, Barracuda, Delinea, NETSCOUT, Kaspersky, Splunk, IBM QRadar, Securonix) để lập **ma trận tuân thủ (compliance matrix)** có chấm điểm.

## 2. THÔNG TIN GÓI THẦU

| Field | Value |
|---|---|
| **Bid Package** | **BP2500701601** |
| TBMT | IB2600177138 |
| KHLCNT | PL2500277614 |
| Project | Thay thế một số giải pháp đảm bảo an toàn bảo mật hệ thống CNTT của UBCKNN |
| Client | Ban Công nghệ và Chuyển đổi số - UBCKNN |
| Funding | Ngân sách nhà nước |
| Contract | Trọn gói, đấu thầu rộng rãi trong nước |
| Duration | 180 ngày |

## 3. YÊU CẦU (REQUIREMENTS)

### 3.1 10 Hạng mục

| # | Hệ thống | Vendor đề xuất | SL |
|---|---|---|---|
| 1 | DDoS Protection | NETSCOUT Arbor AED | 1 |
| 2 | Firewall Core | FortiGate 2200E | 2 |
| 3 | WAF | F5 BIG-IP / Barracuda WAF / Sophos+WSP | 2 |
| 4 | SIEM | Splunk Enterprise Security | 1 |
| 5 | PAM | Delinea Secret Server + Privilege Manager | 1 RDS + 2 PAS |
| 6 | Patch Management | HCL BigFix (gia hạn) | 1 |
| 7 | Mail Gateway | Barracuda Email Security Gateway | 2 |
| 8 | Firewall Trụ sở | FortiGate 2200E / Sophos XGS 4300 | 2 |
| 9 | Web Content Control | FortiGate / Sophos (tích hợp) | 2 |
| 10 | Anti-Malware Endpoint | Kaspersky Endpoint Security + EDR | 500 licenses |

### 3.2 Thang điểm (700 + 300 = 1000)

- **Tối thiểu đạt**: 700 điểm (đáp ứng tất cả yêu cầu tối thiểu trong Chương V)
- **Điểm vượt trội (bonus)**: tối đa 300 điểm

**Các tiêu chí bonus:**

| Hạng mục | Tiêu chí | Điểm |
|---|---|---|
| 1. DDoS | Throughput ≥1 Gbps | 20 |
| | Flood Prevention ≥18 Mpps | 10 |
| 2. Firewall Core | FW Throughput ≥25 Gbps | 30 |
| | Threat Prevention ≥9 Gbps | 20 |
| 3. WAF | Throughput ≥1 Gbps | 20 |
| | SSL TPS ≥15,000 | 10 |
| 4. SIEM | EPS ≥4,000 hoặc 200 GB/ngày | 30 |
| | Cảnh báo đa kênh hoặc phân loại tự động | 20 |
| | Lưu trữ log ≥12 tháng | 10 |
| 5. PAM | RDS: ≥2 CPU Xeon Gold Gen5+ + ≥2.4TB | 10 |
| | PAS: ≥32 cores/CPU + ≥3.6TB | 10 |
| 6. Patch Mgmt | BH mở rộng + license ≥4 năm (tối thiểu 3 năm) | 10 |
| 7. Mail Gateway | SSD NVMe + RAM ≥64 GB | 10 |
| 8. Firewall HQ | FW Throughput ≥25 Gbps | 30 |
| | Threat Prevention ≥9 Gbps | 20 |
| 9. Web Filtering | URL AI/ML hoặc multi-layer rating | 5 |
| | RBAC hoặc LDAP/AD sync | 5 |
| | CC EAL 4+ / FIPS 140-3 hoặc SSL + DLP + AV + TI | 10 |
| 10. Anti-Malware | Behavior Monitoring AI + auto-isolation | 5 |
| | Rollback ransomware | 5 |
| | Sandbox tích hợp | 10 |

## 4. NHỮNG GÌ ĐÃ LÀM (DONE)

### 4.1 Tải datasheet từ các hãng

Đã download **37 file PDF** vào: `Asset\HSMT\Tài liệu tham chiếu\PDF\`

| Hãng | Files | Source |
|---|---|---|
| **Fortinet** (8) | FortiGate 1800F, 2000E, 2200E, FortiDDoS, FortiMail, FortiSIEM, FortiWeb, Product Matrix | fortinet.com (2000E lấy từ imsecurity-global.com) |
| **F5** (5) | BIG-IP Advanced WAF, HW Platforms, System Platforms, Virtual Edition, Silverline WAF | f5.com |
| **Sophos** (4) | XGS Series, XGS Data Sheet, Firewall Brochure, XGS 4300/4500 Operating Instructions | sophos.com |
| **Barracuda** (2) | Email Security Gateway, Email Protection | barracuda.com |
| **Delinea** (5) | Secret Server, Privilege Manager, Privileged Behavior Analytics, Corporate Brochure, Platform Upgrade | delinea.com |
| **NETSCOUT** (3) | Arbor Edge Defense, Arbor Sightline, Capabilities | netscout.com |
| **Kaspersky** (4) | Endpoint Security (Business/Select/Enterprise), EDR Optimum | kaspersky.com |
| **SIEM** (3) | Splunk Enterprise Security, IBM QRadar SIEM, Securonix Platform | splunk.com, ibm.com, securonix.com |
| **Arbor APS** (2) | CC EAL4 Security Target, DDoS Protection Solutions | Từ nhiều nguồn |
| **Xantaro Blog** (1) | Arbor APS Xantaro Blog | xantaro.net |

### 4.2 OCR (Fast mode) — tất cả PDF

Đã chạy OCR trên **37/37 file PDF** → output vào: `Asset\HSMT\Tài liệu tham chiếu\PDF_OCR\`

- **Tool**: `Skill\OCR_PDF\scripts\ocr_processor.py` (Fast mode — PyMuPDF native text extraction)
- **GPU (RTX 3050)**: Chưa cần dùng — các file đều có text layer

### 4.3 Kiểm tra phân phối NTS (Nam Trường Sơn)

File: `Asset\HSMT\Tài liệu tham chiếu\Nam Trường Sơn\NTS_Product_Coverage_Summary.md`

| Hệ thống | Vendor | NTS Coverage | Ghi chú |
|---|---|---|---|
| A1. DDoS | NETSCOUT | ✅ | Arbor AED |
| A2. Firewall Core | FortiGate (đổi từ Sophos) | ⚠️ **Cần xác nhận** | NTS có Fortinet? |
| A3. WAF | F5 / Barracuda / Sophos | ❌ F5 / ⚠️ Barracuda có | Cần quyết định |
| A4. SIEM | Splunk + Dell servers | ⚠️ Cần xác nhận | NTS có OpenText |
| A5. PAM | Delinea | ✅ | Secret Server + PM |
| A6. Patch Mgmt | HCL BigFix | ❌ | Mua trực tiếp HCL |
| A7. Mail Gateway | Barracuda | ✅ | Email Security GW |
| B1. Firewall HQ | FortiGate / Sophos | ✅ (Sophos) | Cần quyết định |
| B2. Web Content | FortiGate / Sophos | ✅ (Sophos) | Tích hợp firewall |
| B3. Anti-Malware | Kaspersky | ✅ | Exclusive VN |

### 4.4 OCR gốc từ "Yêu cầu của khách"

Đã OCR các file PDF yêu cầu kỹ thuật vào: `Asset\HSMT\Yêu cầu của khách\Tổng hợp yêu cầu OCR\`

Các file quan trọng nhất:
- `3. Chuong V_danh_gia_ve_ky_thuat.md` — Thông số kỹ thuật chi tiết tất cả 10 hạng mục (~661 dòng)
- `2.1. Chuong III_Muc 3_Tieu_chuan_danh_gia_ve_ky_thuat_max.md` — Bảng điểm bonus (20 dòng)
- `1. TBMT - Bảo mật UBCK.md` — Thông báo mời thầu

### 4.5 Sophos WAF Crawl (mới)

Đã crawl thêm các nguồn:
- thegioifirewall.com: XGS 3100 (38G FW, 2G TP) + XGS 3300 (40G FW, 2.77G TP)
- accessnetworks.com: XGS 3100 PDF (501 KB) → đã OCR
- sophos.com.vn: Secure Web Gateway
- sophos.com: Firewall Security Brief PDF → đã OCR

→ 4 file mới trong Sophos\: 08–11 (XGS 3100/3300 specs, WAF analysis, compliance table)

### 4.6 Ma trận tuân thủ kỹ thuật (Compliance Matrix)

Đã tạo: `Asset\HSMT\MA_TRAN_TUAN_THU_KY_THUAT.md`

| Nội dung | Kết quả |
|----------|---------|
| Đối chiếu 10 hệ thống với HSMT | ✅ Chi tiết từng thông số |
| Chấm điểm dự kiến | **~980–990 / 1000** |
| Bonus dự kiến đạt | **~280–290 / 300** |
| Khoảng trống phân phối | Đã xác định (F5, BigFix, Fortinet) |

### 4.7 Phân tích khoảng trống phân phối

Đã tạo: `Asset\HSMT\PHAN_TICH_KHOANG_TRONG_PHAN_PHOI.md`

Phân tích chi tiết 3 khoảng trống chính:
1. **A3. WAF**: F5 không qua NTS → **Sophos Web Server Protection** khả thi nhất (NTS có Sophos, đã xác nhận WAF)
2. **A6. Patch Mgmt**: BigFix không qua NTS → **SecPod SanerNow** là alternative qua NTS
3. **Fortinet phân phối**: NTS có logo Fortinet nhưng không phải dòng sản phẩm chính

### 4.8 Crawl bổ sung (đợt 2)

Đã crawl **15+ URLs** trong đợt 2:

| Nhóm | URL | Kết quả |
|------|-----|---------|
| **Sophos Official** | sophos.com XGS 1U + Comparison ⭐ | ✅ **Official specs confirmed**: XGS 3300 TP=10G, XGS 4300 TP=25.2G |
| **Sophos WAF** | enterpriseav.com XGS 4300 ⭐ | ✅ **"Web Server Protection = Web Application Firewall"** |
| **Sophos WAF** | firewalls.com (×2) | ❌ 403 Forbidden (blocked) |
| **Sophos Reseller** | cnttshop.vn XGS 3300 | ✅ Spec VN: TP 3G (base), FW 58G |
| **Sophos VN** | sophos.com.vn | ✅ XGS 2100-4500 overview |
| **XGS News** | e-channelnews.com | ✅ XGS gen2: 2× perf, 50% less power |
| **Arbor APS DDoS** | commoncriteriaportal.org (CC EAL2) | ✅ APS 2100 specs: up to 10G clean, 4×10GbE |
| **Arbor APS** | arbornetworks.com → NETSCOUT TMS | ✅ Redirected |
| **Arbor** | al-jammaz.com (PDF) | ❌ 404 |
| **Arbor** | ncsi.com DDoS Solutions | ✅ Solution brief |
| **NTS** | ntshanoi.com.vn (product menu) | ✅ Full portfolio verified |
| **NTS Barracuda WAF** | ntshanoi WAF page | ✅ **NTS có Barracuda WAF** |
| **NTS SecPod** | ntshanoi SecPod | ✅ **NTS có SecPod SanerNow** |

### 4.9 Phân tích WAF chuyên sâu

Đã tạo: `Asset\HSMT\Tài liệu tham chiếu\Sophos\12_WAF_PhanTich_ChuyenSau.md`

- Xác nhận "Web Server Protection = Web Application Firewall" (nguồn: enterpriseav.com/Sophos)
- Bảng so sánh F5 vs Barracuda vs Sophos WAF
- **Khuyến nghị**: Sophos XGS 3300 + Web Server Protection (qua NTS) — giá thấp, đủ chức năng

### 4.10 Khám phá quan trọng

| Phát hiện | Chi tiết |
|-----------|----------|
| **XGS 3300 TP = 10 Gbps** (official) | Vượt cả >6.5G min và >9G bonus! Reseller (cnttshop) ghi 3G là do Standard bundle |
| **Web Server Protection = WAF** | EnterpriseAV ghi rõ "Web Server Protection: Web Application Firewall" |
| **NTS không có F5** | Có Barracuda WAF và Sophos WAF thay thế |
| **NTS không có BigFix** | Có SecPod SanerNow patch management thay thế |
| **NTS có logo Fortinet** | Nhưng không phải sản phẩm chính — cần xác nhận thêm |

## 5. NHỮNG VIỆC CẦN LÀM TIẾP THEO (NEXT STEPS)

### 5.1 Đã hoàn thành

- [x] **Compile compliance matrix**: `MA_TRAN_TUAN_THU_KY_THUAT.md` — ~980–990/1000
- [x] **Crawl Sophos WAF**: EnterpriseAV xác nhận Web Server Protection = WAF
- [x] **Crawl Arbor APS**: CC EAL2 cert, up to 10G clean traffic
- [x] **Crawl NTS phân phối**: Xác nhận Barracuda WAF (+14 vendors)
- [x] **Phân tích WAF chuyên sâu**: 3 phương án so sánh

### 5.2 Cần quyết định

- [ ] **A3 WAF**: Chọn phương án — **Sophos WAF (qua NTS)** / Barracuda WAF / F5 (qua VTI)
- [ ] **A2+B1 Firewall**: **FortiGate 2200E** / Sophos XGS 3300/4300 (cần xác nhận NTS-Fortinet)
- [ ] **A6 Patch Mgmt**: HCL BigFix (trực tiếp HCL) / **SecPod SanerNow (qua NTS)**

### 5.3 Crawl thêm (nếu cần)

- [ ] Barracuda WAF datasheet (nếu chọn phương án Barracuda)
- [ ] SecPod SanerNow specs (nếu chọn thay thế BigFix)

## 6. CẤU TRÚC THƯ MỤC

```
Asset\HSMT\
├── RECOVERY_CHECKPOINT.md              ← file này
├── MA_TRAN_TUAN_THU_KY_THUAT.md        ← Compliance matrix (chấm điểm 1000)
├── PHAN_TICH_KHOANG_TRONG_PHAN_PHOI.md ← Gap analysis distribution
├── Tài liệu tham chiếu\
│   ├── Nam Trường Sơn\                 ← NTS product coverage
│   │   └── NTS_Product_Coverage_Summary.md
│   ├── PDF\                            ← 36 vendor PDF gốc
│   │   ├── FortiGate_*.pdf
│   │   ├── F5_*.pdf
│   │   ├── Sophos_*.pdf
│   │   ├── Barracuda_*.pdf
│   │   ├── Delinea_*.pdf
│   │   ├── NETSCOUT_*.pdf
│   │   ├── Kaspersky_*.pdf
│   │   ├── Splunk_Enterprise_Security.pdf
│   │   ├── IBM_QRadar_SIEM.pdf
│   │   ├── Securonix_Platform.pdf
│   │   └── Arbor_*.pdf / .md
    │   ├── PDF_OCR\                        ← 37 OCR output .md
    │   │   └── (tương ứng với PDF)
    │   ├── Sophos\                         ← 12 structured crawl files
    │   │       ├── 01-07: Sophos XGS specs crawl
    │   │       ├── 08-09: TheGioiFirewall specs (3100, 3300)
    │   │       ├── 10: WAF Web Server Protection Analysis
    │   │       ├── 11: WAF Compliance Table
    │   │       └── 12: WAF PhanTich ChuyenSau
    │   └── DDoS\                           ← Arbor APS crawl (4 files + 2 PDF)
    │       ├── Arbor_APS_2100_Series_Security_Target.md
    │       ├── Arbor_DDoS_Attack_Protection_Solutions.md
    │       ├── Arbor_Threat_Mitigation_System.md
    │       ├── Arbor_ST_Security_Target.pdf
    │       ├── Arbor_DDoS_Attack_Protection_Solutions.pdf
    │       └── URL_Crawl_Status_Report.md
└── Yêu cầu của khách\
    ├── Tổng hợp yêu cầu\               ← PDF gốc từ khách
    │   ├── 1. TBMT - Bảo mật UBCK.pdf
    │   ├── 2. E-HSMT Bảo mật UBCK.pdf
    │   ├── 2.1. Chuong III_Muc 3_Tieu_chuan_danh_gia_ve_ky_thuat.pdf
    │   ├── 2.2. Chuong III_Muc 4_Tieu_chuan_danh_gia_ve_tai_chinh.pdf
    │   ├── 3. Chuong V_danh_gia_ve_ky_thuat.pdf
    │   └── 3.1. Chuong V_PL_Chi_dan_ky_thuat.pdf
    └── Tổng hợp yêu cầu OCR\           ← OCR output
        ├── 1. TBMT - Bảo mật UBCK.md
        ├── 2. E-HSMT Bảo mật UBCK.md
        ├── 2.1. Chuong III_Muc 3_Tieu_chuan_danh_gia_ve_ky_thuat_max.md
        ├── 2.1. Chuong III_Muc 3_Tieu_chuan_danh_gia_ve_ky_thuat.md
        ├── 2.2. Chuong III_Muc 4_Tieu_chuan_danh_gia_ve_tai_chinh_max.md
        ├── 2.2. Chuong III_Muc 4_Tieu_chuan_danh_gia_ve_tai_chinh.md
        ├── 3. Chuong V_danh_gia_ve_ky_thuat.md
        └── 3.1. Chuong V_PL_Chi_dan_ky_thuat.md

Skill\OCR_PDF\scripts\ocr_processor.py   ← OCR engine
```

## 7. CÔNG CỤ OCR

```powershell
# Fast mode (native text — đã chạy xong cho tất cả)
python Skill\OCR_PDF\scripts\ocr_processor.py --input "file.pdf" --output "file.md" --mode fast

# Max mode + GPU (nếu cần OCR lại file scan)
python Skill\OCR_PDF\scripts\ocr_processor.py --input "file.pdf" --output "file.md" --mode max --gpu

# Batch all PDFs trong thư mục:
Get-ChildItem "PDF\*.pdf" | ForEach-Object {
    python Skill\OCR_PDF\scripts\ocr_processor.py --input $_.FullName --output "PDF_OCR\$($_.BaseName).md" --mode fast
}
```

## 8. CÁC VẤN ĐỀ ĐÃ BIẾT (KNOWN ISSUES)

**FortiGate_2000E_Series.pdf**: File gốc từ fortinet.com bị hỏng (web trả 404, download được file 0 trang). Đã thay thế bằng bản từ `imsecurity-global.com/wp-content/uploads/2021/12/FortiGate_2000E.pdf` (6 trang, 2.6 MB).

**OCR errors**: File `PDF_OCR\ocr_errors.json` ghi lại lỗi cho FortiGate_2000E_Series.pdf (exception khi load file cũ). Đã fix bằng cách tải lại file.

---

*Khi mất điện, mở file này trước, chạy `git status` và `git log --oneline -5` để biết trạng thái, sau đó tiếp tục từ mục 5 (Next Steps).*

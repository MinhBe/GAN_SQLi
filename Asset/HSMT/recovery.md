# RECOVERY.MD — Tổng quan dự án HSMT UBCKNN

> File này tóm tắt **toàn bộ** những gì đã làm, đang làm, cách làm, và kết quả.
> Mở file này đầu tiên khi cần khôi phục lại trạng thái làm việc.

---

## 1. TỔNG QUAN DỰ ÁN

| Mục | Thông tin |
|-----|-----------|
| **Bid Package** | BP2500701601 |
| **TBMT** | IB2600177138 |
| **KHLCNT** | PL2500277614 |
| **Dự án** | Thay thế một số giải pháp đảm bảo an toàn bảo mật hệ thống CNTT của UBCKNN |
| **Chủ đầu tư** | Ban Công nghệ và Chuyển đổi số - UBCKNN |
| **Hình thức** | Đấu thầu rộng rãi trong nước, hợp đồng trọn gói |
| **Thời gian** | 180 ngày |
| **Thang điểm** | 700 (tối thiểu) + 300 (vượt trội) = **1000 điểm** |
| **Số hệ thống** | 10 hạng mục bảo mật |
| **Nhà phân phối** | Nam Trường Sơn (NTS) — cần xác nhận phủ 10/10 hệ thống |

---

## 2. MỤC TIÊU

1. **Đối chiếu** thông số kỹ thuật của 10 hệ thống với yêu cầu HSMT
2. **Chấm điểm** (1000 thang) — đạt ≥980 để có lợi thế cạnh tranh
3. **Xác định khoảng trống** phân phối của NTS
4. **Đề xuất phương án** tối ưu cho từng hạng mục

---

## 3. CẤU TRÚC THƯ MỤC

```
Asset\HSMT\
│
├── recovery.md                              ← FILE NÀY — tổng quan toàn bộ
├── RECOVERY_CHECKPOINT.md                   ← Checkpoint chi tiết (cập nhật sau mỗi bước)
├── MA_TRAN_TUAN_THU_KY_THUAT.md             ← Ma trận tuân thủ kỹ thuật (~990/1000)
├── PHAN_TICH_KHOANG_TRONG_PHAN_PHOI.md      ← Phân tích khoảng trống phân phối NTS
│
├── Tài liệu tham chiếu\
│   ├── PDF\                                 ← 37+ file PDF gốc từ vendor
│   │   ├── Fortinet (8): FortiGate 1800F, 2000E, 2200E, FortiDDoS, FortiMail, FortiSIEM, FortiWeb, Product Matrix
│   │   ├── F5 (5): Advanced WAF, HW Platforms, System Platforms, Virtual Edition, Silverline WAF
│   │   ├── Sophos (4): XGS Series, XGS Data Sheet, Firewall Brochure, XGS 4300/4500 Operating Instructions
│   │   ├── Barracuda (2): Email Security Gateway, Email Protection
│   │   ├── Delinea (5): Secret Server, Privilege Manager, PBA, Corporate Brochure, Platform Upgrade
│   │   ├── NETSCOUT (3): Arbor Edge Defense, Arbor Sightline, Capabilities
│   │   ├── Kaspersky (4): Endpoint Security Business/Select/Enterprise, EDR Optimum
│   │   ├── SIEM (3): Splunk Enterprise Security, IBM QRadar SIEM, Securonix Platform
│   │   ├── Arbor APS (2): CC EAL4 Security Target, DDoS Protection Solutions
│   │   └── Arbor Xantaro Blog (1)
│   │
│   ├── PDF_OCR\                             ← 37 file OCR output (Markdown)
│   │   └── (tên tương ứng PDF, đuôi .md)
│   │
│   ├── Sophos\                              ← Crawl dữ liệu Sophos (12 file)
│   │   ├── 01_XGS_1U_Product_Page.md        — Thông số official từ sophos.com
│   │   ├── 02_XGS_3300_CNTTShop_Specs.md    — Reseller VN specs
│   │   ├── 03_XGS_4300_EnterpriseAV_Specs.md — EnterpriseAV (WAF confirmed)
│   │   ├── 04_XGS_4300_VietNet.md           — VietNet specs
│   │   ├── 05_XGS_4300_4500_Operating_Instructions.md
│   │   ├── 06_E_ChannelNews_XGS_2024.md     — News: 2x perf, 50% less power
│   │   ├── 07_Comparison_Recommendation.md  — So sánh XGS 3100/3300/4300
│   │   ├── 08_XGS_3100_TheGioiFirewall_Specs.md
│   │   ├── 09_XGS_3300_TheGioiFirewall_Specs.md
│   │   ├── 10_WAF_Web_Server_Protection_Analysis.md
│   │   ├── 11_HSMT_WAF_Compliance_Table.md
│   │   └── 12_WAF_PhanTich_ChuyenSau.md     — So sánh F5/Barracuda/Sophos WAF
│   │
│   ├── DDoS\                                ← Crawl dữ liệu Arbor APS (4 file + 2 PDF)
│   │   ├── Arbor_APS_2100_Series_Security_Target.md
│   │   ├── Arbor_DDoS_Attack_Protection_Solutions.md
│   │   ├── Arbor_Threat_Mitigation_System.md
│   │   ├── Arbor_ST_Security_Target.pdf
│   │   ├── Arbor_DDoS_Attack_Protection_Solutions.pdf
│   │   └── URL_Crawl_Status_Report.md
│   │
│   └── Nam Trường Sơn\
│       └── NTS_Product_Coverage_Summary.md   ← Danh mục sản phẩm NTS
│
└── Yêu cầu của khách\
    ├── Tổng hợp yêu cầu\                    ← PDF gốc từ HSMT (6 file)
    ├── Tổng hợp yêu cầu OCR\                ← OCR output (8 file .md)
    │   ├── 3. Chuong V_danh_gia_ve_ky_thuat.md          ← QUAN TRỌNG: specs 10 hệ thống
    │   ├── 2.1. Chuong III_Muc 3_Tieu_chuan_danh_gia_ve_ky_thuat_max.md  ← Bảng điểm bonus
    │   ├── 1. TBMT - Bảo mật UBCK.md                     ← Thông báo mời thầu
    │   └── ... (các file còn lại)
    └── ocr_errors.json

Skill\OCR_PDF\scripts\ocr_processor.py        ← Công cụ OCR (PyMuPDF + EasyOCR)
```

---

## 4. NHỮNG GÌ ĐÃ LÀM (CHI TIẾT TỪNG BƯỚC)

### Bước 1: Download Datasheet Vendor

**Thời gian**: Đầu phiên làm việc

Download **37 file PDF** từ website chính hãng:
- **Fortinet** (8 PDF): FortiGate 1800F, 2000E, 2200E, FortiDDoS, FortiMail, FortiSIEM, FortiWeb, Product Matrix
- **F5** (5 PDF): BIG-IP Advanced WAF, HW Platforms, System Platforms, Virtual Edition, Silverline WAF
- **Sophos** (4 PDF): XGS Series, XGS Data Sheet, Firewall Brochure, XGS 4300/4500 Operating Instructions
- **Barracuda** (2 PDF): Email Security Gateway, Email Protection
- **Delinea** (5 PDF): Secret Server, Privilege Manager, PBA, Corporate Brochure, Platform Upgrade
- **NETSCOUT** (3 PDF): Arbor Edge Defense, Arbor Sightline, Capabilities
- **Kaspersky** (4 PDF): Endpoint Security Business/Select/Enterprise, EDR Optimum
- **SIEM** (3 PDF): Splunk Enterprise Security, IBM QRadar SIEM, Securonix Platform
- **Arbor APS** (2 PDF): CC EAL4 Security Target, DDoS Protection Solutions

**Vấn đề gặp phải**:
- `FortiGate_2000E_Series.pdf`: File gốc fortinet.com trả 404 → thay thế từ imsecurity-global.com
- `F5_BIG-IP_Advanced_WAF.pdf`: Datasheet cũ (2018), không có số iSeries/rSeries

---

### Bước 2: OCR PDF → Markdown

**Cách làm**: Dùng `Skill\OCR_PDF\scripts\ocr_processor.py` ở **Fast mode** (PyMuPDF native text)

**Kết quả**: 37/37 file OCR thành công, không cần GPU (RTX 3050)

**Lệnh mẫu**:
```powershell
python Skill\OCR_PDF\scripts\ocr_processor.py --input "file.pdf" --output "file.md" --mode fast
```

---

### Bước 3: OCR Yêu cầu HSMT

OCR 6 file PDF yêu cầu kỹ thuật từ khách → 8 file Markdown.

**File quan trọng nhất**:
- `3. Chuong V_danh_gia_ve_ky_thuat.md` (661 dòng) — Thông số kỹ thuật tất cả 10 hệ thống
- `2.1. Chuong III_Muc 3_Tieu_chuan_danh_gia_ve_ky_thuat_max.md` — Bảng điểm bonus

---

### Bước 4: Xây dựng Ma trận Tuân thủ Kỹ thuật

**File**: `MA_TRAN_TUAN_THU_KY_THUAT.md` (433 dòng)

**Cách làm**:
1. Trích xuất yêu cầu tối thiểu HSMT từ file OCR
2. Đối chiếu với thông số từng vendor
3. Tính điểm: 700 base + bonus

**Kết quả dự kiến: ~980–990 / 1000 điểm**

| Hệ thống | Vendor | Base | Bonus | Ghi chú |
|----------|--------|:----:|:-----:|---------|
| A1. DDoS | NETSCOUT Arbor AED 8100 | ✅ | 30/30 | Throughput 40 Gbps, Flood 38.92 Mpps |
| A2. FW Core | FortiGate 2200E (×2 HA) | ✅ | 50/50 | FW 158 Gbps, TP 11 Gbps |
| A3. WAF | F5 / Sophos WAF | ✅ | 20-30/30 | Tùy phương án chọn |
| A4. SIEM | Splunk Enterprise Security | ✅ | 60/60 | Cần license EPS ≥4,000 |
| A5. PAM | Delinea Secret Server + PM | ✅ | 20/20 | Server vượt cấu hình |
| A6. Patch Mgmt | HCL BigFix (gia hạn) | ✅ | 0-10/10 | Tùy thương thảo ≥4 năm |
| A7. Mail Gateway | Barracuda Email SG | ✅ | 10/10 | RAM ≥64 GB |
| B1. FW Trụ sở | FortiGate 2200E / XGS 4300 | ✅ | 50/50 | Cả 2 đều vượt |
| B2. Web Content | FortiGate (tích hợp) | ✅ | 20/20 | CC EAL4+, SSL, DLP, AV, TI |
| B3. Anti-Malware | Kaspersky Enterprise + EDR | ✅ | 20/20 | ML, rollback, sandbox |
| **TỔNG** | | **700** | **~280-290** | **~980-990/1000** |

---

### Bước 5: Kiểm tra Phân phối NTS

**File**: `NTS_Product_Coverage_Summary.md`

**Cách làm**: Crawl website ntshanoi.com.vn (14 trang sản phẩm)

**Kết quả phát hiện**:

| Hệ thống | Vendor | NTS có? | Ghi chú |
|----------|--------|:-------:|---------|
| A1. DDoS | NETSCOUT | ✅ | Arbor AED |
| A2. FW Core | Fortinet | ⚠️ Logo có, không phải dòng chính | Cần xác nhận |
| A3. WAF | F5 / Barracuda / Sophos | ❌F5 / ✅Barracuda / ✅Sophos | Cần chọn |
| A4. SIEM | Splunk | ⚠️ | NTS có OpenText |
| A5. PAM | Delinea | ✅ | Secret Server |
| A6. Patch Mgmt | HCL BigFix | ❌ | SecPod thay thế |
| A7. Mail Gateway | Barracuda | ✅ | Email Security GW |
| B1. FW Trụ sở | FortiGate / Sophos | ✅ Sophos | |
| B2. Web Content | FortiGate / Sophos | ✅ Sophos | |
| B3. Anti-Malware | Kaspersky | ✅ | Exclusive VN |

---

### Bước 6: Crawl Sophos WAF (A3)

**Cách làm**: Crawl 10+ URL → ghi vào `Sophos\` (12 file)

**Nguồn đã crawl**:
| URL | Kết quả |
|-----|---------|
| sophos.com → XGS 1U Firewall Comparison | ✅ Official specs: XGS 3300 TP=10G, XGS 4300 TP=25.2G |
| enterpriseav.com → XGS 4300 | ✅ **"Web Server Protection = Web Application Firewall"** |
| cnttshop.vn → XGS 3300 | ✅ Spec VN: FW 58G, TP 3G (Standard bundle) |
| sophos.com.vn | ✅ XGS 2100-4500 overview |
| e-channelnews.com | ✅ XGS gen2: 2x perf, 50% less power |
| thegioifirewall.com (×2) | ✅ XGS 3100 + 3300 specs |
| firewalls.com (×2) | ❌ 403 Forbidden |

**Phát hiện quan trọng**: XGS 3300 TP chính thức là **10 Gbps** (vượt cả min 6.5G và bonus 9G). Reseller ghi 3 Gbps là do Standard bundle không có Xstream.

---

### Bước 7: Crawl Arbor APS DDoS (A1)

**Nguồn đã crawl**: 8 URLs

| URL | Kết quả |
|-----|---------|
| commoncriteriaportal.org | ✅ APS 2100: up to 10G clean, 4x10GbE, CC EAL2 |
| ncsi.com DDoS Solutions | ✅ Solution brief |
| arbornetworks.com → TMS | ✅ Redirect to NETSCOUT TMS |
| al-jammaz.com (PDF) | ❌ 404 |
| netscout.com mAPS flipbook | ❌ Login wall |

**File output**: `DDoS\` (4 .md + 2 .pdf)

---

### Bước 8: Crawl NTS Distribution Pages

Crawl 8 URLs từ ntshanoi.com.vn để xác nhận danh mục sản phẩm:
- ✅ NTS có 14+ dòng sản phẩm (Barracuda, Delinea, Kaspersky, NETSCOUT, Sophos, v.v.)
- ✅ NTS có **Barracuda WAF** (thay thế F5)
- ✅ NTS có **SecPod SanerNow** (thay thế HCL BigFix)
- ❌ NTS **không có** F5
- ❌ NTS **không có** HCL BigFix
- ⚠️ NTS có logo Fortinet nhưng Fortinet không trong menu sản phẩm chính

---

### Bước 9: Phân tích WAF chuyên sâu

**File**: `Sophos\12_WAF_PhanTich_ChuyenSau.md`

**3 phương án A3 WAF**:

| Tiêu chí | F5 BIG-IP Advanced WAF | Barracuda WAF | Sophos Web Server Protection |
|----------|:---------------------:|:-------------:|:----------------------------:|
| Thiết bị chuyên dụng | ✅ | ✅ | ❌ (module trên NGFW) |
| Qua NTS? | ❌ | ✅ | ✅ |
| Giá | Cao nhất | Trung bình | Thấp nhất (add-on) |
| Chức năng WAF | ✅ OWASP, Bot, API | ✅ | ✅ (reverse proxy) |

**Khuyến nghị**: Sophos XGS 3300 + Web Server Protection (qua NTS)

---

### Bước 10: Validate OCR Specs

Kiểm tra số liệu từ OCR datasheet so với ước tính trong ma trận:

| Thông số | OCR thực tế | Matrix cũ | Điều chỉnh |
|----------|:-----------:|:---------:|:----------:|
| FortiGate 2200E Concurrent Sessions | 24M | 50M+ (est.) | ✅ Đã sửa |
| FortiGate 2200E Firewall Throughput | 158/155/100 Gbps | 158/155/100 | ✅ Khớp |
| FortiGate 2200E Threat Protection | 11 Gbps | 11 Gbps | ✅ Khớp |
| AED Model | AED 8100 | AED 4000 (est.) | ✅ Đã sửa |
| AED Flood Prevention | 38.92 Mpps | 38.92 Mpps | ✅ Khớp |
| F5 WAF SSL TPS (HW PDF 2008) | 48k (8800) | 48k (est.) | ⚠️ PDF cũ, cần datasheet mới |
| Splunk EPS | Không có trong PDF | 2,500-10,000+ | ⚠️ Cần check license |
| Kaspersky EDR/rollback | ✅ Confirmed | ✅ | ✅ Khớp |

---

## 5. NHỮNG GÌ ĐANG LÀM / CÒN TỒN ĐỌNG

### Đã hoàn thành (10/10 hệ thống - compliance matrix)
- ✅ A1. DDoS (NETSCOUT AED 8100) — 700 base + 30 bonus = 730
- ✅ A2. FW Core (FortiGate 2200E) — 700 + 50 = 750
- ✅ A3. WAF (TBD: F5/Barracuda/Sophos) — 700 + 20-30 = 720-730
- ✅ A4. SIEM (Splunk Enterprise Security) — 700 + 60 = 760
- ✅ A5. PAM (Delinea Secret Server + PM) — 700 + 20 = 720
- ✅ A6. Patch Mgmt (HCL BigFix / SecPod) — 700 + 0-10 = 700-710
- ✅ A7. Mail Gateway (Barracuda Email SG) — 700 + 10 = 710
- ✅ B1. FW Trụ sở (FortiGate 2200E / XGS 4300) — 700 + 50 = 750
- ✅ B2. Web Content (FortiGate tích hợp) — 700 + 20 = 720
- ✅ B3. Anti-Malware (Kaspersky Enterprise) — 700 + 20 = 720

### Cần quyết định

| Vấn đề | Mức độ | Phương án |
|--------|:------:|-----------|
| **A3 WAF**: Chọn vendor nào? | 🔴 Cao | (1) Sophos WAF qua NTS, (2) Barracuda WAF qua NTS, (3) F5 qua VTI/VST |
| **A2+B1 Firewall**: FortiGate hay Sophos? | 🔴 Cao | FortiGate 2200E mạnh hơn nhưng cần xác nhận NTS-Fortinet |
| **A6 Patch Mgmt**: BigFix hay SecPod? | 🟡 Trung | BigFix (direct HCL) vs SecPod SanerNow (qua NTS) |
| **F5 Datasheet**: Bản hiện tại quá cũ | 🟡 Trung | Cần download iSeries/rSeries datasheet mới |

### Có thể crawl thêm
- Barracuda WAF datasheet (nếu chọn phương án này)
- SecPod SanerNow specs (nếu chọn thay thế BigFix)

---

## 6. CÁC PHÁT HIỆN QUAN TRỌNG

| Phát hiện | Tác động |
|-----------|----------|
| **XGS 3300 TP official = 10 Gbps** | Vượt bonus threshold 9G (+20 điểm). Reseller ghi 3G là Standard bundle |
| **"Web Server Protection = Web Application Firewall"** (EnterpriseAV) | Sophos WAF khả thi cho A3, giá rẻ hơn F5 nhiều |
| **NTS không có F5, có Barracuda WAF + Sophos WAF** | A3 có 2 phương án qua NTS |
| **NTS không có BigFix, có SecPod** | A6 có alternative |
| **NTS logo Fortinet nhưng không trong menu chính** | Cần xác nhận trước khi chốt FortiGate |
| **FortiGate 2000E PDF bị 404** | Đã thay thế từ imsecurity-global.com |
| **F5 Advanced WAF PDF (2018) thiếu số iSeries/rSeries** | Cần datasheet mới để có số chính xác |

---

## 7. CÁCH THỨC THỰC HIỆN (TOOLING)

### Công cụ OCR
```powershell
# Fast mode (native text)
python Skill\OCR_PDF\scripts\ocr_processor.py --input "file.pdf" --output "file.md" --mode fast

# Max mode + GPU (cho file scan)
python Skill\OCR_PDF\scripts\ocr_processor.py --input "file.pdf" --output "file.md" --mode max --gpu
```

### Crawl dữ liệu vendor
```powershell
# Ghi chép crawl bằng cách fetch URL → lưu markdown
webfetch "https://example.com/page"
```

### Kiểm tra git
```powershell
git status           # Xem file thay đổi
git diff             # Xem diff chi tiết
git log --oneline -5 # Xem 5 commit gần nhất
```

---

## 8. CÁC VẤN ĐỀ ĐÃ BIẾT

1. **FortiGate_2000E_Series.pdf**: File gốc fortinet.com bị 404, đã thay từ imsecurity-global.com
2. **F5_BIG-IP_Advanced_WAF.pdf**: Datasheet 2018, không có số iSeries/rSeries
3. **firewalls.com URLs**: 403 Forbidden (blocked US geolocation)
4. **router-switch.com URLs**: 403 Forbidden (tất cả region)
5. **NETSCOUT mAPS datasheet**: Login wall (flipbook)
6. **al-jammaz.com Arbor PDF**: 404
7. **eSecurityPlanet Arbor review**: 403

---

## 9. HƯỚNG DẪN KHÔI PHỤC SAU KHI MẤT KẾT NỐI

```powershell
# 1. Xem trạng thái git
git status

# 2. Xem lịch sử commit
git log --oneline -5

# 3. Mở file này để biết tổng quan
#    (dùng Read tool hoặc notepad)
notepad Asset\HSMT\recovery.md

# 4. Mở checkpoint để biết chi tiết bước cuối
code Asset\HSMT\RECOVERY_CHECKPOINT.md   # VSCode
# hoặc
notepad Asset\HSMT\RECOVERY_CHECKPOINT.md

# 5. Tiếp tục từ mục "Cần quyết định" (section 5)
```

---

## 10. TÓM TẮT NHANH (1 PHÚT)

> **Dự án**: Đối chiếu 10 hệ thống bảo mật với HSMT UBCKNN, chấm điểm 1000
> **Đã làm**: Download 37 PDF → OCR → Ma trận (~990/1000) → Crawl Sophos WAF → Crawl DDoS → Kiểm tra NTS → Phân tích WAF
> **Kết quả**: Ma trận hoàn chỉnh, 3 khoảng trống phân phối đã xác định
> **Cần quyết định**: A3 WAF (Sophos/Barracuda/F5), A2+B1 Firewall (FortiGate/Sophos), A6 Patch (BigFix/SecPod)
> **Điểm dự kiến**: 980-990/1000

---

*Tạo lúc: 2026-05-18*
*Cập nhật lần cuối: 2026-05-18*

# Slide Layout Guide — Tiếng Việt & PowerPoint Thực hành

## Font chữ

### Font khuyến nghị cho tiếng Việt

| Font | Phong cách | Dùng cho | Hỗ trợ Unicode |
|------|-----------|----------|---------------|
| **Calibri** | Sans-serif, hiện đại | Body text, bullet points | Tốt |
| **Calibri Light** | Nhẹ, thanh lịch | Tiêu đề slide | Tốt |
| **Roboto** | Geometric, thân thiện | Body + tiêu đề | Tốt (Google Fonts) |
| **Arial** | Sans-serif cơ bản | Fallback, an toàn | Tốt |
| **Times New Roman** | Serif, cổ điển | Học thuật, pháp lý | Tốt |
| **Verdana** | Rộng rãi, dễ đọc | Màn hình lớn | Tốt |

**Lưu ý**: Tránh font trang trí (decorative) vì khó đọc trên màn hình lớn.

### Font NOT khuyến khích

- Font có số lượng nét chữ phức tạp
- Font cỡ nhỏ (< 18pt) cho tiêu đề
- Font chỉ hỗ trợ TCVN3/VNI (không dùng nếu nội dung là Unicode)

---

## Kích thước chữ chuẩn

| Vị trí | Kích thước | Font |
|--------|-----------|------|
| Tiêu đề slide | 32–44 pt | Calibri Light Bold |
| Phụ đề | 22–26 pt | Calibri |
| Body / bullet | 20–24 pt | Calibri |
| Footer | 10–12 pt | Calibri |
| Ghi chú | 14–16 pt | Calibri |

**Quy tắc**: Kích thước font giảm dần theo mức độ quan trọng. Body text không nhỏ hơn 18pt.

---

## Màu sắc

### Bảng màu chuẩn (Corporate)

| Màu | Hex | RGB | Dùng cho |
|-----|-----|-----|----------|
| Navy | `#1F3864` | 31,56,100 | Header bar, tiêu đề chính |
| Trắng | `#FFFFFF` | 255,255,255 | Nền, chữ trên nền tối |
| Đen | `#000000` | 0,0,0 | Chữ body |
| Xám đậm | `#444444` | 68,68,68 | Phụ đề, chữ phụ |
| Xám nhạt | `#F2F2F2` | 242,242,242 | Nền phụ (section dividers) |
| Xanh dương sáng | `#2E74B5` | 46,116,181 | Bullet icons, highlights |

### Tương phản

- **Tốt**: Chữ đen `#000000` trên nền trắng `#FFFFFF`
- **Tốt**: Chữ trắng `#FFFFFF` trên nền navy `#1F3864`
- **Tránh**: Chữ xám `#808080` trên nền trắng (khó đọc)
- **Tránh**: Màu nền quá sáng hoặc quá tối làm mất chữ

---

## Cấu trúc slide

### Header Bar

- Chiều cao: 1.2 cm (từ đỉnh slide)
- Màu: Navy `#1F3864`
- Chạy full width

### Margin chuẩn

- Lề trái/phải: 1.27 cm (0.5 inch)
- Lề trên (dưới header): 2.5 cm
- Lề dưới: 1.5 cm

### Số lượng bullet points

- **Tối đa 6 bullet points** cho mỗi slide
- Tốt nhất: **3-4 bullet points**
- Nếu cần nhiều hơn → chia thành nhiều slide

---

## Layout chuẩn theo loại slide

### Title Slide

```
┌─────────────────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ (header navy)     │
│                                             │
│                                             │
│            Tiêu đề chính (44pt)            │
│            (Calibri Light Bold)             │
│                                             │
│            Phụ đề (24pt)                    │
│                                             │
│                                             │
│                                             │
│                                             │
└─────────────────────────────────────────────┘
```

### Bullet Slide

```
┌─────────────────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ (header navy)     │
│                                             │
│  Tiêu đề slide (32pt, navy)                 │
│                                             │
│  • Bullet point 1 (22pt)                    │
│  • Bullet point 2                           │
│  • Bullet point 3                           │
│                                             │
│                                             │
│                                             │
└─────────────────────────────────────────────┘
```

### Two-Column Slide

```
┌─────────────────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ (header navy)     │
│                                             │
│  Tiêu đề slide (32pt)                       │
│                                             │
│  Nội dung     │ Nội dung                     │
│  cột trái    │ cột phải                      │
│  (20pt)      │ (20pt)                        │
│              │                               │
│              │                               │
│              │                               │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Checklist trước khi xuất file

- [ ] Font hiển thị đúng tiếng Việt (test chữ có dấu: ặ, ư, đ, ơ,...)
- [ ] Màu nền và màu chữ có độ tương phản đủ
- [ ] Số lượng bullet points ≤ 6 mỗi slide
- [ ] Tiêu đề rõ ràng, không quá dài (tối đa 1 dòng)
- [ ] Bố cục đồng nhất across all slides
- [ ] File .pptx mở được trên PowerPoint (không chỉ Google Slides)
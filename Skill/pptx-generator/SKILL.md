---
name: pptx-generator
description: |
  Tạo file PowerPoint (.pptx) từ nội dung text hoặc cấu hình slide được mô tả.
  Trigger khi: user yêu cầu tạo/generate/make presentation, slide deck, PowerPoint, file .pptx,
  hoặc muốn "ghép slide", "làm bài thuyết trình", "xuất ra PowerPoint".
  Cũng trigger khi user cung cấp nội dung và hỏi "làm slide được không".
  Không trigger khi: user chỉ muốn đọc/examine file pptx có sẵn, hoặc muốn xuất ra PDF/Word.
---

# pptx-generator — Skill Guide

## Role & Prime Directive

Tạo file PowerPoint (.pptx) chuyên nghiệp bằng python-pptx. Luôn dùng script
`scripts/create_pptx.py` — không tự viết code python-pptx trực tiếp trong conversation.

## Workflow

### Step 1: Parse user request

Từ prompt của user, trích xuất:

- **Output path**: Đường dẫn file .pptx đầu ra (user chỉ định hoặc hỏi lại)
- **Slides**: Mảng các slide config, mỗi slide gồm:
  - `type`: `"title"` | `"bullet"` | `"two_col"` | `"blank"`
  - `title`: Tiêu đề slide
  - `bullets`: Danh sách bullet points (cho type `bullet` / `two_col`)
  - `col_left` / `col_right`: Nội dung 2 cột (cho `two_col`)
  - `subtitle`: Phụ đề (cho `title`)
  - `bg_color`: Màu nền hex (tùy chọn)
  - `font_color`: Màu chữ hex (tùy chọn)

### Step 2: Build slides_config

Ghép nối nội dung user cung cấp thành cấu hình slides cho script.

### Step 3: Run script

```bash
python "C:\Projects\GAN_SQLi\Skill\pptx-generator\scripts\create_pptx.py" \
  --output "C:\path\to\output.pptx" \
  --slides '[{"type":"title","title":"Tiêu đề","subtitle":"Phụ đề"},{"type":"bullet","title":"Tiêu đề","bullets":["Point 1","Point 2"]}]'
```

### Step 4: Verify

- Kiểm tra file .pptx được tạo tại output path
- Báo user đường dẫn đầy đủ

## Slide Type Reference

### `title` — Slide tiêu đề
```json
{"type": "title", "title": "Tiêu đề chính", "subtitle": "Phụ đề / mô tả ngắn"}
```

### `bullet` — Slide danh sách
```json
{"type": "bullet", "title": "Nội dung chính", "bullets": ["Điểm 1", "Điểm 2", "Điểm 3"]}
```

### `two_col` — Slide 2 cột
```json
{"type": "two_col", "title": "Tiêu đề", "col_left": "Nội dung cột trái", "col_right": "Nội dung cột phải"}
```

### `blank` — Slide trắng
```json
{"type": "blank", "title": "Nội dung tùy ý"}
```

## Slide Layout Guide

Đọc `references/layout_guide.md` để biết font chữ, màu sắc, kích thước chuẩn.

**Tóm tắt nhanh cho slide tiếng Việt:**

- Font tiêu đề: **Calibri Light** hoặc **Roboto** (nếu có), size 44pt
- Font body: **Calibri**, size 24pt, tối đa 6 bullet points mỗi slide
- Màu nền chuẩn: trắng `FFFFFF` hoặc xanh navy `1F3864`
- Màu chữ: đen `000000` hoặc trắng `FFFFFF` (trên nền tối)
- Logo/brand: góc phải dưới
- Header bar: xanh navy ở đỉnh slide, cao 1.5cm

## Script API

### Command Line

```bash
python create_pptx.py --output "path/to/output.pptx" --slides '[{"type":"title","title":"Test"}]'
```

### JSON slides format

```json
[
  {
    "type": "title",
    "title": "OpenCode",
    "subtitle": "AI-powered coding assistant"
  },
  {
    "type": "bullet",
    "title": "Tính năng chính",
    "bullets": [
      "Multi-file editing",
      "Terminal integration",
      "Code search & navigation"
    ]
  }
]
```

### Python API

```python
from create_pptx import create_presentation

slides = [
    {"type": "title", "title": "OpenCode", "subtitle": "AI-powered"},
    {"type": "bullet", "title": "Features", "bullets": ["Fast", "Accurate"]},
]
create_presentation(slides, "output.pptx")
```

## Edge Cases

- **Không có output path** → hỏi user nơi lưu file
- **Slide quá dài** → tự động giảm font size hoặc chia thành 2 slide
- **Tiếng Việt bị lỗi font** → dùng font fallback: Calibri (hỗ trợ Unicode tốt)
- **File đã tồn tại** → ghi đè (python-pptx không hỏi)
- **JSON parse lỗi** → thử parse với `ast.literal_eval` như fallback

## Design Principles

Thiết kế slide theo phong cách **corporate-clean**:

1. **Đồng nhất**: Font, màu sắc, spacing giữ nguyên across all slides
2. **Tối giản**: Mỗi slide tối đa 1 ý chính, 4-6 bullet points
3. **Tương phản**: Chữ trắng trên nền tối, chữ đen trên nền sáng
4. **Không clutter**: Không nhồi nhét quá nhiều nội dung, để khoảng trắng
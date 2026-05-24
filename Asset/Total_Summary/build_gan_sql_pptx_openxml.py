from __future__ import annotations

import html
import zipfile
from pathlib import Path


OUT = Path(__file__).resolve().parent / "GAN_SQLi_GAN_Central_Presentation_230526.pptx"

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"

SLIDE_W = 12192000
SLIDE_H = 6858000


def emu(x: float) -> int:
    return int(x * 914400)


def esc(text: str) -> str:
    return html.escape(text, quote=True)


COLORS = {
    "navy": "153A5B",
    "blue": "2B6CB0",
    "cyan": "1A9BAA",
    "green": "2F855A",
    "red": "C53030",
    "orange": "C05621",
    "purple": "6B46C1",
    "gray": "4A5568",
    "light": "EDF2F7",
    "lighter": "F7FAFC",
    "white": "FFFFFF",
    "black": "111827",
}


def solid_fill(color: str) -> str:
    return f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'


def text_runs(text: str, size: int = 1800, color: str = COLORS["black"], bold: bool = False) -> str:
    lines = text.split("\n")
    out = []
    for idx, line in enumerate(lines):
        b = ' b="1"' if bold else ""
        out.append(
            f'<a:p><a:r><a:rPr lang="en-US" sz="{size}"{b}>{solid_fill(color)}'
            f'<a:latin typeface="Calibri"/></a:rPr><a:t>{esc(line)}</a:t></a:r>'
            '<a:endParaRPr lang="en-US"/></a:p>'
        )
    return "".join(out)


def shape_xml(
    shape_id: int,
    x: int,
    y: int,
    w: int,
    h: int,
    text: str = "",
    fill: str = "FFFFFF",
    line: str = "153A5B",
    radius: bool = False,
    font_size: int = 1700,
    font_color: str = COLORS["black"],
    bold: bool = False,
    align: str = "ctr",
) -> str:
    geom = "roundRect" if radius else "rect"
    bold_attr = ' b="1"' if bold else ""
    tx = ""
    if text:
        tx = (
            '<p:txBody><a:bodyPr wrap="square" lIns="91440" tIns="68580" rIns="91440" bIns="68580"/>'
            '<a:lstStyle/>'
            f'<a:p><a:pPr algn="{align}"/>'
            f'<a:r><a:rPr lang="en-US" sz="{font_size}"{bold_attr}>{solid_fill(font_color)}'
            '<a:latin typeface="Calibri"/></a:rPr>'
            f'<a:t>{esc(text)}</a:t></a:r><a:endParaRPr lang="en-US"/></a:p></p:txBody>'
        )
    return f"""
    <p:sp>
      <p:nvSpPr><p:cNvPr id="{shape_id}" name="Shape {shape_id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>
        <a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>
        {solid_fill(fill)}
        <a:ln w="19050"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>
      </p:spPr>
      {tx}
    </p:sp>
    """


def textbox_xml(
    shape_id: int,
    x: int,
    y: int,
    w: int,
    h: int,
    text: str,
    font_size: int = 1800,
    font_color: str = COLORS["black"],
    bold: bool = False,
    align: str = "l",
) -> str:
    bold_attr = ' b="1"' if bold else ""
    return f"""
    <p:sp>
      <p:nvSpPr><p:cNvPr id="{shape_id}" name="Text {shape_id}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
      <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>
      <p:txBody><a:bodyPr wrap="square"/><a:lstStyle/>
      <a:p><a:pPr algn="{align}"/><a:r><a:rPr lang="en-US" sz="{font_size}"{bold_attr}>{solid_fill(font_color)}<a:latin typeface="Calibri"/></a:rPr><a:t>{esc(text)}</a:t></a:r><a:endParaRPr lang="en-US"/></a:p>
      </p:txBody>
    </p:sp>
    """


def line_xml(shape_id: int, x1: int, y1: int, x2: int, y2: int, color: str = "153A5B") -> str:
    x = min(x1, x2)
    y = min(y1, y2)
    w = abs(x2 - x1) or 1
    h = abs(y2 - y1) or 1
    flip_h = ' flipH="1"' if x2 < x1 else ""
    flip_v = ' flipV="1"' if y2 < y1 else ""
    return f"""
    <p:cxnSp>
      <p:nvCxnSpPr><p:cNvPr id="{shape_id}" name="Arrow {shape_id}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>
      <p:spPr>
        <a:xfrm{flip_h}{flip_v}><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>
        <a:prstGeom prst="straightConnector1"><a:avLst/></a:prstGeom>
        <a:ln w="28575"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:tailEnd type="none"/><a:headEnd type="triangle"/></a:ln>
      </p:spPr>
    </p:cxnSp>
    """


def header(title: str, subtitle: str | None = None) -> list[str]:
    parts = [
        shape_xml(10, 0, 0, SLIDE_W, emu(0.58), "", COLORS["navy"], COLORS["navy"]),
        textbox_xml(11, emu(0.35), emu(0.12), emu(12.2), emu(0.35), title, 1850, COLORS["white"], True),
    ]
    if subtitle:
        parts.append(textbox_xml(12, emu(0.55), emu(0.78), emu(12.2), emu(0.35), subtitle, 1250, COLORS["gray"]))
    return parts


def bullets(shape_id: int, x: float, y: float, w: float, h: float, lines: list[str], size: int = 1500) -> str:
    text = "\n".join([f"- {line}" for line in lines])
    return textbox_xml(shape_id, emu(x), emu(y), emu(w), emu(h), text, size, COLORS["black"], False, "l")


def table(slide_id: int, x: float, y: float, rows: list[list[str]], col_w: list[float], row_h: float = 0.45) -> list[str]:
    parts = []
    sid = slide_id
    for r, row in enumerate(rows):
        xx = x
        for c, cell in enumerate(row):
            fill = COLORS["navy"] if r == 0 else (COLORS["lighter"] if r % 2 == 0 else COLORS["white"])
            color = COLORS["white"] if r == 0 else COLORS["black"]
            parts.append(
                shape_xml(
                    sid,
                    emu(xx),
                    emu(y + r * row_h),
                    emu(col_w[c]),
                    emu(row_h),
                    cell,
                    fill,
                    "CBD5E0",
                    False,
                    1050 if r else 1100,
                    color,
                    r == 0,
                )
            )
            sid += 1
            xx += col_w[c]
    return parts


def slide_xml(parts: list[str]) -> str:
    body = "\n".join(parts)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}">
  <p:cSld>
    <p:bg><p:bgPr>{solid_fill(COLORS["white"])}<a:effectLst/></p:bgPr></p:bg>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      {body}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""


def build_slides() -> list[str]:
    slides: list[list[str]] = []

    slides.append([
        shape_xml(2, 0, 0, SLIDE_W, SLIDE_H, "", COLORS["navy"], COLORS["navy"]),
        textbox_xml(3, emu(0.7), emu(1.25), emu(12), emu(1.2), "Vai tro cua GAN trong SQL Injection", 3600, COLORS["white"], True, "ctr"),
        textbox_xml(4, emu(1.2), emu(2.65), emu(11), emu(0.8), "Tu generator fail gate den augmentation-engine va real-space policy", 1900, "DDEBFF", False, "ctr"),
        shape_xml(5, emu(1.0), emu(4.25), emu(3.2), emu(0.9), "Da lam\nPhase 1-8", COLORS["blue"], COLORS["white"], True, 1500, COLORS["white"], True),
        shape_xml(6, emu(5.0), emu(4.25), emu(3.2), emu(0.9), "Ket qua\nGAN generator fail", COLORS["orange"], COLORS["white"], True, 1500, COLORS["white"], True),
        shape_xml(7, emu(9.0), emu(4.25), emu(3.2), emu(0.9), "Dinh huong\nGAN doi vai", COLORS["green"], COLORS["white"], True, 1500, COLORS["white"], True),
        line_xml(8, emu(4.2), emu(4.7), emu(5.0), emu(4.7), COLORS["white"]),
        line_xml(9, emu(8.2), emu(4.7), emu(9.0), emu(4.7), COLORS["white"]),
    ])

    slides.append(header("Thay yeu cau lam ro nhung gi?", "Tom tat tu buoi trao doi 13/05/2026") + [
        shape_xml(20, emu(0.7), emu(1.35), emu(2.7), emu(1.0), "Dataset\nnguon + schema", COLORS["light"], COLORS["blue"], True, 1350, COLORS["black"], True),
        shape_xml(21, emu(3.8), emu(1.35), emu(2.7), emu(1.0), "Nhan\ntechnique + DB", COLORS["light"], COLORS["blue"], True, 1350, COLORS["black"], True),
        shape_xml(22, emu(6.9), emu(1.35), emu(2.7), emu(1.0), "Mo hinh\nG-D-WAF", COLORS["light"], COLORS["blue"], True, 1350, COLORS["black"], True),
        shape_xml(23, emu(10.0), emu(1.35), emu(2.7), emu(1.0), "Reward\ndung o dau?", COLORS["light"], COLORS["blue"], True, 1350, COLORS["black"], True),
        shape_xml(24, emu(0.7), emu(3.1), emu(2.7), emu(1.0), "Collapse\nSeqGAN cu", COLORS["light"], COLORS["orange"], True, 1350, COLORS["black"], True),
        shape_xml(25, emu(3.8), emu(3.1), emu(2.7), emu(1.0), "So sanh\nbaseline", COLORS["light"], COLORS["orange"], True, 1350, COLORS["black"], True),
        shape_xml(26, emu(6.9), emu(3.1), emu(2.7), emu(1.0), "Firewall/WAF\nlabel/reward/eval", COLORS["light"], COLORS["orange"], True, 1350, COLORS["black"], True),
        shape_xml(27, emu(10.0), emu(3.1), emu(2.7), emu(1.0), "Tien do\nxong/fail/tiep", COLORS["light"], COLORS["orange"], True, 1350, COLORS["black"], True),
        textbox_xml(28, emu(1.0), emu(5.25), emu(11.4), emu(0.8), "Muc tieu slide deck: tra loi ro moi quan he giua du lieu - GAN - detector/WAF - reward - huong tiep theo.", 1550, COLORS["gray"], True, "ctr"),
    ])

    slides.append(header("Dataset va label pipeline", "Tu nhieu nguon ve mot schema co audit") + [
        shape_xml(30, emu(0.5), emu(1.7), emu(2.3), emu(0.85), "Public SQLi\nKaggle / payload lists", COLORS["lighter"], COLORS["blue"], True, 1200, COLORS["black"], True),
        shape_xml(31, emu(0.5), emu(3.0), emu(2.3), emu(0.85), "Benign / user input\nnegative evidence", COLORS["lighter"], COLORS["blue"], True, 1200, COLORS["black"], True),
        shape_xml(32, emu(3.7), emu(2.25), emu(2.3), emu(1.0), "Normalize + merge\nsource tracking", COLORS["light"], COLORS["cyan"], True, 1300, COLORS["black"], True),
        shape_xml(33, emu(6.9), emu(1.25), emu(2.5), emu(0.75), "payload_working", COLORS["white"], COLORS["green"], True, 1100),
        shape_xml(34, emu(6.9), emu(2.15), emu(2.5), emu(0.75), "payload_delex_v5", COLORS["white"], COLORS["green"], True, 1100),
        shape_xml(35, emu(6.9), emu(3.05), emu(2.5), emu(0.75), "technique_primary", COLORS["white"], COLORS["green"], True, 1100),
        shape_xml(36, emu(6.9), emu(3.95), emu(2.5), emu(0.75), "db_family + confidence", COLORS["white"], COLORS["green"], True, 1100),
        shape_xml(37, emu(10.2), emu(2.45), emu(2.3), emu(1.0), "Gold / Silver\nreview + audit", COLORS["light"], COLORS["purple"], True, 1250, COLORS["black"], True),
        line_xml(38, emu(2.8), emu(2.1), emu(3.7), emu(2.7), COLORS["blue"]),
        line_xml(39, emu(2.8), emu(3.4), emu(3.7), emu(2.8), COLORS["blue"]),
        line_xml(40, emu(6.0), emu(2.75), emu(6.9), emu(2.75), COLORS["cyan"]),
        line_xml(41, emu(9.4), emu(2.75), emu(10.2), emu(2.9), COLORS["green"]),
        textbox_xml(42, emu(0.75), emu(5.55), emu(12), emu(0.6), "Diem sua so voi ban cu: label/confidence khong con la cam tinh; co reason, audit va split chong leakage.", 1350, COLORS["gray"], True, "ctr"),
    ])

    slides.append(header("Phat hien quan trong: template leakage", "Ly do phai danh gia tren cluster split moi") + [
        shape_xml(50, emu(0.7), emu(1.45), emu(3.4), emu(1.0), "1.6M rows", COLORS["blue"], COLORS["blue"], True, 1800, COLORS["white"], True),
        shape_xml(51, emu(4.95), emu(1.45), emu(3.4), emu(1.0), "~77,804 templates", COLORS["orange"], COLORS["orange"], True, 1800, COLORS["white"], True),
        shape_xml(52, emu(9.2), emu(1.45), emu(3.4), emu(1.0), "Random split\nleaks templates", COLORS["red"], COLORS["red"], True, 1600, COLORS["white"], True),
        line_xml(53, emu(4.1), emu(1.95), emu(4.95), emu(1.95), COLORS["gray"]),
        line_xml(54, emu(8.35), emu(1.95), emu(9.2), emu(1.95), COLORS["gray"]),
        shape_xml(55, emu(1.2), emu(3.2), emu(3.0), emu(0.85), "train\n1,561,364", COLORS["lighter"], COLORS["green"], True, 1300, COLORS["black"], True),
        shape_xml(56, emu(5.15), emu(3.2), emu(3.0), emu(0.85), "dev\n150,694", COLORS["lighter"], COLORS["green"], True, 1300, COLORS["black"], True),
        shape_xml(57, emu(9.1), emu(3.2), emu(3.0), emu(0.85), "test\n272,315", COLORS["lighter"], COLORS["green"], True, 1300, COLORS["black"], True),
        textbox_xml(58, emu(1.0), emu(4.85), emu(11.4), emu(0.7), "Cluster split theo delex-template: train/dev/test template overlap = 0", 1700, COLORS["green"], True, "ctr"),
    ])

    slides.append(header("Vi sao full-sequence GAN fail?", "Ket qua am co co che, khong phai chi do tuning") + [
        shape_xml(60, emu(0.7), emu(1.45), emu(2.6), emu(0.9), "SeqGAN / REINFORCE", COLORS["lighter"], COLORS["red"], True, 1250, COLORS["black"], True),
        shape_xml(61, emu(4.0), emu(1.45), emu(2.6), emu(0.9), "D hoc qua nhanh", COLORS["lighter"], COLORS["red"], True, 1250, COLORS["black"], True),
        shape_xml(62, emu(7.3), emu(1.45), emu(2.6), emu(0.9), "G mat tin hieu", COLORS["lighter"], COLORS["red"], True, 1250, COLORS["black"], True),
        shape_xml(63, emu(10.3), emu(1.45), emu(2.2), emu(0.9), "Collapse", COLORS["red"], COLORS["red"], True, 1350, COLORS["white"], True),
        line_xml(64, emu(3.3), emu(1.9), emu(4.0), emu(1.9), COLORS["red"]),
        line_xml(65, emu(6.6), emu(1.9), emu(7.3), emu(1.9), COLORS["red"]),
        line_xml(66, emu(9.9), emu(1.9), emu(10.3), emu(1.9), COLORS["red"]),
        bullets(67, 1.0, 3.0, 11.3, 2.2, [
            "Discrete token generation lam gradient cho Generator yeu.",
            "WGAN-GP / SpectralNorm / TTUR / Gumbel khong giai quyet tri de.",
            "Bai hoc: khong tiep tuc tune full-sequence GAN; doi don vi sinh sang slot/action."
        ], 1450),
    ])

    slides.append(header("Phase 8: H5' paired masked payload-surgery GAN", "Thu nghiem doi don vi sinh tu full payload sang slot/local action") + [
        shape_xml(70, emu(0.7), emu(2.0), emu(2.2), emu(0.85), "Delex frame", COLORS["lighter"], COLORS["blue"], True, 1300, COLORS["black"], True),
        shape_xml(71, emu(3.5), emu(2.0), emu(2.2), emu(0.85), "Mask slot /\nlocal token", COLORS["lighter"], COLORS["cyan"], True, 1250, COLORS["black"], True),
        shape_xml(72, emu(6.3), emu(2.0), emu(2.2), emu(0.85), "Generator\nH5'", COLORS["blue"], COLORS["blue"], True, 1350, COLORS["white"], True),
        shape_xml(73, emu(9.1), emu(1.25), emu(2.6), emu(0.8), "Paired D\nreal vs fake", COLORS["purple"], COLORS["purple"], True, 1250, COLORS["white"], True),
        shape_xml(74, emu(9.1), emu(3.0), emu(2.6), emu(0.8), "Evaluator\nvalid/novel/evasion", COLORS["green"], COLORS["green"], True, 1150, COLORS["white"], True),
        line_xml(75, emu(2.9), emu(2.43), emu(3.5), emu(2.43), COLORS["blue"]),
        line_xml(76, emu(5.7), emu(2.43), emu(6.3), emu(2.43), COLORS["cyan"]),
        line_xml(77, emu(8.5), emu(2.43), emu(9.1), emu(1.65), COLORS["purple"]),
        line_xml(78, emu(8.5), emu(2.43), emu(9.1), emu(3.4), COLORS["green"]),
        textbox_xml(79, emu(0.95), emu(5.25), emu(11.5), emu(0.75), "Muc tieu: giam collapse bang cach khong de GAN sinh toan bo chuoi SQLi.", 1450, COLORS["gray"], True, "ctr"),
    ])

    slides.append(header("Evaluator contract: tach truc, tranh tu lua", "D-score va keyword-only khong duoc dung lam ground truth") + [
        shape_xml(80, emu(0.8), emu(1.55), emu(2.6), emu(1.05), "Validity\nbalanced / parse", COLORS["lighter"], COLORS["green"], True, 1300, COLORS["black"], True),
        shape_xml(81, emu(3.9), emu(1.55), emu(2.6), emu(1.05), "Novelty\ntrain dup / batch dup", COLORS["lighter"], COLORS["green"], True, 1250, COLORS["black"], True),
        shape_xml(82, emu(7.0), emu(1.55), emu(2.6), emu(1.05), "Conditioning\nhint debug only", COLORS["lighter"], COLORS["orange"], True, 1250, COLORS["black"], True),
        shape_xml(83, emu(10.1), emu(1.55), emu(2.3), emu(1.05), "Evasion\nonly with oracle", COLORS["lighter"], COLORS["red"], True, 1250, COLORS["black"], True),
        textbox_xml(84, emu(0.9), emu(3.55), emu(11.5), emu(1.1), "Quy tac: mau chi dung cho main claim khi validity, novelty va evasion deu do duoc. Technique hint chi la debug.", 1550, COLORS["black"], True, "ctr"),
        textbox_xml(85, emu(1.0), emu(5.2), emu(11.2), emu(0.5), "Dung evaluator nay de ket luan am mot cach cong bang.", 1400, COLORS["gray"], False, "ctr"),
    ])

    slides.append(header("Ket qua: H5' generator fail pre-registered gate", "Classifier-oracle bypass: adversarial contribution gan bang 0") + table(90, 1.4, 1.45, [
        ["Method", "Role", "Bypass"],
        ["Anchor-only", "No GAN / supervised", "0.0050"],
        ["Mutation-engine", "No learning", "0.0000"],
        ["H5' max-local", "GAN generator", "0.0000"],
        ["H5' max-aggressive", "GAN generator", "0.0050"],
        ["Oracle-aware search", "Post-processing", "0.0050"],
    ], [4.2, 4.0, 2.0], 0.55) + [
        shape_xml(110, emu(1.8), emu(5.35), emu(9.6), emu(0.65), "Ket luan: GAN-as-payload-generator khong vuot anchor-only/mutation-engine.", COLORS["red"], COLORS["red"], True, 1450, COLORS["white"], True),
    ])

    slides.append(header("Tai sao delex-space khong do duoc evasion that?", "Classifier oracle qua de tach SQLi/benign trong representation da chuan hoa") + [
        shape_xml(120, emu(0.8), emu(1.45), emu(3.4), emu(1.0), "Delex oracle\nAUC ~ 1.0", COLORS["red"], COLORS["red"], True, 1600, COLORS["white"], True),
        shape_xml(121, emu(5.0), emu(1.45), emu(3.4), emu(1.0), "Surface evasion\nbi xoa/normalize", COLORS["orange"], COLORS["orange"], True, 1450, COLORS["white"], True),
        shape_xml(122, emu(9.1), emu(1.45), emu(3.4), emu(1.0), "Can real-space\nrehydrate + WAF", COLORS["green"], COLORS["green"], True, 1450, COLORS["white"], True),
        line_xml(123, emu(4.2), emu(1.95), emu(5.0), emu(1.95), COLORS["gray"]),
        line_xml(124, emu(8.4), emu(1.95), emu(9.1), emu(1.95), COLORS["gray"]),
        bullets(125, 1.2, 3.25, 10.8, 1.9, [
            "Delex tot cho generation/conditioning, nhung xoa casing, comment, encoding, literal.",
            "Evasion la hien tuong be mat; phai do sau rehydrate tren WAF/detector real-space.",
            "AUC=1.0 la ly do doi khong gian do, khong phai ly do bo GAN."
        ], 1400),
    ])

    slides.append(header("Pivot: GAN van trung tam, nhung doi vai", "Khong tiep tuc cuu vai generator da fail gate") + [
        shape_xml(130, emu(0.7), emu(1.55), emu(3.3), emu(1.45), "GAN-as-generator\n\nDa test\nFail gate\nHa xuong ablation", COLORS["lighter"], COLORS["red"], True, 1250, COLORS["black"], True),
        shape_xml(131, emu(5.0), emu(1.55), emu(3.3), emu(1.45), "GAN-as-augmentation\n\nPhong thu\nRobust detector\nHuong chinh", COLORS["lighter"], COLORS["green"], True, 1250, COLORS["black"], True),
        shape_xml(132, emu(9.0), emu(1.55), emu(3.3), emu(1.45), "GAN-as-policy\n\nReal-space\nWAF reward\nVertical slice", COLORS["lighter"], COLORS["blue"], True, 1250, COLORS["black"], True),
        textbox_xml(133, emu(1.0), emu(4.75), emu(11.4), emu(0.8), "Thong diep voi thay: GAN khong bi bo; em doi vai GAN sang noi co headroom that hon.", 1550, COLORS["gray"], True, "ctr"),
    ])

    slides.append(header("Huong 1: GAN-as-augmentation-engine", "Pivot phong thu: GAN sinh du lieu de train detector robust hon") + [
        shape_xml(140, emu(0.7), emu(2.0), emu(2.4), emu(0.8), "Train goc", COLORS["lighter"], COLORS["blue"], True, 1250, COLORS["black"], True),
        shape_xml(141, emu(3.7), emu(1.25), emu(2.5), emu(0.75), "Detector D0\nno aug", COLORS["white"], COLORS["gray"], True, 1100),
        shape_xml(142, emu(3.7), emu(2.25), emu(2.5), emu(0.75), "Detector D1\nmutation aug", COLORS["white"], COLORS["gray"], True, 1100),
        shape_xml(143, emu(3.7), emu(3.25), emu(2.5), emu(0.75), "Detector D2\nGAN aug", COLORS["white"], COLORS["green"], True, 1100),
        shape_xml(144, emu(7.0), emu(2.25), emu(2.5), emu(0.9), "Held-out +\nadversarial test", COLORS["lighter"], COLORS["orange"], True, 1200, COLORS["black"], True),
        shape_xml(145, emu(10.2), emu(2.25), emu(2.3), emu(0.9), "Robustness\nDelta", COLORS["green"], COLORS["green"], True, 1300, COLORS["white"], True),
        line_xml(146, emu(3.1), emu(2.4), emu(3.7), emu(1.6), COLORS["blue"]),
        line_xml(147, emu(3.1), emu(2.4), emu(3.7), emu(2.6), COLORS["blue"]),
        line_xml(148, emu(3.1), emu(2.4), emu(3.7), emu(3.6), COLORS["blue"]),
        line_xml(149, emu(6.2), emu(2.6), emu(7.0), emu(2.7), COLORS["orange"]),
        line_xml(150, emu(9.5), emu(2.7), emu(10.2), emu(2.7), COLORS["green"]),
        textbox_xml(151, emu(0.9), emu(5.15), emu(11.5), emu(0.55), "Cau hoi khoa hoc: GAN samples co giup detector tong quat hoa hon mutation-only khong?", 1400, COLORS["gray"], True, "ctr"),
    ])

    slides.append(header("Huong 2: GAN-as-policy trong real-space", "Tra loi truc tiep cau hoi: WAF reward dung o dau?") + [
        shape_xml(160, emu(0.6), emu(2.0), emu(2.1), emu(0.8), "Rehydrated\npayload", COLORS["lighter"], COLORS["blue"], True, 1200, COLORS["black"], True),
        shape_xml(161, emu(3.2), emu(2.0), emu(2.1), emu(0.8), "Policy G\nchon action", COLORS["blue"], COLORS["blue"], True, 1250, COLORS["white"], True),
        shape_xml(162, emu(5.8), emu(2.0), emu(2.1), emu(0.8), "Apply\nmutation", COLORS["lighter"], COLORS["cyan"], True, 1200, COLORS["black"], True),
        shape_xml(163, emu(8.4), emu(2.0), emu(2.1), emu(0.8), "WAF / DB\noracle", COLORS["orange"], COLORS["orange"], True, 1200, COLORS["white"], True),
        shape_xml(164, emu(10.9), emu(2.0), emu(1.8), emu(0.8), "Reward", COLORS["green"], COLORS["green"], True, 1300, COLORS["white"], True),
        line_xml(165, emu(2.7), emu(2.4), emu(3.2), emu(2.4), COLORS["blue"]),
        line_xml(166, emu(5.3), emu(2.4), emu(5.8), emu(2.4), COLORS["cyan"]),
        line_xml(167, emu(7.9), emu(2.4), emu(8.4), emu(2.4), COLORS["orange"]),
        line_xml(168, emu(10.5), emu(2.4), emu(10.9), emu(2.4), COLORS["green"]),
        line_xml(169, emu(11.8), emu(3.0), emu(4.25), emu(4.55), COLORS["green"]),
        shape_xml(170, emu(3.2), emu(4.25), emu(2.2), emu(0.75), "Update/rerank\nPolicy G", COLORS["lighter"], COLORS["green"], True, 1150, COLORS["black"], True),
        textbox_xml(171, emu(0.95), emu(5.55), emu(11.4), emu(0.55), "Reward cao = valid + intent preserved + not detected; reward am = invalid/broken.", 1350, COLORS["gray"], True, "ctr"),
    ])

    slides.append(header("Kien truc tong the moi", "Lam ro moi quan he G - D - WAF - reward") + [
        shape_xml(180, emu(0.7), emu(1.35), emu(2.6), emu(0.85), "Real / Delex\nData", COLORS["lighter"], COLORS["blue"], True, 1200, COLORS["black"], True),
        shape_xml(181, emu(4.0), emu(1.1), emu(2.6), emu(0.85), "Generator\nPolicy / Aug", COLORS["blue"], COLORS["blue"], True, 1200, COLORS["white"], True),
        shape_xml(182, emu(7.3), emu(1.1), emu(2.6), emu(0.85), "WAF / Oracle\nValidity gate", COLORS["orange"], COLORS["orange"], True, 1150, COLORS["white"], True),
        shape_xml(183, emu(10.2), emu(1.1), emu(2.3), emu(0.85), "Reward\nScore", COLORS["green"], COLORS["green"], True, 1200, COLORS["white"], True),
        shape_xml(184, emu(4.0), emu(3.2), emu(2.6), emu(0.85), "Augmented\nTraining Set", COLORS["lighter"], COLORS["green"], True, 1150, COLORS["black"], True),
        shape_xml(185, emu(7.3), emu(3.2), emu(2.6), emu(0.85), "Detector D\nPhong thu", COLORS["purple"], COLORS["purple"], True, 1200, COLORS["white"], True),
        line_xml(186, emu(3.3), emu(1.75), emu(4.0), emu(1.52), COLORS["blue"]),
        line_xml(187, emu(6.6), emu(1.52), emu(7.3), emu(1.52), COLORS["orange"]),
        line_xml(188, emu(9.9), emu(1.52), emu(10.2), emu(1.52), COLORS["green"]),
        line_xml(189, emu(5.3), emu(2.0), emu(5.3), emu(3.2), COLORS["green"]),
        line_xml(190, emu(6.6), emu(3.62), emu(7.3), emu(3.62), COLORS["purple"]),
        line_xml(191, emu(11.2), emu(2.0), emu(5.3), emu(4.55), COLORS["green"]),
        textbox_xml(192, emu(1.0), emu(5.45), emu(11.4), emu(0.55), "Hai cach dung reward: rerank/select mau kho, hoac update policy trong real-space.", 1350, COLORS["gray"], True, "ctr"),
    ])

    slides.append(header("Ke hoach thuc nghiem tiep theo", "Quyet dinh pivot bang du lieu, khong bang nhu cau de tai") + table(200, 0.75, 1.35, [
        ["Buoc", "Viec can lam", "Ket qua can co"],
        ["1", "Diversity/coverage: GAN vs mutation @ fixed validity", "Biet generator con gia tri ton du khong"],
        ["2", "Augmentation smoke test", "Detector + GAN aug co robust hon khong"],
        ["3", "Real-space vertical slice", "Rehydrate + libinjection/local WAF"],
        ["4", "Chot thesis", "Augmentation positive hoac negative-methodology"],
    ], [1.0, 6.4, 4.6], 0.62))

    slides.append(header("Ket luan de noi voi thay", "Trung thuc voi ket qua, van giu GAN lam trung tam") + [
        shape_xml(220, emu(0.9), emu(1.45), emu(3.4), emu(1.0), "Da lam", COLORS["blue"], COLORS["blue"], True, 1700, COLORS["white"], True),
        shape_xml(221, emu(4.95), emu(1.45), emu(3.4), emu(1.0), "Ket qua", COLORS["orange"], COLORS["orange"], True, 1700, COLORS["white"], True),
        shape_xml(222, emu(9.0), emu(1.45), emu(3.4), emu(1.0), "Dinh huong", COLORS["green"], COLORS["green"], True, 1700, COLORS["white"], True),
        textbox_xml(223, emu(0.9), emu(2.85), emu(3.4), emu(1.5), "Dataset audit\nCluster split\nBaselines\nH5' GAN\nEvaluator", 1350, COLORS["black"], False, "ctr"),
        textbox_xml(224, emu(4.95), emu(2.85), emu(3.4), emu(1.5), "GAN generator\nkhong vuot baseline\ntrong delex-space", 1350, COLORS["black"], False, "ctr"),
        textbox_xml(225, emu(9.0), emu(2.85), emu(3.4), emu(1.5), "GAN doi vai:\naugmentation-engine\nreal-space policy", 1350, COLORS["black"], False, "ctr"),
        textbox_xml(226, emu(0.9), emu(5.35), emu(11.4), emu(0.65), "GAN van la trung tam theo nghia nghien cuu vai tro cua GAN trong SQLi pipeline, khong phai ep GAN generator phai thang moi baseline.", 1350, COLORS["gray"], True, "ctr"),
    ])

    return [slide_xml(s) for s in slides]


def content_types(n: int) -> str:
    slides = "\n".join([f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' for i in range(1, n + 1)])
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  {slides}
</Types>"""


def presentation_xml(n: int) -> str:
    ids = "\n".join([f'<p:sldId id="{255 + i}" r:id="rId{i + 1}"/>' for i in range(1, n + 1)])
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:sldIdLst>{ids}</p:sldIdLst>
  <p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""


def presentation_rels(n: int) -> str:
    rels = ['<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>']
    for i in range(1, n + 1):
        rels.append(f'<Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>')
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {''.join(rels)}
</Relationships>"""


ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>"""


SLIDE_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>"""


MASTER_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>"""


LAYOUT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""


SLIDE_MASTER = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>"""


SLIDE_LAYOUT = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}" type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>"""


THEME = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="{NS_A}" name="GAN_SQLi Theme">
  <a:themeElements>
    <a:clrScheme name="Custom">
      <a:dk1><a:srgbClr val="111827"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="153A5B"/></a:dk2><a:lt2><a:srgbClr val="EDF2F7"/></a:lt2>
      <a:accent1><a:srgbClr val="2B6CB0"/></a:accent1><a:accent2><a:srgbClr val="2F855A"/></a:accent2>
      <a:accent3><a:srgbClr val="C05621"/></a:accent3><a:accent4><a:srgbClr val="6B46C1"/></a:accent4>
      <a:accent5><a:srgbClr val="1A9BAA"/></a:accent5><a:accent6><a:srgbClr val="C53030"/></a:accent6>
      <a:hlink><a:srgbClr val="2B6CB0"/></a:hlink><a:folHlink><a:srgbClr val="6B46C1"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Calibri"><a:majorFont><a:latin typeface="Calibri"/></a:majorFont><a:minorFont><a:latin typeface="Calibri"/></a:minorFont></a:fontScheme>
    <a:fmtScheme name="Simple"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme>
  </a:themeElements>
</a:theme>"""


def build_pptx() -> Path:
    slides = build_slides()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types(len(slides)))
        z.writestr("_rels/.rels", ROOT_RELS)
        z.writestr("ppt/presentation.xml", presentation_xml(len(slides)))
        z.writestr("ppt/_rels/presentation.xml.rels", presentation_rels(len(slides)))
        z.writestr("ppt/slideMasters/slideMaster1.xml", SLIDE_MASTER)
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", MASTER_RELS)
        z.writestr("ppt/slideLayouts/slideLayout1.xml", SLIDE_LAYOUT)
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", LAYOUT_RELS)
        z.writestr("ppt/theme/theme1.xml", THEME)
        for idx, slide in enumerate(slides, start=1):
            z.writestr(f"ppt/slides/slide{idx}.xml", slide)
            z.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", SLIDE_RELS)
    return OUT


if __name__ == "__main__":
    print(build_pptx())

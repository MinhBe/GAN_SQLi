from __future__ import annotations

from build_gan_sql_pptx_openxml import COLORS, NS_A, NS_P, emu, esc, header, shape_xml, solid_fill, table, textbox_xml


def _dash_xml(dashed: bool) -> str:
    return '<a:prstDash val="dash"/>' if dashed else ""


def node(
    shape_id: int,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    color: str,
    done: bool = True,
    font: int = 1150,
) -> str:
    fill = color if done else COLORS["lighter"]
    font_color = COLORS["white"] if done else color
    dash = _dash_xml(not done)
    return f"""
    <p:sp xmlns:a="{NS_A}" xmlns:p="{NS_P}">
      <p:nvSpPr><p:cNvPr id="{shape_id}" name="Node {shape_id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
        <a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom>
        {solid_fill(fill)}
        <a:ln w="28575"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{dash}</a:ln>
      </p:spPr>
      <p:txBody><a:bodyPr wrap="square" lIns="91440" tIns="68580" rIns="91440" bIns="68580"/><a:lstStyle/>
        <a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="vi-VN" sz="{font}" b="1">{solid_fill(font_color)}<a:latin typeface="Calibri"/></a:rPr><a:t>{esc(title)}</a:t></a:r><a:endParaRPr lang="vi-VN"/></a:p>
      </p:txBody>
    </p:sp>
    """


def arrow(shape_id: int, x1: float, y1: float, x2: float, y2: float, color: str, dashed: bool = False, w: int = 28575) -> str:
    x = emu(min(x1, x2))
    y = emu(min(y1, y2))
    cx = max(1, emu(abs(x2 - x1)))
    cy = max(1, emu(abs(y2 - y1)))
    flip_h = ' flipH="1"' if x2 < x1 else ""
    flip_v = ' flipV="1"' if y2 < y1 else ""
    return f"""
    <p:cxnSp xmlns:a="{NS_A}" xmlns:p="{NS_P}">
      <p:nvCxnSpPr><p:cNvPr id="{shape_id}" name="Arrow {shape_id}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>
      <p:spPr>
        <a:xfrm{flip_h}{flip_v}><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
        <a:prstGeom prst="straightConnector1"><a:avLst/></a:prstGeom>
        <a:ln w="{w}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{_dash_xml(dashed)}<a:tailEnd type="none"/><a:headEnd type="triangle"/></a:ln>
      </p:spPr>
    </p:cxnSp>
    """


def elbow(shape_id: int, x1: float, y1: float, x2: float, y2: float, color: str, dashed: bool = False, w: int = 28575) -> str:
    x = emu(min(x1, x2))
    y = emu(min(y1, y2))
    cx = max(1, emu(abs(x2 - x1)))
    cy = max(1, emu(abs(y2 - y1)))
    flip_h = ' flipH="1"' if x2 < x1 else ""
    flip_v = ' flipV="1"' if y2 < y1 else ""
    return f"""
    <p:cxnSp xmlns:a="{NS_A}" xmlns:p="{NS_P}">
      <p:nvCxnSpPr><p:cNvPr id="{shape_id}" name="Elbow {shape_id}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>
      <p:spPr>
        <a:xfrm{flip_h}{flip_v}><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
        <a:prstGeom prst="bentConnector3"><a:avLst/></a:prstGeom>
        <a:ln w="{w}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{_dash_xml(dashed)}<a:tailEnd type="none"/><a:headEnd type="triangle"/></a:ln>
      </p:spPr>
    </p:cxnSp>
    """


def arrow_label(shape_id: int, x: float, y: float, text: str, color: str, w: float = 2.0, h: float = 0.34, font: int = 820) -> str:
    return shape_xml(shape_id, emu(x), emu(y), emu(w), emu(h), text, COLORS["white"], "CBD5E0", True, font, color, True)


def legend(shape_id: int, x: float, y: float) -> list[str]:
    return [
        node(shape_id, x, y, 0.42, 0.25, "", COLORS["green"], True, 700),
        textbox_xml(shape_id + 1, emu(x + 0.52), emu(y - 0.02), emu(2.3), emu(0.28), "Đã làm (Phase 1-8)", 850, COLORS["gray"], False, "l"),
        node(shape_id + 2, x, y + 0.42, 0.42, 0.25, "", COLORS["orange"], False, 700),
        textbox_xml(shape_id + 3, emu(x + 0.52), emu(y + 0.40), emu(2.4), emu(0.28), "Tương lai (đề xuất)", 850, COLORS["gray"], False, "l"),
    ]


def master_loop_parts(start_id: int = 1000) -> list[str]:
    sid = start_id
    parts = header("Vòng lặp đối kháng G-D-WAF-reward", "Một sơ đồ trả lời trực tiếp: các khối nối với nhau thế nào và reward dùng ở đâu?")
    parts += [
        node(sid, 0.55, 2.35, 1.95, 0.8, "Dataset /\nDelex-frame", COLORS["blue"], True, 1050),
        node(sid + 1, 3.05, 1.35, 1.85, 0.82, "Generator G", COLORS["blue"], True, 1120),
        node(sid + 2, 5.45, 1.35, 1.85, 0.82, "Candidates", COLORS["cyan"], True, 1120),
        node(sid + 3, 8.0, 1.35, 2.0, 0.82, "Discriminator D\n/ Detector", COLORS["purple"], True, 980),
        node(sid + 4, 8.15, 3.45, 2.0, 0.82, "WAF / Oracle", COLORS["orange"], True, 1080),
        node(sid + 5, 5.4, 4.85, 1.95, 0.82, "Reward /\nScore", COLORS["green"], True, 1050),
        node(sid + 6, 10.75, 4.7, 1.9, 0.82, "Augmented\ntraining set", COLORS["green"], False, 920),
        arrow(sid + 10, 2.5, 2.55, 3.05, 1.75, COLORS["blue"]),
        arrow_label(sid + 11, 1.75, 1.65, "frame + điều kiện", COLORS["blue"], 1.75, 0.32),
        arrow(sid + 12, 4.9, 1.76, 5.45, 1.76, COLORS["blue"]),
        arrow_label(sid + 13, 4.65, 1.2, "sinh slot / biến thể", COLORS["blue"], 1.95, 0.32),
        arrow(sid + 14, 7.3, 1.76, 8.0, 1.76, COLORS["purple"]),
        arrow_label(sid + 15, 6.9, 1.2, "đưa real vs fake", COLORS["purple"], 1.9, 0.32),
        elbow(sid + 16, 8.0, 1.42, 4.0, 1.08, COLORS["purple"]),
        arrow_label(sid + 17, 5.05, 0.72, "tín hiệu đối kháng", COLORS["purple"], 2.05, 0.32),
        arrow(sid + 18, 6.55, 2.17, 8.15, 3.45, COLORS["orange"]),
        arrow_label(sid + 19, 6.55, 2.7, "validity + evasion", COLORS["orange"], 2.0, 0.32),
        arrow(sid + 20, 8.15, 3.98, 7.35, 5.0, COLORS["green"]),
        arrow_label(sid + 21, 7.35, 4.35, "điểm số", COLORS["green"], 1.05, 0.32),
        elbow(sid + 22, 5.4, 5.26, 3.85, 2.17, COLORS["green"]),
        arrow_label(sid + 23, 2.65, 4.65, "reward -> rerank / penalty", COLORS["green"], 2.35, 0.32),
        elbow(sid + 24, 6.5, 5.26, 4.45, 2.17, COLORS["green"], True),
        arrow_label(sid + 25, 4.35, 5.52, "-> policy update", COLORS["green"], 1.65, 0.32),
        arrow(sid + 26, 10.15, 3.98, 10.75, 5.05, COLORS["green"], True),
        arrow_label(sid + 27, 9.75, 4.45, "dữ liệu gắn nhãn", COLORS["green"], 1.95, 0.32),
        elbow(sid + 28, 11.7, 4.7, 9.2, 2.17, COLORS["purple"], True),
        arrow_label(sid + 29, 10.1, 3.0, "augment -> D robust hơn", COLORS["purple"], 2.2, 0.32),
        textbox_xml(sid + 30, emu(0.75), emu(5.85), emu(11.6), emu(0.35), "G sinh ứng viên; D tạo tín hiệu đối kháng; WAF/Oracle chấm validity/evasion; reward quay về để chọn mẫu và mở đường policy update.", 1050, COLORS["gray"], True, "ctr"),
    ]
    parts += legend(sid + 40, 10.35, 0.75)
    return parts


def zoom_h5_parts(start_id: int = 2000) -> list[str]:
    sid = start_id
    parts = header("Zoom 1 - Hiện trạng: H5' Paired Masked Surgery GAN", "Đã làm: sinh slot/local token trong delex-frame, rồi đo với baseline và evaluator")
    parts += [
        node(sid, 0.55, 1.55, 1.75, 0.75, "Delex frame", COLORS["blue"], True),
        node(sid + 1, 0.55, 2.55, 1.75, 0.75, "Mask slot", COLORS["cyan"], True),
        node(sid + 2, 0.55, 3.55, 1.75, 0.75, "Condition", COLORS["blue"], True),
        node(sid + 3, 3.15, 1.45, 1.75, 0.62, "token emb", COLORS["blue"], True, 920),
        node(sid + 4, 3.15, 2.25, 1.75, 0.62, "condition emb", COLORS["blue"], True, 880),
        node(sid + 5, 3.15, 3.05, 1.75, 0.62, "position emb", COLORS["blue"], True, 880),
        node(sid + 6, 5.35, 2.25, 1.75, 0.72, "Conv1D", COLORS["blue"], True, 1050),
        node(sid + 7, 7.55, 2.25, 1.75, 0.72, "linear head\n-> token dist", COLORS["cyan"], True, 850),
        node(sid + 8, 10.0, 1.45, 2.25, 0.72, "Paired D\nreal-fill vs fake-fill", COLORS["purple"], True, 820),
        node(sid + 9, 10.0, 2.65, 2.25, 0.72, "Evaluator\nvalid/novel/evasion", COLORS["orange"], True, 800),
        node(sid + 10, 10.0, 3.85, 2.25, 0.72, "Gate result\nGAN ~= baseline", COLORS["red"], True, 850),
        arrow(sid + 20, 2.3, 1.92, 3.15, 1.76, COLORS["blue"]),
        arrow(sid + 21, 2.3, 2.92, 3.15, 2.56, COLORS["blue"]),
        arrow(sid + 22, 2.3, 3.92, 3.15, 3.36, COLORS["blue"]),
        arrow(sid + 23, 4.9, 2.56, 5.35, 2.61, COLORS["blue"]),
        arrow(sid + 24, 7.1, 2.61, 7.55, 2.61, COLORS["cyan"]),
        arrow(sid + 25, 9.3, 2.61, 10.0, 1.8, COLORS["purple"]),
        arrow(sid + 26, 9.3, 2.61, 10.0, 3.0, COLORS["orange"]),
        arrow(sid + 27, 11.1, 3.37, 11.1, 3.85, COLORS["red"]),
        arrow_label(sid + 28, 4.85, 1.6, "G internals", COLORS["blue"], 1.35, 0.32),
        arrow_label(sid + 29, 8.55, 1.35, "so real/fake", COLORS["purple"], 1.35, 0.32),
        arrow_label(sid + 30, 8.55, 3.18, "tách trục đo", COLORS["orange"], 1.35, 0.32),
        shape_xml(sid + 31, emu(0.85), emu(5.0), emu(5.2), emu(0.62), "Loss: L = anchor-CE + lambda*adv + entropy", COLORS["lighter"], COLORS["green"], True, 1200, COLORS["green"], True),
        shape_xml(sid + 32, emu(6.55), emu(4.85), emu(5.55), emu(0.85), "Gate: anchor 0.0050; mutation 0.0000; H5' 0.0000-0.0050\n=> adversarial contribution ~= 0; delex oracle AUC ~= 1.0", COLORS["lighter"], COLORS["red"], True, 1050, COLORS["red"], True),
    ]
    return parts


def zoom_augmentation_parts(start_id: int = 3000) -> list[str]:
    sid = start_id
    parts = header("Zoom 2 - Tương lai 1: GAN-as-Augmentation-Engine", "Phòng thủ: dùng GAN để tạo training data khó hơn, đo bằng detector robustness")
    parts += [
        node(sid, 0.65, 2.3, 1.8, 0.78, "Train gốc", COLORS["blue"], True),
        node(sid + 1, 3.0, 2.3, 2.0, 0.78, "GAN sinh\nbiến thể đa dạng", COLORS["blue"], False, 900),
        node(sid + 2, 5.65, 2.3, 2.05, 0.78, "Tập tăng\ncường", COLORS["green"], False, 940),
        node(sid + 3, 8.35, 2.3, 1.9, 0.78, "Train\nDetector", COLORS["purple"], False, 980),
        node(sid + 4, 10.9, 2.3, 1.55, 0.78, "Held-out +\nadversarial test", COLORS["orange"], False, 800),
        arrow(sid + 10, 2.45, 2.69, 3.0, 2.69, COLORS["blue"], True),
        arrow(sid + 11, 5.0, 2.69, 5.65, 2.69, COLORS["green"], True),
        arrow(sid + 12, 7.7, 2.69, 8.35, 2.69, COLORS["purple"], True),
        arrow(sid + 13, 10.25, 2.69, 10.9, 2.69, COLORS["orange"], True),
        arrow_label(sid + 14, 2.55, 1.85, "augment", COLORS["blue"], 1.0, 0.32),
        arrow_label(sid + 15, 5.0, 1.85, "gắn nhãn", COLORS["green"], 1.0, 0.32),
        arrow_label(sid + 16, 7.75, 1.85, "học robust hơn", COLORS["purple"], 1.45, 0.32),
        textbox_xml(sid + 17, emu(1.0), emu(4.25), emu(11.2), emu(0.45), "So sánh: D0 no aug | D1 mutation aug | D2 GAN aug | D3 mutation + GAN", 1300, COLORS["black"], True, "ctr"),
        shape_xml(sid + 18, emu(1.5), emu(5.05), emu(9.9), emu(0.6), "Metrics: recall | F1 | FPR benign | robustness delta", COLORS["lighter"], COLORS["green"], True, 1200, COLORS["green"], True),
    ]
    return parts


def zoom_policy_parts(start_id: int = 4000) -> list[str]:
    sid = start_id
    parts = header("Zoom 3 - Tương lai 2: GAN-as-Real-Space Policy", "Tấn công thật: reward từ WAF/libinjection quay về policy G trong vòng kín")
    parts += [
        node(sid, 0.4, 2.1, 1.55, 0.72, "Delex", COLORS["blue"], True, 1050),
        node(sid + 1, 2.35, 2.1, 1.75, 0.72, "Rehydrate\nliteral/case", COLORS["cyan"], False, 820),
        node(sid + 2, 4.55, 2.1, 1.95, 0.72, "Policy G\nchọn action", COLORS["blue"], False, 880),
        node(sid + 3, 6.95, 2.1, 1.75, 0.72, "Apply\nmutation", COLORS["cyan"], False, 900),
        node(sid + 4, 9.1, 2.1, 1.75, 0.72, "Real WAF /\nlibinjection", COLORS["orange"], False, 820),
        node(sid + 5, 11.25, 2.1, 1.2, 0.72, "Reward", COLORS["green"], False, 900),
        arrow(sid + 10, 1.95, 2.46, 2.35, 2.46, COLORS["cyan"], True),
        arrow(sid + 11, 4.1, 2.46, 4.55, 2.46, COLORS["blue"], True),
        arrow(sid + 12, 6.5, 2.46, 6.95, 2.46, COLORS["cyan"], True),
        arrow(sid + 13, 8.7, 2.46, 9.1, 2.46, COLORS["orange"], True),
        arrow(sid + 14, 10.85, 2.46, 11.25, 2.46, COLORS["green"], True),
        elbow(sid + 15, 11.85, 2.82, 5.5, 4.7, COLORS["green"], True),
        node(sid + 16, 4.25, 4.45, 2.55, 0.58, "policy update / rerank", COLORS["green"], False, 900),
        arrow_label(sid + 17, 2.1, 1.58, "khôi phục surface", COLORS["cyan"], 1.65, 0.32),
        arrow_label(sid + 18, 4.35, 1.58, "comment/case/operator/encode/space", COLORS["blue"], 2.7, 0.32),
        arrow_label(sid + 19, 9.05, 1.58, "validity + evasion", COLORS["orange"], 1.8, 0.32),
        arrow_label(sid + 20, 7.65, 4.55, "reward feedback", COLORS["green"], 1.55, 0.32),
        shape_xml(sid + 21, emu(1.0), emu(5.35), emu(11.0), emu(0.48), "Reward rule: valid + giữ intent + không bị detect = cao; invalid = âm; bị detect = thấp.", COLORS["lighter"], COLORS["green"], True, 1050, COLORS["green"], True),
    ]
    return parts


def title_parts() -> list[str]:
    return [
        shape_xml(2, 0, 0, emu(13.333), emu(7.5), "", COLORS["navy"], COLORS["navy"]),
        textbox_xml(3, emu(0.85), emu(1.25), emu(11.7), emu(1.0), "Kiến trúc GAN-SQLi: vòng lặp đối kháng có nhãn quan hệ", 2800, COLORS["white"], True, "ctr"),
        textbox_xml(4, emu(1.15), emu(2.55), emu(11.1), emu(0.7), "G - D - WAF/Oracle - Reward: kết nối nào, tín hiệu nào, dùng ở đâu", 1600, "DDEBFF", False, "ctr"),
        node(5, 1.0, 4.25, 2.6, 0.8, "MASTER loop", COLORS["blue"], True, 1150),
        node(6, 5.35, 4.25, 2.6, 0.8, "3 zoom slides", COLORS["purple"], True, 1150),
        node(7, 9.7, 4.25, 2.6, 0.8, "Deck tích hợp", COLORS["green"], True, 1150),
        arrow(8, 3.6, 4.65, 5.35, 4.65, COLORS["white"]),
        arrow(9, 7.95, 4.65, 9.7, 4.65, COLORS["white"]),
    ]

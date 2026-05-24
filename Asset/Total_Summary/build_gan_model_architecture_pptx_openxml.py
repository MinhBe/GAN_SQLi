from __future__ import annotations

import zipfile
from pathlib import Path

from build_gan_sql_pptx_openxml import (
    COLORS,
    LAYOUT_RELS,
    MASTER_RELS,
    NS_A,
    ROOT_RELS,
    SLIDE_H,
    SLIDE_LAYOUT,
    SLIDE_MASTER,
    SLIDE_RELS,
    SLIDE_W,
    THEME,
    content_types,
    emu,
    header,
    line_xml,
    presentation_rels,
    presentation_xml,
    shape_xml,
    slide_xml,
    solid_fill,
    table,
    textbox_xml,
)
from pptx_diagram_helpers import master_loop_parts, zoom_augmentation_parts, zoom_h5_parts, zoom_policy_parts


OUT = Path(__file__).resolve().parent / "GAN_SQLi_Model_Architecture_Report_230526.pptx"


def bullets(shape_id: int, x: float, y: float, w: float, h: float, lines: list[str], size: int = 1400) -> str:
    return textbox_xml(shape_id, emu(x), emu(y), emu(w), emu(h), "\n".join([f"- {line}" for line in lines]), size, COLORS["black"], False, "l")


def mini_label(shape_id: int, x: float, y: float, text: str, color: str) -> str:
    return shape_xml(shape_id, emu(x), emu(y), emu(2.25), emu(0.48), text, COLORS["white"], color, True, 950, color, True)


def build_slides() -> list[str]:
    slides: list[list[str]] = []

    slides.append([
        shape_xml(2, 0, 0, SLIDE_W, SLIDE_H, "", COLORS["navy"], COLORS["navy"]),
        textbox_xml(3, emu(0.85), emu(0.95), emu(11.8), emu(1.1), "Kien truc mo hinh GAN cho SQL Injection sau gop y", 3150, COLORS["white"], True, "ctr"),
        textbox_xml(4, emu(1.35), emu(2.25), emu(10.8), emu(0.8), "Dataset - Generator - Discriminator - WAF/Evaluator - Reward - Baseline - Huong tiep", 1700, "DDEBFF", False, "ctr"),
        shape_xml(5, emu(0.95), emu(4.2), emu(2.25), emu(0.85), "Da lam\nPhase 1-8", COLORS["blue"], COLORS["white"], True, 1250, COLORS["white"], True),
        shape_xml(6, emu(3.95), emu(4.2), emu(2.25), emu(0.85), "Kien truc\nG-D-WAF", COLORS["purple"], COLORS["white"], True, 1250, COLORS["white"], True),
        shape_xml(7, emu(6.95), emu(4.2), emu(2.25), emu(0.85), "Ket qua\nGate fail", COLORS["red"], COLORS["white"], True, 1250, COLORS["white"], True),
        shape_xml(8, emu(9.95), emu(4.2), emu(2.25), emu(0.85), "Tiep theo\nDoi vai GAN", COLORS["green"], COLORS["white"], True, 1250, COLORS["white"], True),
        line_xml(9, emu(3.2), emu(4.62), emu(3.95), emu(4.62), COLORS["white"]),
        line_xml(10, emu(6.2), emu(4.62), emu(6.95), emu(4.62), COLORS["white"]),
        line_xml(11, emu(9.2), emu(4.62), emu(9.95), emu(4.62), COLORS["white"]),
    ])

    slides.append(header("Thay da yeu cau lam ro gi?", "Deck nay tra loi truc tiep cac diem sau gop y") + [
        shape_xml(20, emu(0.75), emu(1.45), emu(2.6), emu(1.05), "Dataset\nnguon + nhan", COLORS["lighter"], COLORS["blue"], True, 1250, COLORS["black"], True),
        shape_xml(21, emu(3.85), emu(1.45), emu(2.6), emu(1.05), "Generator /\nDiscriminator", COLORS["lighter"], COLORS["purple"], True, 1250, COLORS["black"], True),
        shape_xml(22, emu(6.95), emu(1.45), emu(2.6), emu(1.05), "WAF / Evaluator\nreward", COLORS["lighter"], COLORS["orange"], True, 1200, COLORS["black"], True),
        shape_xml(23, emu(10.05), emu(1.45), emu(2.6), emu(1.05), "Baseline /\ncollapse", COLORS["lighter"], COLORS["red"], True, 1250, COLORS["black"], True),
        textbox_xml(24, emu(1.05), emu(3.35), emu(11.0), emu(0.65), "Thong diep chinh: em da lam ro pipeline du lieu, kien truc G-D-WAF, noi dung reward, ket qua fail gate va huong doi vai GAN.", 1450, COLORS["black"], True, "ctr"),
        bullets(25, 1.4, 4.55, 10.0, 1.05, [
            "Khong chi ke pivot; moi slide gan voi mot thanh phan ky thuat.",
            "Nhan manh dieu da lam sau gop y va cach danh gia cong bang."
        ], 1250),
    ])

    slides.append(header("Kien truc dataset hien tai", "Multiple sources -> normalize -> label/confidence -> delex -> audit -> cluster split") + [
        shape_xml(30, emu(0.45), emu(2.0), emu(1.85), emu(0.75), "Multiple\nsources", COLORS["lighter"], COLORS["blue"], True, 1100, COLORS["black"], True),
        shape_xml(31, emu(2.65), emu(2.0), emu(1.85), emu(0.75), "Normalize\nschema", COLORS["lighter"], COLORS["blue"], True, 1100, COLORS["black"], True),
        shape_xml(32, emu(4.85), emu(2.0), emu(1.85), emu(0.75), "Label +\nconfidence", COLORS["lighter"], COLORS["blue"], True, 1050, COLORS["black"], True),
        shape_xml(33, emu(7.05), emu(2.0), emu(1.85), emu(0.75), "Delex\nv5", COLORS["lighter"], COLORS["cyan"], True, 1100, COLORS["black"], True),
        shape_xml(34, emu(9.25), emu(2.0), emu(1.85), emu(0.75), "Audit", COLORS["lighter"], COLORS["orange"], True, 1150, COLORS["black"], True),
        shape_xml(35, emu(11.45), emu(2.0), emu(1.45), emu(0.75), "Cluster\nsplit", COLORS["green"], COLORS["green"], True, 1050, COLORS["white"], True),
        line_xml(36, emu(2.3), emu(2.38), emu(2.65), emu(2.38), COLORS["blue"]),
        line_xml(37, emu(4.5), emu(2.38), emu(4.85), emu(2.38), COLORS["blue"]),
        line_xml(38, emu(6.7), emu(2.38), emu(7.05), emu(2.38), COLORS["cyan"]),
        line_xml(39, emu(8.9), emu(2.38), emu(9.25), emu(2.38), COLORS["orange"]),
        line_xml(40, emu(11.1), emu(2.38), emu(11.45), emu(2.38), COLORS["green"]),
        textbox_xml(41, emu(0.85), emu(3.65), emu(11.6), emu(0.45), "Field chinh", 1400, COLORS["navy"], True, "ctr"),
        mini_label(42, 0.95, 4.35, "payload_working", COLORS["blue"]),
        mini_label(43, 3.35, 4.35, "payload_delex_v5", COLORS["cyan"]),
        mini_label(44, 5.75, 4.35, "is_sqli", COLORS["green"]),
        mini_label(45, 8.15, 4.35, "technique_primary", COLORS["purple"]),
        mini_label(46, 10.55, 4.35, "db_family + confidence", COLORS["orange"]),
    ])

    slides.append(header("Labeling va quality control", "Sua diem yeu: confidence khong con la nhan chu quan") + [
        shape_xml(50, emu(0.8), emu(2.0), emu(2.25), emu(0.85), "Raw payload", COLORS["lighter"], COLORS["blue"], True, 1200, COLORS["black"], True),
        shape_xml(51, emu(3.7), emu(2.0), emu(2.25), emu(0.85), "Rule/script\nlabel", COLORS["lighter"], COLORS["purple"], True, 1150, COLORS["black"], True),
        shape_xml(52, emu(6.6), emu(2.0), emu(2.25), emu(0.85), "Confidence\n+ reason", COLORS["lighter"], COLORS["orange"], True, 1150, COLORS["black"], True),
        shape_xml(53, emu(9.5), emu(2.0), emu(2.25), emu(0.85), "Conflict audit", COLORS["lighter"], COLORS["red"], True, 1200, COLORS["black"], True),
        shape_xml(54, emu(5.2), emu(4.05), emu(2.8), emu(0.85), "Gold / Silver\ntraining slices", COLORS["green"], COLORS["green"], True, 1200, COLORS["white"], True),
        line_xml(55, emu(3.05), emu(2.42), emu(3.7), emu(2.42), COLORS["blue"]),
        line_xml(56, emu(5.95), emu(2.42), emu(6.6), emu(2.42), COLORS["purple"]),
        line_xml(57, emu(8.85), emu(2.42), emu(9.5), emu(2.42), COLORS["orange"]),
        line_xml(58, emu(10.6), emu(2.85), emu(6.6), emu(4.05), COLORS["green"]),
        textbox_xml(59, emu(0.9), emu(5.35), emu(11.5), emu(0.55), "Moi label co nguon, ly do va muc tin cay; mau conflict duoc audit truoc khi dung cho claim.", 1350, COLORS["gray"], True, "ctr"),
    ])

    slides.append(header("Leakage audit va cluster-safe split", "Random split qua lac quan vi cung template xuat hien o train/test") + [
        shape_xml(60, emu(0.75), emu(1.45), emu(3.0), emu(1.0), "1.6M rows", COLORS["blue"], COLORS["blue"], True, 1700, COLORS["white"], True),
        shape_xml(61, emu(5.05), emu(1.45), emu(3.0), emu(1.0), "~77,804\ntemplates", COLORS["orange"], COLORS["orange"], True, 1500, COLORS["white"], True),
        shape_xml(62, emu(9.35), emu(1.45), emu(3.0), emu(1.0), "Random split\nbi leak", COLORS["red"], COLORS["red"], True, 1450, COLORS["white"], True),
        line_xml(63, emu(3.75), emu(1.95), emu(5.05), emu(1.95), COLORS["gray"]),
        line_xml(64, emu(8.05), emu(1.95), emu(9.35), emu(1.95), COLORS["gray"]),
        shape_xml(65, emu(1.2), emu(3.55), emu(3.0), emu(0.78), "train templates", COLORS["lighter"], COLORS["green"], True, 1250, COLORS["black"], True),
        shape_xml(66, emu(5.15), emu(3.55), emu(3.0), emu(0.78), "dev templates", COLORS["lighter"], COLORS["green"], True, 1250, COLORS["black"], True),
        shape_xml(67, emu(9.1), emu(3.55), emu(3.0), emu(0.78), "test templates", COLORS["lighter"], COLORS["green"], True, 1250, COLORS["black"], True),
        textbox_xml(68, emu(1.0), emu(5.1), emu(11.4), emu(0.7), "Cluster split: template overlap train/dev/test = 0", 1750, COLORS["green"], True, "ctr"),
    ])

    slides.append(header("SeqGAN/full-sequence cu va ly do fail", "Noise/condition -> G sinh full payload -> D real/fake -> reward/loss") + [
        shape_xml(70, emu(0.7), emu(2.0), emu(2.3), emu(0.85), "Noise /\ncondition", COLORS["lighter"], COLORS["blue"], True, 1150, COLORS["black"], True),
        shape_xml(71, emu(3.65), emu(2.0), emu(2.3), emu(0.85), "Generator\nfull payload", COLORS["blue"], COLORS["blue"], True, 1200, COLORS["white"], True),
        shape_xml(72, emu(6.6), emu(2.0), emu(2.3), emu(0.85), "Discriminator\nreal/fake", COLORS["purple"], COLORS["purple"], True, 1150, COLORS["white"], True),
        shape_xml(73, emu(9.55), emu(2.0), emu(2.3), emu(0.85), "Reward /\nloss", COLORS["green"], COLORS["green"], True, 1200, COLORS["white"], True),
        line_xml(74, emu(3.0), emu(2.42), emu(3.65), emu(2.42), COLORS["blue"]),
        line_xml(75, emu(5.95), emu(2.42), emu(6.6), emu(2.42), COLORS["purple"]),
        line_xml(76, emu(8.9), emu(2.42), emu(9.55), emu(2.42), COLORS["green"]),
        bullets(77, 1.0, 3.75, 11.0, 1.65, [
            "Discrete token lam gradient cho G rat yeu.",
            "D qua manh, phan biet real/fake nhanh hon kha nang G hoc.",
            "G mat tin hieu, mode collapse; tuning WGAN-GP/SN/TTUR khong du gate."
        ], 1350),
    ])

    slides.append(header("Kien truc H5' Paired Masked Payload-Surgery GAN", "Khong sinh toan chuoi; chi dien slot trong frame da delex") + [
        shape_xml(80, emu(0.65), emu(2.15), emu(2.1), emu(0.8), "Delex frame", COLORS["lighter"], COLORS["blue"], True, 1200, COLORS["black"], True),
        shape_xml(81, emu(3.25), emu(2.15), emu(2.1), emu(0.8), "Mask slot", COLORS["lighter"], COLORS["cyan"], True, 1200, COLORS["black"], True),
        shape_xml(82, emu(5.85), emu(2.15), emu(2.1), emu(0.8), "Generator", COLORS["blue"], COLORS["blue"], True, 1250, COLORS["white"], True),
        shape_xml(83, emu(8.55), emu(1.25), emu(2.65), emu(0.78), "Paired\nDiscriminator", COLORS["purple"], COLORS["purple"], True, 1100, COLORS["white"], True),
        shape_xml(84, emu(8.55), emu(3.05), emu(2.65), emu(0.78), "Evaluator\nvalid/novel", COLORS["orange"], COLORS["orange"], True, 1100, COLORS["white"], True),
        shape_xml(85, emu(11.6), emu(2.15), emu(1.05), emu(0.8), "Score", COLORS["green"], COLORS["green"], True, 1100, COLORS["white"], True),
        line_xml(86, emu(2.75), emu(2.55), emu(3.25), emu(2.55), COLORS["blue"]),
        line_xml(87, emu(5.35), emu(2.55), emu(5.85), emu(2.55), COLORS["cyan"]),
        line_xml(88, emu(7.95), emu(2.55), emu(8.55), emu(1.64), COLORS["purple"]),
        line_xml(89, emu(7.95), emu(2.55), emu(8.55), emu(3.44), COLORS["orange"]),
        line_xml(90, emu(11.2), emu(1.64), emu(11.6), emu(2.45), COLORS["green"]),
        line_xml(91, emu(11.2), emu(3.44), emu(11.6), emu(2.45), COLORS["green"]),
        textbox_xml(92, emu(1.0), emu(5.35), emu(11.3), emu(0.55), "Muc tieu: kiem tra GAN co tao gia tri tren slot surgery hay khong, voi baseline ro rang.", 1350, COLORS["gray"], True, "ctr"),
    ])

    slides.append(header("Generator trong H5' co gi?", "Input masked payload + technique; output token logits cho masked slots") + [
        shape_xml(100, emu(0.8), emu(1.45), emu(2.45), emu(0.78), "Token\nembedding", COLORS["lighter"], COLORS["blue"], True, 1100, COLORS["black"], True),
        shape_xml(101, emu(0.8), emu(2.55), emu(2.45), emu(0.78), "Condition\nembedding", COLORS["lighter"], COLORS["blue"], True, 1100, COLORS["black"], True),
        shape_xml(102, emu(0.8), emu(3.65), emu(2.45), emu(0.78), "Position\nembedding", COLORS["lighter"], COLORS["blue"], True, 1100, COLORS["black"], True),
        shape_xml(103, emu(4.25), emu(2.45), emu(2.55), emu(0.95), "Conv1D\nencoder", COLORS["blue"], COLORS["blue"], True, 1250, COLORS["white"], True),
        shape_xml(104, emu(7.85), emu(2.45), emu(2.25), emu(0.95), "Linear\nhead", COLORS["cyan"], COLORS["cyan"], True, 1250, COLORS["white"], True),
        shape_xml(105, emu(10.85), emu(2.45), emu(1.8), emu(0.95), "Token\ndist.", COLORS["green"], COLORS["green"], True, 1150, COLORS["white"], True),
        line_xml(106, emu(3.25), emu(1.84), emu(4.25), emu(2.92), COLORS["blue"]),
        line_xml(107, emu(3.25), emu(2.94), emu(4.25), emu(2.94), COLORS["blue"]),
        line_xml(108, emu(3.25), emu(4.04), emu(4.25), emu(2.98), COLORS["blue"]),
        line_xml(109, emu(6.8), emu(2.92), emu(7.85), emu(2.92), COLORS["cyan"]),
        line_xml(110, emu(10.1), emu(2.92), emu(10.85), emu(2.92), COLORS["green"]),
        textbox_xml(111, emu(1.05), emu(5.25), emu(11.2), emu(0.65), "Loss = anchor CE + adversarial + entropy; anchor CE giu G khong roi khoi distribution hop le.", 1350, COLORS["gray"], True, "ctr"),
    ])

    slides.append(header("Discriminator trong H5' co gi?", "Paired discriminator de tranh shortcut tren frame/template") + [
        shape_xml(120, emu(0.75), emu(1.45), emu(2.5), emu(0.75), "Frame embedding", COLORS["lighter"], COLORS["purple"], True, 1100, COLORS["black"], True),
        shape_xml(121, emu(0.75), emu(2.45), emu(2.5), emu(0.75), "Filled payload\nembedding", COLORS["lighter"], COLORS["purple"], True, 1050, COLORS["black"], True),
        shape_xml(122, emu(0.75), emu(3.45), emu(2.5), emu(0.75), "Condition +\nposition", COLORS["lighter"], COLORS["purple"], True, 1050, COLORS["black"], True),
        shape_xml(123, emu(4.35), emu(2.35), emu(2.55), emu(0.9), "Conv1D\nencoder", COLORS["purple"], COLORS["purple"], True, 1250, COLORS["white"], True),
        shape_xml(124, emu(7.8), emu(2.35), emu(2.35), emu(0.9), "Mean/max\npooling", COLORS["orange"], COLORS["orange"], True, 1200, COLORS["white"], True),
        shape_xml(125, emu(10.9), emu(2.35), emu(1.75), emu(0.9), "Real/fake\nscore", COLORS["green"], COLORS["green"], True, 1050, COLORS["white"], True),
        line_xml(126, emu(3.25), emu(1.82), emu(4.35), emu(2.78), COLORS["purple"]),
        line_xml(127, emu(3.25), emu(2.82), emu(4.35), emu(2.82), COLORS["purple"]),
        line_xml(128, emu(3.25), emu(3.82), emu(4.35), emu(2.88), COLORS["purple"]),
        line_xml(129, emu(6.9), emu(2.8), emu(7.8), emu(2.8), COLORS["orange"]),
        line_xml(130, emu(10.15), emu(2.8), emu(10.9), emu(2.8), COLORS["green"]),
        textbox_xml(131, emu(1.0), emu(5.2), emu(11.4), emu(0.65), "Paired D so sanh real/fake trong cung frame de khong thang bang template shortcut.", 1350, COLORS["gray"], True, "ctr"),
    ])

    slides.append(header("Baseline da trien khai", "GAN phai vuot baseline moi duoc claim co dong gop") + [
        shape_xml(140, emu(1.1), emu(1.75), emu(4.3), emu(1.45), "Anchor-only\n\nSupervised slot infill\nKhong adversarial", COLORS["lighter"], COLORS["blue"], True, 1250, COLORS["black"], True),
        shape_xml(141, emu(7.0), emu(1.75), emu(4.3), emu(1.45), "Mutation-engine\n\nRule-based mutation\nKhong hoc", COLORS["lighter"], COLORS["orange"], True, 1250, COLORS["black"], True),
        textbox_xml(142, emu(1.0), emu(4.45), emu(11.4), emu(0.85), "Vai tro baseline: neu GAN khong vuot hai moc nay, khong claim GAN tao evasion/robustness rieng.", 1550, COLORS["red"], True, "ctr"),
    ])

    slides.append(header("Evaluator/WAF architecture", "Candidate duoc cham tren nhieu truc, khong chi bang D-score") + [
        shape_xml(150, emu(0.6), emu(2.45), emu(2.1), emu(0.8), "Candidate", COLORS["blue"], COLORS["blue"], True, 1250, COLORS["white"], True),
        shape_xml(151, emu(3.45), emu(1.25), emu(2.3), emu(0.75), "Validity", COLORS["lighter"], COLORS["green"], True, 1150, COLORS["black"], True),
        shape_xml(152, emu(3.45), emu(2.25), emu(2.3), emu(0.75), "Novelty", COLORS["lighter"], COLORS["green"], True, 1150, COLORS["black"], True),
        shape_xml(153, emu(3.45), emu(3.25), emu(2.3), emu(0.75), "Technique debug", COLORS["lighter"], COLORS["orange"], True, 1050, COLORS["black"], True),
        shape_xml(154, emu(3.45), emu(4.25), emu(2.3), emu(0.75), "Evasion oracle", COLORS["lighter"], COLORS["red"], True, 1100, COLORS["black"], True),
        shape_xml(155, emu(7.15), emu(2.45), emu(2.35), emu(0.8), "WAF / Detector\nresult", COLORS["orange"], COLORS["orange"], True, 1100, COLORS["white"], True),
        shape_xml(156, emu(10.55), emu(2.45), emu(1.8), emu(0.8), "Report\nscore", COLORS["green"], COLORS["green"], True, 1100, COLORS["white"], True),
        line_xml(157, emu(2.7), emu(2.85), emu(3.45), emu(1.62), COLORS["green"]),
        line_xml(158, emu(2.7), emu(2.85), emu(3.45), emu(2.62), COLORS["green"]),
        line_xml(159, emu(2.7), emu(2.85), emu(3.45), emu(3.62), COLORS["orange"]),
        line_xml(160, emu(2.7), emu(2.85), emu(3.45), emu(4.62), COLORS["red"]),
        line_xml(161, emu(5.75), emu(4.62), emu(7.15), emu(2.85), COLORS["orange"]),
        line_xml(162, emu(9.5), emu(2.85), emu(10.55), emu(2.85), COLORS["green"]),
        textbox_xml(163, emu(0.9), emu(5.45), emu(11.5), emu(0.45), "Evasion chi tinh khi co detector/WAF result; technique hint chi dung de debug.", 1250, COLORS["gray"], True, "ctr"),
    ])

    slides.append(header("Reward/score dung o dau?", "WAF/evaluator score -> rerank/select; hoac policy update trong real-space") + [
        shape_xml(170, emu(0.75), emu(2.1), emu(2.55), emu(0.85), "WAF / Evaluator\nscore", COLORS["orange"], COLORS["orange"], True, 1120, COLORS["white"], True),
        shape_xml(171, emu(4.25), emu(1.35), emu(2.8), emu(0.8), "Rerank /\nselect", COLORS["green"], COLORS["green"], True, 1180, COLORS["white"], True),
        shape_xml(172, emu(4.25), emu(3.05), emu(2.8), emu(0.8), "Policy update\nneu real-space", COLORS["green"], COLORS["green"], True, 1080, COLORS["white"], True),
        shape_xml(173, emu(8.2), emu(1.35), emu(3.7), emu(0.8), "valid + novel + not detected = cao", COLORS["lighter"], COLORS["green"], True, 1050, COLORS["black"], True),
        shape_xml(174, emu(8.2), emu(2.45), emu(3.7), emu(0.8), "invalid = am", COLORS["lighter"], COLORS["red"], True, 1150, COLORS["black"], True),
        shape_xml(175, emu(8.2), emu(3.55), emu(3.7), emu(0.8), "detected = thap", COLORS["lighter"], COLORS["orange"], True, 1150, COLORS["black"], True),
        line_xml(176, emu(3.3), emu(2.52), emu(4.25), emu(1.75), COLORS["green"]),
        line_xml(177, emu(3.3), emu(2.52), emu(4.25), emu(3.45), COLORS["green"]),
        line_xml(178, emu(7.05), emu(1.75), emu(8.2), emu(1.75), COLORS["green"]),
        line_xml(179, emu(7.05), emu(3.45), emu(8.2), emu(3.95), COLORS["green"]),
    ])

    slides.append(header("Ket qua H5': gate fail", "Classifier-oracle bypass cho thay adversarial contribution gan bang 0") + table(190, 1.3, 1.35, [
        ["Method", "Role", "Classifier-oracle bypass"],
        ["Anchor-only", "supervised", "0.0050"],
        ["Mutation-engine", "rule-based", "0.0000"],
        ["H5' max-local", "GAN", "0.0000"],
        ["H5' max-aggressive", "GAN", "0.0050"],
        ["Oracle-aware search", "post-process", "0.0050"],
    ], [3.7, 3.1, 3.3], 0.55) + [
        shape_xml(215, emu(1.55), emu(5.25), emu(10.0), emu(0.72), "Ket luan: adversarial contribution ~= 0; khong claim GAN generator vuot baseline.", COLORS["red"], COLORS["red"], True, 1350, COLORS["white"], True),
    ])

    slides.append(header("Vi sao delex-space khong do evasion that?", "Delex tot cho schema, nhung xoa nhieu tin hieu be mat cua WAF") + [
        shape_xml(220, emu(0.85), emu(1.75), emu(3.2), emu(0.95), "Delex removes\ncase/comment/encoding/literal", COLORS["red"], COLORS["red"], True, 1200, COLORS["white"], True),
        shape_xml(221, emu(5.05), emu(1.75), emu(3.2), emu(0.95), "Classifier oracle\nAUC ~ 1.0", COLORS["orange"], COLORS["orange"], True, 1450, COLORS["white"], True),
        shape_xml(222, emu(9.25), emu(1.75), emu(3.2), emu(0.95), "Need real-space\nrehydrate + WAF", COLORS["green"], COLORS["green"], True, 1300, COLORS["white"], True),
        line_xml(223, emu(4.05), emu(2.22), emu(5.05), emu(2.22), COLORS["gray"]),
        line_xml(224, emu(8.25), emu(2.22), emu(9.25), emu(2.22), COLORS["gray"]),
        bullets(225, 1.1, 3.6, 11.0, 1.45, [
            "Evasion that nam o surface form: comment, whitespace, encoding, casing, literals.",
            "Do do can rehydrate payload ve real-space roi cham bang libinjection/local WAF/detector."
        ], 1350),
    ])

    slides.append(header("Kien truc moi 1: GAN-as-Augmentation-Engine", "Dung GAN de tao training data phong thu, khong ep no tu vuot WAF mot minh") + [
        shape_xml(230, emu(0.7), emu(2.25), emu(2.1), emu(0.8), "Original\ntrain", COLORS["lighter"], COLORS["blue"], True, 1150, COLORS["black"], True),
        shape_xml(231, emu(3.35), emu(2.25), emu(2.3), emu(0.8), "GAN\naugmentation", COLORS["blue"], COLORS["blue"], True, 1150, COLORS["white"], True),
        shape_xml(232, emu(6.2), emu(2.25), emu(2.35), emu(0.8), "Augmented\ntrain set", COLORS["lighter"], COLORS["green"], True, 1100, COLORS["black"], True),
        shape_xml(233, emu(9.1), emu(2.25), emu(1.9), emu(0.8), "Train\ndetector", COLORS["purple"], COLORS["purple"], True, 1100, COLORS["white"], True),
        shape_xml(234, emu(11.4), emu(2.25), emu(1.1), emu(0.8), "Test", COLORS["orange"], COLORS["orange"], True, 1150, COLORS["white"], True),
        line_xml(235, emu(2.8), emu(2.65), emu(3.35), emu(2.65), COLORS["blue"]),
        line_xml(236, emu(5.65), emu(2.65), emu(6.2), emu(2.65), COLORS["green"]),
        line_xml(237, emu(8.55), emu(2.65), emu(9.1), emu(2.65), COLORS["purple"]),
        line_xml(238, emu(11.0), emu(2.65), emu(11.4), emu(2.65), COLORS["orange"]),
        textbox_xml(239, emu(1.0), emu(4.35), emu(11.3), emu(0.65), "So sanh D0 no aug, D1 mutation aug, D2 GAN aug, D3 mutation + GAN.", 1400, COLORS["gray"], True, "ctr"),
    ])

    slides.append(header("Thanh phan trong augmentation-engine", "Metric chinh la detector robustness, khong phai bypass rieng le cua G") + [
        shape_xml(250, emu(0.9), emu(1.45), emu(3.1), emu(1.15), "Generator\nsinh bien the kho / coverage cao", COLORS["lighter"], COLORS["blue"], True, 1150, COLORS["black"], True),
        shape_xml(251, emu(5.0), emu(1.45), emu(3.1), emu(1.15), "Detector\nhoc boundary robust hon", COLORS["lighter"], COLORS["purple"], True, 1150, COLORS["black"], True),
        shape_xml(252, emu(9.1), emu(1.45), emu(3.1), emu(1.15), "Evaluator\ndo held-out/adversarial", COLORS["lighter"], COLORS["orange"], True, 1150, COLORS["black"], True),
        textbox_xml(253, emu(0.9), emu(3.75), emu(11.4), emu(0.45), "Metrics", 1400, COLORS["navy"], True, "ctr"),
        mini_label(254, 1.0, 4.55, "recall", COLORS["green"]),
        mini_label(255, 3.4, 4.55, "F1", COLORS["green"]),
        mini_label(256, 5.8, 4.55, "FPR benign", COLORS["red"]),
        mini_label(257, 8.2, 4.55, "robustness delta", COLORS["orange"]),
    ])

    slides.append(header("Kien truc moi 2: GAN-as-Real-Space Policy", "Policy G chon action tren payload da rehydrate, WAF tra reward") + [
        shape_xml(270, emu(0.45), emu(2.0), emu(1.8), emu(0.75), "Delex\npayload", COLORS["lighter"], COLORS["blue"], True, 1050, COLORS["black"], True),
        shape_xml(271, emu(2.75), emu(2.0), emu(1.8), emu(0.75), "Rehydrate", COLORS["lighter"], COLORS["cyan"], True, 1100, COLORS["black"], True),
        shape_xml(272, emu(5.05), emu(2.0), emu(1.8), emu(0.75), "Policy G\nchooses action", COLORS["blue"], COLORS["blue"], True, 950, COLORS["white"], True),
        shape_xml(273, emu(7.35), emu(2.0), emu(1.8), emu(0.75), "Apply\nmutation", COLORS["lighter"], COLORS["cyan"], True, 1050, COLORS["black"], True),
        shape_xml(274, emu(9.65), emu(2.0), emu(1.8), emu(0.75), "WAF / validity\noracle", COLORS["orange"], COLORS["orange"], True, 950, COLORS["white"], True),
        shape_xml(275, emu(11.85), emu(2.0), emu(0.8), emu(0.75), "Reward", COLORS["green"], COLORS["green"], True, 850, COLORS["white"], True),
        line_xml(276, emu(2.25), emu(2.38), emu(2.75), emu(2.38), COLORS["blue"]),
        line_xml(277, emu(4.55), emu(2.38), emu(5.05), emu(2.38), COLORS["cyan"]),
        line_xml(278, emu(6.85), emu(2.38), emu(7.35), emu(2.38), COLORS["blue"]),
        line_xml(279, emu(9.15), emu(2.38), emu(9.65), emu(2.38), COLORS["orange"]),
        line_xml(280, emu(11.45), emu(2.38), emu(11.85), emu(2.38), COLORS["green"]),
        textbox_xml(281, emu(1.05), emu(3.65), emu(11.1), emu(0.55), "Action examples: insert comment, change case, replace operator, encode literal, whitespace mutation.", 1320, COLORS["black"], True, "ctr"),
        line_xml(282, emu(12.25), emu(2.75), emu(5.95), emu(5.0), COLORS["green"]),
        shape_xml(283, emu(4.7), emu(4.7), emu(2.5), emu(0.6), "update / rerank", COLORS["lighter"], COLORS["green"], True, 1050, COLORS["black"], True),
    ])

    slides.append(header("Tong kien truc G-D-WAF-reward cuoi cung", "Hai nhanh: augmentation de phong thu va real-space policy de do evasion that") + [
        shape_xml(290, emu(0.65), emu(1.35), emu(2.1), emu(0.75), "Dataset", COLORS["lighter"], COLORS["blue"], True, 1150, COLORS["black"], True),
        shape_xml(291, emu(3.15), emu(1.35), emu(2.1), emu(0.75), "Preprocess /\ndelex / rehydrate", COLORS["lighter"], COLORS["cyan"], True, 920, COLORS["black"], True),
        shape_xml(292, emu(5.9), emu(1.0), emu(2.3), emu(0.75), "GAN augmentation\nengine", COLORS["blue"], COLORS["blue"], True, 950, COLORS["white"], True),
        shape_xml(293, emu(8.8), emu(1.0), emu(1.9), emu(0.75), "Detector D", COLORS["purple"], COLORS["purple"], True, 1120, COLORS["white"], True),
        shape_xml(294, emu(11.2), emu(1.0), emu(1.25), emu(0.75), "Metrics", COLORS["green"], COLORS["green"], True, 980, COLORS["white"], True),
        shape_xml(295, emu(5.9), emu(3.45), emu(2.3), emu(0.75), "Real-space\npolicy G", COLORS["blue"], COLORS["blue"], True, 1000, COLORS["white"], True),
        shape_xml(296, emu(8.8), emu(3.45), emu(1.9), emu(0.75), "WAF /\nvalidity oracle", COLORS["orange"], COLORS["orange"], True, 900, COLORS["white"], True),
        shape_xml(297, emu(11.2), emu(3.45), emu(1.25), emu(0.75), "Reward", COLORS["green"], COLORS["green"], True, 980, COLORS["white"], True),
        line_xml(298, emu(2.75), emu(1.72), emu(3.15), emu(1.72), COLORS["blue"]),
        line_xml(299, emu(5.25), emu(1.72), emu(5.9), emu(1.38), COLORS["blue"]),
        line_xml(300, emu(8.2), emu(1.38), emu(8.8), emu(1.38), COLORS["purple"]),
        line_xml(301, emu(10.7), emu(1.38), emu(11.2), emu(1.38), COLORS["green"]),
        line_xml(302, emu(5.25), emu(1.72), emu(5.9), emu(3.82), COLORS["blue"]),
        line_xml(303, emu(8.2), emu(3.82), emu(8.8), emu(3.82), COLORS["orange"]),
        line_xml(304, emu(10.7), emu(3.82), emu(11.2), emu(3.82), COLORS["green"]),
        line_xml(305, emu(11.82), emu(4.2), emu(7.1), emu(5.25), COLORS["green"]),
    ])

    slides.append(header("Ke hoach thuc nghiem tiep", "Ba buoc nho de chot vai tro GAN bang bang chung") + table(320, 0.75, 1.35, [
        ["Buoc", "Thuc nghiem", "Dau ra"],
        ["1", "Diversity/coverage GAN vs mutation", "Biet GAN co mo rong khong gian mau khong"],
        ["2", "Augmentation smoke test", "Recall/F1/FPR/robustness delta"],
        ["3", "Real-space vertical slice", "Rehydrate + WAF/libinjection + reward"],
    ], [1.0, 5.7, 5.1], 0.65) + [
        textbox_xml(340, emu(1.0), emu(5.25), emu(11.4), emu(0.55), "Neu augmentation khong thang, van co ket qua negative-methodology ro rang va co baseline.", 1320, COLORS["gray"], True, "ctr"),
    ])

    slides.append(header("Ket luan trinh bay voi thay", "Kien truc da ro; ket qua am duoc bien thanh quyet dinh ky thuat") + [
        shape_xml(350, emu(0.85), emu(1.45), emu(3.35), emu(1.0), "Em da lam ro\nkien truc theo gop y", COLORS["blue"], COLORS["blue"], True, 1350, COLORS["white"], True),
        shape_xml(351, emu(4.95), emu(1.45), emu(3.35), emu(1.0), "GAN generator\ndelex-space fail baseline", COLORS["red"], COLORS["red"], True, 1250, COLORS["white"], True),
        shape_xml(352, emu(9.05), emu(1.45), emu(3.35), emu(1.0), "Giu GAN trung tam\nbang doi vai", COLORS["green"], COLORS["green"], True, 1300, COLORS["white"], True),
        textbox_xml(353, emu(0.95), emu(3.25), emu(11.5), emu(0.9), "Huong tiep: GAN-as-Augmentation-Engine va GAN-as-Real-Space Policy co WAF reward that.", 1550, COLORS["black"], True, "ctr"),
        textbox_xml(354, emu(0.95), emu(4.85), emu(11.5), emu(0.75), "Claim can than: khong noi GAN da bypass tot hon; noi rang pipeline da co evaluator va baseline de quyet dinh vai tro GAN.", 1300, COLORS["gray"], True, "ctr"),
    ])

    cleaned_slides = (
        slides[:1]
        + [master_loop_parts()]
        + slides[1:6]
        + [zoom_h5_parts()]
        + slides[9:14]
        + [zoom_augmentation_parts()]
        + [zoom_policy_parts()]
        + slides[18:20]
    )

    return [slide_xml(s) for s in cleaned_slides]


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

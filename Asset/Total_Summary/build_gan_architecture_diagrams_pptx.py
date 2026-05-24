from __future__ import annotations

import zipfile
from pathlib import Path

from build_gan_sql_pptx_openxml import (
    LAYOUT_RELS,
    MASTER_RELS,
    ROOT_RELS,
    SLIDE_LAYOUT,
    SLIDE_MASTER,
    SLIDE_RELS,
    THEME,
    content_types,
    presentation_rels,
    presentation_xml,
    slide_xml,
)
from pptx_diagram_helpers import master_loop_parts, title_parts, zoom_augmentation_parts, zoom_h5_parts, zoom_policy_parts


OUT = Path(__file__).resolve().parent / "GAN_SQLi_Architecture_Diagrams_230526.pptx"


def build_slides() -> list[str]:
    slide_parts = [
        title_parts(),
        master_loop_parts(),
        zoom_h5_parts(),
        zoom_augmentation_parts(),
        zoom_policy_parts(),
    ]
    return [slide_xml(parts) for parts in slide_parts]


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

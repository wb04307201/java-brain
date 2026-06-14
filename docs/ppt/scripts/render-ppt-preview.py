#!/usr/bin/env python3
"""
render-ppt-preview.py — 把 javabrain.pptx 的每页渲染成 PNG,用于预览效果
仅本地校对用,aspose 免费版会带水印,不影响校对。
"""
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import aspose.slides as slides

PPTX = Path(__file__).resolve().parent.parent / "javabrain.pptx"
OUT_DIR = Path(__file__).resolve().parent.parent / "preview"

OUT_DIR.mkdir(exist_ok=True)

print(f"输入:{PPTX}")
print(f"输出:{OUT_DIR}")
print()

with slides.Presentation(str(PPTX)) as pres:
    print(f"幻灯片总数:{len(pres.slides)}")
    print(f"尺寸:{pres.slide_size.size.width}x{pres.slide_size.size.height} pt")
    print()
    for i, slide in enumerate(pres.slides, 1):
        # 1.0x 缩放(原始 1280x720 像素)
        img = slide.get_image(1.0, 1.0)
        out_path = OUT_DIR / f"page-{i:02d}.png"
        img.save(str(out_path))
        kb = out_path.stat().st_size / 1024
        print(f"[{i:2d}/10] {out_path.name}  {kb:.1f} KB")

print(f"\n✅ 10 张预览图已写入 {OUT_DIR}")

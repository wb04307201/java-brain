#!/usr/bin/env python3
"""
grid-preview.py — 把 10 张预览拼成 2 列 5 行大图,整体看风格
"""
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from PIL import Image, ImageDraw, ImageFont

PREVIEW_DIR = Path(__file__).resolve().parent.parent / "preview"
OUT = Path(__file__).resolve().parent.parent / "preview" / "_grid.png"

# 加载 10 张
imgs = [Image.open(PREVIEW_DIR / f"page-{i:02d}.png") for i in range(1, 11)]
w, h = imgs[0].size
print(f"单页尺寸: {w}x{h}")

# 网格: 2 列 × 5 行
cols, rows = 2, 5
gap = 20
label_h = 40
W = cols * w + (cols + 1) * gap
H = rows * (h + label_h) + (rows + 1) * gap

canvas = Image.new("RGB", (W, H), (32, 32, 32))
draw = ImageDraw.Draw(canvas)

# 字体
try:
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 24)
except Exception:
    font = ImageFont.load_default()

for i, im in enumerate(imgs):
    col = i % cols
    row = i // cols
    x = gap + col * (w + gap)
    y = gap + row * (h + label_h + gap)
    # 标签
    draw.text((x, y), f"P{i+1}", fill="white", font=font)
    # 图片
    canvas.paste(im, (x, y + label_h))

canvas.save(str(OUT))
print(f"网格图: {OUT}  ({OUT.stat().st_size/1024:.1f} KB)  {W}x{H}")

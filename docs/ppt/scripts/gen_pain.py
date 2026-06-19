#!/usr/bin/env python3
"""生成 P2 痛点图（4 道坎，2×2 网格）。"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# 颜色
BG_DEEP = (10, 14, 26)
BG_PANEL = (16, 23, 42)
DANGER = (255, 77, 109)
TEXT_PRIMARY = (228, 231, 241)
TEXT_SECONDARY = (124, 138, 168)
SUCCESS = (0, 255, 156)

W, H = 1280, 720


def load_font(size):
    for fp in ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]:
        try:
            return ImageFont.truetype(fp, size)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_pain():
    img = Image.new("RGB", (W, H), BG_DEEP)
    draw = ImageDraw.Draw(img)

    font_title = load_font(32)
    font_num = load_font(64)
    font_label = load_font(20)
    font_sub = load_font(16)
    font_arrow = load_font(24)

    # 标题
    title = "企业 AI 落地的 4 道坎"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    draw.text(((W - bbox[2]) / 2, 50), title, fill=TEXT_PRIMARY, font=font_title)

    # 4 个痛点 (2×2 网格)
    pains = [
        ("3 个月", "接入 AI 平均周期", "自己造"),
        ("5 天", "业务取数平均周期", "等开发写 SQL"),
        ("3 天", "CRUD 页面平均工时", "前端 + 后端 + 联调"),
        ("还要装 CLI", "才能用 AI", "0 业务人员能独立操作"),
    ]

    positions = [
        (80, 180),   # 左上
        (700, 180),  # 右上
        (80, 430),   # 左下
        (700, 430),  # 右下
    ]

    for idx, (num, label, sub) in enumerate(pains):
        x, y = positions[idx]
        # 背景卡片
        draw.rounded_rectangle([x, y, x + 520, y + 220], radius=12, fill=BG_PANEL)
        # 大数字
        draw.text((x + 200, y + 30), num, fill=DANGER, font=font_num)
        # 标签
        bbox = draw.textbbox((0, 0), label, font=font_label)
        draw.text((x + (520 - bbox[2]) / 2, y + 140), label, fill=TEXT_PRIMARY, font=font_label)
        # 副标签
        bbox = draw.textbbox((0, 0), sub, font=font_sub)
        draw.text((x + (520 - bbox[2]) / 2, y + 180), sub, fill=TEXT_SECONDARY, font=font_sub)

    # 底部反衬行（JavaBrain → ...）
    y_bottom = 660
    arrows = [
        ("JavaBrain →", SUCCESS),
        ("3 分钟启动", SUCCESS),
        ("90 秒出报告", SUCCESS),
        ("10 分钟出页面", SUCCESS),
        ("浏览器打开即用", SUCCESS),
    ]
    x_pos = 60
    for text, color in arrows:
        draw.text((x_pos, y_bottom), text, fill=color, font=font_arrow)
        x_pos += 240

    output = Path("images/page-02-pain.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output))
    print(f"[OK] 已保存：{output}")


if __name__ == "__main__":
    draw_pain()

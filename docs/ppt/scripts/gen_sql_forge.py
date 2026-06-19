#!/usr/bin/env python3
"""生成 P5 SQL 工坊架构图（Calcite 跨库联邦查询）。"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# 颜色
BG_DEEP = (10, 14, 26)
BG_PANEL = (16, 23, 42)
PRIMARY = (0, 217, 255)
ACCENT = (167, 139, 250)
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


def draw_sql_forge():
    img = Image.new("RGB", (W, H), BG_DEEP)
    draw = ImageDraw.Draw(img)

    font_title = load_font(28)
    font_center = load_font(22)
    font_db = load_font(20)
    font_label = load_font(16)

    # 标题
    title = "SQL 工坊 · Calcite 跨库联邦查询"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    draw.text(((W - bbox[2]) / 2, 50), title, fill=TEXT_PRIMARY, font=font_title)

    # 中央 SQL 查询图标（用圆角矩形 + 文字代替）
    cx, cy = W / 2 - 100, 280
    draw.rounded_rectangle([cx, cy, cx + 200, cy + 100], radius=16, fill=BG_PANEL, outline=PRIMARY, width=3)
    draw.text((cx + 40, cy + 30), "SQL 查询", fill=PRIMARY, font=font_center)

    # 3 个数据库（MySQL, PostgreSQL, H2）
    dbs = [
        ("MySQL", 200, 480),
        ("PostgreSQL", 540, 480),
        ("H2", 920, 480),
    ]

    for name, x, y in dbs:
        draw.rounded_rectangle([x, y, x + 180, y + 80], radius=12, fill=BG_PANEL, outline=ACCENT, width=2)
        bbox = draw.textbbox((0, 0), name, font=font_db)
        draw.text((x + (180 - bbox[2]) / 2, y + 25), name, fill=ACCENT, font=font_db)

        # 连线（从数据库到中央）
        draw.line([(x + 90, y), (cx + 100, cy + 100)], fill=ACCENT, width=2)

    # JOIN 结果（底部）
    join_x, join_y = W / 2 - 120, 600
    draw.rounded_rectangle([join_x, join_y, join_x + 240, join_y + 60], radius=12, fill=BG_PANEL, outline=SUCCESS, width=3)
    bbox = draw.textbbox((0, 0), "JOIN 结果", font=font_center)
    draw.text((join_x + (240 - bbox[2]) / 2, join_y + 15), "JOIN 结果", fill=SUCCESS, font=font_center)

    # 从 3 个数据库到 JOIN 结果的连线
    for name, x, y in dbs:
        draw.line([(x + 90, y + 80), (join_x + 120, join_y)], fill=SUCCESS, width=2)

    # 顶部说明
    desc = "一条 SQL 跨 MySQL + PostgreSQL + H2 跨库 JOIN，无需 ETL"
    bbox = draw.textbbox((0, 0), desc, font=font_label)
    draw.text(((W - bbox[2]) / 2, 130), desc, fill=TEXT_SECONDARY, font=font_label)

    output = Path("images/page-05-sql-forge.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output))
    print(f"[OK] 已保存：{output}")


if __name__ == "__main__":
    draw_sql_forge()

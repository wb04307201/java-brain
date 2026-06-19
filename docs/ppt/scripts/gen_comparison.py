#!/usr/bin/env python3
"""生成 P8 对比图（精确控制文字内容）。

使用 PIL 直接绘制，确保 6 个维度、3 列对比色、底部金句完全符合 OUTLINE。
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


# 颜色定义（与 tools.py 一致）
BG_DEEP = (10, 14, 26)          # 深色背景
BG_PANEL = (16, 23, 42)         # 次级面板
GRID_LINE = (26, 34, 56)        # 网格线
TEXT_PRIMARY = (228, 231, 241)  # 主文字
TEXT_SECONDARY = (124, 138, 168) # 次级文字
DANGER = (255, 77, 109)         # 警示红（ChatGPT 列）
SUCCESS = (0, 255, 156)         # 成功绿（JavaBrain 列）
GRAY = (120, 120, 120)          # 灰色（低代码列）
WARN = (250, 204, 21)           # 警示金

# 尺寸
W, H = 1280, 720
COL_W = 380
COL_H = 480
COL_X = [80, 450, 820]
COL_Y = 180

# 6 个维度 + 3 列数据
DIMENSIONS = [
    "业务取数",
    "CRUD 页面",
    "跨库 JOIN",
    "LLM 可控性",
    "工具/技能管控",
    "列名识别",
]

DATA = {
    "低代码": {
        "color": GRAY,
        "values": [
            ("✓", "模板查询"),
            ("✗", "不懂业务"),
            ("✗", ""),
            ("n/a", ""),
            ("✗", "各自为战"),
            ("n/a", ""),
        ],
    },
    "ChatGPT+插件": {
        "color": DANGER,
        "values": [
            ("✓", "但数据外发"),
            ("", "需配合代码"),
            ("✗", ""),
            ("", "锁定 OpenAI"),
            ("✗", "插件野生无审核"),
            ("✗", "经常错"),
        ],
    },
    "JavaBrain": {
        "color": SUCCESS,
        "values": [
            ("✓", "90 秒出报告"),
            ("✓", "AI 语义推断"),
            ("✓", "Calcite 联邦"),
            ("✓", "任意供应商，可换本地模型"),
            ("✓", "MCP/Skill 审核评估后上线"),
            ("✓", "强制读 DDL"),
        ],
    },
}

# 底部金句
BOTTOM_TEXT = "低代码不懂业务，ChatGPT 锁定供应商——JavaBrain 六个维度全领先。"


def load_font(size):
    """加载中文字体。"""
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",       # Microsoft YaHei
        "C:/Windows/Fonts/simhei.ttf",     # SimHei
        "C:/Windows/Fonts/msyhbd.ttc",     # Microsoft YaHei Bold
    ]
    for fp in font_paths:
        try:
            return ImageFont.truetype(fp, size)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_comparison():
    """绘制对比图。"""
    img = Image.new("RGB", (W, H), BG_DEEP)
    draw = ImageDraw.Draw(img)

    # 加载字体
    font_title = load_font(28)
    font_header = load_font(22)
    font_dim = load_font(16)
    font_value = load_font(14)
    font_bottom = load_font(18)

    # 标题
    title = "三大开发范式能力对比分析"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = bbox[2] - bbox[0]
    draw.text(((W - title_w) / 2, 60), title, fill=TEXT_PRIMARY, font=font_title)

    # 副标题（6 个维度说明）
    subtitle = "业务取数 · CRUD 页面 · 跨库 JOIN · LLM 可控性 · 工具管控 · 列名识别"
    bbox = draw.textbbox((0, 0), subtitle, font=font_dim)
    sub_w = bbox[2] - bbox[0]
    draw.text(((W - sub_w) / 2, 110), subtitle, fill=TEXT_SECONDARY, font=font_dim)

    # 绘制 3 列
    for col_idx, (col_name, col_data) in enumerate(DATA.items()):
        x = COL_X[col_idx]
        color = col_data["color"]

        # 列标题背景
        header_bg = (color[0] // 3, color[1] // 3, color[2] // 3)
        draw.rounded_rectangle(
            [x, COL_Y, x + COL_W, COL_Y + 40],
            radius=8,
            fill=header_bg,
        )

        # 列标题文字
        bbox = draw.textbbox((0, 0), col_name, font=font_header)
        text_w = bbox[2] - bbox[0]
        draw.text(
            (x + (COL_W - text_w) / 2, COL_Y + 8),
            col_name,
            fill=color,
            font=font_header,
        )

        # 6 行数据
        for row_idx, dim in enumerate(DIMENSIONS):
            y = COL_Y + 60 + row_idx * 70
            symbol, detail = col_data["values"][row_idx]

            # 维度名（左对齐）
            draw.text((x + 15, y), dim, fill=TEXT_SECONDARY, font=font_dim)

            # 符号 + 详情（右对齐）
            if symbol:
                symbol_color = SUCCESS if symbol == "✓" else (DANGER if symbol == "✗" else TEXT_SECONDARY)
                draw.text((x + COL_W - 120, y), symbol, fill=symbol_color, font=font_header)
            if detail:
                bbox = draw.textbbox((0, 0), detail, font=font_value)
                detail_w = bbox[2] - bbox[0]
                draw.text(
                    (x + COL_W - 120 - detail_w - 10, y + 28),
                    detail,
                    fill=TEXT_PRIMARY,
                    font=font_value,
                )

    # 底部金句
    bbox = draw.textbbox((0, 0), BOTTOM_TEXT, font=font_bottom)
    bottom_w = bbox[2] - bbox[0]
    draw.text(
        ((W - bottom_w) / 2, H - 80),
        BOTTOM_TEXT,
        fill=SUCCESS,
        font=font_bottom,
    )

    # 保存
    output = Path("images/page-08-comparison.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output))
    print(f"[OK] 已保存：{output}")

    return output


if __name__ == "__main__":
    draw_comparison()

#!/usr/bin/env python3
"""生成 P9 路线图（2 个独立仓库 + 1 个 MCP 模块 + 时间线）。"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# 颜色
BG_DEEP = (10, 14, 26)
BG_PANEL = (16, 23, 42)
PRIMARY = (0, 217, 255)
ACCENT = (167, 139, 250)
SUCCESS = (0, 255, 156)
TEXT_PRIMARY = (228, 231, 241)
TEXT_SECONDARY = (124, 138, 168)
GRID_LINE = (26, 34, 56)

W, H = 1280, 720


def load_font(size):
    for fp in ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]:
        try:
            return ImageFont.truetype(fp, size)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_roadmap():
    img = Image.new("RGB", (W, H), BG_DEEP)
    draw = ImageDraw.Draw(img)

    font_title = load_font(28)
    font_repo = load_font(20)
    font_sub = load_font(14)
    font_timeline = load_font(18)
    font_value = load_font(16)

    # 标题
    title = "灵梭平台 · 开源项目路线图"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    draw.text(((W - bbox[2]) / 2, 50), title, fill=TEXT_PRIMARY, font=font_title)

    # 副标题
    subtitle = "SQL 工坊系列 · 核心组件演进全景"
    bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
    draw.text(((W - bbox[2]) / 2, 95), subtitle, fill=TEXT_SECONDARY, font=font_sub)

    # 3 个仓库卡片
    repos = [
        ("灵梭", "spring-ai-loom-agent", "13 个 Maven 模块", "只做 AI 编排"),
        ("SQL 工坊", "sql-forge", "14 个 Maven 模块", "只做数据管理"),
        ("SQL 工坊 MCP", "sql-forge（同仓库）", "MCP 工具模块", "只做 AI ↔ DB"),
    ]

    card_w, card_h = 340, 160
    card_y = 160
    card_x = [80, 470, 860]

    for idx, (name, repo, modules, desc) in enumerate(repos):
        x = card_x[idx]
        # 卡片背景
        draw.rounded_rectangle([x, card_y, x + card_w, card_y + card_h], radius=12,
                                fill=BG_PANEL, outline=PRIMARY, width=2)
        # 组件名
        draw.text((x + 20, card_y + 15), name, fill=PRIMARY, font=font_repo)
        # 仓库名
        draw.text((x + 20, card_y + 55), repo, fill=TEXT_SECONDARY, font=font_sub)
        # 模块数
        draw.text((x + 20, card_y + 90), modules, fill=TEXT_SECONDARY, font=font_sub)
        # 描述
        draw.text((x + 20, card_y + 125), desc, fill=TEXT_SECONDARY, font=font_sub)

    # 连接线（从卡片到时间线）
    line_y = card_y + card_h + 40
    for x in [card_x[i] + card_w / 2 for i in range(3)]:
        draw.line([(x, card_y + card_h), (x, line_y)], fill=GRID_LINE, width=2)

    # 时间线
    draw.line([(60, line_y), (W - 60, line_y)], fill=PRIMARY, width=3)

    # 4 个版本节点
    versions = [
        ("V1.0", "当前", "基础 CRUD\n+ NL2SQL\n+ HTML 报告", "开箱即用"),
        ("V1.1", "2026 Q4", "多租户\n字段级权限\n灵梭 SSO 集成", "企业级权限管控"),
        ("V1.2", "2027 Q1", "移动端 Amis\n（PWA）", "随时随地用"),
        ("V1.3", "2027 Q2", "工作流引擎\n审批/通知", "完整业务流程"),
    ]

    node_x = [160, 440, 720, 1000]

    for idx, (ver, date, features, value) in enumerate(versions):
        x = node_x[idx]
        # 节点圆点
        draw.ellipse([x - 15, line_y - 15, x + 15, line_y + 15], fill=SUCCESS)
        # 版本号
        bbox = draw.textbbox((0, 0), ver, font=font_timeline)
        draw.text((x - bbox[2] / 2, line_y + 25), ver, fill=SUCCESS, font=font_timeline)
        # 日期
        bbox = draw.textbbox((0, 0), date, font=font_sub)
        draw.text((x - bbox[2] / 2, line_y + 55), date, fill=TEXT_SECONDARY, font=font_sub)
        # 功能（多行）
        y_feat = line_y + 90
        for feat in features.split("\n"):
            bbox = draw.textbbox((0, 0), feat, font=font_sub)
            draw.text((x - bbox[2] / 2, y_feat), feat, fill=TEXT_PRIMARY, font=font_sub)
            y_feat += 22
        # 价值描述
        bbox = draw.textbbox((0, 0), value, font=font_value)
        draw.text((x - bbox[2] / 2, line_y + 170), value, fill=SUCCESS, font=font_value)

    output = Path("images/page-09-roadmap.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output))
    print(f"[OK] 已保存：{output}")


if __name__ == "__main__":
    draw_roadmap()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重生成 3 张内容页插图(更科技感/更华丽)。

- p3_dependency.png   (1200x600) 依赖关系图:3D 球 + 等距网格 + 径向辉光 + 粒子连线
- p4a-ai-orchestrate.png (800x800) 灵梭演进时间轴:4 阶段 v1.0→v2.0 横向时间轴
- p5a-calcite-federation.png (800x800) SQL工坊联邦图:中心 SQL 工坊 + 4 业务系统环绕
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Force UTF-8 stdout
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

IMG_DIR = Path(__file__).resolve().parent.parent / "images" / "ai"
IMG_DIR.mkdir(parents=True, exist_ok=True)

# 配色(spec §4.1)
JAVA_BLUE = (0x00, 0x73, 0x96)
JAVA_BLUE_LIGHT = (0xE0, 0xF2, 0xFE)
JAVA_BLUE_DARK = (0x00, 0x52, 0x6E)
AI_PURPLE = (0x6B, 0x46, 0xC1)
AI_PURPLE_LIGHT = (0xED, 0xE9, 0xFE)
AI_PURPLE_DARK = (0x4C, 0x32, 0x8B)
SEMANTIC_RED = (0xDC, 0x26, 0x26)
SEMANTIC_GREEN = (0x10, 0xB9, 0x81)
SEMANTIC_GREEN_LIGHT = (0xD1, 0xFA, 0xE5)
GOLD = (0xF5, 0x9E, 0x0B)
GOLD_LIGHT = (0xFE, 0xF3, 0xC7)
TEXT_PRIMARY = (0x1F, 0x29, 0x37)
TEXT_SECONDARY = (0x6B, 0x72, 0x80)
DIVIDER = (0xE5, 0xE7, 0xEB)
WHITE = (0xFF, 0xFF, 0xFF)
BG_LIGHT = (0xFA, 0xFB, 0xFC)

# 字体(Windows 系统字体)
FONT_CN_PATH = r"C:\Windows\Fonts\msyh.ttc"
FONT_EN_PATH = r"C:\Windows\Fonts\consola.ttf"


def get_font(size: int, *, mono: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_EN_PATH if mono else FONT_CN_PATH
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


# ============ 通用工具 ============
def iso_ball(img: Image.Image, cx: int, cy: int, r: int, color: tuple,
             *, shadow: bool = True, highlight: bool = True):
    """画一个 2.5D 球(径向渐变 + 顶部高光 + 底部投影)。

    直接修改 img;返回 None。
    """
    if shadow:
        # 投影(下方偏移椭圆)
        sh_y = cy + int(r * 0.85)
        sh_w = int(r * 2.0)
        sh_h = int(r * 0.35)
        sh_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sh_d = ImageDraw.Draw(sh_layer)
        sh_d.ellipse(
            [cx - sh_w // 2, sh_y - sh_h // 2, cx + sh_w // 2, sh_y + sh_h // 2],
            fill=(0, 0, 0, 50),
        )
        sh_layer = sh_layer.filter(ImageFilter.GaussianBlur(8))
        img.alpha_composite(sh_layer)

    # 球主体(径向渐变:中心浅→边缘深)
    ball_layer = Image.new("RGBA", (r * 2 + 4, r * 2 + 4), (0, 0, 0, 0))
    bd = ImageDraw.Draw(ball_layer)
    for i in range(r, 0, -1):
        # 中心颜色(浅)→ 边缘颜色(深)
        ratio = (r - i) / r  # 0=中心 1=边缘
        r_c = int(color[0] + (color[0] * 0.5 - color[0]) * ratio)
        g_c = int(color[1] + (color[1] * 0.5 - color[1]) * ratio)
        b_c = int(color[2] + (color[2] * 0.5 - color[2]) * ratio)
        r_c = max(0, min(255, r_c))
        g_c = max(0, min(255, g_c))
        b_c = max(0, min(255, b_c))
        bd.ellipse([i, i, 2 * r + 2 - i, 2 * r + 2 - i],
                   fill=(r_c, g_c, b_c, 255))
    if highlight:
        # 顶部高光(小白椭圆)
        hl_w = int(r * 0.5)
        hl_h = int(r * 0.25)
        hl_x = cx - hl_w // 2
        hl_y = cy - r + int(r * 0.15)
        hl_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        hld = ImageDraw.Draw(hl_layer)
        hld.ellipse([hl_x, hl_y, hl_x + hl_w, hl_y + hl_h],
                    fill=(255, 255, 255, 180))
        hl_layer = hl_layer.filter(ImageFilter.GaussianBlur(3))
        img.alpha_composite(hl_layer)

    img.alpha_composite(ball_layer, dest=(cx - r, cy - r))


def iso_rect(img: Image.Image, x: int, y: int, w: int, h: int, color: tuple,
             *, depth: int = 8, rounded: int = 12, highlight: bool = True):
    """画一个 2.5D 圆角矩形(主面 + 右侧深度面 + 顶部高光条)。"""
    # 深度面(右下偏移)
    depth_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(depth_layer)
    dd.rounded_rectangle(
        [x + depth, y + depth, x + w + depth, y + h + depth],
        radius=rounded,
        fill=(max(0, color[0] - 60), max(0, color[1] - 60), max(0, color[2] - 60), 255),
    )
    img.alpha_composite(depth_layer)

    # 主面
    main = Image.new("RGBA", img.size, (0, 0, 0, 0))
    md = ImageDraw.Draw(main)
    md.rounded_rectangle(
        [x, y, x + w, y + h],
        radius=rounded,
        fill=color,
    )
    img.alpha_composite(main)

    if highlight:
        # 顶部高光条
        hl = Image.new("RGBA", img.size, (0, 0, 0, 0))
        hd = ImageDraw.Draw(hl)
        hd.rounded_rectangle(
            [x + 4, y + 3, x + w - 4, y + int(h * 0.18)],
            radius=max(1, rounded // 2),
            fill=(255, 255, 255, 80),
        )
        hl = hl.filter(ImageFilter.GaussianBlur(2))
        img.alpha_composite(hl)


def draw_grid(img: Image.Image, w: int, h: int, *, step: int = 40,
              color: tuple = (0x00, 0x73, 0x96), alpha: int = 25):
    """画等距点阵网格(科技感背景)。"""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(0, h, step):
        for x in range(0, w, step):
            d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(*color, alpha))
    img.alpha_composite(layer)


def draw_radial_glow(img: Image.Image, cx: int, cy: int, r: int,
                     color: tuple, *, max_alpha: int = 80):
    """画径向辉光(从中心淡出)。"""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(r, 0, -5):
        a = int(max_alpha * (i / r) ** 2)
        d.ellipse([cx - i, cy - i, cx + i, cy + i], fill=(*color, a))
    layer = layer.filter(ImageFilter.GaussianBlur(15))
    img.alpha_composite(layer)


def draw_bezier_line(draw: ImageDraw.ImageDraw, start: tuple, end: tuple,
                     color: tuple, *, width: int = 4, max_alpha: int = 200,
                     particles: bool = True):
    """画一条贝塞尔曲线 + 沿线粒子点(中心粗末端细,渐变透明)。"""
    sx, sy = start
    ex, ey = end
    # 贝塞尔控制点(让曲线有点弯曲)
    cx_ctrl = (sx + ex) // 2 + (ey - sy) // 6
    cy_ctrl = (sy + ey) // 2 - (ex - sx) // 6
    # 取若干点
    steps = 50
    points = []
    for t_i in range(steps + 1):
        t = t_i / steps
        # 二次贝塞尔
        x = (1 - t) ** 2 * sx + 2 * (1 - t) * t * cx_ctrl + t ** 2 * ex
        y = (1 - t) ** 2 * sy + 2 * (1 - t) * t * cy_ctrl + t ** 2 * ey
        points.append((x, y))
    # 画线段(宽度从粗到细)
    for j in range(len(points) - 1):
        t_j = j / (len(points) - 1)
        w_j = max(1, int(width * (1 - 0.4 * t_j)))
        a_j = int(max_alpha * (1 - 0.3 * t_j))
        draw.line([points[j], points[j + 1]],
                  fill=(*color, a_j), width=w_j)
    if particles:
        # 沿线 3-4 个粒子
        for k, ratio in enumerate([0.25, 0.5, 0.75]):
            idx = int(ratio * (len(points) - 1))
            px, py = points[idx]
            pr = 4 - k  # 4, 3, 2
            draw.ellipse([px - pr, py - pr, px + pr, py + pr],
                         fill=(*color, 220))
            draw.ellipse([px - pr - 2, py - pr - 2, px + pr + 2, py + pr + 2],
                         outline=(*color, 80), width=1)


def draw_text_with_shadow(d: ImageDraw.ImageDraw, xy: tuple, text: str,
                          font, *, fill, shadow_color=(0xFF, 0xFF, 0xFF, 60)):
    """画文字(带白色阴影,在浅底上更清晰)。"""
    x, y = xy
    # 阴影
    d.text((x + 1, y + 1), text, font=font, fill=shadow_color)
    # 主文字
    d.text(xy, text, font=font, fill=fill)


# ============ P3 依赖关系图(1200x600)科技感升级 ============
def gen_p3_dependency():
    W, H = 1200, 600
    img = Image.new("RGBA", (W, H), (*BG_LIGHT, 255))
    d = ImageDraw.Draw(img)

    # 1) 等距网格点阵
    draw_grid(img, W, H, step=30, color=JAVA_BLUE, alpha=30)

    # 2) 中心径向辉光(浅紫,突出中心)
    draw_radial_glow(img, W // 2, H // 2, 280, AI_PURPLE, max_alpha=50)

    # 3) 节点定义(3 核心 + 6 周边)
    cores = [
        (W // 2, 200, "灵梭", JAVA_BLUE, "AI"),       # 上
        (W // 2 - 180, H // 2 + 30, "SQL工坊", AI_PURPLE, "DB"),  # 左下
        (W // 2 + 180, H // 2 + 30, "SQL工坊 MCP", SEMANTIC_GREEN, "MCP"),  # 右下
    ]
    perms = [
        (W // 2 - 380, 120, "H2", "H2"),
        (W // 2 + 380, 120, "Flyway", "FW"),
        (W // 2 - 480, H // 2 + 30, "MyBatis", "MB"),
        (W // 2 + 480, H // 2 + 30, "Calcite", "CT"),
        (W // 2 - 380, H - 120, "Amis", "AM"),
        (W // 2 + 380, H - 120, "Qwen", "QW"),
    ]

    # 4) 画连线(贝塞尔曲线 + 粒子)— 核心→周边
    for cx, cy, _, _, _ in cores:
        for px, py, _, _ in perms:
            draw_bezier_line(d, (cx, cy), (px, py), JAVA_BLUE,
                             width=3, max_alpha=120, particles=True)

    # 5) 画周边 6 节点(灰球 + 文字标签)
    for px, py, name, tag in perms:
        iso_ball(img, px, py, 35, TEXT_SECONDARY,
                 shadow=True, highlight=True)
        # 标签(节点下方)
        font_tag = get_font(14, mono=True)
        bbox = d.textbbox((0, 0), tag, font=font_tag)
        tw = bbox[2] - bbox[0]
        d.text((px - tw // 2, py - 8), tag, font=font_tag,
               fill=(*WHITE, 255))

    # 6) 画核心 3 节点(彩色 3D 球 + 大标签)
    for cx, cy, name, color, tag in cores:
        iso_ball(img, cx, cy, 60, color, shadow=True, highlight=True)
        # 球内 tag
        font_tag = get_font(22, mono=True)
        bbox = d.textbbox((0, 0), tag, font=font_tag)
        tw = bbox[2] - bbox[0]
        d.text((cx - tw // 2, cy - 14), tag, font=font_tag,
               fill=(*WHITE, 255))
        # 球下方中文标签(白底圆角矩形 + 深色字)
        font_name = get_font(20)
        bbox2 = d.textbbox((0, 0), name, font=font_name)
        nw = bbox2[2] - bbox2[0] + 24
        nh = 36
        # 背景框
        d.rounded_rectangle(
            [cx - nw // 2, cy + 75, cx + nw // 2, cy + 75 + nh],
            radius=8, fill=(*color, 255),
        )
        # 文字
        d.text((cx - (bbox2[2] - bbox2[0]) // 2 - bbox2[0],
                cy + 75 + (nh - (bbox2[3] - bbox2[1])) // 2 - bbox2[1]),
               name, font=font_name, fill=(*WHITE, 255))

    img.convert("RGB").save(IMG_DIR / "p3_dependency.png", "PNG", optimize=True)
    print(f"[OK] p3_dependency.png  {W}x{H}")


# ============ P4-a 演进时间轴(800x800) ============
def gen_p4a_timeline():
    W, H = 800, 800
    img = Image.new("RGBA", (W, H), (*BG_LIGHT, 255))
    d = ImageDraw.Draw(img)

    # 1) 等距网格
    draw_grid(img, W, H, step=32, color=JAVA_BLUE, alpha=25)

    # 2) 4 阶段横向时间轴(y=400 居中)
    axis_y = 400
    stages = [
        # x, color, version, name, desc, file_label
        (140,  TEXT_SECONDARY, "v1.0", "裸用",  "20 行 YAML 配置",  ".yml"),
        (320,  JAVA_BLUE,      "v1.2", "+ MCP", "+8 工具接入",      ".st"),
        (500,  AI_PURPLE,      "v1.5", "+ Skill", "模板即提示词",    ".st"),
        (680,  GOLD,           "v2.0", "杀手锏",  "50行 → 1行",      ".st"),
    ]

    # 3) 主时间轴线(灰→蓝→紫→金 渐变 — 用 4 段拼接)
    for i in range(3):
        x1 = stages[i][0] + 25
        x2 = stages[i + 1][0] - 25
        # 渐变线段(画 N 条像素,每条颜色稍微变化)
        segs = max(1, x2 - x1)
        for k in range(segs):
            ratio = k / segs
            r = int(stages[i][1][0] + (stages[i + 1][1][0] - stages[i][1][0]) * ratio)
            g = int(stages[i][1][1] + (stages[i + 1][1][1] - stages[i][1][1]) * ratio)
            b = int(stages[i][1][2] + (stages[i + 1][1][2] - stages[i][1][2]) * ratio)
            d.rectangle([x1 + k, axis_y - 2, x1 + k + 1, axis_y + 2],
                        fill=(r, g, b, 220))

    # 4) 4 个阶段节点(2.5D 球 + 版本号 + 名称 + 描述 + 文件标签)
    for x, color, ver, name, desc, file_lbl in stages:
        # 球
        iso_ball(img, x, axis_y, 25, color, shadow=True, highlight=True)
        # 版本号(球上方)
        font_ver = get_font(18, mono=True)
        bbox = d.textbbox((0, 0), ver, font=font_ver)
        tw = bbox[2] - bbox[0]
        d.text((x - tw // 2 - bbox[0], axis_y - 75 - bbox[1]), ver,
               font=font_ver, fill=(*color, 255))
        # 阶段名(球上方)
        font_name = get_font(20)
        bbox2 = d.textbbox((0, 0), name, font=font_name)
        nw = bbox2[2] - bbox2[0]
        d.text((x - nw // 2 - bbox2[0], axis_y - 50 - bbox2[1]), name,
               font=font_name, fill=(*color, 255))
        # 描述(球下方)
        font_desc = get_font(14)
        bbox3 = d.textbbox((0, 0), desc, font=font_desc)
        dw = bbox3[2] - bbox3[0]
        d.text((x - dw // 2 - bbox3[0], axis_y + 40 - bbox3[1]), desc,
               font=font_desc, fill=(*TEXT_PRIMARY, 255))
        # 文件标签(.yml / .st)— 圆角小标签
        font_file = get_font(12, mono=True)
        bbox4 = d.textbbox((0, 0), file_lbl, font=font_file)
        fw = bbox4[2] - bbox4[0] + 16
        fh = 22
        d.rounded_rectangle(
            [x - fw // 2, axis_y + 75, x + fw // 2, axis_y + 75 + fh],
            radius=4, fill=(*color, 30),
            outline=(*color, 200), width=1,
        )
        d.text((x - (bbox4[2] - bbox4[0]) // 2 - bbox4[0],
                axis_y + 75 + (fh - (bbox4[3] - bbox4[1])) // 2 - bbox4[1]),
               file_lbl, font=font_file, fill=(*color, 255))

    # 5) 底部"演进"标签(箭头)
    font_arrow = get_font(28)
    d.text((W // 2 - 30, 100), "演进方向 →", font=font_arrow,
           fill=(*TEXT_SECONDARY, 180))

    # 6) 顶部主标"灵梭 4 阶段演进"(在轴上方)
    font_title = get_font(22)
    title = "灵梭 · 4 阶段演进"
    bbox = d.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    d.text((W // 2 - tw // 2 - bbox[0], 30 - bbox[1]), title,
           font=font_title, fill=(*TEXT_PRIMARY, 255))

    img.convert("RGB").save(IMG_DIR / "p4a-ai-orchestrate.png", "PNG", optimize=True)
    print(f"[OK] p4a-ai-orchestrate.png  {W}x{H}")


# ============ P5-a SQL工坊联邦:中心 + 4 业务系统环绕(800x800) ============
def gen_p5a_federation():
    W, H = 800, 800
    img = Image.new("RGBA", (W, H), (*BG_LIGHT, 255))
    d = ImageDraw.Draw(img)

    # 1) 等距网格
    draw_grid(img, W, H, step=32, color=AI_PURPLE, alpha=25)

    # 2) 中心径向辉光(Java 蓝 — SQL工坊 主色)
    draw_radial_glow(img, W // 2, H // 2 + 20, 220, JAVA_BLUE, max_alpha=70)

    # 3) 4 个业务系统(4 个角)— 灰蓝色小方块
    cx_center = W // 2
    cy_center = H // 2 + 20
    systems = [
        # x, y, name, color
        (cx_center - 240, cy_center - 200, "财务系统", TEXT_SECONDARY),
        (cx_center + 240, cy_center - 200, "CRM",      TEXT_SECONDARY),
        (cx_center - 240, cy_center + 200, "ERP",      TEXT_SECONDARY),
        (cx_center + 240, cy_center + 200, "OA/HR",    TEXT_SECONDARY),
    ]
    # 4 个业务系统 — 2.5D 方块
    for sx, sy, name, color in systems:
        iso_rect(img, sx - 60, sy - 30, 120, 60, (*color, 255),
                 depth=6, rounded=8, highlight=True)
        # 名称
        font_name = get_font(18)
        bbox = d.textbbox((0, 0), name, font=font_name)
        nw = bbox[2] - bbox[0]
        d.text((sx - nw // 2 - bbox[0], sy - (bbox[3] - bbox[1]) // 2 - bbox[1]),
               name, font=font_name, fill=(*WHITE, 255))

    # 4) 中央 SQL 工坊 — 大方块(Java 蓝)
    cw, ch = 220, 130
    iso_rect(img, cx_center - cw // 2, cy_center - ch // 2, cw, ch,
             (*JAVA_BLUE, 255), depth=10, rounded=12, highlight=True)
    # "SQL 工坊" 大字
    font_main = get_font(28)
    main_text = "SQL 工坊"
    bbox = d.textbbox((0, 0), main_text, font=font_main)
    mw = bbox[2] - bbox[0]
    d.text((cx_center - mw // 2 - bbox[0],
            cy_center - 22 - (bbox[3] - bbox[1]) // 2 - bbox[1]),
           main_text, font=font_main, fill=(*WHITE, 255))
    # 副标"统一数据出口"
    font_sub = get_font(14)
    sub_text = "统一数据出口"
    bbox2 = d.textbbox((0, 0), sub_text, font=font_sub)
    sw_ = bbox2[2] - bbox2[0]
    d.text((cx_center - sw_ // 2 - bbox2[0],
            cy_center + 18 - (bbox2[3] - bbox2[1]) // 2 - bbox2[1]),
           sub_text, font=font_sub, fill=(*WHITE, 240))

    # 5) 4 条双向渐变粗细箭头(业务系统 → 中心)
    for sx, sy, _, _ in systems:
        draw_bezier_line(d, (sx, sy), (cx_center, cy_center),
                         JAVA_BLUE, width=6, max_alpha=200, particles=False)

    img.convert("RGB").save(IMG_DIR / "p5a-calcite-federation.png", "PNG", optimize=True)
    print(f"[OK] p5a-calcite-federation.png  {W}x{H}")


if __name__ == "__main__":
    gen_p3_dependency()
    gen_p4a_timeline()
    gen_p5a_federation()
    print("\n[OK] 3 张新插图全部生成完毕")
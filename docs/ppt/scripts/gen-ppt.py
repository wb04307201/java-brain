#!/usr/bin/env python3
"""
gen-ppt.py — 用 python-pptx 生成 JavaBrain 答辩 PPT

视觉:深色科技风(深蓝/紫色背景 + 白色文字 + 金色杀手锏徽章)
字体:Microsoft YaHei(中文)/ Consolas(代码)/ Arial(英文)
规格:16:9(13.333 x 7.5 inch = 1280x720 像素)
输出:../javabrain.pptx
"""
import os
import sys
from pathlib import Path

# 强制 stdout 用 UTF-8(Windows GBK 终端下输出 emoji/中文不报错)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

# ==================== 路径 ====================
SCRIPT_DIR = Path(__file__).resolve().parent
PPTX_DIR = SCRIPT_DIR.parent
IMAGES_DIR = PPTX_DIR / "images"
OUTPUT_FILE = PPTX_DIR / "javabrain.pptx"

# ==================== 配色(深色科技风) ====================
BG_DARK = RGBColor(0x0F, 0x17, 0x2A)        # 主背景:深蓝
BG_DARKER = RGBColor(0x07, 0x0C, 0x19)     # 更深(封面/结尾)
BG_PANEL = RGBColor(0x1E, 0x2A, 0x47)      # 卡片底色
JAVA_BLUE = RGBColor(0x00, 0x73, 0x96)     # Java 蓝(主色)
AI_PURPLE = RGBColor(0x6B, 0x46, 0xC1)     # AI 紫(强调)
TEXT_WHITE = RGBColor(0xF8, 0xFA, 0xFC)    # 主文字
TEXT_GRAY = RGBColor(0xCB, 0xD5, 0xE1)     # 次要文字
TEXT_MUTED = RGBColor(0x94, 0xA3, 0xB8)    # 暗文字
GOLD = RGBColor(0xF5, 0x9E, 0x0B)          # 杀手锏徽章
RED_ACCENT = RGBColor(0xEF, 0x44, 0x44)    # 警告红
GREEN_OK = RGBColor(0x10, 0xB9, 0x81)      # 成功绿

# ==================== 字体 ====================
FONT_CN = "Microsoft YaHei"     # 微软雅黑
FONT_EN = "Consolas"            # 等宽
FONT_TITLE = "Microsoft YaHei"

# ==================== 工具函数 ====================

def set_cn_font(run, font_name=FONT_CN, size_pt=18, bold=False, color=None):
    """设置 run 字体(含东亚字体,保证中文正常显示)"""
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
    # 东亚字体
    rPr = run._r.get_or_add_rPr()
    for tag in ('ea', 'cs'):
        existing = rPr.find(qn(f'a:{tag}'))
        if existing is not None:
            rPr.remove(existing)
        elem = etree.SubElement(rPr, qn(f'a:{tag}'))
        elem.set('typeface', font_name)


def add_textbox(slide, left, top, width, height, text, *,
                font=FONT_CN, size=18, bold=False, color=TEXT_WHITE,
                align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=1.2):
    """加一个文字框(text 可以是字符串或字符串列表,每行一段)"""
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)

    lines = text if isinstance(text, list) else [text]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        run = p.add_run()
        run.text = line
        set_cn_font(run, font_name=font, size_pt=size, bold=bold, color=color)
    return box


def add_badge(slide, left, top, width, height, text, fill=AI_PURPLE, color=TEXT_WHITE, size=12, bold=True):
    """左上角徽章(带圆角矩形底)"""
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.fill.background()  # 无边框
    tf = shp.text_frame
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    set_cn_font(run, size_pt=size, bold=bold, color=color)
    return shp


def set_background(slide, color=BG_DARK):
    """slide 背景色"""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_fade_transition(slide, duration_ms=700, thru_black=False):
    """给 slide 添加淡入淡出转场(从本页切到下一页时的过渡效果)

    duration_ms:转场时长,默认 700ms
    thru_black:是否经过黑场(默认 False,直接淡入淡出)
    """
    spPr = slide.element
    # 移除已有 transition
    for existing in spPr.findall(qn('p:transition')):
        spPr.remove(existing)
    # 创建新 transition
    transition = etree.SubElement(spPr, qn('p:transition'))
    transition.set('spd', 'fast')
    # p14 命名空间(精确控制毫秒)
    p14_attr = '{http://schemas.microsoft.com/office/powerpoint/2010/main}dur'
    transition.set(p14_attr, str(duration_ms))
    fade = etree.SubElement(transition, qn('p:fade'))
    if thru_black:
        fade.set('thruBlk', '1')


def add_title_bar(slide, text, *, color=TEXT_WHITE, accent=AI_PURPLE, size=32):
    """顶部统一标题:左侧紫色色块 + 白色标题文字"""
    # 左侧色块
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                  Inches(0.5), Inches(0.4),
                                  Inches(0.12), Inches(0.6))
    bar.fill.solid()
    bar.fill.fore_color.rgb = accent
    bar.line.fill.background()
    # 标题
    add_textbox(slide, Inches(0.75), Inches(0.32), Inches(12), Inches(0.8),
                text, size=size, bold=True, color=color, anchor=MSO_ANCHOR.MIDDLE)


def add_top_bar(slide, title, subtitle=None, badge=None, accent=AI_PURPLE,
                title_size=28):
    """统一顶部 bar:色块 + 标题(28pt) + 副标(13pt) + 可选徽章"""
    # 左侧色块
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                  Inches(0.5), Inches(0.32),
                                  Inches(0.12), Inches(0.7))
    bar.fill.solid()
    bar.fill.fore_color.rgb = accent
    bar.line.fill.background()
    # 标题
    add_textbox(slide, Inches(0.75), Inches(0.22), Inches(10.5), Inches(0.5),
                title, size=title_size, bold=True, color=TEXT_WHITE,
                anchor=MSO_ANCHOR.MIDDLE)
    # 副标
    if subtitle:
        add_textbox(slide, Inches(0.75), Inches(0.7), Inches(10.5), Inches(0.35),
                    subtitle, size=12, color=TEXT_GRAY,
                    anchor=MSO_ANCHOR.MIDDLE)
    # 徽章(右上角)
    if badge:
        add_badge(slide, Inches(11.4), Inches(0.4), Inches(1.7), Inches(0.4),
                  badge, fill=accent, size=11)


def add_bottom_gold(slide, gold_text, small_text=None):
    """统一底部金句 panel:金色边框 + 18pt 金色金句 + 可选小字"""
    # 金色边框 panel
    panel = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                    Inches(0.6), Inches(6.3),
                                    Inches(12.1), Inches(0.55))
    panel.fill.solid()
    panel.fill.fore_color.rgb = BG_PANEL
    panel.line.color.rgb = GOLD
    panel.line.width = Pt(1.5)
    # 金句(18pt 金色)
    add_textbox(slide, Inches(0.7), Inches(6.32), Inches(11.9), Inches(0.5),
                gold_text, size=18, bold=True, color=GOLD,
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    # 小字
    if small_text:
        add_textbox(slide, Inches(0.6), Inches(6.95), Inches(12.1), Inches(0.4),
                    small_text, size=10, color=TEXT_MUTED,
                    align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def add_picture_fit(slide, path, left, top, max_w, max_h):
    """等比缩放,放入 (left, top, max_w, max_h) 框内,返回图片框"""
    from PIL import Image
    try:
        with Image.open(path) as im:
            iw, ih = im.size
    except Exception:
        iw, ih = 16, 9
    ratio = min(max_w / iw, max_h / ih)
    w = int(iw * ratio)
    h = int(ih * ratio)
    # 居中
    x = left + (max_w - w) // 2
    y = top + (max_h - h) // 2
    return slide.shapes.add_picture(str(path), x, y, width=w, height=h)


def add_panel(slide, left, top, width, height, fill=BG_PANEL, line_color=None):
    """半透明面板(深色卡片)"""
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line_color is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line_color
    return shp


# ==================== 10 页幻灯片 ====================

def slide_1_cover(prs):
    """P1 封面"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # 空白版式
    set_background(slide, BG_DARKER)
    # 配图全屏
    add_picture_fit(slide, IMAGES_DIR / "page-01-cover.png",
                    Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    # 底部叠加标题(深色半透明底, 减薄到 1.5 英寸)
    panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                   Inches(0), Inches(6.0),
                                   Inches(13.333), Inches(1.5))
    panel.fill.solid()
    panel.fill.fore_color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    panel.line.fill.background()
    # 主标题
    add_textbox(slide, Inches(0.8), Inches(6.1), Inches(11.7), Inches(0.7),
                "JavaBrain", size=46, bold=True, color=TEXT_WHITE,
                align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
    # 副标题
    add_textbox(slide, Inches(0.8), Inches(6.75), Inches(11.7), Inches(0.4),
                "Spring Boot AI Agent + 数据库低代码一站式解决方案",
                size=16, color=TEXT_GRAY, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
    # 团队信息
    add_textbox(slide, Inches(0.8), Inches(7.1), Inches(11.7), Inches(0.35),
                "灵梭 + SQL 工坊 + SQL 工坊 MCP   ·   开源 · 私有化 · 业务语义",
                size=11, color=TEXT_MUTED, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)


def slide_2_pain(prs):
    """P2 痛点:3 个数字"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_DARK)
    add_top_bar(slide, "企业 AI 落地的 3 个真实数字",
                subtitle="3 个月 / 5 天 / 3 天  →  3 分钟 / 90 秒 / 10 分钟",
                accent=RED_ACCENT)
    # 主体:配图
    add_picture_fit(slide, IMAGES_DIR / "page-02-pain.png",
                    Inches(0.6), Inches(1.2), Inches(12.1), Inches(4.9))
    # 底部金句
    add_bottom_gold(slide, "3 分钟启动  ·  90 秒出报告  ·  10 分钟出可用的页面",
                    small_text="JavaBrain 把这 3 个数字,从月压到分")


def slide_3_position(prs):
    """P3 定位 + 组成"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_DARK)
    add_top_bar(slide, "定位 + 组成",
                subtitle="三个 Spring Boot 依赖库,按需引入,不需要全栈改造",
                accent=AI_PURPLE)
    # 核心金句(在配图上方)
    add_textbox(slide, Inches(0.6), Inches(1.15), Inches(12.1), Inches(0.5),
                "JavaBrain = 灵梭 AI Agent  +  SQL 工坊  +  SQL 工坊 MCP",
                size=22, bold=True, color=TEXT_WHITE, align=PP_ALIGN.CENTER,
                anchor=MSO_ANCHOR.MIDDLE)
    # 配图(主体 1.8 - 6.2)
    add_picture_fit(slide, IMAGES_DIR / "page-03-position.png",
                    Inches(1.5), Inches(1.75), Inches(10.3), Inches(4.3))
    # 底部金句
    add_bottom_gold(slide, "三个都是依赖库,组合 = 企业 AI 落地完整闭环",
                    small_text="灵梭 / SQL 工坊 / SQL 工坊 MCP,各自独立可用,按需组合")


def slide_4_loom(prs):
    """P4 灵梭:6 大功能"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_DARK)
    add_top_bar(slide, "灵梭 · 6 大功能模块",
                subtitle="Spring AI 编排 + RAG / MCP / Skill 全部装进一个依赖库",
                accent=AI_PURPLE, badge="🧩 独立依赖库")
    # 主体:配图
    add_picture_fit(slide, IMAGES_DIR / "page-04-loom.png",
                    Inches(0.6), Inches(1.2), Inches(12.1), Inches(4.9))
    # 底部金句
    add_bottom_gold(slide, "★ 杀手锏:MCP 工具集成  ·  Skill 技能库(改一个 .st 文件,AI 行为就变)",
                    small_text="对话持久化(H2 + Flyway)  ·  流式输出  ·  思维链可观测  ·  Spring Boot 自动配置")


def slide_5_forge(prs):
    """P5 SQL 工坊 + MCP:4 starter + 6 大功能"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_DARK)
    add_top_bar(slide, "SQL 工坊 + MCP · 4 starter + 6 大功能",
                subtitle="4 个 starter 按需组合,AI 隔离在 5 个受限工具之后",
                accent=JAVA_BLUE, badge="🧩 4 starter")
    # 4 个 starter chip(放在主体顶部,1.15-1.65)
    starters = [
        "sql-forge 基础 CRUD",
        "+ calcite 跨库联邦",
        "+ web Amis 低代码",
        "+ mcp 本次演示",
    ]
    chip_w = Inches(2.9)
    chip_h = Inches(0.5)
    gap = Inches(0.15)
    total = chip_w * 4 + gap * 3
    start_x = (Inches(13.333) - total) // 2
    for i, s in enumerate(starters):
        x = start_x + (chip_w + gap) * i
        shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.2), chip_w, chip_h)
        shp.fill.solid()
        shp.fill.fore_color.rgb = BG_PANEL
        shp.line.color.rgb = JAVA_BLUE
        shp.line.width = Pt(1.5)
        tf = shp.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = s
        set_cn_font(r, size_pt=12, bold=True, color=TEXT_WHITE)
    # 配图(1.8 - 6.2)
    add_picture_fit(slide, IMAGES_DIR / "page-05-forge.png",
                    Inches(0.6), Inches(1.8), Inches(12.1), Inches(4.3))
    # 底部金句
    add_bottom_gold(slide, "★ 杀手锏:JSON CRUD 协议  ·  Calcite 跨库联邦  ·  MCP 5 个受限工具",
                    small_text="AI 隔离后,私有化部署,数据不出企业")


def slide_6_demo1(prs):
    """P6 录屏 1:一句话出分析报告"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_DARK)
    add_top_bar(slide, "录屏 1:一句话出分析报告",
                subtitle="演示基于 oms 订单管理系统(只用了 SQL 工坊的 基础 + MCP + Web 三个 starter)",
                accent=GOLD)
    # 演示语(放在主体顶部 1.15-1.7)
    add_panel(slide, Inches(0.6), Inches(1.15), Inches(12.1), Inches(0.55),
              fill=BG_DARKER, line_color=AI_PURPLE)
    add_textbox(slide, Inches(0.75), Inches(1.18), Inches(12), Inches(0.5),
                "💬 演示语:订单系统各分类商品数,画柱状图,保存 HTML 报告",
                size=14, bold=True, color=TEXT_WHITE, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
    # 录屏画面占位 / 真图(主体 1.85 - 6.15)
    demo1_path = IMAGES_DIR / "page-06-demo1.png"
    if demo1_path.exists():
        add_picture_fit(slide, demo1_path, Inches(0.6), Inches(1.85), Inches(12.1), Inches(4.2))
    else:
        # 6 步时间轴占位(虚线框)
        ph = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                    Inches(0.6), Inches(1.85),
                                    Inches(12.1), Inches(4.2))
        ph.fill.solid()
        ph.fill.fore_color.rgb = BG_DARKER
        ph.line.color.rgb = TEXT_MUTED
        ph.line.width = Pt(1.5)
        ph.line.dash_style = 7
        steps = [
            ("① 输入", "5s"),
            ("② AI 推理", "15s"),
            ("③ 表格+柱状图", "20s"),
            ("④ 保存 HTML", "10s"),
            ("⑤ 打开预览", "20s"),
            ("⑥ 展示链接", "20s"),
        ]
        add_textbox(slide, Inches(0.6), Inches(2.05), Inches(12.1), Inches(0.4),
                    "📹 录屏占位(录完后自动替换为真截图) — 画面 6 步分解:",
                    size=12, color=TEXT_MUTED, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        chip_w = Inches(1.85)
        chip_h = Inches(0.95)
        gap = Inches(0.1)
        total = chip_w * 6 + gap * 5
        start_x = (Inches(13.333) - total) // 2
        for i, (name, dur) in enumerate(steps):
            x = start_x + (chip_w + gap) * i
            shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(3.05), chip_w, chip_h)
            shp.fill.solid()
            shp.fill.fore_color.rgb = BG_PANEL
            shp.line.color.rgb = AI_PURPLE
            shp.line.width = Pt(1)
            tf = shp.text_frame
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = name
            set_cn_font(r, size_pt=12, bold=True, color=TEXT_WHITE)
            p2 = tf.add_paragraph()
            p2.alignment = PP_ALIGN.CENTER
            r2 = p2.add_run()
            r2.text = dur
            set_cn_font(r2, size_pt=11, color=GOLD)
        # ffmpeg 命令
        add_textbox(slide, Inches(0.6), Inches(5.4), Inches(12.1), Inches(0.4),
                    "ffmpeg -i videos/demo1/demo1-final.mp4 -ss 5 -vframes 1 images/page-06-demo1.png",
                    size=10, color=TEXT_MUTED, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, font=FONT_EN)
    # 底部金句
    add_bottom_gold(slide, "90 秒出可用分析报告  —  录屏即将开始",
                    small_text="演示用的是基于 SQL 工坊搭建的 oms 订单管理系统,但 SQL 工坊不绑死订单,任何业务系统都能用")


def slide_7_demo2(prs):
    """P7 录屏 2:一句话生成 CRUD"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_DARK)
    add_top_bar(slide, "录屏 2:一句话生成 CRUD",
                subtitle="演示基于同一套 oms 订单管理系统(用 SQL 工坊的低代码 + CRUD 能力)",
                accent=GOLD)
    # 演示语
    add_panel(slide, Inches(0.6), Inches(1.15), Inches(12.1), Inches(0.55),
              fill=BG_DARKER, line_color=AI_PURPLE)
    add_textbox(slide, Inches(0.75), Inches(1.18), Inches(12), Inches(0.5),
                "💬 演示语 2 轮:① 帮我做一个订单明细(ORDER_ITEMS)的维护页   ② 没问题,直接生成",
                size=13, bold=True, color=TEXT_WHITE, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
    # 录屏画面占位 / 真图
    demo2_path = IMAGES_DIR / "page-07-demo2.png"
    if demo2_path.exists():
        add_picture_fit(slide, demo2_path, Inches(0.6), Inches(1.85), Inches(12.1), Inches(4.2))
    else:
        # 6 步时间轴占位
        ph = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                    Inches(0.6), Inches(1.85),
                                    Inches(12.1), Inches(4.2))
        ph.fill.solid()
        ph.fill.fore_color.rgb = BG_DARKER
        ph.line.color.rgb = TEXT_MUTED
        ph.line.width = Pt(1.5)
        ph.line.dash_style = 7
        steps = [
            ("① 输入+推断", "15s"),
            ("② 确认生成", "10s"),
            ("③ 3 行输出", "5s"),
            ("④ 切 oms", "20s"),
            ("⑤ 4 个功能", "40s"),
            ("⑥ 切回聊天", "10s"),
        ]
        add_textbox(slide, Inches(0.6), Inches(2.05), Inches(12.1), Inches(0.4),
                    "📹 录屏占位(录完后自动替换为真截图) — 画面 6 步分解:",
                    size=12, color=TEXT_MUTED, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        chip_w = Inches(1.85)
        chip_h = Inches(0.95)
        gap = Inches(0.1)
        total = chip_w * 6 + gap * 5
        start_x = (Inches(13.333) - total) // 2
        for i, (name, dur) in enumerate(steps):
            x = start_x + (chip_w + gap) * i
            shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(3.05), chip_w, chip_h)
            shp.fill.solid()
            shp.fill.fore_color.rgb = BG_PANEL
            shp.line.color.rgb = AI_PURPLE
            shp.line.width = Pt(1)
            tf = shp.text_frame
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = name
            set_cn_font(r, size_pt=12, bold=True, color=TEXT_WHITE)
            p2 = tf.add_paragraph()
            p2.alignment = PP_ALIGN.CENTER
            r2 = p2.add_run()
            r2.text = dur
            set_cn_font(r2, size_pt=11, color=GOLD)
        # ffmpeg 命令
        add_textbox(slide, Inches(0.6), Inches(5.4), Inches(12.1), Inches(0.4),
                    "ffmpeg -i videos/demo2/demo2-final.mp4 -ss 60 -vframes 1 images/page-07-demo2.png",
                    size=10, color=TEXT_MUTED, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, font=FONT_EN)
    # 底部金句
    add_bottom_gold(slide, "100 秒出可用管理页  —  录屏即将开始",
                    small_text="演示用的 oms 订单系统只是 JavaBrain 的一种组合示例,任何业务库都能这么玩")


def slide_8_compare(prs):
    """P8 实战 + 对比(左实战 / 右对比, 删掉重复配图)"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_DARK)
    add_top_bar(slide, "7 轮实战验证 + 3 维度对比",
                subtitle="0 漂移 / 0 错误链接 / 0 乱码 / 5/5 自检 / >80% 节省",
                accent=GOLD)
    # 左半:实战数据
    add_textbox(slide, Inches(0.6), Inches(1.15), Inches(5.5), Inches(0.45),
                "📊 实战数据(技术派)", size=18, bold=True, color=JAVA_BLUE,
                align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
    add_panel(slide, Inches(0.6), Inches(1.65), Inches(5.5), Inches(4.45),
              fill=BG_PANEL, line_color=JAVA_BLUE)
    # 大数字
    big_data_top = Inches(1.85)
    add_textbox(slide, Inches(0.85), big_data_top, Inches(5.0), Inches(0.6),
                "7 张表", size=24, bold=True, color=JAVA_BLUE,
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(slide, Inches(0.85), big_data_top + Inches(0.6), Inches(5.0), Inches(0.35),
                "简单表 / 字典表 / 自关联 / 多外键",
                size=10, color=TEXT_GRAY, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(slide, Inches(0.85), big_data_top + Inches(1.05), Inches(5.0), Inches(0.5),
                "0 漂移  ·  0 错误链接  ·  0 中文乱码",
                size=13, bold=True, color=GREEN_OK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(slide, Inches(0.85), big_data_top + Inches(1.65), Inches(5.0), Inches(0.45),
                "5 / 5  AI 字段推断自检通过",
                size=14, bold=True, color=TEXT_WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(slide, Inches(0.85), big_data_top + Inches(2.2), Inches(5.0), Inches(0.65),
                "> 80%", size=30, bold=True, color=GOLD,
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(slide, Inches(0.85), big_data_top + Inches(2.85), Inches(5.0), Inches(0.35),
                "节省 CRUD 开发时间",
                size=11, color=TEXT_GRAY, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    # 右半:对比表
    add_textbox(slide, Inches(6.5), Inches(1.15), Inches(6.3), Inches(0.45),
                "📋 横向对比(商业派)", size=18, bold=True, color=AI_PURPLE,
                align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
    rows = [
        ("维度", "低代码", "ChatGPT+插件", "JavaBrain"),
        ("业务取数", "模板查询", "✅ 但数据外发", "✅ 90秒+私有化"),
        ("CRUD 页面", "不懂业务", "需配合代码", "✅ AI 语义推断"),
        ("跨库 JOIN", "❌", "❌", "✅ Calcite 联邦"),
        ("私有化", "✅", "❌", "✅"),
        ("列名识别", "n/a", "❌ 经常错", "✅ 强制读 DDL"),
    ]
    tbl_left = Inches(6.5)
    tbl_top = Inches(1.65)
    col_widths = [Inches(1.4), Inches(1.4), Inches(1.7), Inches(1.8)]
    row_height = Inches(0.5)
    header_colors = [BG_PANEL, RGBColor(0x4B, 0x55, 0x63), RED_ACCENT, GREEN_OK]
    for ri, row in enumerate(rows):
        x = tbl_left
        for ci, cell in enumerate(row):
            shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, tbl_top + row_height * ri,
                                         col_widths[ci], row_height)
            if ri == 0:
                shp.fill.solid()
                shp.fill.fore_color.rgb = header_colors[ci]
            else:
                shp.fill.solid()
                shp.fill.fore_color.rgb = BG_PANEL if ci == 0 else (BG_DARKER if ci == 3 else RGBColor(0x1A, 0x1F, 0x2E))
            shp.line.color.rgb = BG_DARK
            shp.line.width = Pt(0.5)
            tf = shp.text_frame
            tf.margin_left = Inches(0.06)
            tf.margin_right = Inches(0.06)
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if ci > 0 else PP_ALIGN.LEFT
            r = p.add_run()
            r.text = cell
            color = TEXT_WHITE if ri == 0 else (
                GREEN_OK if ci == 3 else (TEXT_WHITE if ci == 0 else TEXT_GRAY)
            )
            set_cn_font(r, size_pt=11, bold=(ri == 0 or ci == 3), color=color)
            x += col_widths[ci]
    # 底部金句
    add_bottom_gold(slide, "JavaBrain 在「安全 + 智能 + 私有化」三角都做到了",
                    small_text="既不像低代码只能跑模板查询,也不像 ChatGPT+插件把数据外发到云端")


def slide_9_roadmap(prs):
    """P9 开源 + 路线图"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_DARK)
    add_top_bar(slide, "已开源 + 未来规划",
                subtitle="三个独立仓库,各自独立维护,按需组合",
                accent=GREEN_OK)
    # 3 个仓库卡片
    repos = [
        ("灵梭", "spring-ai-loom-agent", "7 模块 · AI 编排", AI_PURPLE),
        ("SQL 工坊", "sql-forge", "12 模块 · 数据管理", JAVA_BLUE),
        ("SQL 工坊 MCP", "sql-forge-mcp", "AI ↔ DB 工具", GREEN_OK),
    ]
    repo_w = Inches(3.9)
    repo_h = Inches(1.0)
    repo_gap = Inches(0.15)
    repo_total = repo_w * 3 + repo_gap * 2
    repo_x = (Inches(13.333) - repo_total) // 2
    for i, (name, repo, desc, color) in enumerate(repos):
        x = repo_x + (repo_w + repo_gap) * i
        add_panel(slide, x, Inches(1.2), repo_w, repo_h, fill=BG_PANEL, line_color=color)
        add_textbox(slide, x + Inches(0.2), Inches(1.28), repo_w - Inches(0.4), Inches(0.35),
                    name, size=14, bold=True, color=color, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
        add_textbox(slide, x + Inches(0.2), Inches(1.6), repo_w - Inches(0.4), Inches(0.3),
                    repo, size=10, color=TEXT_GRAY, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
        add_textbox(slide, x + Inches(0.2), Inches(1.85), repo_w - Inches(0.4), Inches(0.3),
                    f"🧩 独立可用 · {desc}", size=9, color=TEXT_MUTED, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
    # 路线图配图
    add_picture_fit(slide, IMAGES_DIR / "page-09-roadmap.png",
                    Inches(0.6), Inches(2.4), Inches(12.1), Inches(3.7))
    # 底部金句
    add_bottom_gold(slide, "三个仓库独立维护,演示只是其中一种组合示例",
                    small_text="V1.0 当前 → V1.1 多租户/字段权限 → V1.2 移动端 Amis → V1.3 工作流引擎")


def slide_10_ending(prs):
    """P10 结尾(配图缩小到中央 60%, 文字分上下两块不重叠)"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_DARKER)
    # 顶部 3 句话(深色 panel)
    add_panel(slide, Inches(0), Inches(0.3), Inches(13.333), Inches(1.95),
              fill=BG_DARKER, line_color=None)
    add_textbox(slide, Inches(0.8), Inches(0.45), Inches(11.7), Inches(0.5),
                "1.  JavaBrain = 开箱即用 + 私有化 + 业务语义",
                size=18, bold=True, color=TEXT_WHITE, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(slide, Inches(0.8), Inches(0.95), Inches(11.7), Inches(0.5),
                "2.  一行命令启动,一个文件改 AI 行为",
                size=18, bold=True, color=TEXT_WHITE, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(slide, Inches(0.8), Inches(1.45), Inches(11.7), Inches(0.5),
                "3.  让每一个 Spring Boot 项目都自带 AI 能力",
                size=18, bold=True, color=TEXT_WHITE, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
    # 中部配图(终端画面, 缩到中央 60%)
    add_picture_fit(slide, IMAGES_DIR / "page-10-ending.png",
                    Inches(2.0), Inches(2.45), Inches(9.3), Inches(3.4))
    # 底部金句
    add_panel(slide, Inches(0), Inches(5.95), Inches(13.333), Inches(1.55),
              fill=BG_DARKER, line_color=GOLD)
    add_textbox(slide, Inches(0.8), Inches(6.05), Inches(11.7), Inches(0.7),
                "让 AI 不再是 Demo,让企业系统真正智能。",
                size=28, bold=True, color=GOLD, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(slide, Inches(0.8), Inches(6.75), Inches(11.7), Inches(0.4),
                "JavaBrain —— 一个文件改 AI 行为",
                size=15, color=TEXT_WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_textbox(slide, Inches(0.8), Inches(7.1), Inches(11.7), Inches(0.35),
                "感谢聆听 · 欢迎交流",
                size=12, color=TEXT_MUTED, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


# ==================== 主流程 ====================

def main():
    # 16:9 宽屏:13.333 x 7.5 inch
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    print(f"输出文件:{OUTPUT_FILE}")
    print(f"配图目录:{IMAGES_DIR}")
    print(f"配图数量:{len(list(IMAGES_DIR.glob('page-*.png')))}")

    slide_1_cover(prs)
    print("[1/10] 封面 ✓")
    slide_2_pain(prs)
    print("[2/10] 痛点 ✓")
    slide_3_position(prs)
    print("[3/10] 定位 ✓")
    slide_4_loom(prs)
    print("[4/10] 灵梭 ✓")
    slide_5_forge(prs)
    print("[5/10] SQL 工坊 ✓")
    slide_6_demo1(prs)
    print("[6/10] 录屏 1 ✓")
    slide_7_demo2(prs)
    print("[7/10] 录屏 2 ✓")
    slide_8_compare(prs)
    print("[8/10] 实战+对比 ✓")
    slide_9_roadmap(prs)
    print("[9/10] 开源+路线图 ✓")
    slide_10_ending(prs)
    print("[10/10] 结尾 ✓")

    # 转场:录屏 1/2 前后共 3 个 fade 转场点
    #  - P5 → P6  (进入录屏 1)
    #  - P6 → P7  (录屏 1 → 录屏 2)
    #  - P7 → P8  (录屏 2 → 实战对比)
    add_fade_transition(prs.slides[4], duration_ms=700)  # P5
    add_fade_transition(prs.slides[5], duration_ms=700)  # P6
    add_fade_transition(prs.slides[6], duration_ms=700)  # P7
    print("转场: P5 / P6 / P7 加 fade(0.7s)✓")

    prs.save(str(OUTPUT_FILE))
    size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"\n✅ 完成!{OUTPUT_FILE}  ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()

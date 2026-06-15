#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JavaBrain 答辩 PPT 生成器 - v2(白底 2.5D 乐高)"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

# ============== 路径 ==============
SCRIPT_DIR = Path(__file__).resolve().parent
PPT_DIR = SCRIPT_DIR.parent
OUTPUT = PPT_DIR / "javabrain.pptx"

# ============== 幻灯片尺寸(16:9) ==============
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

# ============== 配色(7 色 + 4 中性,见 spec §4.1) ==============
JAVA_BLUE = RGBColor(0x00, 0x73, 0x96)
AI_PURPLE = RGBColor(0x6B, 0x46, 0xC1)
SEMANTIC_RED = RGBColor(0xDC, 0x26, 0x26)
SEMANTIC_GREEN = RGBColor(0x10, 0xB9, 0x81)
GOLD = RGBColor(0xF5, 0x9E, 0x0B)
TEXT_PRIMARY = RGBColor(0x1F, 0x29, 0x37)
TEXT_SECONDARY = RGBColor(0x6B, 0x72, 0x80)
BG_LIGHT = RGBColor(0xFA, 0xFB, 0xFC)
DIVIDER = RGBColor(0xE5, 0xE7, 0xEB)
GOLD_BG = RGBColor(0xFE, 0xF3, 0xC7)
GREEN_BG = RGBColor(0xD1, 0xFA, 0xE5)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

# ============== 字体 ==============
FONT_CN = "阿里巴巴普惠体 3.0"
FONT_EN = "Inter"
FONT_MONO = "JetBrains Mono"

# ============== 动画类型(见 spec §5.2) ==============
ANIM_PRESETS = {
    "fade_in":   ("entr", "10"),
    "fade_out":  ("exit", "11"),
    "zoom_in":   ("entr", "23"),
    "appear":    ("entr", "1"),
    "fly_left":  ("entr", "3"),
    "fly_right": ("entr", "2"),
    "fly_top":   ("entr", "5"),
    "fly_bot":   ("entr", "4"),
    "pulse":     ("emph", "26"),
    "spin":      ("emph", "8"),
}


def add_anim(slide, shape, anim_type, *, delay_ms=0, dur_ms=500, loop=False):
    """注入 PowerPoint 动画节点。
    anim_type: 见 ANIM_PRESETS 的 key
    loop=True: 生成 repeatCount="indefinite"(持续到翻页,转视频核心)
    fill="hold" 保持动画间形状可见;loop=True 时必需
    """
    if anim_type not in ANIM_PRESETS:
        raise ValueError(
            f"unknown anim_type {anim_type!r}; valid: {list(ANIM_PRESETS)}"
        )
    preset_class, preset_id = ANIM_PRESETS[anim_type]
    shape_id = shape.shape_id
    repeat_attr = ' repeatCount="indefinite"' if loop else ""

    timing_xml = f'''<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:tnLst>
    <p:par>
      <p:pPr/>
      <p:par>
        <p:cond><p:tnCond val="0"/></p:cond>
        <p:par>
          <p:cTn id="{shape_id + 1}" nodeType="withEffect" dur="{dur_ms}" begin="{delay_ms}ms" fill="hold"{repeat_attr}>
            <p:animEffect presetClass="{preset_class}" presetId="{preset_id}" dur="{dur_ms}"/>
          </p:cTn>
        </p:par>
      </p:par>
    </p:par>
  </p:tnLst>
</p:timing>'''
    timing_elem = etree.fromstring(timing_xml)
    slide._element.append(timing_elem)


def iso_lego(slide, x_in, y_in, w_in, h_in, color, *, studs=True, highlight=False):
    """画一个 2.5D 乐高积木(圆角矩形主体 + 顶部 4 圆钉)。
    返回主形状(用于 add_anim)。
    本版本第一版先简化:不做高光条和软阴影(后续可加)。
    """
    In = Inches
    main = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                   In(x_in), In(y_in), In(w_in), In(h_in))
    main.fill.solid()
    main.fill.fore_color.rgb = color
    main.line.fill.background()
    if studs:
        stud_r = min(w_in, h_in) * 0.16
        stud_y = y_in - stud_r * 0.5
        stud_xs = [x_in + w_in * 0.18, x_in + w_in * 0.40,
                   x_in + w_in * 0.60, x_in + w_in * 0.82]
        for sx in stud_xs:
            stud = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                           In(sx - stud_r / 2), In(stud_y),
                                           In(stud_r), In(stud_r))
            stud.fill.solid()
            stud.fill.fore_color.rgb = color
            stud.line.fill.background()
    if highlight:
        hl = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                     In(x_in), In(y_in), In(w_in), In(h_in * 0.12))
        hl.fill.solid()
        hl.fill.fore_color.rgb = WHITE
        hl.line.fill.background()
        # 设置 30% alpha(spec §4.4 "白色 alpha 30%")
        from lxml import etree as _etree
        solidFill = hl._element.spPr.find(qn("a:solidFill"))
        if solidFill is not None:
            alpha = _etree.SubElement(solidFill, qn("a:alpha"))
            alpha.set("val", "30000")  # 30000 = 30%
    return main


def styled_text(slide, x, y, w, h, text, *,
                font=None, size=18, color=None, bold=False, center=True):
    """创建并配置一个文本框。返回 textbox shape。
    font/color 默认:font=FONT_CN, color=TEXT_PRIMARY
    center=True → PP_ALIGN.CENTER
    """
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True  # 避免自动收缩字号
    tf.text = text
    p = tf.paragraphs[0]
    if center:
        p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.name = font if font else FONT_CN
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color if color else TEXT_PRIMARY
    return tb


def slide_1_cover(prs):
    """P1 封面:3 乐高 + JavaBrain 大字 + 副标 + 金钩 + 5 fade_in"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    # 3 乐高横排(Java 蓝 / AI 紫 / 语义绿)
    lego_y = 1.5
    lego_size = 1.2
    lego_gap = 0.4
    total_w = 3 * lego_size + 2 * lego_gap
    lego_x0 = (13.333 - total_w) / 2
    legos = []
    for i, color in enumerate([JAVA_BLUE, AI_PURPLE, SEMANTIC_GREEN]):
        x = lego_x0 + i * (lego_size + lego_gap)
        lego = iso_lego(s, x, lego_y, lego_size, lego_size, color)
        legos.append(lego)

    # JavaBrain 大字(72pt 居中)
    tb_title = styled_text(s, 1.0, 3.4, 11.333, 1.4,
                           "JavaBrain",
                           font=FONT_EN, size=72, color=TEXT_PRIMARY, bold=True)

    # 副标"让 Spring Boot 秒变 AI 中枢"
    tb_sub = styled_text(s, 1.0, 4.8, 11.333, 0.5,
                          "让 Spring Boot 秒变 AI 中枢",
                          font=FONT_CN, size=24, color=TEXT_SECONDARY)

    # 金钩"3 组件 · 1 starter · 0 漂移"(圆角矩形 + 文字叠加)
    hook_box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                   Inches(4.0), Inches(5.5),
                                   Inches(5.333), Inches(0.6))
    hook_box.fill.solid()
    hook_box.fill.fore_color.rgb = GOLD
    hook_box.line.fill.background()
    hook_text = styled_text(s, 4.0, 5.55, 5.333, 0.5,
                             "3 组件 · 1 starter · 0 漂移",
                             font=FONT_CN, size=18, color=WHITE, bold=True)

    # ====== 5 个动画(策略 A 入场群) ======
    add_anim(s, legos[0], "fade_in", delay_ms=0,    dur_ms=500)
    add_anim(s, legos[1], "fade_in", delay_ms=300,  dur_ms=500)
    add_anim(s, legos[2], "fade_in", delay_ms=600,  dur_ms=500)
    add_anim(s, tb_title, "fade_in", delay_ms=900,  dur_ms=500)
    add_anim(s, hook_box, "fade_in", delay_ms=1400, dur_ms=500)


def slide_2_pain(prs):
    """P2 痛点:3 红 vs 3 绿 + 杀手锏金边 pulse_loop(策略 B)"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    # 标题
    tb_t = styled_text(s, 0.5, 0.4, 12.333, 0.7,
                       "接入 AI 的 3 个痛点 vs JavaBrain 的 3 个解法",
                       size=28, bold=True)

    # 左半:3 红字
    reds = ["3 月", "5 天", "3 天"]
    red_boxes = []
    for i, txt in enumerate(reds):
        tb = styled_text(s, 0.5, 2.0 + i * 1.3, 4.5, 1.0,
                         txt, font=FONT_EN, size=48, color=SEMANTIC_RED, bold=True)
        red_boxes.append(tb)

    # 中间箭头
    tb_arrow = styled_text(s, 5.0, 3.4, 3.333, 1.0,
                           "→", font=FONT_EN, size=72, color=GOLD, bold=True)

    # 右半:3 绿字
    greens = ["3 分", "90 秒", "10 分"]
    green_boxes = []
    for i, txt in enumerate(greens):
        tb = styled_text(s, 8.333, 2.0 + i * 1.3, 4.5, 1.0,
                         txt, font=FONT_EN, size=48, color=SEMANTIC_GREEN, bold=True)
        green_boxes.append(tb)

    # 杀手锏金边"3 月 vs 3 分"
    hook = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                              Inches(3.5), Inches(6.3),
                              Inches(6.333), Inches(0.7))
    hook.fill.solid()
    hook.fill.fore_color.rgb = GOLD_BG
    hook.line.color.rgb = GOLD
    hook.line.width = Pt(3)
    styled_text(s, 3.5, 6.35, 6.333, 0.6,
                "★ 3 月 vs 3 分 = 1440 倍效率提升",
                size=20, color=GOLD, bold=True)

    # ====== 8 动画(策略 B) ======
    add_anim(s, red_boxes[0], "fade_in", delay_ms=0,    dur_ms=500)
    add_anim(s, red_boxes[1], "fade_in", delay_ms=600,  dur_ms=500)
    add_anim(s, red_boxes[2], "fade_in", delay_ms=1200, dur_ms=500)
    add_anim(s, tb_arrow,    "fade_in", delay_ms=2000, dur_ms=500)
    add_anim(s, green_boxes[0], "fade_in", delay_ms=2800, dur_ms=500)
    add_anim(s, green_boxes[1], "fade_in", delay_ms=3400, dur_ms=500)
    add_anim(s, green_boxes[2], "fade_in", delay_ms=4000, dur_ms=500)
    add_anim(s, hook, "pulse", delay_ms=5000, dur_ms=1500, loop=True)  # ★ 杀手锏持续脉冲


def slide_3_position(prs):
    """P3 定位:3 乐高(带标签)+ 4 行 ✓ + 首行金脉冲(策略 A:4 动画=3 入场 + 1 循环)"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    # 标题
    tb_t = styled_text(s, 0.5, 0.4, 12.333, 0.7,
                       "JavaBrain = 灵梭 + SQL工坊 + SQL工坊 MCP",
                       size=28, bold=True)

    # 3 乐高横排(带标签)
    lego_y = 1.5
    lego_size = 0.9
    lego_gap = 0.6
    total_w = 3 * lego_size + 2 * lego_gap
    lego_x0 = (13.333 - total_w) / 2
    lego_labels = [("灵梭", JAVA_BLUE), ("SQL工坊", AI_PURPLE), ("SQL工坊 MCP", SEMANTIC_GREEN)]
    legos = []
    for i, (label, color) in enumerate(lego_labels):
        x = lego_x0 + i * (lego_size + lego_gap)
        lego = iso_lego(s, x, lego_y, lego_size, lego_size, color)
        legos.append(lego)
        # 标签
        styled_text(s, x - 0.3, lego_y + lego_size + 0.05, lego_size + 0.6, 0.3,
                    label, size=12, color=color, bold=True)

    # 4 行 ✓
    items = [
        ("✓ 三个都是依赖库,不是产品", GOLD, True),
        ("✓ 组件化、按需引入,各自独立可用", TEXT_PRIMARY, False),
        ("✓ ├── 灵梭 / SQL工坊 / SQL工坊 MCP 都可单独用", TEXT_SECONDARY, False),
        ("✓ 组合起来 = 企业 AI 落地完整闭环", TEXT_PRIMARY, False),
    ]
    item_boxes = []
    for i, (text, color, _) in enumerate(items):
        tb = styled_text(s, 1.5, 3.5 + i * 0.6, 10.333, 0.5,
                         text, size=18, color=color, bold=(i == 0))
        item_boxes.append(tb)

    # 4 动画:策略 A(标题入场 + 1 乐高入场 + 首行金行入场 + 1 循环)
    add_anim(s, tb_t, "fade_in", delay_ms=0, dur_ms=500)
    add_anim(s, legos[0], "fade_in", delay_ms=600, dur_ms=500)
    add_anim(s, item_boxes[0], "fade_in", delay_ms=1200, dur_ms=500)
    add_anim(s, item_boxes[0], "pulse", delay_ms=2000, dur_ms=1500, loop=True)


def slide_4a_loom_intro(prs):
    """P4-a 灵梭 · 整体定位(策略 A:4 动画=3 入场 + 1 循环)"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    # 小标
    styled_text(s, 0.5, 0.4, 12.333, 0.4,
                "灵梭 · LoomAgent",
                font=FONT_EN, size=16, color=JAVA_BLUE, bold=True)

    # 主标
    tb_t = styled_text(s, 0.5, 1.0, 12.333, 1.0,
                       "Spring AI 一键启动 · 改 .st 文件 AI 行为就变",
                       size=32, bold=True)

    # 4 特性卡(2x2)
    advs = [
        ("📦 6 大功能模块\n一站集成", JAVA_BLUE, False),
        ("🔌 MCP 可热插拔\n8+ 服务", GOLD, True),
        ("🧠 Skill 模板\n改 .st 即生效", GOLD, True),
        ("💬 流式对话 + 思维链\nSSE + 可折叠", JAVA_BLUE, False),
    ]
    cards = []
    cw, ch = 5.0, 1.3
    gap = 0.3
    cx0 = (13.333 - 2 * cw - gap) / 2
    cy0 = 2.5
    for i, (text, color, killer) in enumerate(advs):
        row, col = i // 2, i % 2
        x = cx0 + col * (cw + gap)
        y = cy0 + row * (ch + gap)
        card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                  Inches(x), Inches(y), Inches(cw), Inches(ch))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = GOLD if killer else DIVIDER
        card.line.width = Pt(3) if killer else Pt(1)
        # 卡片文字(独立 textbox 因为有 emoji 多行)
        styled_text(s, x, y + 0.2, cw, ch - 0.4,
                    text, size=18, color=color, bold=True)
        cards.append(card)

    # 引导
    styled_text(s, 0.5, 6.0, 12.333, 0.4,
                "▼ 下一页 · 6 大功能模块",
                size=16, color=AI_PURPLE, bold=True)

    # 4 动画:策略 A(标题入场 + 卡片入场 + Skill 金脉冲)
    add_anim(s, tb_t, "fade_in", delay_ms=0, dur_ms=500)
    add_anim(s, cards[0], "fade_in", delay_ms=600, dur_ms=500)
    add_anim(s, cards[2], "fade_in", delay_ms=1200, dur_ms=500)  # Skill 杀手锏
    add_anim(s, cards[2], "pulse", delay_ms=2000, dur_ms=1500, loop=True)


def slide_4b_loom_modules(prs):
    """P4-b 灵梭 · 6 模块功能 + 2 chase pulse(策略 C:8 动画=6 入场 + 2 chase 循环)"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    # 标题
    styled_text(s, 0.5, 0.4, 12.333, 0.6,
                "灵梭 · 6 大功能模块",
                size=28, bold=True)

    # 6 卡片(2x3)
    modules = [
        ("📚 RAG 知识库", "Tika + JVector", JAVA_BLUE, False),
        ("🔧 MCP ★", "8+ 服务可热插拔", GOLD, True),
        ("🧠 Skill ★", ".st 模板即提示词", GOLD, True),
        ("📁 文件管理", "磁盘 + H2 元数据", JAVA_BLUE, False),
        ("💬 对话 UI", "SSE + 思维链折叠", JAVA_BLUE, False),
        ("🛠️ 内置工具", "时间 / Git / Maven", JAVA_BLUE, False),
    ]
    cards = []
    cw, ch = 4.0, 1.8
    gap_x, gap_y = 0.2, 0.2
    cx0 = (13.333 - 3 * cw - 2 * gap_x) / 2
    cy0 = 1.3
    for i, (name, desc, color, killer) in enumerate(modules):
        col, row = i % 3, i // 3
        x = cx0 + col * (cw + gap_x)
        y = cy0 + row * (ch + gap_y)
        card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                  Inches(x), Inches(y), Inches(cw), Inches(ch))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        if killer:
            card.line.color.rgb = GOLD
            card.line.width = Pt(3)
        else:
            card.line.color.rgb = DIVIDER
            card.line.width = Pt(1)
        # 名字
        styled_text(s, x, y + 0.2, cw, 0.6, name, size=20, color=color, bold=True)
        # 描述
        styled_text(s, x, y + 0.9, cw, 0.5, desc, size=14, color=TEXT_SECONDARY)
        cards.append(card)

    # 底部金句
    styled_text(s, 0.5, 6.5, 12.333, 0.5,
                "★ 改一个 .st 文件,AI 行为就变",
                size=20, color=GOLD, bold=True)

    # 8 动画:6 入场 + 2 chase(策略 C,chase 错开 2s)
    for i in range(6):
        add_anim(s, cards[i], "fade_in",
                 delay_ms=i * 200, dur_ms=500)
    # 2 杀手锏金边 chase(MCP + Skill)
    add_anim(s, cards[1], "pulse", delay_ms=10000, dur_ms=1500, loop=True)  # MCP
    add_anim(s, cards[2], "pulse", delay_ms=12000, dur_ms=1500, loop=True)  # Skill


def slide_5a_forge_intro(prs):
    """P5-a SQL工坊 · 整体定位(策略 A:3 入场 + 1 循环)"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    # 小标
    styled_text(s, 0.5, 0.4, 12.333, 0.4,
                "SQL工坊 · SQL Forge",
                font=FONT_EN, size=16, color=AI_PURPLE, bold=True)

    # 主标
    tb_t = styled_text(s, 0.5, 1.0, 12.333, 1.0,
                       "JSON CRUD + Calcite 联邦 + Amis 低代码",
                       size=32, bold=True)

    # 4 特性卡(2x2)
    advs = [
        ("🔌 JSON CRUD\n一套协议 5 method", GOLD, True),
        ("🌐 Calcite 联邦\n跨 MySQL+PG+H2", GOLD, True),
        ("🎨 Amis 低代码\nJSON 模板 + Console", GOLD, True),
        ("🔒 MCP 5 受限工具\n数据不出企业", JAVA_BLUE, False),
    ]
    cards = []
    cw, ch = 5.0, 1.3
    gap = 0.3
    cx0 = (13.333 - 2 * cw - gap) / 2
    cy0 = 2.5
    for i, (text, color, killer) in enumerate(advs):
        row, col = i // 2, i % 2
        x = cx0 + col * (cw + gap)
        y = cy0 + row * (ch + gap)
        card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                  Inches(x), Inches(y), Inches(cw), Inches(ch))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = GOLD if killer else DIVIDER
        card.line.width = Pt(3) if killer else Pt(1)
        styled_text(s, x, y + 0.2, cw, ch - 0.4,
                    text, size=18, color=color, bold=True)
        cards.append(card)

    # 引导
    styled_text(s, 0.5, 6.0, 12.333, 0.4,
                "▼ 下一页 · 4 starter + 6 功能",
                size=16, color=AI_PURPLE, bold=True)

    # 4 动画:策略 A
    add_anim(s, tb_t, "fade_in", delay_ms=0, dur_ms=500)
    add_anim(s, cards[0], "fade_in", delay_ms=600, dur_ms=500)
    add_anim(s, cards[3], "fade_in", delay_ms=1200, dur_ms=500)
    add_anim(s, cards[3], "pulse", delay_ms=2000, dur_ms=1500, loop=True)  # 数据不出企业脉冲


def slide_5b_forge_4plus6(prs):
    """P5-b SQL工坊 · 4 starter + 6 功能 + 3 chase pulse(策略 C)"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    # 标题
    styled_text(s, 0.5, 0.3, 12.333, 0.5,
                "SQL工坊 · 4 starter + 6 功能",
                size=24, bold=True)

    # 4 starter 横条
    starters = [
        ("sql-forge-starter", SEMANTIC_GREEN),
        ("sql-forge-calcite", JAVA_BLUE),
        ("sql-forge-web", JAVA_BLUE),
        ("sql-forge-mcp", AI_PURPLE),
    ]
    starter_boxes = []
    sw, sh = 3.0, 0.5
    gap = 0.1
    sx0 = (13.333 - 4 * sw - 3 * gap) / 2
    sy = 1.0
    for i, (name, color) in enumerate(starters):
        x = sx0 + i * (sw + gap)
        box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                 Inches(x), Inches(sy), Inches(sw), Inches(sh))
        box.fill.solid()
        box.fill.fore_color.rgb = color
        box.line.fill.background()
        styled_text(s, x, sy + 0.05, sw, 0.4,
                    name, font=FONT_MONO, size=11, color=WHITE, bold=True)
        starter_boxes.append(box)

    # 6 功能卡(2x3)
    funcs = [
        ("🔌 JSON CRUD ★", GOLD, True),
        ("🌐 Calcite ★", GOLD, True),
        ("🔒 MCP 5 受限 ★", GOLD, True),
        ("🎨 Amis", JAVA_BLUE, False),
        ("🏗️ 实体", JAVA_BLUE, False),
        ("🛡️ 零直连", JAVA_BLUE, False),
    ]
    func_cards = []
    cw, ch = 4.0, 1.4
    gap_x, gap_y = 0.2, 0.2
    cx0 = (13.333 - 3 * cw - 2 * gap_x) / 2
    cy0 = 1.8
    for i, (name, color, killer) in enumerate(funcs):
        col, row = i % 3, i // 3
        x = cx0 + col * (cw + gap_x)
        y = cy0 + row * (ch + gap_y)
        card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                  Inches(x), Inches(y), Inches(cw), Inches(ch))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        if killer:
            card.line.color.rgb = GOLD
            card.line.width = Pt(3)
        else:
            card.line.color.rgb = DIVIDER
            card.line.width = Pt(1)
        styled_text(s, x, y + 0.4, cw, ch - 0.8,
                    name, size=18, color=color, bold=True)
        func_cards.append(card)

    # 金句
    styled_text(s, 0.5, 6.5, 12.333, 0.5,
                "★ AI 通过 5 个受限通道安全对话业务库,数据不出企业",
                size=18, color=GOLD, bold=True)

    # 11 动画:4 starter + 6 功能 + 3 chase(策略 C)
    for i in range(4):
        add_anim(s, starter_boxes[i], "fade_in",
                 delay_ms=i * 200, dur_ms=500)
    for i in range(6):
        add_anim(s, func_cards[i], "fade_in",
                 delay_ms=1000 + i * 200, dur_ms=500)
    # 3 杀手锏 chase pulse 错开 2s
    add_anim(s, func_cards[0], "pulse", delay_ms=15000, dur_ms=1500, loop=True)  # JSON CRUD
    add_anim(s, func_cards[1], "pulse", delay_ms=17000, dur_ms=1500, loop=True)  # Calcite
    add_anim(s, func_cards[2], "pulse", delay_ms=19000, dur_ms=1500, loop=True)  # MCP


def main():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    slide_1_cover(prs)
    slide_2_pain(prs)
    slide_3_position(prs)
    slide_4a_loom_intro(prs)
    slide_4b_loom_modules(prs)
    slide_5a_forge_intro(prs)
    slide_5b_forge_4plus6(prs)
    prs.save(str(OUTPUT))
    print(f"OK: {OUTPUT} (7 pages)")


if __name__ == "__main__":
    main()

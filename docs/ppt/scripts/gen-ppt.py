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


def main():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    slide_1_cover(prs)
    slide_2_pain(prs)
    prs.save(str(OUTPUT))
    print(f"OK: {OUTPUT} (2 pages)")


if __name__ == "__main__":
    main()

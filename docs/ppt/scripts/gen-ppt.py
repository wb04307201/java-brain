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
    """
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
    return main


def main():
    """空 main —— 后续 T1-T9 在此追加 slide_X 函数并注册到总账。"""
    pass


if __name__ == "__main__":
    main()

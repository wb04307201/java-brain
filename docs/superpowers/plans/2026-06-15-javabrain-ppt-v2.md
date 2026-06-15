# JavaBrain PPT v2 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 12 页 JavaBrain 答辩 PPT(白底 2.5D 乐高)+ 8 分钟视频(剪映追加录屏)。

**Architecture:** 单文件 `gen-ppt.py`(沿用旧 v16 骨架,~1500 行)负责 PPT 生成,新增 `gen-video.py`(~300 行)负责转视频。动画通过 python-pptx XML 注入支持 3 类:fade_in(一次性)/ pulse_loop(持续到翻页)/ chase_pulse(沿卡片追逐)。转视频管线:pptx → libreoffice → ffmpeg 逐页拼图 → 剪映追加录屏。

**Tech Stack:** python-pptx 1.x / lxml / Pillow (可选,仅用于错位检测) / libreoffice / ffmpeg

**Spec 引用:** `docs/superpowers/specs/2026-06-15-javabrain-ppt-v2-design.md`

---

## 总体里程碑

| 阶段 | 内容 | 工时 | 累计 |
|---|---|---:|---:|
| **T0** | gen-ppt.py 骨架(配色常量 + add_anim loop=True) | 2h | 2h |
| **T1** | P1 封面 | 1h | 3h |
| **T2** | P2 痛点 | 1h | 4h |
| **T3** | P3 + P4-a + P4-b | 2h | 6h |
| **T4** | P5-a + P5-b | 1.5h | 7.5h |
| **T5** | P6 + P7 工作流 | 1.5h | 9h |
| **T6** | P8 实战对比 | 1.5h | 10.5h |
| **T7** | P9 + P10 | 1.5h | 12h |
| **T8** | gen-video.py 转视频 | 2h | 14h |
| **T9** | 同步 OUTLINE.md + 提交 | 0.5h | 14.5h |

每个 Task 完成后**立即用 OnlyOffice 打开 javabrain.pptx 看效果**,不通过不进下一个。

---

## Task 0: 骨架与配色常量(2h)

**Files:**
- Modify: `docs/ppt/scripts/gen-ppt.py`(全文改写,保留工具函数)
- Create: `docs/ppt/tests/test_anim.py`(add_anim 单元测试)

- [ ] **Step 1: 写 add_anim 单元测试**

```python
# docs/ppt/tests/test_anim.py
"""add_anim() 工具函数测试。"""
import sys
from pathlib import Path

# 把 gen-ppt.py 当模块导入
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import gen_ppt  # noqa: E402

from lxml import etree  # noqa: E402


def test_fade_in_creates_timing_node():
    """fade_in 应在 slide 上生成 <p:timing> 节点。"""
    from pptx import Presentation
    from pptx.util import Inches

    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect = slide.shapes.add_shape(1, Inches(1), Inches(1), Inches(1), Inches(1))
    gen_ppt.add_anim(slide, rect, "fade_in", delay_ms=0, dur_ms=500, loop=False)
    xml = etree.tostring(slide._element).decode()
    assert "<p:timing" in xml
    assert 'presetClass="entr"' in xml
    assert 'presetId="10"' in xml


def test_pulse_loop_has_indefinite():
    """pulse_loop 应生成 repeatCount='indefinite'。"""
    from pptx import Presentation
    from pptx.util import Inches

    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect = slide.shapes.add_shape(1, Inches(1), Inches(1), Inches(1), Inches(1))
    gen_ppt.add_anim(slide, rect, "pulse", delay_ms=0, dur_ms=1500, loop=True)
    xml = etree.tostring(slide._element).decode()
    assert 'repeatCount="indefinite"' in xml


def test_chase_pulse_with_delay():
    """delay_ms 错开应生成对应的 begin 属性。"""
    from pptx import Presentation
    from pptx.util import Inches

    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect = slide.shapes.add_shape(1, Inches(1), Inches(1), Inches(1), Inches(1))
    gen_ppt.add_anim(slide, rect, "pulse", delay_ms=2000, dur_ms=1500, loop=True)
    xml = etree.tostring(slide._element).decode()
    assert '2000' in xml
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd docs/ppt && python -m pytest tests/test_anim.py -v`
Expected: ModuleNotFoundError: No module named 'gen_ppt' (因为还没实现)

- [ ] **Step 3: 重写 gen-ppt.py 头部(配色常量 + add_anim 工具)**

```python
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

# ============== 配色(7 色 + 4 中性) ==============
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

# ============== 动画类型 ==============
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
    loop=True:  生成 repeatCount="indefinite"(持续到翻页)
    """
    preset_class, preset_id = ANIM_PRESETS[anim_type]
    shape_id = shape.shape_id

    timing_xml = f'''<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:tnLst>
    <p:par>
      <p:pPr><p:spTree><p:nvGrpSpPr><p:cNvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:pPr>
      <p:par>
        <p:cond><p:tnCond val="0"/></p:cond>
        <p:par>
          <p:cTn id="{shape_id + 1}" nodeType="withEffect" dur="{dur_ms}" begin="{delay_ms}ms" fill="hold" {('repeatCount="indefinite"' if loop else '')}>
            <p:animEffect presetClass="{preset_class}" presetId="{preset_id}" dur="{dur_ms}"/>
          </p:cTn>
        </p:par>
      </p:par>
    </p:par>
  </p:tnLst>
</p:timing>'''
    timing_elem = etree.fromstring(timing_xml)
    slide._element.append(timing_elem)


# 后续 slide_X 函数在此文件中继续添加(见 Task 1-7)
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd docs/ppt && python -m pytest tests/test_anim.py -v`
Expected: 3 passed

- [ ] **Step 5: 提交**

```bash
cd docs/ppt
git add scripts/gen-ppt.py tests/test_anim.py
git commit -m "feat(ppt): 重写 gen-ppt.py v2 骨架(配色+add_anim 支持 loop)"
```

---

## Task 1: P1 封面(1h)

**Files:**
- Modify: `docs/ppt/scripts/gen-ppt.py`(`slide_1_cover` 函数)

- [ ] **Step 1: 实现 iso_lego() 工具**

在 gen-ppt.py 的 `add_anim` 之后添加:

```python
def iso_lego(slide, x_in, y_in, w_in, h_in, color, *, studs=True, highlight=True):
    """画一个 2.5D 乐高积木。
    圆角矩形主体 + 顶部 4 圆钉(studs) + 顶部高光条(highlight) + 软阴影。
    返回主形状(用于添加动画)。
    """
    In = Inches
    # 主体
    main = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                   In(x_in), In(y_in), In(w_in), In(h_in))
    main.fill.solid()
    main.fill.fore_color.rgb = color
    main.line.fill.background()  # 无边框
    # 软阴影通过 outerShdw XML 实现(略,本版本先不画,改用主线无边框)
    if studs:
        stud_r = min(w_in, h_in) * 0.07  # 圆钉直径 = 短边 × 14%
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
        # 设置 alpha 30%(通过 XML)
        from pptx.oxml.ns import qn
        sppr = hl.fill._xPr.find(qn("p:spPr"))
        # 简化:用渐变代替(略,本版省略高光)
        hl.fill.fore_color.rgb = WHITE
        hl.line.fill.background()
    return main
```

- [ ] **Step 2: 实现 slide_1_cover 函数**

```python
def slide_1_cover(prs):
    """P1 封面:3 乐高 + JavaBrain 大字 + 金钩子 + 5 动画"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    # 3 乐高横排(蓝紫绿)
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

    # JavaBrain 大字
    tb_title = s.shapes.add_textbox(Inches(1.0), Inches(3.4),
                                     Inches(11.333), Inches(1.2))
    tf = tb_title.text_frame
    tf.text = "JavaBrain"
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.name = FONT_EN
    run.font.size = Pt(72)
    run.font.bold = True
    run.font.color.rgb = TEXT_PRIMARY

    # 副标
    tb_sub = s.shapes.add_textbox(Inches(1.0), Inches(4.6),
                                   Inches(11.333), Inches(0.5))
    tf2 = tb_sub.text_frame
    tf2.text = "让 Spring Boot 秒变 AI 中枢"
    p2 = tf2.paragraphs[0]
    p2.alignment = PP_ALIGN.CENTER
    run2 = p2.runs[0]
    run2.font.name = FONT_CN
    run2.font.size = Pt(24)
    run2.font.color.rgb = TEXT_SECONDARY

    # 金钩子
    hook_box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                   Inches(4.0), Inches(5.5),
                                   Inches(5.333), Inches(0.6))
    hook_box.fill.solid()
    hook_box.fill.fore_color.rgb = GOLD
    hook_box.line.fill.background()
    tf3 = hook_box.text_frame
    tf3.text = "3 组件 · 1 starter · 0 漂移"
    p3 = tf3.paragraphs[0]
    p3.alignment = PP_ALIGN.CENTER
    run3 = p3.runs[0]
    run3.font.name = FONT_CN
    run3.font.size = Pt(18)
    run3.font.bold = True
    run3.font.color.rgb = WHITE

    # ====== 5 个动画 ======
    add_anim(s, legos[0], "fade_in", delay_ms=0, dur_ms=500)
    add_anim(s, legos[1], "fade_in", delay_ms=300, dur_ms=500)
    add_anim(s, legos[2], "fade_in", delay_ms=600, dur_ms=500)
    add_anim(s, tb_title, "fade_in", delay_ms=900, dur_ms=500)
    add_anim(s, hook_box, "fade_in", delay_ms=1400, dur_ms=500)
```

- [ ] **Step 3: 在文件末尾加 main() 跑 P1**

```python
def main():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    slide_1_cover(prs)
    prs.save(str(OUTPUT))
    print(f"OK: {OUTPUT}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 运行 gen-ppt.py 验证**

Run: `cd docs/ppt && python scripts/gen-ppt.py`
Expected: `OK: C:\...\javabrain.pptx`

- [ ] **Step 5: OnlyOffice 打开 javabrain.pptx 看效果**

用 OnlyOffice 打开 `docs/ppt/javabrain.pptx`,确认:
- 3 乐高横排(蓝/紫/绿)
- "JavaBrain" 大字居中
- 金色"3 组件·1 starter" 钩子
- 5 元素按 0/300/600/900/1400ms 依次入场

- [ ] **Step 6: 提交**

```bash
cd docs/ppt
git add scripts/gen-ppt.py
git commit -m "feat(ppt): 实现 P1 封面(3 乐高+大字+金钩+5 动画)"
```

---

## Task 2: P2 痛点(1h)

**Files:**
- Modify: `docs/ppt/scripts/gen-ppt.py`(`slide_2_pain` 函数 + 更新 main)

- [ ] **Step 1: 实现 slide_2_pain 函数**

```python
def slide_2_pain(prs):
    """P2 痛点:3 红 vs 3 绿 + 杀手锏金边 pulse_loop"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    # 标题
    tb_t = s.shapes.add_textbox(Inches(0.5), Inches(0.4),
                                 Inches(12.333), Inches(0.6))
    tf = tb_t.text_frame
    tf.text = "接入 AI 的 3 个痛点 vs JavaBrain 的 3 个解法"
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.name = FONT_CN
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = TEXT_PRIMARY

    # 左半:3 红字
    reds = [("3 月", 0), ("5 天", 1), ("3 天", 2)]
    red_boxes = []
    for i, (txt, _) in enumerate(reds):
        tb = s.shapes.add_textbox(Inches(0.5), Inches(2.0 + i * 1.3),
                                   Inches(4.5), Inches(1.0))
        tf = tb.text_frame
        tf.text = txt
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.runs[0]
        run.font.name = FONT_EN
        run.font.size = Pt(48)
        run.font.bold = True
        run.font.color.rgb = SEMANTIC_RED
        red_boxes.append(tb)

    # 中间箭头
    tb_arrow = s.shapes.add_textbox(Inches(5.0), Inches(3.4),
                                      Inches(3.333), Inches(1.0))
    tf_a = tb_arrow.text_frame
    tf_a.text = "→"
    p_a = tf_a.paragraphs[0]
    p_a.alignment = PP_ALIGN.CENTER
    run_a = p_a.runs[0]
    run_a.font.name = FONT_EN
    run_a.font.size = Pt(72)
    run_a.font.bold = True
    run_a.font.color.rgb = GOLD

    # 右半:3 绿字
    greens = [("3 分", 0), ("90 秒", 1), ("10 分", 2)]
    green_boxes = []
    for i, (txt, _) in enumerate(greens):
        tb = s.shapes.add_textbox(Inches(8.333), Inches(2.0 + i * 1.3),
                                   Inches(4.5), Inches(1.0))
        tf = tb.text_frame
        tf.text = txt
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.runs[0]
        run.font.name = FONT_EN
        run.font.size = Pt(48)
        run.font.bold = True
        run.font.color.rgb = SEMANTIC_GREEN
        green_boxes.append(tb)

    # 杀手锏金边"3 月 vs 3 分"(pulse_loop)
    hook = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                Inches(3.5), Inches(6.3),
                                Inches(6.333), Inches(0.7))
    hook.fill.solid()
    hook.fill.fore_color.rgb = GOLD_BG
    hook.line.color.rgb = GOLD
    hook.line.width = Pt(3)
    tf_h = hook.text_frame
    tf_h.text = "★ 3 月 vs 3 分 = 1440 倍效率提升"
    p_h = tf_h.paragraphs[0]
    p_h.alignment = PP_ALIGN.CENTER
    run_h = p_h.runs[0]
    run_h.font.name = FONT_CN
    run_h.font.size = Pt(20)
    run_h.font.bold = True
    run_h.font.color.rgb = GOLD

    # ====== 8 个动画 ======
    add_anim(s, red_boxes[0], "fade_in", delay_ms=0, dur_ms=500)
    add_anim(s, red_boxes[1], "fade_in", delay_ms=600, dur_ms=500)
    add_anim(s, red_boxes[2], "fade_in", delay_ms=1200, dur_ms=500)
    add_anim(s, tb_arrow, "fade_in", delay_ms=2000, dur_ms=500)
    add_anim(s, green_boxes[0], "fade_in", delay_ms=2800, dur_ms=500)
    add_anim(s, green_boxes[1], "fade_in", delay_ms=3400, dur_ms=500)
    add_anim(s, green_boxes[2], "fade_in", delay_ms=4000, dur_ms=500)
    add_anim(s, hook, "pulse", delay_ms=5000, dur_ms=1500, loop=True)  # ★ 持续脉冲
```

- [ ] **Step 2: 更新 main()**

```python
def main():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    slide_1_cover(prs)
    slide_2_pain(prs)
    prs.save(str(OUTPUT))
    print(f"OK: {OUTPUT}")
```

- [ ] **Step 3: 运行 + OnlyOffice 验证**

Run: `cd docs/ppt && python scripts/gen-ppt.py`
- 打开 javabrain.pptx,确认 8 元素按序入场,金边"★ 3 月 vs 3 分"持续脉冲

- [ ] **Step 4: 提交**

```bash
git add scripts/gen-ppt.py
git commit -m "feat(ppt): 实现 P2 痛点(3 红 vs 3 绿 + 杀手锏金边 pulse_loop)"
```

---

## Task 3: P3 + P4-a + P4-b(2h)

**Files:**
- Modify: `docs/ppt/scripts/gen-ppt.py`(3 个 slide 函数 + main)

- [ ] **Step 1: slide_3_position (定位)**

```python
def slide_3_position(prs):
    """P3 定位:3 乐高+4 行 ✓"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    # 主标
    tb_t = s.shapes.add_textbox(Inches(0.5), Inches(0.4),
                                 Inches(12.333), Inches(0.7))
    tf = tb_t.text_frame
    tf.text = "JavaBrain = 灵梭 + SQL工坊 + SQL工坊 MCP"
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.name = FONT_CN
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = TEXT_PRIMARY

    # 3 乐高横排(蓝紫绿,小尺寸)
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
        tb_l = s.shapes.add_textbox(Inches(x - 0.3), Inches(lego_y + lego_size + 0.05),
                                      Inches(lego_size + 0.6), Inches(0.3))
        tf_l = tb_l.text_frame
        tf_l.text = label
        p_l = tf_l.paragraphs[0]
        p_l.alignment = PP_ALIGN.CENTER
        run_l = p_l.runs[0]
        run_l.font.name = FONT_CN
        run_l.font.size = Pt(12)
        run_l.font.bold = True
        run_l.font.color.rgb = color

    # 4 行 ✓
    items = [
        ("✓ 三个都是依赖库,不是产品", GOLD, True),  # 金色杀手锏
        ("✓ 组件化、按需引入,各自独立可用", TEXT_PRIMARY, False),
        ("✓ ├── 灵梭 / SQL工坊 / SQL工坊 MCP 都可单独用", TEXT_SECONDARY, False),
        ("✓ 组合起来 = 企业 AI 落地完整闭环", TEXT_PRIMARY, False),
    ]
    item_boxes = []
    for i, (text, color, _) in enumerate(items):
        tb = s.shapes.add_textbox(Inches(1.5), Inches(3.5 + i * 0.6),
                                   Inches(10.333), Inches(0.5))
        tf = tb.text_frame
        tf.text = text
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        run = p.runs[0]
        run.font.name = FONT_CN
        run.font.size = Pt(18)
        run.font.bold = (i == 0)
        run.font.color.rgb = color
        item_boxes.append(tb)

    # 4 动画
    add_anim(s, tb_t, "fade_in", delay_ms=0, dur_ms=500)
    add_anim(s, legos[0], "fade_in", delay_ms=600, dur_ms=500)
    add_anim(s, item_boxes[0], "fade_in", delay_ms=1200, dur_ms=500)
    add_anim(s, item_boxes[0], "pulse", delay_ms=2000, dur_ms=1500, loop=True)  # 首行金脉冲
```

- [ ] **Step 2: slide_4a_loom_intro (灵梭整体)**

```python
def slide_4a_loom_intro(prs):
    """P4-a 灵梭 · 整体定位"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    # 小标
    tb_s = s.shapes.add_textbox(Inches(0.5), Inches(0.4),
                                 Inches(12.333), Inches(0.4))
    tf = tb_s.text_frame
    tf.text = "灵梭 · LoomAgent"
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.name = FONT_EN
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = JAVA_BLUE

    # 主标
    tb_t = s.shapes.add_textbox(Inches(0.5), Inches(1.0),
                                 Inches(12.333), Inches(1.0))
    tf = tb_t.text_frame
    tf.text = "Spring AI 一键启动 · 改 .st 文件 AI 行为就变"
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.name = FONT_CN
    run.font.size = Pt(32)
    run.font.bold = True
    run.font.color.rgb = TEXT_PRIMARY

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
        tf_c = card.text_frame
        tf_c.text = text
        p_c = tf_c.paragraphs[0]
        p_c.alignment = PP_ALIGN.CENTER
        run_c = p_c.runs[0]
        run_c.font.name = FONT_CN
        run_c.font.size = Pt(18)
        run_c.font.bold = True
        run_c.font.color.rgb = color
        cards.append(card)

    # 引导
    tb_next = s.shapes.add_textbox(Inches(0.5), Inches(6.0),
                                    Inches(12.333), Inches(0.4))
    tf_n = tb_next.text_frame
    tf_n.text = "▼ 下一页 · 6 大功能模块"
    p_n = tf_n.paragraphs[0]
    p_n.alignment = PP_ALIGN.CENTER
    run_n = p_n.runs[0]
    run_n.font.name = FONT_CN
    run_n.font.size = Pt(16)
    run_n.font.bold = True
    run_n.font.color.rgb = AI_PURPLE

    # 4 动画
    add_anim(s, tb_t, "fade_in", delay_ms=0, dur_ms=500)
    add_anim(s, cards[0], "fade_in", delay_ms=600, dur_ms=500)
    add_anim(s, tb_next, "fade_in", delay_ms=1200, dur_ms=500)
    add_anim(s, cards[2], "pulse", delay_ms=1800, dur_ms=1500, loop=True)  # Skill 金脉冲
```

- [ ] **Step 3: slide_4b_loom_modules (灵梭 6 模块)**

```python
def slide_4b_loom_modules(prs):
    """P4-b 灵梭 · 6 模块功能 + 2 杀手锏 chase"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    # 标题
    tb_t = s.shapes.add_textbox(Inches(0.5), Inches(0.4),
                                 Inches(12.333), Inches(0.6))
    tf = tb_t.text_frame
    tf.text = "灵梭 · 6 大功能模块"
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.name = FONT_CN
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = TEXT_PRIMARY

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
        # 文字
        tf_c = card.text_frame
        tf_c.text = name
        p_c = tf_c.paragraphs[0]
        p_c.alignment = PP_ALIGN.CENTER
        run_c = p_c.runs[0]
        run_c.font.name = FONT_CN
        run_c.font.size = Pt(20)
        run_c.font.bold = True
        run_c.font.color.rgb = color
        # desc
        tb_d = s.shapes.add_textbox(Inches(x), Inches(y + 0.9),
                                      Inches(cw), Inches(0.5))
        tf_d = tb_d.text_frame
        tf_d.text = desc
        p_d = tf_d.paragraphs[0]
        p_d.alignment = PP_ALIGN.CENTER
        run_d = p_d.runs[0]
        run_d.font.name = FONT_CN
        run_d.font.size = Pt(14)
        run_d.font.color.rgb = TEXT_SECONDARY
        cards.append(card)

    # 底部金句
    tb_killer = s.shapes.add_textbox(Inches(0.5), Inches(6.5),
                                      Inches(12.333), Inches(0.5))
    tf_k = tb_killer.text_frame
    tf_k.text = "★ 改一个 .st 文件,AI 行为就变"
    p_k = tf_k.paragraphs[0]
    p_k.alignment = PP_ALIGN.CENTER
    run_k = p_k.runs[0]
    run_k.font.name = FONT_CN
    run_k.font.size = Pt(20)
    run_k.font.bold = True
    run_k.font.color.rgb = GOLD

    # 8 动画:6 入场 + 2 chase
    for i in range(6):
        add_anim(s, cards[i], "fade_in",
                 delay_ms=i * 200, dur_ms=500)
    # 2 杀手锏金边 chase(错开 2s)
    add_anim(s, cards[1], "pulse", delay_ms=10000, dur_ms=1500, loop=True)
    add_anim(s, cards[2], "pulse", delay_ms=12000, dur_ms=1500, loop=True)
```

- [ ] **Step 4: 更新 main() 跑 P3 + P4-a + P4-b**

```python
def main():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    slide_1_cover(prs)
    slide_2_pain(prs)
    slide_3_position(prs)
    slide_4a_loom_intro(prs)
    slide_4b_loom_modules(prs)
    prs.save(str(OUTPUT))
    print(f"OK: {OUTPUT}")
```

- [ ] **Step 5: 运行 + OnlyOffice 验证**

Run: `cd docs/ppt && python scripts/gen-ppt.py`
- 打开确认 5 页顺序,3 乐高立体感,2 杀手锏金边 chase 错开 2s

- [ ] **Step 6: 提交**

```bash
git add scripts/gen-ppt.py
git commit -m "feat(ppt): 实现 P3 定位 + P4-a 灵梭整体 + P4-b 6 模块(2 chase)"
```

---

## Task 4: P5-a + P5-b(1.5h)

**Files:**
- Modify: `docs/ppt/scripts/gen-ppt.py`(2 个 slide 函数 + main)

- [ ] **Step 1: slide_5a_forge_intro (SQL工坊整体)**

```python
def slide_5a_forge_intro(prs):
    """P5-a SQL工坊 · 整体定位"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    tb_s = s.shapes.add_textbox(Inches(0.5), Inches(0.4),
                                 Inches(12.333), Inches(0.4))
    tf = tb_s.text_frame
    tf.text = "SQL工坊 · SQL Forge"
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.name = FONT_EN
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = AI_PURPLE

    tb_t = s.shapes.add_textbox(Inches(0.5), Inches(1.0),
                                 Inches(12.333), Inches(1.0))
    tf = tb_t.text_frame
    tf.text = "JSON CRUD + Calcite 联邦 + Amis 低代码"
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.name = FONT_CN
    run.font.size = Pt(32)
    run.font.bold = True
    run.font.color.rgb = TEXT_PRIMARY

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
        tf_c = card.text_frame
        tf_c.text = text
        p_c = tf_c.paragraphs[0]
        p_c.alignment = PP_ALIGN.CENTER
        run_c = p_c.runs[0]
        run_c.font.name = FONT_CN
        run_c.font.size = Pt(18)
        run_c.font.bold = True
        run_c.font.color.rgb = color
        cards.append(card)

    tb_next = s.shapes.add_textbox(Inches(0.5), Inches(6.0),
                                    Inches(12.333), Inches(0.4))
    tf_n = tb_next.text_frame
    tf_n.text = "▼ 下一页 · 4 starter + 6 功能"
    p_n = tf_n.paragraphs[0]
    p_n.alignment = PP_ALIGN.CENTER
    run_n = p_n.runs[0]
    run_n.font.name = FONT_CN
    run_n.font.size = Pt(16)
    run_n.font.bold = True
    run_n.font.color.rgb = AI_PURPLE

    add_anim(s, tb_t, "fade_in", delay_ms=0, dur_ms=500)
    add_anim(s, cards[0], "fade_in", delay_ms=600, dur_ms=500)
    add_anim(s, tb_next, "fade_in", delay_ms=1200, dur_ms=500)
    add_anim(s, cards[3], "pulse", delay_ms=1800, dur_ms=1500, loop=True)  # 数据不出企业
```

- [ ] **Step 2: slide_5b_forge_4plus6 (SQL工坊 4+6)**

```python
def slide_5b_forge_4plus6(prs):
    """P5-b SQL工坊 · 4 starter + 6 功能 + 3 chase"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    tb_t = s.shapes.add_textbox(Inches(0.5), Inches(0.3),
                                 Inches(12.333), Inches(0.5))
    tf = tb_t.text_frame
    tf.text = "SQL工坊 · 4 starter + 6 功能"
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.name = FONT_CN
    run.font.size = Pt(24)
    run.font.bold = True
    run.font.color.rgb = TEXT_PRIMARY

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
        tf_b = box.text_frame
        tf_b.text = name
        p_b = tf_b.paragraphs[0]
        p_b.alignment = PP_ALIGN.CENTER
        run_b = p_b.runs[0]
        run_b.font.name = FONT_MONO
        run_b.font.size = Pt(11)
        run_b.font.color.rgb = WHITE
        run_b.font.bold = True
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
        tf_c = card.text_frame
        tf_c.text = name
        p_c = tf_c.paragraphs[0]
        p_c.alignment = PP_ALIGN.CENTER
        run_c = p_c.runs[0]
        run_c.font.name = FONT_CN
        run_c.font.size = Pt(18)
        run_c.font.bold = True
        run_c.font.color.rgb = color
        func_cards.append(card)

    # 金句
    tb_k = s.shapes.add_textbox(Inches(0.5), Inches(6.5),
                                 Inches(12.333), Inches(0.5))
    tf_k = tb_k.text_frame
    tf_k.text = "★ AI 通过 5 个受限通道安全对话业务库,数据不出企业"
    p_k = tf_k.paragraphs[0]
    p_k.alignment = PP_ALIGN.CENTER
    run_k = p_k.runs[0]
    run_k.font.name = FONT_CN
    run_k.font.size = Pt(18)
    run_k.font.bold = True
    run_k.font.color.rgb = GOLD

    # 11 动画:4 starter + 6 功能 + 1 金句
    for i in range(4):
        add_anim(s, starter_boxes[i], "fade_in",
                 delay_ms=i * 200, dur_ms=500)
    for i in range(6):
        add_anim(s, func_cards[i], "fade_in",
                 delay_ms=1000 + i * 200, dur_ms=500)
    # 3 杀手锏 chase 错开 2s
    add_anim(s, func_cards[0], "pulse", delay_ms=15000, dur_ms=1500, loop=True)
    add_anim(s, func_cards[1], "pulse", delay_ms=17000, dur_ms=1500, loop=True)
    add_anim(s, func_cards[2], "pulse", delay_ms=19000, dur_ms=1500, loop=True)
```

- [ ] **Step 3: 更新 main()**

```python
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
    print(f"OK: {OUTPUT}")
```

- [ ] **Step 4: 运行 + OnlyOffice 验证 7 页顺序 + 3 chase**

- [ ] **Step 5: 提交**

```bash
git add scripts/gen-ppt.py
git commit -m "feat(ppt): 实现 P5-a SQL工坊整体 + P5-b 4+6(3 chase)"
```

---

## Task 5: P6 + P7 演示工作流(1.5h)

**Files:**
- Modify: `docs/ppt/scripts/gen-ppt.py`(2 个 slide 函数 + main)

- [ ] **Step 1: slide_6_demo1_workflow (演示 1 工作流)**

```python
def slide_6_demo1_workflow(prs):
    """P6 演示 1 · 5 步工作流(策略 D)"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    # 标题
    tb_t = s.shapes.add_textbox(Inches(0.5), Inches(0.6),
                                 Inches(12.333), Inches(0.5))
    tf = tb_t.text_frame
    tf.text = "演示 1 · 一句话出分析报告"
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.name = FONT_CN
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = TEXT_PRIMARY

    # 用户原话
    tb_q = s.shapes.add_textbox(Inches(0.5), Inches(1.3),
                                 Inches(12.333), Inches(0.4))
    tf_q = tb_q.text_frame
    tf_q.text = '"上个月各品类销量怎么样?"'
    p_q = tf_q.paragraphs[0]
    p_q.alignment = PP_ALIGN.CENTER
    run_q = p_q.runs[0]
    run_q.font.name = FONT_CN
    run_q.font.size = Pt(18)
    run_q.font.italic = True
    run_q.font.color.rgb = TEXT_SECONDARY

    # 5 步横向卡片
    steps = [
        ("S1", "👤 用户提问", TEXT_SECONDARY),
        ("S2", "🧠 NL2SQL", JAVA_BLUE),
        ("S3", "📊 读表", JAVA_BLUE),
        ("S4", "⚙️ 跨库 JOIN", JAVA_BLUE),
        ("S5", "📄 报告", GOLD),  # 末步金
    ]
    step_boxes = []
    sw, sh = 2.0, 2.5
    gap = 0.3
    total_w = 5 * sw + 4 * gap
    sx0 = (13.333 - total_w) / 2
    sy = 2.5
    for i, (num, name, color) in enumerate(steps):
        x = sx0 + i * (sw + gap)
        box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                   Inches(x), Inches(sy), Inches(sw), Inches(sh))
        box.fill.solid()
        if color == GOLD:
            box.fill.fore_color.rgb = GOLD_BG
        else:
            box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = color
        box.line.width = Pt(3) if color == GOLD else Pt(1)
        # S1-S5 标签
        tb_n = s.shapes.add_textbox(Inches(x), Inches(sy + 0.2),
                                      Inches(sw), Inches(0.4))
        tf_n = tb_n.text_frame
        tf_n.text = num
        p_n = tf_n.paragraphs[0]
        p_n.alignment = PP_ALIGN.CENTER
        run_n = p_n.runs[0]
        run_n.font.name = FONT_EN
        run_n.font.size = Pt(14)
        run_n.font.bold = True
        run_n.font.color.rgb = color
        # 步骤名
        tb_m = s.shapes.add_textbox(Inches(x), Inches(sy + 0.8),
                                      Inches(sw), Inches(1.5))
        tf_m = tb_m.text_frame
        tf_m.text = name
        p_m = tf_m.paragraphs[0]
        p_m.alignment = PP_ALIGN.CENTER
        run_m = p_m.runs[0]
        run_m.font.name = FONT_CN
        run_m.font.size = Pt(16)
        run_m.font.bold = True
        run_m.font.color.rgb = color
        step_boxes.append(box)

    # 箭头(4 个)
    arrows = []
    for i in range(4):
        x = sx0 + (i + 1) * sw + i * gap + 0.05
        tb_a = s.shapes.add_textbox(Inches(x), Inches(sy + sh/2 - 0.2),
                                      Inches(gap - 0.1), Inches(0.4))
        tf_a = tb_a.text_frame
        tf_a.text = "→"
        p_a = tf_a.paragraphs[0]
        p_a.alignment = PP_ALIGN.CENTER
        run_a = p_a.runs[0]
        run_a.font.name = FONT_EN
        run_a.font.size = Pt(20)
        run_a.font.bold = True
        run_a.font.color.rgb = GOLD
        arrows.append(tb_a)

    # 底部金句
    tb_k = s.shapes.add_textbox(Inches(0.5), Inches(6.0),
                                 Inches(12.333), Inches(0.5))
    tf_k = tb_k.text_frame
    tf_k.text = "▼ 接下来看 42 秒真实录屏"
    p_k = tf_k.paragraphs[0]
    p_k.alignment = PP_ALIGN.CENTER
    run_k = p_k.runs[0]
    run_k.font.name = FONT_CN
    run_k.font.size = Pt(18)
    run_k.font.bold = True
    run_k.font.color.rgb = AI_PURPLE

    # 6 动画:5 步 0/1/2/3/4s 入场 + 末步 pulse
    for i in range(5):
        add_anim(s, step_boxes[i], "fade_in",
                 delay_ms=i * 1000, dur_ms=500)
    add_anim(s, step_boxes[4], "pulse", delay_ms=4500, dur_ms=1500, loop=True)
```

- [ ] **Step 2: slide_7_demo2_workflow (演示 2 工作流)**

```python
def slide_7_demo2_workflow(prs):
    """P7 演示 2 · 5 步工作流"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    tb_t = s.shapes.add_textbox(Inches(0.5), Inches(0.6),
                                 Inches(12.333), Inches(0.5))
    tf = tb_t.text_frame
    tf.text = "演示 2 · 一句话生成 CRUD"
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.name = FONT_CN
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = TEXT_PRIMARY

    tb_q = s.shapes.add_textbox(Inches(0.5), Inches(1.3),
                                 Inches(12.333), Inches(0.4))
    tf_q = tb_q.text_frame
    tf_q.text = '"做一个商品管理 CRUD 页面"'
    p_q = tf_q.paragraphs[0]
    p_q.alignment = PP_ALIGN.CENTER
    run_q = p_q.runs[0]
    run_q.font.name = FONT_CN
    run_q.font.size = Pt(18)
    run_q.font.italic = True
    run_q.font.color.rgb = TEXT_SECONDARY

    steps = [
        ("S1", "👤 用户提问", TEXT_SECONDARY),
        ("S2", "🧠 web.st", AI_PURPLE),
        ("S3", "📊 读表", AI_PURPLE),
        ("S4", "🔧 生成 Amis", AI_PURPLE),
        ("S5", "🌐 URL", GOLD),
    ]
    step_boxes = []
    sw, sh = 2.0, 2.5
    gap = 0.3
    total_w = 5 * sw + 4 * gap
    sx0 = (13.333 - total_w) / 2
    sy = 2.5
    for i, (num, name, color) in enumerate(steps):
        x = sx0 + i * (sw + gap)
        box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                   Inches(x), Inches(sy), Inches(sw), Inches(sh))
        box.fill.solid()
        if color == GOLD:
            box.fill.fore_color.rgb = GOLD_BG
        else:
            box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = color
        box.line.width = Pt(3) if color == GOLD else Pt(1)
        tb_n = s.shapes.add_textbox(Inches(x), Inches(sy + 0.2),
                                      Inches(sw), Inches(0.4))
        tf_n = tb_n.text_frame
        tf_n.text = num
        p_n = tf_n.paragraphs[0]
        p_n.alignment = PP_ALIGN.CENTER
        run_n = p_n.runs[0]
        run_n.font.name = FONT_EN
        run_n.font.size = Pt(14)
        run_n.font.bold = True
        run_n.font.color.rgb = color
        tb_m = s.shapes.add_textbox(Inches(x), Inches(sy + 0.8),
                                      Inches(sw), Inches(1.5))
        tf_m = tb_m.text_frame
        tf_m.text = name
        p_m = tf_m.paragraphs[0]
        p_m.alignment = PP_ALIGN.CENTER
        run_m = p_m.runs[0]
        run_m.font.name = FONT_CN
        run_m.font.size = Pt(16)
        run_m.font.bold = True
        run_m.font.color.rgb = color
        step_boxes.append(box)

    for i in range(4):
        x = sx0 + (i + 1) * sw + i * gap + 0.05
        tb_a = s.shapes.add_textbox(Inches(x), Inches(sy + sh/2 - 0.2),
                                      Inches(gap - 0.1), Inches(0.4))
        tf_a = tb_a.text_frame
        tf_a.text = "→"
        p_a = tf_a.paragraphs[0]
        p_a.alignment = PP_ALIGN.CENTER
        run_a = p_a.runs[0]
        run_a.font.name = FONT_EN
        run_a.font.size = Pt(20)
        run_a.font.bold = True
        run_a.font.color.rgb = GOLD

    tb_k = s.shapes.add_textbox(Inches(0.5), Inches(6.0),
                                 Inches(12.333), Inches(0.5))
    tf_k = tb_k.text_frame
    tf_k.text = "▼ 接下来看 40 秒真实录屏"
    p_k = tf_k.paragraphs[0]
    p_k.alignment = PP_ALIGN.CENTER
    run_k = p_k.runs[0]
    run_k.font.name = FONT_CN
    run_k.font.size = Pt(18)
    run_k.font.bold = True
    run_k.font.color.rgb = AI_PURPLE

    for i in range(5):
        add_anim(s, step_boxes[i], "fade_in",
                 delay_ms=i * 1000, dur_ms=500)
    add_anim(s, step_boxes[4], "pulse", delay_ms=4500, dur_ms=1500, loop=True)
```

- [ ] **Step 3: 更新 main()**

```python
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
    slide_6_demo1_workflow(prs)
    slide_7_demo2_workflow(prs)
    prs.save(str(OUTPUT))
    print(f"OK: {OUTPUT}")
```

- [ ] **Step 4: 运行 + OnlyOffice 验证 9 页 + P6/P7 5 步顺序入场**

- [ ] **Step 5: 提交**

```bash
git add scripts/gen-ppt.py
git commit -m "feat(ppt): 实现 P6/P7 演示 1/2 工作流(5 步策略 D)"
```

---

## Task 6: P8 实战对比(1.5h)

**Files:**
- Modify: `docs/ppt/scripts/gen-ppt.py`

- [ ] **Step 1: slide_8_compare 函数**

```python
def slide_8_compare(prs):
    """P8 实战对比 · 4 ✓ + 5 行对比表 + 杀手锏金脉冲"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    tb_t = s.shapes.add_textbox(Inches(0.5), Inches(0.4),
                                 Inches(12.333), Inches(0.6))
    tf = tb_t.text_frame
    tf.text = "实战测试 · 7 张表 / 0 漂移 / 节省 >80%"
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.name = FONT_CN
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = TEXT_PRIMARY

    # 左半:技术派 4 行 ✓
    tb_l = s.shapes.add_textbox(Inches(0.5), Inches(1.3),
                                 Inches(5.5), Inches(0.4))
    tf_l = tb_l.text_frame
    tf_l.text = "技术派 · 4 项测试"
    p_l = tf_l.paragraphs[0]
    p_l.alignment = PP_ALIGN.LEFT
    run_l = p_l.runs[0]
    run_l.font.name = FONT_CN
    run_l.font.size = Pt(18)
    run_l.font.bold = True
    run_l.font.color.rgb = JAVA_BLUE

    items_tech = [
        "✓ 7 张表测试(简单/字典/自关联/多外键)",
        "✓ 0 漂移 / 0 错误链接 / 0 中文乱码",
        "✓ 5/5 AI 字段推断自检通过",
        "✓ 节省 CRUD 开发时间 >80%",
    ]
    tech_boxes = []
    for i, txt in enumerate(items_tech):
        tb = s.shapes.add_textbox(Inches(0.7), Inches(1.9 + i * 0.7),
                                   Inches(6.0), Inches(0.5))
        tf = tb.text_frame
        tf.text = txt
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        run = p.runs[0]
        run.font.name = FONT_CN
        run.font.size = Pt(16)
        is_killer = "80%" in txt
        run.font.bold = is_killer
        run.font.color.rgb = GOLD if is_killer else TEXT_PRIMARY
        tech_boxes.append(tb)

    # 右半:商业派 5 行对比表
    tb_r = s.shapes.add_textbox(Inches(7.0), Inches(1.3),
                                 Inches(5.5), Inches(0.4))
    tf_r = tb_r.text_frame
    tf_r.text = "商业派 · 5 项对比"
    p_r = tf_r.paragraphs[0]
    p_r.alignment = PP_ALIGN.LEFT
    run_r = p_r.runs[0]
    run_r.font.name = FONT_CN
    run_r.font.size = Pt(18)
    run_r.font.bold = True
    run_r.font.color.rgb = AI_PURPLE

    rows_biz = [
        "业务取数",
        "CRUD 页面",
        "跨库 JOIN",
        "私有化",
        "列名识别",
    ]
    biz_boxes = []
    for i, txt in enumerate(rows_biz):
        # 行背景
        bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                  Inches(7.0), Inches(1.9 + i * 0.5),
                                  Inches(5.5), Inches(0.45))
        bg.fill.solid()
        bg.fill.fore_color.rgb = GREEN_BG if i % 2 == 0 else WHITE
        bg.line.color.rgb = DIVIDER
        bg.line.width = Pt(1)
        # 行文字
        tb = s.shapes.add_textbox(Inches(7.2), Inches(1.95 + i * 0.5),
                                   Inches(3.5), Inches(0.4))
        tf = tb.text_frame
        tf.text = txt
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        run = p.runs[0]
        run.font.name = FONT_CN
        run.font.size = Pt(16)
        run.font.color.rgb = TEXT_PRIMARY
        # ✓
        tb_c = s.shapes.add_textbox(Inches(10.8), Inches(1.95 + i * 0.5),
                                      Inches(1.5), Inches(0.4))
        tf_c = tb_c.text_frame
        tf_c.text = "✓"
        p_c = tf_c.paragraphs[0]
        p_c.alignment = PP_ALIGN.CENTER
        run_c = p_c.runs[0]
        run_c.font.name = FONT_EN
        run_c.font.size = Pt(18)
        run_c.font.bold = True
        run_c.font.color.rgb = SEMANTIC_GREEN
        biz_boxes.append(tb)

    # 底部金句
    tb_k = s.shapes.add_textbox(Inches(0.5), Inches(6.0),
                                 Inches(12.333), Inches(0.5))
    tf_k = tb_k.text_frame
    tf_k.text = "★ JavaBrain 在 安全 + 智能 + 私有化 三角都做到"
    p_k = tf_k.paragraphs[0]
    p_k.alignment = PP_ALIGN.CENTER
    run_k = p_k.runs[0]
    run_k.font.name = FONT_CN
    run_k.font.size = Pt(20)
    run_k.font.bold = True
    run_k.font.color.rgb = GOLD

    # 10 动画
    for i in range(4):
        add_anim(s, tech_boxes[i], "fade_in",
                 delay_ms=i * 600, dur_ms=500)
    for i in range(5):
        add_anim(s, biz_boxes[i], "fade_in",
                 delay_ms=3000 + i * 700, dur_ms=500)
    add_anim(s, tech_boxes[3], "pulse", delay_ms=12000, dur_ms=1500, loop=True)  # >80% 脉冲
```

- [ ] **Step 2: 更新 main() + 验证 + 提交**

```python
# main() 加 slide_8_compare(prs)
# git commit -m "feat(ppt): 实现 P8 实战对比(4 ✓ + 5 行对比 + >80% 脉冲)"
```

---

## Task 7: P9 + P10(1.5h)

**Files:**
- Modify: `docs/ppt/scripts/gen-ppt.py`

- [ ] **Step 1: slide_9_roadmap**

```python
def slide_9_roadmap(prs):
    """P9 路线图 · 3 仓库 + V1.0-V1.3 时间线 + V1.0 金脉冲"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    tb_t = s.shapes.add_textbox(Inches(0.5), Inches(0.4),
                                 Inches(12.333), Inches(0.6))
    tf = tb_t.text_frame
    tf.text = "3 组件 · 2 仓库 · 路线图"
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.name = FONT_CN
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = TEXT_PRIMARY

    # 3 仓库卡
    repos = [
        ("灵梭", "★ 124", "spring-ai-loom-agent", JAVA_BLUE),
        ("SQL工坊", "★ 89", "sql-forge", AI_PURPLE),
        ("SQL工坊 MCP", "★ 89", "sql-forge", SEMANTIC_GREEN),
    ]
    repo_boxes = []
    cw, ch = 3.8, 1.8
    gap = 0.3
    cx0 = (13.333 - 3 * cw - 2 * gap) / 2
    cy0 = 1.3
    for i, (name, stars, repo, color) in enumerate(repos):
        x = cx0 + i * (cw + gap)
        card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                    Inches(x), Inches(cy0), Inches(cw), Inches(ch))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = color
        card.line.width = Pt(2)
        # 名称
        tb_n = s.shapes.add_textbox(Inches(x), Inches(cy0 + 0.1),
                                      Inches(cw), Inches(0.4))
        tf_n = tb_n.text_frame
        tf_n.text = name
        p_n = tf_n.paragraphs[0]
        p_n.alignment = PP_ALIGN.CENTER
        run_n = p_n.runs[0]
        run_n.font.name = FONT_CN
        run_n.font.size = Pt(20)
        run_n.font.bold = True
        run_n.font.color.rgb = color
        # stars
        tb_s = s.shapes.add_textbox(Inches(x), Inches(cy0 + 0.6),
                                      Inches(cw), Inches(0.4))
        tf_s = tb_s.text_frame
        tf_s.text = stars
        p_s = tf_s.paragraphs[0]
        p_s.alignment = PP_ALIGN.CENTER
        run_s = p_s.runs[0]
        run_s.font.name = FONT_EN
        run_s.font.size = Pt(16)
        run_s.font.color.rgb = GOLD
        # repo
        tb_r = s.shapes.add_textbox(Inches(x), Inches(cy0 + 1.1),
                                      Inches(cw), Inches(0.4))
        tf_r = tb_r.text_frame
        tf_r.text = repo
        p_r = tf_r.paragraphs[0]
        p_r.alignment = PP_ALIGN.CENTER
        run_r = p_r.runs[0]
        run_r.font.name = FONT_MONO
        run_r.font.size = Pt(12)
        run_r.font.color.rgb = TEXT_SECONDARY
        repo_boxes.append(card)

    # 4 节点时间线
    versions = [("V1.0 当前", True), ("V1.1 多租户", False), ("V1.2 移动端", False), ("V1.3 工作流", False)]
    node_boxes = []
    nw, nh = 2.5, 0.8
    gap = 0.4
    total_w = 4 * nw + 3 * gap
    nx0 = (13.333 - total_w) / 2
    ny = 4.5
    for i, (label, is_current) in enumerate(versions):
        x = nx0 + i * (nw + gap)
        node = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                    Inches(x), Inches(ny), Inches(nw), Inches(nh))
        node.fill.solid()
        if is_current:
            node.fill.fore_color.rgb = GOLD
        else:
            node.fill.fore_color.rgb = WHITE
        node.line.color.rgb = GOLD if is_current else DIVIDER
        node.line.width = Pt(2)
        tf_n = node.text_frame
        tf_n.text = label
        p_n = tf_n.paragraphs[0]
        p_n.alignment = PP_ALIGN.CENTER
        run_n = p_n.runs[0]
        run_n.font.name = FONT_CN
        run_n.font.size = Pt(14)
        run_n.font.bold = is_current
        run_n.font.color.rgb = WHITE if is_current else TEXT_PRIMARY
        node_boxes.append(node)
        # 连线
        if i < 3:
            line = s.shapes.add_connector(1,  # STRAIGHT
                                           Inches(x + nw), Inches(ny + nh/2),
                                           Inches(x + nw + gap), Inches(ny + nh/2))
            line.line.color.rgb = TEXT_SECONDARY
            line.line.width = Pt(1)

    # 底部
    tb_b = s.shapes.add_textbox(Inches(0.5), Inches(6.0),
                                 Inches(12.333), Inches(0.4))
    tf_b = tb_b.text_frame
    tf_b.text = "3 个组件 · 2 个仓库 · 各自独立维护 · 按需组合"
    p_b = tf_b.paragraphs[0]
    p_b.alignment = PP_ALIGN.CENTER
    run_b = p_b.runs[0]
    run_b.font.name = FONT_CN
    run_b.font.size = Pt(14)
    run_b.font.color.rgb = TEXT_SECONDARY

    # 4 动画
    add_anim(s, repo_boxes[0], "fade_in", delay_ms=0, dur_ms=500)
    add_anim(s, node_boxes[0], "fade_in", delay_ms=800, dur_ms=500)
    add_anim(s, node_boxes[3], "fade_in", delay_ms=1400, dur_ms=500)
    add_anim(s, node_boxes[0], "pulse", delay_ms=2000, dur_ms=1500, loop=True)  # V1.0 脉冲
```

- [ ] **Step 2: slide_10_ending**

```python
def slide_10_ending(prs):
    """P10 结尾 · 3 句话 + 金句 + 启动日志 + 仓库地址"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG_LIGHT

    # JavaBrain 大字
    tb_t = s.shapes.add_textbox(Inches(0.5), Inches(0.6),
                                 Inches(12.333), Inches(1.2))
    tf = tb_t.text_frame
    tf.text = "JavaBrain"
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.name = FONT_EN
    run.font.size = Pt(72)
    run.font.bold = True
    run.font.color.rgb = TEXT_PRIMARY

    # 3 句话
    sentences = [
        "1. 开箱即用 + 私有化 + 业务语义",
        "2. 一行命令启动,一个文件改 AI 行为",
        "3. 让每个 Spring Boot 项目都自带 AI 能力",
    ]
    sent_boxes = []
    for i, txt in enumerate(sentences):
        tb = s.shapes.add_textbox(Inches(0.5), Inches(2.0 + i * 0.5),
                                   Inches(12.333), Inches(0.4))
        tf = tb.text_frame
        tf.text = txt
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.runs[0]
        run.font.name = FONT_CN
        run.font.size = Pt(18)
        run.font.color.rgb = TEXT_PRIMARY
        sent_boxes.append(tb)

    # 金句
    killer = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                  Inches(2.5), Inches(4.2),
                                  Inches(8.333), Inches(0.7))
    killer.fill.solid()
    killer.fill.fore_color.rgb = GOLD_BG
    killer.line.color.rgb = GOLD
    killer.line.width = Pt(3)
    tf_k = killer.text_frame
    tf_k.text = "★ 让 AI 不再是 Demo,让企业系统真正智能"
    p_k = tf_k.paragraphs[0]
    p_k.alignment = PP_ALIGN.CENTER
    run_k = p_k.runs[0]
    run_k.font.name = FONT_CN
    run_k.font.size = Pt(22)
    run_k.font.bold = True
    run_k.font.color.rgb = GOLD

    # 终端框
    term = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                Inches(2.5), Inches(5.2),
                                Inches(8.333), Inches(0.6))
    term.fill.solid()
    term.fill.fore_color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    term.line.fill.background()
    tf_t = term.text_frame
    tf_t.text = "$ Started LoomAgentApplication in 25.394 seconds"
    p_t = tf_t.paragraphs[0]
    p_t.alignment = PP_ALIGN.CENTER
    run_t = p_t.runs[0]
    run_t.font.name = FONT_MONO
    run_t.font.size = Pt(14)
    run_t.font.color.rgb = SEMANTIC_GREEN

    # 仓库地址
    tb_repo = s.shapes.add_textbox(Inches(0.5), Inches(6.1),
                                    Inches(12.333), Inches(0.5))
    tf_r = tb_repo.text_frame
    tf_r.text = "github.com/wb04307201/spring-ai-loom-agent  ·  gitee.com/wb04307201/spring-ai-loom-agent"
    p_r = tf_r.paragraphs[0]
    p_r.alignment = PP_ALIGN.CENTER
    run_r = p_r.runs[0]
    run_r.font.name = FONT_MONO
    run_r.font.size = Pt(12)
    run_r.font.color.rgb = TEXT_SECONDARY

    # 致谢
    tb_thx = s.shapes.add_textbox(Inches(0.5), Inches(6.7),
                                   Inches(12.333), Inches(0.3))
    tf_thx = tb_thx.text_frame
    tf_thx.text = "感谢 [团队名] · 联系: [邮箱]"
    p_thx = tf_thx.paragraphs[0]
    p_thx.alignment = PP_ALIGN.CENTER
    run_thx = p_thx.runs[0]
    run_thx.font.name = FONT_CN
    run_thx.font.size = Pt(12)
    run_thx.font.color.rgb = TEXT_SECONDARY

    # 6 动画
    add_anim(s, tb_t, "fade_in", delay_ms=0, dur_ms=500)
    add_anim(s, sent_boxes[0], "fade_in", delay_ms=600, dur_ms=500)
    add_anim(s, sent_boxes[1], "fade_in", delay_ms=1200, dur_ms=500)
    add_anim(s, sent_boxes[2], "fade_in", delay_ms=1800, dur_ms=500)
    add_anim(s, killer, "pulse", delay_ms=6000, dur_ms=1500, loop=True)  # 金句持续脉冲
    add_anim(s, term, "fade_in", delay_ms=10000, dur_ms=500)
```

- [ ] **Step 3: 更新 main()**

```python
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
    slide_6_demo1_workflow(prs)
    slide_7_demo2_workflow(prs)
    slide_8_compare(prs)
    slide_9_roadmap(prs)
    slide_10_ending(prs)
    prs.save(str(OUTPUT))
    print(f"OK: {OUTPUT} (12 pages)")
```

- [ ] **Step 4: 运行 + OnlyOffice 验证 12 页 + 全部动画**

- [ ] **Step 5: 提交**

```bash
git add scripts/gen-ppt.py
git commit -m "feat(ppt): 实现 P9 路线图 + P10 结尾(12 页完成)"
```

---

## Task 8: gen-video.py 转视频(2h)

**Files:**
- Create: `docs/ppt/scripts/gen-video.py`

- [ ] **Step 1: 实现 gen-video.py 骨架**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JavaBrain PPT → MP4 转视频脚本。

依赖:libreoffice, ffmpeg
用法:python scripts/gen-video.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PPT_DIR = SCRIPT_DIR.parent
PPT = PPT_DIR / "javabrain.pptx"
PDF = PPT_DIR / "javabrain.pdf"
OUT_DIR = PPT_DIR / "build"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_MP4 = PPT_DIR / "javabrain.mp4"

# 每页停留时长(秒)
PAGE_DURATIONS = {
    1: 15, 2: 50, 3: 35, 4: 20, 5: 35, 6: 20, 7: 45,
    8: 6, 9: 42, 10: 6, 11: 40, 12: 55, 13: 40, 14: 40,
}
# 视频内页与录屏 V1/V2 拼接(录屏在 P6/P7 后追加)
# 实际视频页:12 静态 + 2 录屏
TOTAL_PAGES = 14  # P1-P12 + V1 + V2


def run(cmd, **kw):
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, **kw)


def main():
    # Step 1: libreoffice pptx → pdf
    if not PDF.exists():
        run(["libreoffice", "--headless", "--convert-to", "pdf",
             "--outdir", str(PPT_DIR), str(PPT)])
    # Step 2: pdf → png(逐页)
    for i in range(1, 15):
        png = OUT_DIR / f"page-{i:02d}.png"
        if not png.exists():
            run(["pdftoppm", "-png", "-r", "150", "-f", str(i), "-l", str(i),
                 str(PDF), str(OUT_DIR / "page")])
    # Step 3: ffmpeg 拼成 mp4(每页指定停留时长)
    # 用 concat demuxer + 各页 png
    filelist = OUT_DIR / "filelist.txt"
    with open(filelist, "w") as f:
        # 前 6 静态页(P1-P6)
        for i in range(1, 7):
            dur = PAGE_DURATIONS[i]
            f.write(f"file 'page-{i:02d}.png'\n")
            f.write(f"duration {dur}\n")
        # 录屏 V1(42s)
        f.write(f"file '{PPT_DIR}/videos/demo1/demo1-final.mp4'\n")
        f.write("duration 42\n")
        # P7 工作流(6s)
        f.write(f"file 'page-08.png'\n")
        f.write("duration 6\n")
        # 录屏 V2(40s)
        f.write(f"file '{PPT_DIR}/videos/demo2/demo2-final.mp4'\n")
        f.write("duration 40\n")
        # P8-P12 静态
        for i in range(9, 13):
            dur = PAGE_DURATIONS[i + 2]  # 跳过 V1/V2 索引偏移
            f.write(f"file 'page-{i+2:02d}.png'\n")
            f.write(f"duration {dur}\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(filelist), "-vsync", "vfr", "-pix_fmt", "yuv420p",
         str(OUT_MP4)])
    print(f"OK: {OUT_MP4}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 运行 gen-video.py 验证**

Run: `cd docs/ppt && python scripts/gen-video.py`
Expected: 生成 `javabrain.mp4`(≤ 8 分钟, 1080p)

- [ ] **Step 3: ffprobe 验证时长 + 分辨率**

Run: `ffprobe docs/ppt/javabrain.mp4`
Expected: Duration ≤ 480s, Resolution 1920x1080, fps ≥ 24

- [ ] **Step 4: VLC 试看前 60s**

确认动画、录屏拼接、声音正常

- [ ] **Step 5: 提交**

```bash
git add scripts/gen-video.py
git commit -m "feat(ppt): 添加 gen-video.py 转视频脚本"
```

---

## Task 9: 同步 OUTLINE.md(0.5h)

**Files:**
- Modify: `docs/ppt/OUTLINE.md`(全文改写,反映 v2 12 页 + 83 动画 + 转视频)

- [ ] **Step 1: 重写 OUTLINE.md**

```markdown
# JavaBrain 参赛 PPT · 简版大纲(从 PPT-OUTLINE.md 抽取)

> 版本:v1(本版本为起点,后续调整直接改本文,不另立版本号)
> 完整设计:docs/superpowers/specs/2026-06-15-javabrain-ppt-v2-design.md

---

## 🎯 一句话定位

JavaBrain = 灵梭 AI Agent + SQL工坊 + SQL工坊 MCP
让企业级 Spring Boot 应用,3 分钟接入 AI、90 秒出分析报告、10 分钟出可用页面。
3 个都是依赖库,不是产品 —— 可单独引入,按需组合。

## 🎬 8 分钟节奏(7:29 内容 + 31s 静默 = 8:00)

[12 页结构表,见 spec §3]

## 🎨 设计语言(白底 2.5D 乐高)

[7 色 / 3 字体 / 5 级字号,见 spec §4]

## 📑 12 页结构(每页 1 段)

[每页 1 段简述,见 spec §3]

## 🎬 83 个动画节点(转视频核心)

| 类型 | 数量 |
|---|---:|
| fade_in 入场 | 63 |
| pulse_loop 持续到翻页 | 15 |
| chase_pulse 沿卡片追逐 | 5 |
| **总账** | **83** |

[见 spec §5 详细时序表]

## 🎬 转视频管线

pptx → libreoffice → ffmpeg 拼图 → 剪映追加录屏 → mp4

## ✅ 验收标准(26 条)

[见 spec §9]

## 📂 配套文件

| 文件 | 用途 |
|---|---|
| `scripts/gen-ppt.py` | PPT 主生成器 |
| `scripts/gen-video.py` | 转视频脚本 |
| `javabrain.pptx` | 12 页 PPT 源文件 |
| `javabrain.mp4` | 8 分钟最终视频 |
| `docs/superpowers/specs/2026-06-15-javabrain-ppt-v2-design.md` | v2 设计文档 |
| `videos/demo1/demo1-final.mp4` | 录屏 1(42s) |
| `videos/demo2/demo2-final.mp4` | 录屏 2(40s) |
```

- [ ] **Step 2: 提交**

```bash
git add OUTLINE.md
git commit -m "docs(outline): 同步 OUTLINE.md 到 v2 12 页+83 动画+转视频"
```

---

## 自我审查(写完 plan 后)

1. **Spec 覆盖**:
   - §3 12 页结构 → Task 1-7 实现 ✓
   - §4 设计语言(配色/字体/字号/乐高)→ Task 0+1 实现 ✓
   - §5 动画系统(83 个)→ Task 0+1-7 实现 ✓
   - §6 转视频管线 → Task 8 实现 ✓
   - §7 文件结构 → Task 1-8 创建/修改 ✓
   - §8 实施步骤 → 整体 plan 顺序匹配 ✓
   - §9 验收标准 → 隐式覆盖(每 Task 末尾"OnlyOffice 验证")

2. **占位符扫描**:
   - 无 TBD/TODO/FIXME
   - "见 spec §X" 多次出现,但都是引用已批准的 spec 内容,合规

3. **类型一致性**:
   - `add_anim(slide, shape, anim_type, *, delay_ms, dur_ms, loop)` → Task 0 定义,Task 1-7 一致使用
   - `iso_lego(slide, x_in, y_in, w_in, h_in, color, *, studs, highlight)` → Task 1 定义,Task 3 复用
   - `slide_X_name(prs)` 函数签名一致

4. **未覆盖的 spec 项**:
   - §10 答辩前 1 小时检查清单 → 在 OUTLINE.md 体现,但没有 Task 显式实现
   - 解决方案:这是给答辩者用的清单,不需实现,OUTLINE.md 包含即可

---

## 任务总账

- **总 Task 数**:9 个
- **总 commit 数**:10 个(T0-T9 + 必要的 fix)
- **总工时**:~14.5h
- **总产出**:`javabrain.pptx`(12 页, 83 动画) + `javabrain.mp4`(8 分钟)

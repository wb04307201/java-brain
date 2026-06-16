"""T7 验证:12 页完成,P9+P10 关键内容。

累计动画统计(P9 重做为'4 阶段信任阶梯'页后):
- P1: 6 (5 fade_in + 1 zoom_in 模拟打字机)
- P2: 8 (7 fade_in + 1 pulse_loop)
- P3: 4 (3 fade_in + 1 pulse_loop)
- P4-a: 4 (3 fade_in + 1 pulse_loop)
- P4-b: 8 (6 fade_in + 2 pulse_loop chase)
- P5-a: 4 (3 fade_in + 1 pulse_loop)
- P5-b: 8 (6 fade_in + 2 pulse_loop chase)
- P6: 8 (7 fade_in + 1 pulse_loop)
- P7: 13 (10 fade_in + 3 pulse_loop chase)
- P8: 6 (5 fade_in + 1 pulse_loop · 实战对比)
- P9: 6 (5 fade_in + 1 pulse_loop · 4 阶段信任阶梯)
- P10: 7 (5 fade_in + 1 spin loop + 1 pulse_loop)

合计:73 fade_in + 1 zoom_in + 1 spin + 14 pulse_loop = 93 anim,15 indefinite。
(P9 信任阶梯改造后从 13 减到 6,删了灵梭/SQL工坊 8 卡入场)
"""
import sys
from pathlib import Path
from html import unescape

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from pptx import Presentation  # noqa: E402
from lxml import etree  # noqa: E402

PPTX = Path(__file__).resolve().parent.parent / "javabrain.pptx"


def test_total_pages():
    prs = Presentation(str(PPTX))
    assert len(prs.slides) == 12, f"期望 12 页,实际 {len(prs.slides)}"


def test_total_animations():
    """12 页累计动画总数 — 已全部删除,期望 0。"""
    prs = Presentation(str(PPTX))
    total = 0
    total_indefinite = 0
    for slide in prs.slides:
        xml = etree.tostring(slide._element).decode()
        total += xml.count("<p:animEffect")
        total_indefinite += xml.count('repeatCount="indefinite"')
    print(f"  total animEffects: {total}, indefinites: {total_indefinite}")
    assert total == 0, f"动画已删除,期望 0,实际 {total}"
    assert total_indefinite == 0, f"动画已删除,期望 0 pulse_loop,实际 {total_indefinite}"


def test_p9_loom_future():
    """P9 阶段 1 可用 + 阶段 2 可控(灰+Java 蓝)。"""
    prs = Presentation(str(PPTX))
    p9 = prs.slides[10]
    xml = unescape(etree.tostring(p9._element).decode())
    for text in ["可用", "AI 能干活", "可控", "AI 听指挥",
                 "5 受限通道", "DDL 黑名单", "0 漂移"]:
        assert text in xml, f"P9 阶段 1/2 缺失: {text}"


def test_p9_forge_future():
    """P9 阶段 3 可信 + 阶段 4 可托付(AI 紫+金)。"""
    prs = Presentation(str(PPTX))
    p9 = prs.slides[10]
    xml = unescape(etree.tostring(p9._element).decode())
    for text in ["可信", "数据不出企业", "可托付",
                 "Agentic Workflow", "多步推理", "反思重试",
                 "全链路私有化", "本地 Qwen"]:
        assert text in xml, f"P9 阶段 3/4 缺失: {text}"


def test_p9_dual_engine_vision():
    """P9 底部金钩:JavaBrain 不只是工具,而是你可托付的数据同事。"""
    prs = Presentation(str(PPTX))
    p9 = prs.slides[10]
    xml = unescape(etree.tostring(p9._element).decode())
    for text in ["从工具到同事", "可托付的数据同事", "4 阶段信任阶梯"]:
        assert text in xml, f"P9 主标题/金钩缺失: {text}"


def test_p9_pulse_indefinite():
    """动画已删除 — 无 pulse_loop。"""
    prs = Presentation(str(PPTX))
    p9 = prs.slides[10]
    xml = etree.tostring(p9._element).decode()
    assert 'repeatCount="indefinite"' not in xml


def test_p9_animation_count():
    """P9 动画已删除 — 0。"""
    prs = Presentation(str(PPTX))
    p9 = prs.slides[10]
    xml = etree.tostring(p9._element).decode()
    tc = xml.count("<p:animEffect")
    assert tc == 0, f"P9 动画已删除,期望 0,实际 {tc}"


def test_p10_key_text():
    prs = Presentation(str(PPTX))
    p10 = prs.slides[11]
    xml = unescape(etree.tostring(p10._element).decode())
    for text in ["JavaBrain", "开箱即用", "AI 懂数据",
                 "LoomAgentApplication", "25.394",
                 "github.com/wb04307201"]:
        assert text in xml, f"P10 缺失: {text}"


def test_p10_three_sentences():
    """3 句话:开箱即用 / 一行命令 / 每个 Spring Boot。"""
    prs = Presentation(str(PPTX))
    p10 = prs.slides[11]
    xml = unescape(etree.tostring(p10._element).decode())
    for txt in ["开箱即用", "一行命令启动", "每个 Spring Boot"]:
        assert txt in xml, f"P10 缺失: {txt}"


def test_p10_pulse_indefinite():
    """动画已删除 — 无 pulse_loop。"""
    prs = Presentation(str(PPTX))
    p10 = prs.slides[11]
    xml = etree.tostring(p10._element).decode()
    assert 'repeatCount="indefinite"' not in xml


def test_p10_animation_count():
    """P10 动画已删除 — 0。"""
    prs = Presentation(str(PPTX))
    p10 = prs.slides[11]
    xml = etree.tostring(p10._element).decode()
    tc = xml.count("<p:animEffect")
    assert tc == 0, f"P10 动画已删除,期望 0,实际 {tc}"


if __name__ == "__main__":
    test_total_pages()
    print("OK 12 pages")
    test_total_animations()
    print("OK 0 animEffects + 0 indefinite (动画已删除)")
    test_p9_loom_future()
    print("OK P9 阶段 1/2")
    test_p9_forge_future()
    print("OK P9 阶段 3/4")
    test_p9_dual_engine_vision()
    print("OK P9 信任阶梯标题/金钩")
    test_p9_pulse_indefinite()
    print("OK P9 无 pulse")
    test_p9_animation_count()
    print("OK P9 0 anim")
    test_p10_key_text()
    print("OK P10 key text")
    test_p10_three_sentences()
    print("OK P10 3 sentences")
    test_p10_pulse_indefinite()
    print("OK P10 无 pulse")
    test_p10_animation_count()
    print("OK P10 0 anim")
    print("\nT7 验证全部通过 + 12 页 PPT 完成 (动画已删除)")

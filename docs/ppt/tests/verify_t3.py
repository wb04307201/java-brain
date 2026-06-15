"""T3 验证:P3/P4-a/P4-b 应该有 5 slides + 各种动画数。"""
import sys
from pathlib import Path
from html import unescape

# Force UTF-8 stdout on Windows to avoid GBK encode errors
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from pptx import Presentation  # noqa: E402
from lxml import etree  # noqa: E402

PPTX = Path(__file__).resolve().parent.parent / "javabrain.pptx"


def test_total_pages():
    prs = Presentation(str(PPTX))
    assert len(prs.slides) >= 5, f"期望 ≥5 页,实际 {len(prs.slides)}"


def test_p3_animation_count():
    """P3 spec §3 写 4 动画(3 入场 + 1 循环);实际实现含 4 动画(tb_t + legos[0] + item[0] + pulse)。"""
    prs = Presentation(str(PPTX))
    p3 = prs.slides[2]
    xml = etree.tostring(p3._element).decode()
    timing_count = xml.count("<p:timing")
    assert timing_count >= 4, f"P3 期望 ≥4 动画,实际 {timing_count}"


def test_p3_pulse_indefinite():
    """P3 首行金脉冲:1 个 indefinite。"""
    prs = Presentation(str(PPTX))
    p3 = prs.slides[2]
    xml = etree.tostring(p3._element).decode()
    assert 'repeatCount="indefinite"' in xml


def test_p3_key_text():
    prs = Presentation(str(PPTX))
    p3 = prs.slides[2]
    xml = unescape(etree.tostring(p3._element).decode())
    for text in ["JavaBrain", "灵梭", "SQL工坊", "依赖库", "组合起来"]:
        assert text in xml, f"P3 缺失: {text}"


def test_p4a_animation_count():
    """P4-a spec §3 写 4 动画。"""
    prs = Presentation(str(PPTX))
    p4a = prs.slides[3]
    xml = etree.tostring(p4a._element).decode()
    timing_count = xml.count("<p:timing")
    assert timing_count >= 4, f"P4-a 期望 ≥4 动画,实际 {timing_count}"


def test_p4a_pulse_indefinite():
    """P4-a Skill 金脉冲:1 个。"""
    prs = Presentation(str(PPTX))
    p4a = prs.slides[3]
    xml = etree.tostring(p4a._element).decode()
    assert 'repeatCount="indefinite"' in xml


def test_p4a_key_text():
    prs = Presentation(str(PPTX))
    p4a = prs.slides[3]
    xml = unescape(etree.tostring(p4a._element).decode())
    for text in ["LoomAgent", "Spring AI 一键启动", "6 大功能模块", ".st"]:
        assert text in xml, f"P4-a 缺失: {text}"


def test_p4b_animation_count():
    """P4-b spec §3 写 8 动画(6 入场 + 2 chase 循环)。"""
    prs = Presentation(str(PPTX))
    p4b = prs.slides[4]
    xml = etree.tostring(p4b._element).decode()
    timing_count = xml.count("<p:timing")
    assert timing_count >= 8, f"P4-b 期望 ≥8 动画,实际 {timing_count}"


def test_p4b_chase_indefinite():
    """P4-b 2 个 chase pulse(MCP + Skill 错开 2s)。"""
    prs = Presentation(str(PPTX))
    p4b = prs.slides[4]
    xml = etree.tostring(p4b._element).decode()
    indefinite_count = xml.count('repeatCount="indefinite"')
    assert indefinite_count >= 2, f"P4-b 期望 ≥2 pulse_loop,实际 {indefinite_count}"


def test_p4b_chase_delay_staggered():
    """2 个 chase pulse 的 delay_ms 应错开约 2s(10000 vs 12000)。"""
    prs = Presentation(str(PPTX))
    p4b = prs.slides[4]
    xml = etree.tostring(p4b._element).decode()
    assert '10000' in xml, "MCP chase delay 10000ms 缺失"
    assert '12000' in xml, "Skill chase delay 12000ms 缺失"


def test_p4b_modules_present():
    prs = Presentation(str(PPTX))
    p4b = prs.slides[4]
    xml = unescape(etree.tostring(p4b._element).decode())
    for text in ["RAG 知识库", "MCP", "Skill", "文件管理", "对话 UI", "内置工具"]:
        assert text in xml, f"P4-b 缺失模块: {text}"


if __name__ == "__main__":
    test_total_pages()
    print("[OK] 5 pages")
    test_p3_animation_count()
    print("[OK] P3 animations")
    test_p3_pulse_indefinite()
    print("[OK] P3 pulse_loop")
    test_p3_key_text()
    print("[OK] P3 key text")
    test_p4a_animation_count()
    print("[OK] P4-a animations")
    test_p4a_pulse_indefinite()
    print("[OK] P4-a pulse_loop")
    test_p4a_key_text()
    print("[OK] P4-a key text")
    test_p4b_animation_count()
    print("[OK] P4-b animations")
    test_p4b_chase_indefinite()
    print("[OK] P4-b 2 chase")
    test_p4b_chase_delay_staggered()
    print("[OK] P4-b chase staggered 2s")
    test_p4b_modules_present()
    print("[OK] P4-b 6 modules")
    print("\nT3 验证全部通过")

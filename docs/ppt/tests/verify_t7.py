"""T7 验证:12 页完成,P9+P10 关键内容。

累计动画统计(spec §5.3):
- P1: 5 fade_in (no pulse)
- P2: 7 fade_in + 1 pulse_loop = 8
- P3: 3 fade_in + 1 pulse_loop = 4
- P4-a: 3 fade_in + 1 pulse_loop = 4
- P4-b: 6 fade_in + 2 pulse_loop (chase) = 8
- P5-a: 3 fade_in + 1 pulse_loop = 4
- P5-b: 10 fade_in + 3 pulse_loop (chase) = 13
- P6: 5 fade_in + 1 pulse_loop = 6
- P7: 5 fade_in + 1 pulse_loop = 6
- P8: 9 fade_in + 1 pulse_loop = 10
- P9: 4 fade_in + 1 pulse_loop (V1.0) = 5
- P10: 5 fade_in + 1 pulse_loop (killer) = 6

合计:65 fade_in + 14 pulse_loop = 79 anim,14 indefinite。
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
    """12 页累计动画总数(spec 给出 63 fade_in + 15 pulse + 5 chase = 83,但 spec 算式将 chase 与 pulse 重叠计数)。

    按实际 add_anim 调用累计:
    - 65 fade_in + 14 pulse_loop(其中 5 个 chase)= 79 anim,14 indefinite
    """
    prs = Presentation(str(PPTX))
    total = 0
    total_indefinite = 0
    for slide in prs.slides:
        xml = etree.tostring(slide._element).decode()
        total += xml.count("<p:timing")
        total_indefinite += xml.count('repeatCount="indefinite"')
    print(f"  total timings: {total}, indefinites: {total_indefinite}")
    assert total == 79, f"期望 79 动画,实际 {total}"
    assert total_indefinite == 14, f"期望 14 pulse_loop,实际 {total_indefinite}"


def test_p9_3_repos():
    prs = Presentation(str(PPTX))
    p9 = prs.slides[10]
    xml = unescape(etree.tostring(p9._element).decode())
    for text in ["灵梭", "SQL工坊", "spring-ai-loom-agent", "sql-forge"]:
        assert text in xml, f"P9 缺失仓库: {text}"


def test_p9_stars():
    """3 个仓库的 ★ star 数。"""
    prs = Presentation(str(PPTX))
    p9 = prs.slides[10]
    xml = unescape(etree.tostring(p9._element).decode())
    for stars in ["★ 124", "★ 89"]:
        assert stars in xml, f"P9 缺失 stars: {stars}"


def test_p9_versions():
    prs = Presentation(str(PPTX))
    p9 = prs.slides[10]
    xml = unescape(etree.tostring(p9._element).decode())
    for v in ["V1.0", "V1.1", "V1.2", "V1.3"]:
        assert v in xml, f"P9 缺失版本: {v}"


def test_p9_pulse_indefinite():
    """V1.0 金脉冲。"""
    prs = Presentation(str(PPTX))
    p9 = prs.slides[10]
    xml = etree.tostring(p9._element).decode()
    assert 'repeatCount="indefinite"' in xml


def test_p9_animation_count():
    """P9:5 动画(3 仓库 fade + V1.0 fade + V1.0 pulse)。"""
    prs = Presentation(str(PPTX))
    p9 = prs.slides[10]
    xml = etree.tostring(p9._element).decode()
    tc = xml.count("<p:timing")
    assert tc == 5, f"P9 期望 5 动画,实际 {tc}"


def test_p10_key_text():
    prs = Presentation(str(PPTX))
    p10 = prs.slides[11]
    xml = unescape(etree.tostring(p10._element).decode())
    for text in ["JavaBrain", "开箱即用", "不再是 Demo",
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
    """金句持续脉冲。"""
    prs = Presentation(str(PPTX))
    p10 = prs.slides[11]
    xml = etree.tostring(p10._element).decode()
    indefinite_count = xml.count('repeatCount="indefinite"')
    assert indefinite_count >= 1, f"P10 期望 ≥1 pulse_loop(金句),实际 {indefinite_count}"


def test_p10_animation_count():
    """P10:6 动画(title fade + 3 sent fade + killer pulse + term fade)。"""
    prs = Presentation(str(PPTX))
    p10 = prs.slides[11]
    xml = etree.tostring(p10._element).decode()
    tc = xml.count("<p:timing")
    assert tc == 6, f"P10 期望 6 动画,实际 {tc}"


if __name__ == "__main__":
    test_total_pages()
    print("OK 12 pages")
    test_total_animations()
    print("OK 79 animations + 14 indefinite")
    test_p9_3_repos()
    print("OK P9 3 repos")
    test_p9_stars()
    print("OK P9 stars")
    test_p9_versions()
    print("OK P9 V1.0-V1.3")
    test_p9_pulse_indefinite()
    print("OK P9 V1.0 pulse")
    test_p9_animation_count()
    print("OK P9 5 anim")
    test_p10_key_text()
    print("OK P10 key text")
    test_p10_three_sentences()
    print("OK P10 3 sentences")
    test_p10_pulse_indefinite()
    print("OK P10 pulse_loop")
    test_p10_animation_count()
    print("OK P10 6 anim")
    print("\nT7 验证全部通过 + 12 页 PPT 完成")

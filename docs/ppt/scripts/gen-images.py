"""AI 配图生成:用阿里云百炼 万相 2.7 (DashScope SDK) 生成 PPT 配图。

P1 封面配图: 抽象 AI 神经网络/光效节点
P2 痛点配图: 3 张红(传统开发痛) + 3 张绿(JavaBrain 解决)
"""
import os
import sys
from pathlib import Path

# Force UTF-8 stdout
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import dashscope
from dashscope import ImageSynthesis

OUT_DIR = Path(__file__).resolve().parent.parent / "images" / "ai"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# === P1 封面:抽象 AI 神经网络 ===
P1_PROMPTS = [
    # 第 1 版:中央节点 + 三卫星
    (
        "p1-neural-v1.png",
        "abstract AI neural network on pure white background, one glowing central "
        "node with three satellite nodes connected by energy beams, soft blue purple "
        "green color palette, 2.5D flat illustration, Apple keynote style, ultra clean, "
        "no text, no people, vector-like minimal design, 8k",
    ),
    # 第 2 版:更"能量辐射"
    (
        "p1-neural-v2.png",
        "glowing energy core with three colored satellite orbs, isometric 2.5D flat "
        "illustration, white background, soft blue purple teal gradient, light rays "
        "radiating outward, no text, no people, minimal Apple keynote style, ultra clean",
    ),
    # 第 3 版:科技感更重
    (
        "p1-neural-v3.png",
        "futuristic tech brain core with three connected nodes, isometric 2.5D flat "
        "design, white background, blue purple green glowing accents, soft shadows, "
        "particle effects, no text, no people, Apple keynote minimal style",
    ),
]

# === P2 痛点:3 红 + 3 绿 ===
# 统一风格前缀(确保 6 张一致)
P2_STYLE = (
    "ultra minimal 2.5D flat illustration, pure white background, "
    "single color monochrome (no gradients, no text, no people), "
    "soft shadow, Apple keynote style, vector-like, clean simple shapes"
)

P2_PROMPTS = [
    # === 3 张红(传统开发痛苦)===
    (
        "p2-red-1-overwork.png",
        "overworked developer silhouette at desk with stacked coffee cups, "
        "red monochrome flat illustration, " + P2_STYLE,
    ),
    (
        "p2-red-2-bureaucracy.png",
        "tall stack of paper documents with red stamps and arrows, "
        "red monochrome flat illustration, " + P2_STYLE,
    ),
    (
        "p2-red-3-tangled.png",
        "tangled messy code lines with red error symbols, "
        "red monochrome flat illustration, " + P2_STYLE,
    ),
    # === 3 张绿(JavaBrain 解决)===
    (
        "p2-green-1-ai-report.png",
        "AI terminal with instant green report output, "
        "green monochrome flat illustration, " + P2_STYLE,
    ),
    (
        "p2-green-2-rocket.png",
        "rocket launching with stopwatch, "
        "green monochrome flat illustration, " + P2_STYLE,
    ),
    (
        "p2-green-3-dashboard.png",
        "auto-generated dashboard with charts, "
        "green monochrome flat illustration, " + P2_STYLE,
    ),
]


def gen_one(filename: str, prompt: str, size: str = "1024*1024") -> str | None:
    """生成单张图,返回保存路径,失败返回 None。"""
    print(f"  生成 {filename} ...")
    print(f"  prompt: {prompt[:80]}...")
    try:
        rsp = ImageSynthesis.call(
            model="wanx2.1-t2i-turbo",  # 万相 2.1 turbo(便宜+快)
            prompt=prompt,
            n=1,
            size=size,
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
        )
        if rsp.status_code == 200 and rsp.output and rsp.output.results:
            url = rsp.output.results[0].url
            # 下载图片
            import urllib.request
            out_path = OUT_DIR / filename
            urllib.request.urlretrieve(url, str(out_path))
            print(f"  ✓ {out_path} ({out_path.stat().st_size} bytes)")
            return str(out_path)
        else:
            print(f"  ✗ 失败: {rsp.status_code} {rsp.message}")
            return None
    except Exception as e:
        print(f"  ✗ 异常: {e}")
        return None


def main():
    print("=" * 60)
    print("P1 封面配图(3 选 1):抽象 AI 神经网络")
    print("=" * 60)
    p1_results = []
    for fn, prompt in P1_PROMPTS:
        result = gen_one(fn, prompt, size="1280*720")  # 16:9 适配 P1
        if result:
            p1_results.append((fn, result))

    print()
    print("=" * 60)
    print("P2 痛点配图(6 张):3 红 + 3 绿")
    print("=" * 60)
    p2_results = []
    for fn, prompt in P2_PROMPTS:
        result = gen_one(fn, prompt, size="800*800")
        if result:
            p2_results.append((fn, result))

    print()
    print("=" * 60)
    print("生成结果汇总")
    print("=" * 60)
    print(f"P1: {len(p1_results)}/3 成功")
    for fn, p in p1_results:
        print(f"  {fn} -> {p}")
    print(f"P2: {len(p2_results)}/6 成功")
    for fn, p in p2_results:
        print(f"  {fn} -> {p}")


if __name__ == "__main__":
    main()

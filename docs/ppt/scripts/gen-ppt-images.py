#!/usr/bin/env python3
"""
Batch-generate PPT cover images via Aliyun DashScope Tongyi Wanxiang.

依赖:Python 3.7+、环境变量 DASHSCOPE_API_KEY
输出:../images/page-XX-主题.png(可重入,已存在自动跳过)

用法:
  export DASHSCOPE_API_KEY=sk-xxx
  python gen-ppt-images.py              # 默认跑全部 10 张
  python gen-ppt-images.py page-04-loom # 只跑指定页
  WANX_MODEL=wanx2.1-t2i-plus python gen-ppt-images.py  # 换更好的模型

环境变量(可选):
  WANX_MODEL  模型名,默认 wanx2.1-t2i-turbo
  WANX_SIZE   图片尺寸,默认 1280*720(PPT 16:9)
  WANX_STYLE  风格参数,默认 <auto>(由模型自适应)
"""
import os
import sys
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

# ==================== 配置 ====================
# 万相 2.7 同步端点(北京地域)
GENERATE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

API_KEY = os.environ.get("DASHSCOPE_API_KEY")
if not API_KEY:
    sys.exit("ERROR: 环境变量 DASHSCOPE_API_KEY 未设置\nexport DASHSCOPE_API_KEY=sk-xxx")

# 强制 stdout 用 UTF-8,避免 Windows GBK 编码崩溃(emoji/中文都能输出)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# 模型:wan2.7-image(标准版,快)/ wan2.7-image-pro(4K 专业版,慢)
MODEL = os.environ.get("WANX_MODEL", "wan2.7-image")
# size:文档示例是 "2K";其他候选 "1024*1024" / "1280*720" / "1920*1080"
SIZE = os.environ.get("WANX_SIZE", "1280*720")
N = 1

# ==================== 路径 ====================
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR.parent / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==================== 10 张配图 prompt(从 PPT-OUTLINE.md 提取并优化) ====================
# 命名:page-<两位页码>-<主题>.png
PROMPTS = {
    "page-01-cover": (
        "JavaBrain 项目封面海报,中央一个发光的紫色 AI 大脑神经网络,周围环绕三个组件化模块积木"
        "(标注灵梭 / SQL 工坊 / SQL 工坊 MCP)和 Java 咖啡杯 Logo,深蓝色到紫色渐变背景,"
        "粒子光效,商业级渲染,主视觉醒目,海报风格,16:9,顶部留空以便叠加项目名称"
    ),
    "page-02-pain": (
        "企业 AI 落地痛点信息图,三个大红色数字\"3 个月\"、\"5 天\"、\"3 天\"从左到右并排,"
        "下方三个剪影(疲惫程序员推石上山、产品经理排队等数据、加班写 CRUD 的开发者),"
        "警示橙红渐变色调,扁平卡通插画风格,16:9"
    ),
    "page-03-position": (
        "JavaBrain 三个组件化依赖库示意图,三个不同颜色的乐高积木(紫色灵梭、蓝色 SQL 工坊、绿色 SQL 工坊 MCP)横向并排,"
        "每个积木上方标注'独立模块,可单独引入',中间用金色金属锁扣连接代表可自由拼装,"
        "积木上分别有清晰 Logo,深色科技背景,极简 3D 渲染,16:9,信息图风格"
    ),
    "page-04-loom": (
        "JavaBrain 灵梭 6 大功能模块架构图,中心是发光的紫色「灵梭 AI 编排」图标,"
        "周围 6 个圆角矩形功能卡片,中文标签分别是:RAG 知识库 / MCP 工具集成 / Skill 技能库 / 文件管理 / 对话交互 UI / 内置工具,"
        "其中 MCP 工具集成 和 Skill 技能库 用金色边框并标注 ★ 杀手锏,"
        "深色科技背景,中文信息图风格,卡片内文字用中文,16:9"
    ),
    "page-05-forge": (
        "JavaBrain SQL 工坊 架构图,顶部 4 个 starter 模块(中文标签:基础 CRUD / Calcite 跨库联邦 / Amis 低代码 / MCP 5 受限工具),"
        "中间是 SQL 查询图标,三条彩色数据流分别流向 MySQL、PostgreSQL、H2 三个数据库图标,"
        "然后汇聚到 JOIN 结果(中文),其中 JSON CRUD 协议、Calcite 跨库联邦、MCP 5 受限工具 三个标 ★ 杀手锏并用金色边框,"
        "深色科技背景,中文信息图风格,16:9"
    ),
    "page-06-demo1": None,  # 占位:录屏 1 录完视频后用 ffmpeg 截帧
    "page-07-demo2": None,  # 占位:录屏 2 录完视频后用 ffmpeg 截帧
    "page-08-compare": (
        "三个并排方块对比图,左侧灰色方块标注\"低代码\",中间红色方块标注\"ChatGPT+插件\","
        "右侧绿色方块标注\"JavaBrain\",每个方块内列出 4 个维度的勾叉图标,"
        "扁平信息图风格,清晰对比,16:9"
    ),
    "page-09-roadmap": (
        "三个 GitHub 风格的开源项目卡片横向并排(代表灵梭、SQL 工坊、SQL 工坊 MCP),"
        "下方一条横向时间线标注 V1.0、V1.1、V1.2、V1.3 四个版本节点,"
        "深色科技背景,产品路线图风格,16:9"
    ),
    "page-10-ending": (
        "Spring Boot 启动成功的终端画面截图,黑底绿字命令行风格,"
        "最后一行高亮显示\"Started LoomAgentApplication in 25.394 seconds\","
        "右上角带 JavaBrain Logo,简洁科技感,16:9"
    ),
}

# ==================== HTTP 工具 ====================

def _request(url, data=None):
    """统一 HTTP POST,返回 dict;失败抛错并打印详情。"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        sys.exit(f"HTTP {e.code} {url}\n响应:{body_text}")
    except urllib.error.URLError as e:
        sys.exit(f"网络错误 {url}: {e.reason}")


def generate(prompt):
    """万相 2.7 同步生成,直接返回 image_url(24h 有效)。"""
    payload = {
        "model": MODEL,
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ]
        },
        "parameters": {
            "size": SIZE,
            "n": N,
            "watermark": False,
        },
    }
    result = _request(GENERATE_URL, data=payload)
    # 同步响应:
    # {"output": {"choices": [{"message": {"content": [{"image": "https://..."}]}}]}}
    try:
        return result["output"]["choices"][0]["message"]["content"][0]["image"]
    except (KeyError, IndexError, TypeError):
        sys.exit(f"响应结构不符: {json.dumps(result, ensure_ascii=False, indent=2)}")


def download(url, dest):
    """下载图片到本地。"""
    req = urllib.request.Request(url, headers={"User-Agent": "gen-ppt-images/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        while True:
            chunk = r.read(8192)
            if not chunk:
                break
            f.write(chunk)


# ==================== 主流程 ====================

def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(PROMPTS.keys())

    print(f"模型:{MODEL}  尺寸:{SIZE}")
    print(f"输出目录:{OUTPUT_DIR}")
    print(f"目标:{len(targets)} 张\n")

    for i, name in enumerate(targets, 1):
        if name not in PROMPTS:
            print(f"[{i}/{len(targets)}] {name} ❌ 不在 PROMPTS 字典中,跳过")
            continue

        out_path = OUTPUT_DIR / f"{name}.png"
        if out_path.exists() and out_path.stat().st_size > 1024:
            print(f"[{i}/{len(targets)}] {name} ⏭️  已存在 ({out_path.stat().st_size} 字节),跳过")
            continue

        prompt = PROMPTS[name]
        if prompt is None:
            print(f"[{i}/{len(targets)}] {name} ⏭️  不需 AI 生成——录完视频用 ffmpeg 截帧,见 ../images/README.md")
            continue
        print(f"[{i}/{len(targets)}] {name} 生成中...")
        print(f"  prompt: {prompt[:60]}...")
        try:
            url = generate(prompt)
            download(url, out_path)
            print(f"  ✅ 已保存: {out_path}  ←  {url}\n")
        except SystemExit:
            raise
        except Exception as e:
            print(f"  ❌ 失败:{e}\n")
            sys.exit(1)

    print("=" * 50)
    print(f"完成!{len(targets)} 张图已写入 {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

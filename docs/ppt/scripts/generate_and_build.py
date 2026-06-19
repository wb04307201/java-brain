#!/usr/bin/env python3
"""根据 OUTLINE_v1.md 生成 PPT 图片并组装 PPT。

流程:
1. 从 OUTLINE 提取每个页面的 AI 配图 prompt
2. 调用万相 API 生成图片
3. 下载并保存到 images/ 目录
4. QA 检查图片质量
5. 组装成 PPT
6. 检查 PPT 内容和一致性
"""

import sys
import re
from pathlib import Path

# 添加 scripts 目录到 path
sys.path.insert(0, str(Path(__file__).parent))

from tools import (
    wanx_generate,
    wanx_download,
    qa_image_check,
    new_presentation,
    qa_pptx_images,
)


# 统一风格前缀（来自 OUTLINE_v1.md）
STYLE_PREFIX = (
    "深色 HUD 风格，科技感，深蓝黑背景（#0A0E1A），高对比度，"
    "**全图只能用中文文字，严禁任何英文字母、英文单词、英文标签**；4K 渲染"
)


# 每个页面的 prompt（从 OUTLINE_v1.md 提取）
PAGE_PROMPTS = {
    "page-01-cover": {
        "prompt": (
            "Spring Boot 科技感封面海报，中央一个发光的 AI 大脑神经网络，"
            "周围环绕数据库节点、Java 咖啡杯 Logo，深蓝色到紫色渐变背景，"
            "粒子光效，商业级 4K 渲染，16:9。"
            "**严禁任何英文字母、英文单词、英文标签，所有视觉元素只用图形**。"
        ),
        "size": "1280*720",
    },
    "page-02-pain": {
        "prompt": (
            "企业 AI 落地痛点信息图，**四个**大红色数字\"3 个月\"、\"5 天\"、\"3 天\"、"
            "\"还要装 CLI\"按 **2×2 网格**排列，每个数字下方有中文小字标签分别是"
            "\"接入 AI 周期\"、\"业务取数周期\"、\"CRUD 页面工时\"、\"才能用 AI\"，"
            "四个剪影（疲惫程序员推石上山、产品经理排队等数据、加班写 CRUD 的开发者、"
            "对着命令行的业务人员），警示橙红渐变色调，扁平卡通插画风格，16:9。"
            "**全图任何角落、装饰、按钮、徽章、角标、说明文字必须全部使用中文，"
            "严禁出现任何英文字母、英文单词、英文标签、英文缩写**；"
            "所有文字只能是中文（汉字），中文使用清晰的黑体或宋体。"
        ),
        "size": "1280*720",
    },
    "page-03-position": {
        "prompt": (
            "左侧三个彩色乐高积木横向并排，中间用金属锁扣连接，代表三个组件，"
            "分别标注\"灵梭\"、\"SQL 工坊\"、\"SQL 工坊 MCP\"。"
            "右侧纵向排列三个发光的助手图标，分别标注\"对话智能体\"、"
            "\"数据智能分析助手\"、\"智能化低代码助手\"。"
            "中间用交织的彩色光线连接左右两侧，表示组件协同支撑助手（非一一对应）。"
            "浅蓝到紫色渐变背景，3D 渲染，极简风，16:9。"
            "**严禁任何英文字母、英文标签**；只显示中文组件名和助手名。"
        ),
        "size": "1280*720",
    },
    "page-04-loom": {
        "prompt": (
            "Spring AI LoomAgent 架构示意图，中心一个发光的 Spring AI 图标，"
            "周围放射状连接 6 个功能模块卡片（标注 RAG 知识库、MCP 工具、Skill 技能、"
            "文件管理、对话 UI、内置工具），每个卡片带有小图标（书本、扳手、大脑、"
            "文件夹、对话框、工具箱）。左上角标注\"13 个 Maven 模块\"徽章。"
            "深色科技背景，信息图风格，16:9。**只能用中文，严禁英文标签**。"
        ),
        "size": "1280*720",
    },
    "page-05-sql-forge": {
        "prompt": (
            "Apache Calcite 跨库联邦查询架构图，中央一个 SQL 查询图标，"
            "三条彩色数据流向下分别流入 MySQL、PostgreSQL、H2 三个数据库图标，"
            "然后汇聚到一条 JOIN 结果，蓝色到青色科技调，架构图风格，16:9。"
            "**只能用中文，严禁英文**；技术名词用通用缩写（英文）可以接受但需自然。"
        ),
        "size": "1280*720",
    },
    "page-08-comparison": {
        "prompt": (
            "三个并排方块对比图，左侧灰色方块标注\"低代码\"，中间红色方块标注"
            "\"ChatGPT+插件\"，右侧绿色方块标注\"JavaBrain\"。"
            "每个方块内列出**6 行**对比，每行左侧是维度名，右侧是勾叉图标。"
            "6 个维度分别是：业务取数、CRUD 页面、跨库 JOIN、LLM 可控性、"
            "工具/技能管控、列名识别。"
            "低代码列：业务取数✓、CRUD 页面✗、跨库 JOIN✗、LLM 可控性 n/a、"
            "工具/技能管控✗、列名识别 n/a。"
            "ChatGPT+插件列：业务取数✓(但数据外发)、CRUD 页面需配合代码、"
            "跨库 JOIN✗、LLM 可控性✗锁定 OpenAI、工具/技能管控✗插件野生无审核、"
            "列名识别✗经常错。"
            "JavaBrain 列全部✓：业务取数 90 秒出报告、CRUD 页面 AI 语义推断、"
            "跨库 JOIN Calcite 联邦、LLM 可控性任意供应商可换本地模型、"
            "工具/技能管控 MCP/Skill 审核评估后上线、列名识别强制读 DDL。"
            "扁平信息图风格，清晰对比，16:9。**严禁英文标签**；所有文字用中文。"
        ),
        "size": "1280*720",
    },
    "page-09-roadmap": {
        "prompt": (
            "三个 GitHub 风格的开源项目卡片横向并排（代表灵梭、SQL 工坊、SQL 工坊 MCP），"
            "下方一条横向时间线标注 V1.0、V1.1、V1.2、V1.3 四个版本节点，"
            "深色科技背景，产品路线图风格，16:9。**只能用中文组件名，严禁英文项目名**。"
        ),
        "size": "1280*720",
    },
    "page-10-ending": {
        "prompt": (
            "Spring Boot 启动成功的终端画面截图，黑底绿字命令行风格，"
            "最后一行高亮显示\"Started LoomAgentApplication in 25.394 seconds\"，"
            "右上角带 JavaBrain Logo，简洁科技感，16:9。"
            "**只能用英文技术词，严禁中文**；终端风格本来就是英文。"
        ),
        "size": "1280*720",
    },
}


def generate_image(page_name: str, prompt_info: dict, output_dir: Path, max_retries: int = 3) -> Path:
    """生成单张图片，返回本地路径。"""
    prompt = f"{STYLE_PREFIX}。{prompt_info['prompt']}"
    size = prompt_info.get("size", "1280*720")
    output_path = output_dir / f"{page_name}.png"

    for attempt in range(1, max_retries + 1):
        print(f"\n[尝试 {attempt}/{max_retries}] 生成 {page_name}...")
        try:
            # 调用万相 API 生成
            image_url = wanx_generate(prompt, size=size)
            print(f"  [OK] 生成成功，URL: {image_url[:80]}...")

            # 下载到本地
            wanx_download(image_url, output_path)
            print(f"  [OK] 下载到: {output_path}")

            # QA 检查
            passed, reasons = qa_image_check(output_path)
            if passed:
                print(f"  [OK] QA 通过")
                return output_path
            else:
                print(f"  [FAIL] QA 失败: {reasons}")
                if attempt < max_retries:
                    print(f"  -> 重试...")
                else:
                    print(f"  [FAIL] 达到最大重试次数，使用当前图片")
                    return output_path

        except Exception as e:
            print(f"  [ERROR] 错误: {e}")
            if attempt < max_retries:
                print(f"  -> 重试...")
            else:
                print(f"  [FAIL] 达到最大重试次数")
                raise

    return output_path


def generate_all_images(output_dir: Path) -> list[Path]:
    """生成所有图片。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []

    for page_name, prompt_info in PAGE_PROMPTS.items():
        path = generate_image(page_name, prompt_info, output_dir)
        paths.append(path)

    return paths


def main():
    """主流程。"""
    # 设置路径 - 脚本在 docs/ppt/scripts/ 下，图片目录是 docs/ppt/images/
    script_dir = Path(__file__).parent  # docs/ppt/scripts/
    images_dir = script_dir.parent / "images"  # docs/ppt/images/

    print("=" * 70)
    print("步骤 1: 生成所有图片")
    print("=" * 70)

    paths = generate_all_images(images_dir)

    print(f"\n[OK] 生成完成，共 {len(paths)} 张图片")

    print("\n" + "=" * 70)
    print("步骤 2: 最终 QA 检查")
    print("=" * 70)

    all_passed = True
    for path in paths:
        passed, reasons = qa_image_check(path)
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} {path.name}")
        if not passed:
            print(f"  问题: {reasons}")
            all_passed = False

    if all_passed:
        print("\n[OK] 所有图片 QA 通过")
    else:
        print("\n[WARN] 部分图片 QA 未通过，请手动检查")

    print("\n" + "=" * 70)
    print("完成")
    print("=" * 70)
    print(f"图片目录: {images_dir}")
    print(f"共生成 {len(paths)} 张图片")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

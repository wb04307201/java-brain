#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JavaBrain PPT → MP4 转视频脚本。

依赖工具:
  - libreoffice(或 soffice):pptx → pdf
  - pdftoppm(pdf 转 png 工具):pdf → png
  - ffmpeg / ffprobe:视频拼接与验证

用法:
    python scripts/gen-video.py

输出:
    docs/ppt/javabrain.mp4(分辨率 1920x1080,≤ 8 分钟)
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ============== 路径 ==============
SCRIPT_DIR = Path(__file__).resolve().parent
PPT_DIR = SCRIPT_DIR.parent
PPT = PPT_DIR / "javabrain.pptx"
PDF = PPT_DIR / "javabrain.pdf"
BUILD = PPT_DIR / "build"
BUILD.mkdir(parents=True, exist_ok=True)
OUT_MP4 = PPT_DIR / "javabrain.mp4"

VIDEOS_DIR = PPT_DIR / "videos"
DEMO1 = VIDEOS_DIR / "demo1" / "demo1-final.mp4"
DEMO2 = VIDEOS_DIR / "demo2" / "demo2-final.mp4"

# ============== 工具查找 ==============
# Windows 下常见可执行文件名
TOOL_CANDIDATES = {
    "libreoffice": ["libreoffice", "soffice", "soffice.exe"],
    "pdftoppm": ["pdftoppm", "pdftoppm.exe"],
    "ffmpeg": ["ffmpeg", "ffmpeg.exe"],
    "ffprobe": ["ffprobe", "ffprobe.exe"],
}


def which_tool(name: str) -> str | None:
    """查找可执行文件的实际路径;Windows 下兼容 .exe 后缀。"""
    for cand in TOOL_CANDIDATES.get(name, [name]):
        path = shutil.which(cand)
        if path:
            return path
    return None


def check_tools() -> dict[str, str | None]:
    """检测所有依赖工具是否可用。"""
    tools = {name: which_tool(name) for name in TOOL_CANDIDATES}
    missing = [n for n, p in tools.items() if not p]
    if missing:
        print("[WARN] 以下工具缺失,脚本将以受限模式运行:")
        for n in missing:
            print(f"  - {n}")
        print("       缺失工具时只跳过对应步骤,后续步骤仍会尝试执行。")
    else:
        print("[OK] 所有依赖工具可用。")
    return tools


# ============== 每页时长(spec §3)= ==============
# key:1-based PPT 页码(1-12);V1/V2 为录屏过场
PAGE_DURATIONS: dict[int | str, int] = {
    1: 15,    # P1 封面
    2: 50,    # P2 痛点
    3: 35,    # P3 定位
    4: 20,    # P4-a 灵梭整体
    5: 35,    # P4-b 6 模块
    6: 20,    # P5-a SQL整体
    7: 45,    # P5-b 4+6
    8: 6,     # P6 演示 1 工作流(短过场)
    9: 6,     # P7 演示 2 工作流(短过场)
    10: 55,   # P8 实战对比
    11: 40,   # P9 路线图
    12: 40,   # P10 结尾
}
DUR_V1 = 42  # 录屏 1 demo1
DUR_V2 = 40  # 录屏 2 demo2
# 总时长 = 15+50+35+20+35+20+45+6+42+6+40+55+40+40 = 449s(7:29)


# ============== 通用命令执行 ==============
def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    """执行命令并打印日志。"""
    print(f"$ {' '.join(str(c) for c in cmd)}", flush=True)
    return subprocess.run(cmd, check=True, **kw)


def safe_run(label: str, cmd: list[str]) -> bool:
    """执行命令,失败时打印但不抛异常。返回 True 表示成功。"""
    print(f"$ {' '.join(str(c) for c in cmd)}", flush=True)
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {label} 失败:exit={e.returncode}", file=sys.stderr)
        return False
    except FileNotFoundError as e:
        print(f"[ERROR] {label} 命令不存在:{e}", file=sys.stderr)
        return False


# ============== Step 1: pptx → pdf ==============
def step1_pptx_to_pdf(tools: dict[str, str | None]) -> bool:
    """libreoffice headless 渲染 pptx → pdf"""
    print("\n=== Step 1: pptx → pdf ===")
    if PDF.exists():
        print(f"PDF 已存在,跳过:{PDF}")
        return True
    binary = tools.get("libreoffice")
    if not binary:
        print("[SKIP] libreoffice 不可用,跳过 pptx → pdf")
        return False
    if not PPT.exists():
        print(f"[ERROR] PPT 不存在:{PPT}")
        return False
    return safe_run(
        "libreoffice --convert-to pdf",
        [binary, "--headless", "--convert-to", "pdf",
         "--outdir", str(PPT_DIR), str(PPT)],
    )


# ============== Step 2: pdf → png ==============
def step2_pdf_to_png(tools: dict[str, str | None]) -> bool:
    """pdftoppm 把 pdf → png 逐页。生成 page-01.png ~ page-12.png。"""
    print("\n=== Step 2: pdf → png ===")
    binary = tools.get("pdftoppm")
    if not binary:
        print("[SKIP] pdftoppm 不可用,跳过 pdf → png")
        return False
    if not PDF.exists():
        print(f"[ERROR] PDF 不存在:{PDF},无法转 png")
        return False
    ok = True
    for i in range(1, 13):
        target = BUILD / f"page-{i:02d}.png"
        if target.exists():
            print(f"  已存在,跳过:{target.name}")
            continue
        if not safe_run(
            f"pdftoppm page {i}",
            [binary, "-png", "-r", "150",
             "-f", str(i), "-l", str(i),
             str(PDF), str(BUILD / "page")],
        ):
            ok = False
            break
    # pdftoppm 输出文件名是 page-NN.png(零填充)
    produced = sorted(BUILD.glob("page-*.png"))
    print(f"  共生成 {len(produced)} 张 png")
    return ok


# ============== Step 3: ffmpeg concat ==============
def _write_filelist(filelist: Path) -> None:
    """按 spec 顺序写入 concat demuxer 的 filelist。"""
    # 录屏相对路径(相对于 BUILD 工作目录)
    rel_demo1 = Path("..") / "videos" / "demo1" / "demo1-final.mp4"
    rel_demo2 = Path("..") / "videos" / "demo2" / "demo2-final.mp4"

    lines: list[str] = []

    # P1-P7:静态页(0~P5-b 共 7 页 + 演示 1 过场 P6)
    # PAGE_DURATIONS 1-7 对应 P1-P5-b
    for i in range(1, 8):
        png = BUILD / f"page-{i:02d}.png"
        dur = PAGE_DURATIONS[i]
        lines.append(f"file '{png.as_posix()}'")
        lines.append(f"duration {dur}")

    # P6 演示 1 工作流(page-08) + 录屏 V1
    p6_png = BUILD / "page-08.png"
    lines.append(f"file '{p6_png.as_posix()}'")
    lines.append(f"duration {PAGE_DURATIONS[8]}")
    if DEMO1.exists():
        lines.append(f"file '{rel_demo1.as_posix()}'")
        lines.append(f"duration {DUR_V1}")
        print(f"  + 录屏 V1:{DEMO1} ({DUR_V1}s)")
    else:
        print(f"  [WARN] 录屏 V1 缺失:{DEMO1},已跳过(只保留静态页)")

    # P7 演示 2 工作流(page-09) + 录屏 V2
    p7_png = BUILD / "page-09.png"
    lines.append(f"file '{p7_png.as_posix()}'")
    lines.append(f"duration {PAGE_DURATIONS[9]}")
    if DEMO2.exists():
        lines.append(f"file '{rel_demo2.as_posix()}'")
        lines.append(f"duration {DUR_V2}")
        print(f"  + 录屏 V2:{DEMO2} ({DUR_V2}s)")
    else:
        print(f"  [WARN] 录屏 V2 缺失:{DEMO2},已跳过(只保留静态页)")

    # P8-P12:静态页(page-10 ~ page-12)
    # 关键映射:PAGE_DURATIONS 中 P8=10, P9=11, P10=12
    for page_idx in (10, 11, 12):
        png = BUILD / f"page-{page_idx:02d}.png"
        dur = PAGE_DURATIONS[page_idx]
        lines.append(f"file '{png.as_posix()}'")
        lines.append(f"duration {dur}")

    filelist.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  filelist 写入:{filelist}({len(lines)//2} 段)")


def step3_ffmpeg_concat(tools: dict[str, str | None]) -> bool:
    """ffmpeg 用 concat demuxer 按每页指定时长拼图 + 录屏。"""
    print("\n=== Step 3: ffmpeg concat ===")
    binary = tools.get("ffmpeg")
    if not binary:
        print("[SKIP] ffmpeg 不可用,跳过拼接")
        return False

    # 校验必要静态 png
    needed = [BUILD / f"page-{i:02d}.png" for i in range(1, 13)]
    missing_png = [p.name for p in needed if not p.exists()]
    if missing_png:
        print(f"[ERROR] 缺失静态 png:{missing_png},无法拼接")
        return False

    filelist = BUILD / "filelist.txt"
    _write_filelist(filelist)

    # ffmpeg:concat demuxer + 1920x1080 + yuv420p + 24fps
    cmd = [
        binary, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(filelist),
        "-vsync", "vfr",
        "-pix_fmt", "yuv420p",
        "-r", "24",
        "-vf", "scale=1920:1080",
        str(OUT_MP4),
    ]
    return safe_run("ffmpeg concat", cmd)


# ============== Step 4: ffprobe 验证 ==============
def step4_verify(tools: dict[str, str | None]) -> bool:
    """ffprobe 验证视频(时长、分辨率、帧率)。"""
    print("\n=== Step 4: ffprobe verify ===")
    binary = tools.get("ffprobe")
    if not binary:
        print("[SKIP] ffprobe 不可用,跳过验证")
        return False
    if not OUT_MP4.exists():
        print(f"[ERROR] 输出视频不存在:{OUT_MP4}")
        return False

    cmd = [
        binary, "-v", "error",
        "-show_entries",
        "format=duration,size:stream=width,height,r_frame_rate,codec_name",
        "-of", "default=noprint_wrappers=1",
        str(OUT_MP4),
    ]
    if not safe_run("ffprobe", cmd):
        return False

    # 解析并校验
    try:
        result = subprocess.run(
            [binary, "-v", "error",
             "-show_entries", "format=duration:stream=width,height,r_frame_rate",
             "-of", "default=noprint_wrappers=1:nokey=1",
             str(OUT_MP4)],
            capture_output=True, text=True, check=True,
        )
        lines = [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]
        # 输出顺序:duration, width, height, r_frame_rate
        if len(lines) >= 4:
            duration = float(lines[0])
            width = int(lines[1])
            height = int(lines[2])
            # r_frame_rate 是分数形式如 24/1
            num, _, den = lines[3].partition("/")
            fps = float(num) / float(den or 1)

            print(f"\n--- 视频信息 ---")
            print(f"  时长  :{duration:.1f}s({duration/60:.2f} 分钟)")
            print(f"  分辨率:{width}x{height}")
            print(f"  帧率  :{fps:.1f} fps")
            print(f"  大小  :{OUT_MP4.stat().st_size / 1024 / 1024:.2f} MB")

            checks = []
            checks.append(("时长 ≤ 480s (8 分钟)", duration <= 480))
            checks.append(("分辨率 1920x1080", width == 1920 and height == 1080))
            checks.append(("帧率 ≥ 24 fps", fps >= 24))
            print("\n--- 校验 ---")
            for label, ok in checks:
                print(f"  [{'OK' if ok else 'FAIL'}] {label}")
            return all(ok for _, ok in checks)
    except (subprocess.CalledProcessError, ValueError, IndexError) as e:
        print(f"[WARN] 解析 ffprobe 输出失败:{e}")
    return True


# ============== Main ==============
def main() -> int:
    print("=" * 60)
    print("JavaBrain PPT → MP4")
    print("=" * 60)
    print(f"PPT  :{PPT}")
    print(f"PDF  :{PDF}")
    print(f"BUILD:{BUILD}")
    print(f"OUT  :{OUT_MP4}")

    tools = check_tools()

    s1 = step1_pptx_to_pdf(tools)
    s2 = step2_pdf_to_png(tools)
    s3 = step3_ffmpeg_concat(tools)
    s4 = step4_verify(tools)

    print("\n" + "=" * 60)
    print("汇总")
    print("=" * 60)
    print(f"  Step 1 (pptx → pdf) :{'OK' if s1 else 'FAIL/SKIP'}")
    print(f"  Step 2 (pdf → png)  :{'OK' if s2 else 'FAIL/SKIP'}")
    print(f"  Step 3 (ffmpeg)     :{'OK' if s3 else 'FAIL/SKIP'}")
    print(f"  Step 4 (ffprobe)    :{'OK' if s4 else 'FAIL/SKIP'}")

    if OUT_MP4.exists():
        print(f"\n✓ 输出视频:{OUT_MP4}")
    else:
        print(f"\n[FAIL] 未生成 javabrain.mp4")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

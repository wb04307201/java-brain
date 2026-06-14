# 录屏视频存放说明

> 用途:存放 JavaBrain 答辩 PPT 第 6 页、第 7 页所需的录屏视频素材。

## 📁 目录结构

```
videos/
├── README.md           ← 本文件
├── demo1/              ← 录屏 1:一句话出数据分析报告(90 秒)
│   ├── demo1-raw.mp4       原始素材(可保留剪辑前版本)
│   ├── demo1-final.mp4     剪辑后(嵌入 PPT 用)
│   ├── demo1-subtitle.srt  字幕文件(可选,剪映/Arctime 导出)
│   ├── demo1-narration.txt 旁白脚本(可选,便于复用)
│   └── demo1-tts.mp3       配音声轨(可选,Edge TTS 生成)
└── demo2/              ← 录屏 2:一句话生成 CRUD(100 秒)
    ├── demo2-raw.mp4
    ├── demo2-final.mp4
    ├── demo2-subtitle.srt
    ├── demo2-narration.txt
    └── demo2-tts.mp3
```

## 🎬 录屏规格建议

| 参数 | 建议值 |
|---|---|
| 分辨率 | **1920×1080** (16:9,PPT 全屏铺满不模糊) |
| 帧率 | 30 fps(够用)或 60 fps(更丝滑,文件大) |
| 编码 | H.264 + AAC(兼容性最好) |
| 比特率 | 4-8 Mbps(1080p) |
| 时长 | demo1 = 90 秒,demo2 = 100 秒(精确到秒) |

## ⏱️ 录屏分镜(从 PPT-OUTLINE.md 抄)

### demo1(90 秒,6 个画面)
1. 0:00-0:05 输入演示语
2. 0:05-0:20 AI 推理过程
3. 0:20-0:40 表格结果 + 柱状图
4. 0:40-0:50 保存 HTML 报告
5. 0:50-1:10 打开预览(慢镜头)
6. 1:10-1:30 返回聊天,展示预览+下载链接

### demo2(100 秒,6 个画面)
1. 0:00-0:15 输入 + AI 字段推断
2. 0:15-0:25 确认 + AI 生成
3. 0:25-0:30 3 行输出(已生成 + 链接)
4. 0:30-0:50 切到 oms 登录 + CRUD 页面(慢镜头)
5. 0:50-1:30 演示搜索 / 新增 / 修改 / 导出
6. 1:30-1:40 切回聊天,展示就这 3 行

## 🛠️ 推荐工具

- **录制**:OBS Studio(免费,跨平台)— Windows 录 1080p 30fps 很稳
- **剪辑**:剪映(国产免费)— 字幕一键识别,导出 SRT
- **配音**:Edge TTS(免费)— 见 `scripts/tts-edge.py`(待补)
- **截图**:ffmpeg(录完视频后跑,见 `../images/README.md` 的 ffmpeg 段)

## 🚀 录完后的工作流

```bash
# 1. 把原始录屏放到 demo1/demo1-raw.mp4
# 2. 用剪映剪辑 → 导出 demo1-final.mp4
# 3. 用剪映自动字幕 → 导出 demo1-subtitle.srt
# 4. 嵌入 PPT:把 demo1-final.mp4 拖到第 6 页(选"自动播放")
# 5. 截缩略图(给 PPT 第 6 页静态封面用):
ffmpeg -i videos/demo1/demo1-final.mp4 -ss 5 -vframes 1 images/page-06-demo1.png
```

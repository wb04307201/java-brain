# JavaBrain 参赛 PPT · 简版大纲(v2 白底 2.5D 乐高)

> 版本:v2(全新方向,基于白底 2.5D 乐高 + 转视频动画控制)
> 日期:2026-06-15
> 状态:已生成 12 页 PPT + 转视频脚本
> 适用受众:答辩评委(技术派 + 商业派)
> 时长上限:8 分钟

---

## 🎯 一句话定位

JavaBrain = 灵梭 AI Agent + SQL 工坊 + SQL 工坊 MCP
让企业级 Spring Boot 应用,3 分钟接入 AI、90 秒出分析报告、10 分钟出可用页面。
**3 个都是依赖库,不是产品** —— 可单独引入,按需组合。

---

## 🎬 8 分钟节奏(449s = 7:29 + 静默 31s)

| 段 | 内容 | 时长 | 累计 | 动画 |
|---|---|---:|---:|---|
| P1 | 封面(3 乐高 + JavaBrain + 金钩) | 15s | 0:15 | 5 fade_in |
| P2 | 痛点(3 红 vs 3 绿 + 杀手锏金边) | 50s | 1:05 | 7 fade + 1 pulse |
| P3 | 定位(3 乐高 + 4 行 ✓) | 35s | 1:40 | 3 fade + 1 pulse |
| P4-a | 灵梭整体(4 特性卡) | 20s | 2:00 | 3 fade + 1 pulse |
| P4-b | 灵梭 6 模块(MCP/Skill 杀手锏) | 35s | 2:35 | 6 fade + 2 chase |
| P5-a | SQL 整体(4 特性卡) | 20s | 2:55 | 3 fade + 1 pulse |
| P5-b | SQL 4 starter + 6 功能(3 杀手锏) | 45s | 3:40 | 10 fade + 3 chase |
| P6 | 演示 1 工作流(5 步说明卡) | 6s | 3:46 | 5 fade + 1 pulse |
| V1 | 🎬 录屏 1 实际效果 | 42s | 4:28 | — |
| P7 | 演示 2 工作流(5 步说明卡) | 6s | 4:34 | 5 fade + 1 pulse |
| V2 | 🎬 录屏 2 实际效果 | 40s | 5:14 | — |
| P8 | 实战对比(4 ✓ + 5 行对比) | 55s | 6:09 | 9 fade + 1 pulse |
| P9 | 路线图(3 仓库 + V1.0-V1.3) | 40s | 6:49 | 4 fade + 1 pulse |
| P10 | 结尾(3 句 + 金句 + 启动日志) | 40s | 7:29 | 5 fade + 1 pulse |
| — | (留白填充到 8:00) | 31s | 8:00 | — |

---

## 🎨 设计语言(白底 2.5D 乐高)

**核心哲学**:Apple Keynote / Vercel 风格,白底 + 立体乐高积木 + 持续脉冲的杀手锏金边,转视频无白屏。

### 7 色 + 4 中性

| 角色 | HEX | 用途 |
|---|---|---|
| Java 蓝 | `#007396` | 灵梭 / 标题 / 关键数据 |
| AI 紫 | `#6B46C1` | SQL 工坊 / 副标 |
| 语义红 | `#DC2626` | 痛点数字 |
| 语义绿 | `#10B981` | 解法数字 / MCP 组件 |
| 钩子金 | `#F59E0B` | 杀手锏金边 / 关键金句 |
| 文字主 | `#1F2937` | 主标 / 卡片 |
| 文字次 | `#6B7280` | 注脚 / 副标 |
| 浅金底 | `#FEF3C7` | 杀手锏金边背景 |
| 浅绿底 | `#D1FAE5` | 对比表 ✓ 行背景 |
| 浅米白底 | `#FAFBFC` | 9 页通用 |

### 字体

- 中文:**阿里巴巴普惠体 3.0**(主)
- 英文:**Inter**(UI/数字)
- 等宽:**JetBrains Mono**(仅 P10 终端)

### 字号 5 级

- 主标 48pt / 副 24pt / 正文 18pt / 数字冲击 36-48pt / 注脚 12pt

### 2.5D 乐高组件

圆角矩形 + 4 圆钉 + 顶部高光条(alpha 30%)+ 软阴影。重复使用于 P1 封面、P3 定位。

---

## 🎬 动画系统(转视频核心)

**4 类时长控制策略**:

| 策略 | 适用页 | 节奏 |
|---|---|---|
| A. 入场群 | P1/P3/P4-a/P5-a/P9 | 0-2s 元素分批入场,之后静默 |
| B. 入场+循环脉冲 | P2/P8/P10 | 0-8s 入场,8s 起关键元素 pulse_loop indefinite |
| C. 入场+高亮追逐 | P4-b/P5-b | 0-12s 入场,12s 起多个杀手锏金边 chase pulse(2s 错开) |
| D. 全工作流连续 | P6/P7 | 0-4s 5 步依次入,末步 pulse_loop |

**3 类动画节点**(实际实现):

| 类型 | 数量 | 占比 | 实现 |
|---|---:|---:|---|
| fade_in 入场(一次性) | 65 | 82% | presetClass="entr" presetId="10" |
| pulse_loop indefinite(普通循环) | 9 | 11% | presetClass="emph" presetId="26" + repeatCount="indefinite" |
| chase_pulse(沿卡片追逐) | 5 | 6% | pulse_loop + delay 错开 2s |
| **总账** | **79** | **100%** | (其中 14 个 indefinite) |

> 注:spec §5.3 原写 83 (63+15+5),实际 add_anim 实现是 79 (65+14) — chase 5 是 pulse_loop 14 的子集,不重复计。每个 `add_anim(loop=True)` 产生 1 个 `<p:timing>` 节点。

**为什么需要 pulse_loop**:
- 转视频时静态元素会让画面冻结 30-50s
- pulse_loop indefinite 持续脉冲,占满每页剩余时长,转视频后无白屏

---

## 🎬 转视频管线

```
gen-ppt.py (产出 javabrain.pptx, 12 页, 79 动画)
        ↓
libreoffice --headless --convert-to pdf
        ↓
pdftoppm -png -r 150 逐页转 PNG
        ↓
ffmpeg concat demuxer 按 PAGE_DURATIONS 拼图
        ↓
[可选] ffmpeg 叠脉冲层(弥补 libreoffice 丢 pulse_loop)
        ↓
剪映追加录屏 V1(42s)在 3:46 + 录屏 V2(40s)在 4:34
        ↓
剪映导出 javabrain.mp4 (≤ 8:00, 1080p, ≥24fps)
```

**依赖工具**(用户需安装):libreoffice / poppler(pdftoppm) / ffmpeg。

---

## 📂 配套文件

| 路径 | 用途 |
|---|---|
| `scripts/gen-ppt.py` | PPT 主生成器(~1500 行,含 7 色 + add_anim + iso_lego + 12 slide_X) |
| `scripts/gen-video.py` | 转视频脚本(libreoffice + pdftoppm + ffmpeg) |
| `javabrain.pptx` | 12 页 PPT 源文件(由 gen-ppt.py 生成) |
| `javabrain.mp4` | 8 分钟最终视频(由 gen-video.py 生成,需先装工具) |
| `tests/test_anim.py` | add_anim 单元测试(3 个) |
| `tests/verify_t1.py` ~ `verify_t7.py` | 12 页内容验证脚本(58 个 check) |
| `docs/superpowers/specs/2026-06-15-javabrain-ppt-v2-design.md` | v2 设计文档 |
| `docs/superpowers/plans/2026-06-15-javabrain-ppt-v2.md` | 实施计划 |
| `videos/demo1/demo1-final.mp4` | 录屏 1(42s,输入) |
| `videos/demo2/demo2-final.mp4` | 录屏 2(40s,输入) |

---

## ✅ 验收标准

### PPT(12 条)
1. 12 页,顺序与本文 §"8 分钟节奏"表一致
2. 16:9 比例(13.333×7.5 in)
3. 配色锁死:#007396 / #F59E0B / #DC2626 / #10B981
4. 字体:阿里巴巴普惠体 3.0 / Inter / JetBrains Mono
5. 每页 5±2 元素,留白≥20%
6. 79 个动画节点(65 fade_in + 14 pulse_loop)
7. 14 个 pulse_loop 用 `repeatCount="indefinite"`
8. 5 个 chase_pulse 的 delay_ms 错开 2s
9. 文字层全部 PowerPoint 矢量
10. 无 PIL 渲染,所有图形用 python-pptx 形状
11. 2.5D 乐高:圆角矩形 + 4 圆钉
12. 5 米外能看清:主标≥48pt,正文≥18pt,注脚≥12pt

### 视频(9 条)
1. 视频总时长 ≤ 8 分钟(480s)
2. 12 页顺序与 §"8 分钟节奏"一致
3. 每页停留时长与 §"8 分钟节奏"一致
4. 录屏 V1(42s)在 P6 后(~3:46),V2(40s)在 P7 后(~4:34)
5. 帧率 ≥ 24fps
6. 分辨率 1920×1080

### 仓库状态(5 条)
1. `OUTLINE.md` 已同步 v2 12 页+79 动画+转视频
2. `.gitignore` 含 `.superpowers/`
3. `javabrain.pptx` 已生成
4. `javabrain.mp4` 可生成(需先装 ffmpeg/libreoffice)
5. 所有源码提交到 git

---

## 🎯 答辩前 1 小时检查清单(给用户)

| 项 | 检查 | 替换为 |
|---|---|---|
| 仓库地址 | Ctrl+F 搜 `wb04307201` | 真名(若有) |
| Star/Fork 数字 | P9 三仓库卡 ★ 124 / ★ 89 / ★ 89 | GitHub 实测 |
| 团队名 | P10 致谢 | 真实团队名 |
| 邮箱 | P10 | 真实邮箱 |
| 启动秒数 | P10 终端 25.394s | `time mvn spring-boot:run` 实测 |
| 字体 | 答辩电脑装好 阿里普惠体 3.0 + Inter + JetBrains Mono | — |
| 视频导出 | javabrain.mp4 试播 1 分钟,确认动画+录屏+声音 | — |

---

## 🚫 不做的事

- ❌ 不做 PIL 背景渲染(纯 python-pptx 矢量)
- ❌ 不加切页动画(转视频用 ffmpeg 拼图)
- ❌ 不动 v16 旧 PPT 文件(已 superseded)
- ❌ 不解决字体替换问题(用答辩电脑装字体解决)
- ❌ 不重新生成 AI 配图(7 张 AI 图已在 v16 决定弃用)

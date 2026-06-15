# JavaBrain 参赛 PPT v2 设计

> 版本:v2(全新方向,基于白底 2.5D 乐高 + 转视频动画控制)
> 日期:2026-06-15
> 状态:brainstorming 已通过 5 段审批,等待用户审 spec
> 适用受众:答辩评委(技术派 + 商业派)
> 时长上限:8 分钟(答辩陈述)

---

## 1. 目的与背景

JavaBrain 是一个 8 分钟比赛答辩 PPT,需要最终转成视频。本设计推翻旧 v16(数字冲击+抽象几何+纯 PowerPoint 形状)的"静态 + 一次性动画"思路,采用**白底 2.5D 乐高**设计语言,核心解决"转视频时静态页面白屏"问题。

**为什么推翻 v16**:
- 旧 v16 的 5 页动画是"入场装饰",转视频后页面静止 30-50s = 30-50s 白屏录屏
- 旧 v16 的"大数字 144pt + 7 色高对比"在答辩现场灯光下视觉疲劳
- 旧 v16 的 10 页结构里,P4/P5 把"产品定位"和"功能清单"挤在一页,信息密度过大

**v2 核心变化**:
- 设计语言:大数字 + 抽象几何 → **白底 2.5D 乐高**(Apple Keynote / Vercel 风格)
- 配色:7 色高对比 → **Java 蓝主 + 语义色**(红=痛,绿=解,金=钩)
- 结构:10 页 → **12 页**(P4 拆 2 + P5 拆 2)
- 动画:15 个一次性 → **78 个**(56 入场 + 17 持续循环 + 5 高亮追逐)
- 产出:PPT → **PPT + 视频**(剪映追加录屏)

---

## 2. 顶层决策(已锁)

| 维度 | 决策 | 备注 |
|---|---|---|
| 用途 | 比赛答辩 | 5 米外能看清 / 数字冲击力 |
| 时长 | 8 分钟陈述(内容 7:29 + 静默 31s) | 上限 8:00 |
| 页数 | 12 页 | P4 拆 2 + P5 拆 2 |
| 设计语言 | C. 白底 2.5D 乐高 | Apple Keynote / Vercel 风格 |
| 录屏过场 | A. 5 步工作流说明卡 | 录屏前先讲"AI 怎么调" |
| 配色 | D. Java 蓝主 + 语义色 | 红=痛,绿=解,金=钩 |
| 动画 | 78 个(P2/P6/P7/P8/P10 5 页有) | 17 个 pulse_loop 持续到翻页 |
| 技术路线 | α. python-pptx 纯矢量 | 不引入 PIL,字体 100% 兼容 |

---

## 3. 12 页结构(7:29 内容 + 31s 静默 = 8:00)

| 页 | 内容 | 时长 | 动画 | 策略 |
|---|---|---:|---|---|
| P1 | 封面 · JavaBrain 三件套 | 15s | 5 fade_in | A 入场群 |
| P2 | 痛点 · 3 红 vs 3 绿 | 50s | 8(7 入场 + 1 循环) | B 入场+循环脉冲 |
| P3 | 定位 · 3 乐高+4 行 | 35s | 4(3 入场 + 1 循环) | A |
| P4-a | **灵梭 · 整体定位**(NEW) | 20s | 4(3 入场 + 1 循环) | A |
| P4-b | 灵梭 · 6 模块功能 | 35s | 8(6 入场 + 2 chase 循环) | C 入场+高亮追逐 |
| P5-a | **SQL工坊 · 整体定位**(NEW) | 20s | 4(3 入场 + 1 循环) | A |
| P5-b | SQL工坊 · 4 starter + 6 功能 | 45s | 11(10 入场 + 3 chase 循环) | C |
| P6 | 演示 1 · 5 步工作流 | 6s | 6(5 入场 + 1 循环) | D 全工作流连续 |
| V1 | 🎬 录屏 1(剪映追加) | 42s | — | 视频 |
| P7 | 演示 2 · 5 步工作流 | 6s | 6(5 入场 + 1 循环) | D |
| V2 | 🎬 录屏 2(剪映追加) | 40s | — | 视频 |
| P8 | 实战对比 · 7 测试 + 5 行对比 | 55s | 10(9 入场 + 1 循环) | B |
| P9 | 路线图 · 3 仓库 + V1.0-V1.3 | 40s | 4(3 入场 + 1 循环) | A |
| P10 | 结尾 · 3 句话 + 金句 + 启动日志 | 40s | 6(4 入场 + 2 循环) | B |

---

## 4. 设计语言(锁死)

### 4.1 配色(7 色)

| 角色 | 颜色 | 用途 |
|---|---|---|
| 主色 | `#007396` Java 蓝 | 灵梭 / 标题 / 关键数据 |
| 辅色 1 | `#6B46C1` AI 紫 | SQL工坊 / 副标 |
| 语义红 | `#DC2626` | 痛点数字(P2 红字) |
| 语义绿 | `#10B981` | 解法数字 / 成功状态(P2 绿字 / MCP 组件) |
| 钩子金 | `#F59E0B` | 杀手锏金边 / 关键金句 |
| 文字主 | `#1F2937` 深灰 | 主标 / 卡片 |
| 文字次 | `#6B7280` 浅灰 | 注脚 / 副标 |
| 底色 | `#FAFBFC` 浅米白 | 9 页通用 |
| 浅金底 | `#FEF3C7` | 杀手锏金边背景 |
| 浅绿底 | `#D1FAE5` | 对比表 ✓ 行背景 |

### 4.2 字体

| 字体 | 用途 |
|---|---|
| 阿里巴巴普惠体 3.0 | 中文(主) |
| Inter | 英文(UI) / 数字 |
| JetBrains Mono | 等宽(仅 P10 终端) |

### 4.3 字号 5 级

| 级别 | 字号 | 用途 |
|---|---:|---|
| 主标 | 48pt | 每页标题 |
| 副标 | 24pt | 章节小标 / 引文 |
| 正文 | 18pt | 卡片文字 |
| 数字冲击 | 36pt | P2 痛点 6 数字 |
| 注脚 | 12pt | 仓库地址 / 致谢 |

### 4.4 2.5D 乐高组件(P1/P3 用)

乐高积木 = 圆角矩形 + 顶部 4 圆钉 + 顶部高光条 + 软阴影
- 圆角矩形:`MSO_SHAPE.ROUNDED_RECTANGLE`,圆角半径 = 短边 × 15%
- 4 圆钉:4 个小圆(`MSO_SHAPE.OVAL`),位于顶部上沿外侧,直径 = 短边 × 15%
- 顶部高光条:同宽 × 8% 高的细矩形,白色 alpha 30%,贴顶部
- 软阴影:XML `<a:outerShdw>` blur=120000(12pt), dist=40000(4pt), color=#000000 alpha=8%

3 种乐高(蓝/紫/绿)在 P1 封面和 P3 定位重复使用,尺寸 60×60 in(P1)/ 80×30 in(P3 横条)。

---

## 5. 动画系统(转视频核心)

### 5.1 4 类时长控制策略

| 策略 | 适用页 | 节奏 |
|---|---|---|
| A. 入场群 | P1/P3/P4-a/P5-a/P9 | 0-2s 元素分批入场,之后静默 |
| B. 入场+循环脉冲 | P2/P8/P10 | 0-8s 入场,8s 起关键元素 pulse_loop indefinite |
| C. 入场+高亮追逐 | P4-b/P5-b | 0-12s 入场,12s 起多个杀手锏金边 chase pulse(2s 错开) |
| D. 全工作流连续 | P6/P7 | 0.5-4.5s 5 步依次入,末步 pulse_loop 1.5s |

### 5.2 动画类型 XML 实现

| 动画 | XML 参数 | 用途 |
|---|---|---|
| `fade_in` | `<p:animEffect preset="entr" presetId="10" dur="500"/>` | 入场,delay_ms 步进 |
| `pulse_loop`(NEW) | `<p:animEffect preset="emph" presetId="26" dur="1500" repeatCount="indefinite"/>` | 持续脉冲,占满剩余时长 |
| `chase_pulse`(NEW) | pulse_loop + delay 错开 2s | 沿卡片依次脉冲,自动 chase 效果 |
| `delay_step` | fade_in + delay_ms 步进 | 多元素按节奏入场 |

### 5.3 动画节点实算(83 个)

| 类型 | 数量 | 说明 |
|---|---:|---|
| fade_in 入场(一次性) | 63 | 1-2s 内完成,之后静止 |
| pulse_loop indefinite(普通循环) | 15 | 占满每页剩余时长,转视频核心 |
| chase_pulse(沿卡片追逐的循环) | 5 | P4b 2 个 + P5b 3 个,各错开 2s;属于 pulse_loop 的子集 |
| **总账** | **83** | 63 + 15 + 5 |

每页动画时序见 OUTLINE.md 的"🎬 动画时序"附录。

### 5.4 add_anim 工具函数签名

```python
def add_anim(slide, shape, anim_type, *, delay_ms=0, dur_ms=500, loop=False):
    """注入 PowerPoint 动画节点。
    anim_type: 'fade_in' / 'fade_out' / 'zoom_in' / 'appear' /
               'fly_left' / 'fly_right' / 'fly_top' / 'fly_bot' / 'pulse'
    loop=True:  生成 repeatCount="indefinite"(持续到翻页)
    """
```

---

## 6. 转视频管线

```
gen-ppt.py (产出 javabrain.pptx, 12 页, 78 动画)
        ↓
libreoffice --headless --convert-to pdf javabrain.pptx
        ↓
ffmpeg 逐页拼图(pptx → pdf → png, 每页指定停留时长)
        ↓
[可选] ffmpeg 手动叠脉冲层(弥补 libreoffice 丢 pulse_loop)
        ↓
剪映追加录屏 V1(42s)在 3:46 + 录屏 V2(40s)在 4:34
        ↓
剪映导出 javabrain.mp4 (≤ 8:00, 1080p, ≥24fps)
```

**风险**:
- libreoffice 渲染 pptx → pdf 时可能丢 `pulse_loop indefinite`(变成静态)
  - **对策**:阶段 8 用 ffmpeg 的 `zoompan` + `drawtext` 给杀手锏金边手动加"金边脉冲"叠加层(透明 PNG 序列)
- PowerPoint 切页动画录屏不友好
  - **对策**:用 ffmpeg 直接拼图(不录 PowerPoint 翻页动作)
- 阿里巴巴普惠体 3.0 在 Windows 渲染时可能用替换字体
  - **对策**:答辩电脑装好字体

---

## 7. 文件结构

| 路径 | 用途 | 状态 |
|---|---|---|
| `docs/ppt/scripts/gen-ppt.py` | PPT 生成器 | ✏️ 重写(旧 1484 行改配色+形状) |
| `docs/ppt/scripts/gen-video.py` | 转视频脚本 | 🆕 新写 |
| `docs/ppt/javabrain.pptx` | 12 页 PPT 源文件 | 📦 输出 |
| `docs/ppt/javabrain.mp4` | 8 分钟最终视频 | 📦 输出 |
| `docs/ppt/OUTLINE.md` | 简版大纲(驾驶舱) | ✏️ 同步更新到 12 页+动画+转视频 |
| `docs/ppt/PPT-OUTLINE.md` | 1.65 万字源文件 | ❌ 不动(已被 OUTLINE 替代) |
| `docs/ppt/videos/demo1/demo1-final.mp4` | 录屏 1(42s) | 📦 输入 |
| `docs/ppt/videos/demo2/demo2-final.mp4` | 录屏 2(40s) | 📦 输入 |
| `docs/ppt/.superpowers/brainstorm/...` | brainstorming 记录 | 🆕 新建(已加 .gitignore) |
| `.gitignore` | 含 `.superpowers/` | ✏️ 更新 |

---

## 8. 实施步骤(9 阶段,~14.5h)

| 阶段 | 内容 | 验证 | 工时 |
|---|---|---|---:|
| 0 | 重写 gen-ppt.py:改配色常量 + 加 iso_lego 工具 + add_anim 加 loop=True | 运行无错,PowerPoint 打开正常 | 2h |
| 1 | 写 P1 封面(iso_lego 画 3 乐高 + 金钩子 + 5 动画) | OnlyOffice 确认立体感 | 1h |
| 2 | 写 P2 痛点(3 红 36pt + 箭头 + 3 绿 + 5 动画 + 1 pulse_loop) | OnlyOffice 确认金边脉冲持续 | 1h |
| 3 | 写 P3 定位 + P4-a 灵梭整体 + P4-b 6 模块 | OnlyOffice 确认 chase pulse 错开 2s | 2h |
| 4 | 写 P5-a SQL整体 + P5-b 4+6(3 杀手锏 chase) | OnlyOffice 确认 3 chase 错开 | 1.5h |
| 5 | 写 P6/P7 演示 1/2 工作流(策略 D) | OnlyOffice 确认 5 步按时序 | 1.5h |
| 6 | 写 P8 实战对比(9 行逐行 + 1 pulse_loop) | OnlyOffice 确认 5 行对比逐行 | 1.5h |
| 7 | 写 P9 路线图 + P10 结尾 | OnlyOffice 确认 P10 情感钩子 | 1.5h |
| 8 | 写 gen-video.py:libreoffice → ffmpeg 逐页拼 → 剪映追加 | 生成 javabrain.mp4,前 60s 试看 | 2h |
| 9 | 同步更新 OUTLINE.md 到 12 页+动画+转视频+清单 | OUTLINE 与实际一致 | 0.5h |

---

## 9. 验收标准

### 9.1 PPT 验收(12 条)

1. PPT 12 页,顺序与 §3 一致
2. 每页 16:9 比例(13.333×7.5 in)
3. 配色锁死:`#007396` / `#F59E0B` / `#DC2626` / `#10B981`
4. 字体:阿里巴巴普惠体 3.0 / Inter / JetBrains Mono
5. 每页 5±2 元素,留白≥20%
6. 83 个动画节点(63 fade_in + 15 pulse_loop + 5 chase_pulse)
7. 20 个 pulse_loop(含 5 个 chase)用 `repeatCount="indefinite"`
8. 5 个 chase_pulse 的 delay_ms 错开 2s
9. 文字层全部 PowerPoint 矢量
10. 无 PIL 渲染,所有图形用 python-pptx 形状
11. 2.5D 乐高:圆角矩形 + 4 圆钉 + 顶部高光 + 软阴影
12. 5 米外能看清:主标≥48pt,正文≥18pt,注脚≥12pt

### 9.2 视频验收(9 条)

1. 视频总时长 ≤ 8 分钟(480s)
2. 12 页顺序与 §3 一致
3. 每页停留时长与 §3 一致
4. 录屏 V1(42s)在 P6 后(时间戳 ~3:46),V2(40s)在 P7 后(~4:34)
5. P2 杀手锏金边 5s→50s 持续脉冲可见
6. P4b 2 个杀手锏 chase pulse 错开 2s 可见
7. P10 杀手锏金句 6s→40s 持续脉冲可见
8. 帧率 ≥ 24fps
9. 分辨率 1920×1080

### 9.3 仓库状态验收(5 条)

1. `OUTLINE.md` 已同步 12 页+动画+转视频
2. `.gitignore` 含 `.superpowers/`
3. `javabrain.pptx` 已生成可打开
4. `javabrain.mp4` 已生成可播放
5. 所有源码提交到 git

---

## 10. 答辩前 1 小时检查清单(给用户用)

| 项 | 检查 | 替换为 |
|---|---|---|
| 仓库地址 | Ctrl+F 搜 `wb04307201` | 真名(若有) |
| Star/Fork 数字 | P9 三仓库卡 ★ 124 / ★ 89 / ★ 89 | GitHub 实测 |
| 团队名 | P1/P10 致谢 | 真实团队名 |
| 邮箱 | P10 | 真实邮箱 |
| 参赛赛道 | P1/P10 | 实际赛道 |
| 启动秒数 | P10 终端 25.394s | `time mvn spring-boot:run` 实测 |
| 字体 | 答辩电脑装好 阿里普惠体 3.0 + Inter + JetBrains Mono | — |
| 视频导出 | javabrain.mp4 试播 1 分钟,确认动画+录屏+声音 | — |

---

## 11. 不做的事(避免范围蔓延)

- ❌ 不做录屏页 PIL 背景(2-6s 过场纯 PowerPoint 渐变 + 文字)
- ❌ 不重新生成 AI 配图(7 张 AI 图已在旧 v16.3 决定弃用)
- ❌ 不动 `PPT-OUTLINE.md`(1.65 万字源文件,被 `OUTLINE.md` 替代)
- ❌ 不改 `javabrain-narration.txt`(待 v2 写完后再同步)
- ❌ 不解决字体替换问题(用答辩电脑装字体解决)
- ❌ 不动 v16 旧 PPT 文件(可后续手动删除)

---

## 12. 开放问题(已确认无需解决)

- 录屏 V1/V2 mp4 格式:已有 `videos/demo1/demo1-final.mp4` 和 `videos/demo2/demo2-final.mp4`,无需重新生成
- V1/V2 在 PPT 内还是剪映内:剪映内追加(避免 pptx 嵌入视频兼容性)
- pulse_loop 在 libreoffice 渲染丢:阶段 8 手动叠脉冲层

---

## 13. 引用

- brainstorming 记录:`docs/ppt/.superpowers/brainstorm/39779-1781534014/content/`(6 个 mockup HTML)
- 旧 v16 大纲:`docs/ppt/OUTLINE.md`(v1 标记,已折叠调整记录)
- 灵梭 README:`C:\developer\IdeaProjects\spring-ai-loom-agent\README.zh-CN.md`
- SQL工坊 README:`C:\developer\IdeaProjects\sql-forge\README.zh-CN.md`
- 仓库根 CLAUDE.md:`C:\developer\IdeaProjects\java-brain\CLAUDE.md`

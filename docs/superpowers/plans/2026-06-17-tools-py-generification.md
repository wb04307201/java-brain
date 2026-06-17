# tools.py 通用化重构 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `docs/ppt/scripts/tools.py` 从带 JavaBrain 项目烙印的"跨版本工具库"改造成主题无关的中立工具库,同时同步改 3 个直接 import 旧 token/函数名的调用方。

**Architecture:** 重命名 token 改名(颜色 5 个) + 改字体默认值(1 个) + 加固 3 个函数的参数化(`hud_corner` / `section_label` / `apply_hud_chrome → apply_chrome`)+ 删 1 个被覆盖的函数(`section_label_v1`)+ 改 3 个调用方的引用。**无新增依赖,无新增文件,无测试新增**(现有 `test_tools.py` 即回归网)。

**Tech Stack:** Python 3.10+、`python-pptx`、`pytest`(回归测试用现有套件)。

---

## 文件结构

**修改**:
| 文件 | 责任 | 修改内容 |
|---|---|---|
| `docs/ppt/scripts/tools.py` | 工具库本体 | 5 个 token 改名 + 1 个字体值改 + 注释清理 + 3 个函数参数化 + 删 1 个函数 |
| `docs/ppt/scripts/gen-ppt-v3-new.py` | v3 PPT 生成器 | import + 11 处 token 引用 |
| `docs/ppt/scripts/qa_ppt_text.py` | 文字 QA | 错误信息字符串(可选改) |
| `docs/ppt/tests/test_tools.py` | tools 单元测试 | import + 12 处引用 |

**不动**:
- `gen-ppt.py`(旧版,自给自足)
- `gen-ppt-images.py` / `qa_image.py`(只用 QA/万相)
- `tests/test_v3_new.py`(测试名字符串不动)
- `OUTLINE_v3.md` / `videos/` / `images/`

---

## Task 1: 改 tools.py 的颜色 token 改名 + 注释清理

**Files:**
- Modify: `docs/ppt/scripts/tools.py:47-66`(颜色常量块)

- [ ] **Step 1: 替换颜色常量**

打开 `docs/ppt/scripts/tools.py`,找到第 47-66 行的颜色块:

```python
# 暗色背景
BG_DEEP = RGBColor(0x0A, 0x0E, 0x1A)       # 深空黑(主背景)
BG_PANEL = RGBColor(0x10, 0x17, 0x2A)      # 次级面板
GRID_LINE = RGBColor(0x1A, 0x22, 0x38)     # 网格线 / 卡片描边
DIVIDER = RGBColor(0x1A, 0x22, 0x38)

# 文字
TEXT_PRIMARY = RGBColor(0xE4, 0xE7, 0xF1)   # 冷白
TEXT_SECONDARY = RGBColor(0x7C, 0x8A, 0xA8) # 冷灰蓝
TEXT_DIM = RGBColor(0x4A, 0x55, 0x6E)       # 注脚

# 品牌主色
JAVA_BLUE = RGBColor(0x00, 0xD9, 0xFF)     # 电光蓝(灵梭)
AI_PURPLE = RGBColor(0xA7, 0x8B, 0xFA)     # AI 紫(SQL 工坊)
HOOK_GREEN = RGBColor(0x00, 0xFF, 0x9C)    # 钩子青绿(杀手锏)
ALERT_RED = RGBColor(0xFF, 0x4D, 0x6D)     # 警示红(痛点)
ALERT_GOLD = RGBColor(0xFA, 0xCC, 0x15)    # 警示金(路线图当前)

WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x00, 0x00, 0x00)
```

**替换为**(BG/TEXT/WHITE/BLACK 块保留,只改品牌主色块 + 注释去烙印):

```python
# 暗色背景
BG_DEEP = RGBColor(0x0A, 0x0E, 0x1A)       # 主背景(深色 HUD)
BG_PANEL = RGBColor(0x10, 0x17, 0x2A)      # 次级面板
GRID_LINE = RGBColor(0x1A, 0x22, 0x38)     # 网格线 / 卡片描边
DIVIDER = RGBColor(0x1A, 0x22, 0x38)

# 文字
TEXT_PRIMARY = RGBColor(0xE4, 0xE7, 0xF1)   # 主文字
TEXT_SECONDARY = RGBColor(0x7C, 0x8A, 0xA8) # 次级文字
TEXT_DIM = RGBColor(0x4A, 0x55, 0x6E)       # 注脚

# 语义主色(中性命名,不绑定项目)
PRIMARY = RGBColor(0x00, 0xD9, 0xFF)       # 主色
ACCENT = RGBColor(0xA7, 0x8B, 0xFA)        # 强调色
SUCCESS = RGBColor(0x00, 0xFF, 0x9C)       # 成功 / 反衬
DANGER = RGBColor(0xFF, 0x4D, 0x6D)        # 警示 / 痛点
WARN = RGBColor(0xFA, 0xCC, 0x15)          # 警示金 / 重点

WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x00, 0x00, 0x00)
```

- [ ] **Step 2: 替换全文 token 引用**

用 `replace_all` 在 tools.py 内全文替换(以下 5 组):

| 旧 | 新 |
|---|---|
| `JAVA_BLUE` | `PRIMARY` |
| `AI_PURPLE` | `ACCENT` |
| `HOOK_GREEN` | `SUCCESS` |
| `ALERT_RED` | `DANGER` |
| `ALERT_GOLD` | `WARN` |

工具函数内部如 `def big_num(..., color=JAVA_BLUE, ...)` 也要改。

- [ ] **Step 3: 改字体默认值**

`tools.py` 第 43 行:

```python
# Before
FONT_CN = "阿里巴巴普惠体 3.0"

# After
FONT_CN = "Microsoft YaHei"
```

- [ ] **Step 4: 验证导入**

```bash
cd "C:/developer/IdeaProjects/java-brain"
python -c "from tools import PRIMARY, ACCENT, SUCCESS, DANGER, WARN, FONT_CN; print(FONT_CN); print('OK')"
```

期望输出:`Microsoft YaHei` + `OK`。

- [ ] **Step 5: Commit**

```bash
cd "C:/developer/IdeaProjects/java-brain"
git add docs/ppt/scripts/tools.py
git commit -m "refactor(tools): rename project-flavored tokens to neutral semantics

JAVA_BLUE -> PRIMARY, AI_PURPLE -> ACCENT, HOOK_GREEN -> SUCCESS,
ALERT_RED -> DANGER, ALERT_GOLD -> WARN. FONT_CN default changed to
'Microsoft YaHei' (was '阿里巴巴普惠体 3.0'). Comment cleaned.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: `hud_corner` 加参数化

**Files:**
- Modify: `docs/ppt/scripts/tools.py:200-209`

- [ ] **Step 1: 重写 `hud_corner`**

把第 200-209 行:

```python
def hud_corner(slide, page_num, total=12):
    """左上 HUD 角标 + 右下页码(每页通用)。"""
    add_text(slide, 0.3, 0.18, 9.0, 0.3,
             "▓ JAVA / SPRING AI ▓ v1.0 ▓ SYS://OK ▓ 25.394s",
             font=FONT_MONO, size=10, color=TEXT_SECONDARY,
             align=PP_ALIGN.LEFT)
    add_text(slide, 10.5, 7.15, 2.5, 0.3,
             f"[ {page_num:02d} / {total} ]   < BACK   NEXT >",
             font=FONT_MONO, size=10, color=TEXT_SECONDARY,
             align=PP_ALIGN.RIGHT)
```

替换为:

```python
def hud_corner(slide, page_num, total=12, *, header='', pager='[ {n:02d} / {t} ]'):
    """HUD 角标(左上 + 右下页码)。header 为空时不显示左上文字。

    Args:
        header: 左上角文字(项目可填入自己的版本号 / 状态条 / 标语)
        pager: 右下角页码模板,用 {n} {t} 占位
    """
    if header:
        add_text(slide, 0.3, 0.18, 9.0, 0.3, header,
                 font=FONT_MONO, size=10, color=TEXT_SECONDARY,
                 align=PP_ALIGN.LEFT)
    add_text(slide, 10.5, 7.15, 2.5, 0.3,
             pager.format(n=page_num, t=total),
             font=FONT_MONO, size=10, color=TEXT_SECONDARY,
             align=PP_ALIGN.RIGHT)
```

- [ ] **Step 2: 验证导入并跑现有测试**

```bash
cd "C:/developer/IdeaProjects/java-brain"
python -c "from tools import hud_corner; print('OK')"
cd docs/ppt && python -m pytest tests/test_tools.py -v 2>&1 | tail -20
```

期望:`OK` + 测试全部 PASS(Task 2 之前测试里的 `apply_hud_chrome` 调用还有效,只是 import 行还没改 — 这是预期)。

- [ ] **Step 3: Commit**

```bash
cd "C:/developer/IdeaProjects/java-brain"
git add docs/ppt/scripts/tools.py
git commit -m "refactor(tools): parametrize hud_corner header and pager

Remove hardcoded '▓ JAVA / SPRING AI ▓ v1.0 ...' string. Add header/pager
kwargs; default pager is '[ {n:02d} / {t} ]'. Empty header hides the
upper-left text.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: `section_label` 参数化 + 删除 `section_label_v1`

**Files:**
- Modify: `docs/ppt/scripts/tools.py:212-224`

- [ ] **Step 1: 重写 `section_label`**

把第 212-216 行:

```python
def section_label(slide, text):
    """顶部章节标(等宽 11pt,冷灰蓝,带 ─── 装饰)。"""
    add_text(slide, 0.5, 0.55, 12.333, 0.3, text,
             font=FONT_MONO, size=11, color=TEXT_SECONDARY,
             align=PP_ALIGN.LEFT)
```

替换为:

```python
def section_label(slide, text, *,
                  size=11, color=TEXT_SECONDARY,
                  prefix='', font=FONT_MONO, bold=False):
    """顶部章节标。prefix 用于装饰前缀(如 '── ')。

    Args:
        prefix: 文本前拼接的装饰字符串(如 '── ')
        size/color/font/bold: 透传给内部 add_text
    """
    add_text(slide, 0.5, 0.55, 12.333, 0.3,
             f"{prefix}{text}", font=font, size=size,
             color=color, bold=bold, align=PP_ALIGN.LEFT)
```

- [ ] **Step 2: 删除 `section_label_v1`**

删除第 219-224 行整段 `section_label_v1` 函数:

```python
def section_label_v1(slide, text):
    """v3 章节标(等宽 14pt,Java 蓝 + 钩子青绿混色,带 ── 装饰前缀)。"""
    add_text(slide, 0.5, 0.55, 12.333, 0.3,
             f"── {text}",
             font=FONT_MONO, size=14, color=JAVA_BLUE, bold=True,
             align=PP_ALIGN.LEFT)
```

直接删除(grep 已确认无外部 import 引用)。

- [ ] **Step 3: 更新文件头部 docstring**

`tools.py` 第 1-18 行 docstring 的"分组"段,把第 6 行:

```python
B. 布局/装饰:   set_solid_bg, grid_bg, hud_corner, section_label,
                section_label_v1, corner_badge, add_page_number
```

改为:

```python
B. 布局/装饰:   set_solid_bg, grid_bg, hud_corner, section_label,
                corner_badge, add_page_number, apply_chrome
```

- [ ] **Step 4: 验证**

```bash
cd "C:/developer/IdeaProjects/java-brain"
python -c "from tools import section_label; print(hasattr(__import__('tools'), 'section_label_v1'))"
```

期望输出:`False`(`section_label_v1` 已删)。

- [ ] **Step 5: Commit**

```bash
cd "C:/developer/IdeaProjects/java-brain"
git add docs/ppt/scripts/tools.py
git commit -m "refactor(tools): parametrize section_label and drop v1 variant

section_label now accepts prefix/size/color/font/bold kwargs (replaces
v1 variant). Drop section_label_v1 (was a duplicate with hardcoded
'── ' prefix and JAVA_BLUE color).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: `apply_hud_chrome` → `apply_chrome` 重命名 + 参数化

**Files:**
- Modify: `docs/ppt/scripts/tools.py:244-258`

- [ ] **Step 1: 重写函数**

把第 244-258 行:

```python
def apply_hud_chrome(slide, page_num, total, section_text) -> None:
    """v3 标准化 slide 装饰四件套:背景 + 网格 + HUD 角标 + 章节标。

    等价于连续调用:
        set_solid_bg(slide, BG_DEEP)
        grid_bg(slide)
        hud_corner(slide, page_num, total=total)
        section_label(slide, section_text)

    适合 v3 / 后续版本每页都套这层 chrome。
    """
    set_solid_bg(slide, BG_DEEP)
    grid_bg(slide)
    hud_corner(slide, page_num, total=total)
    section_label(slide, section_text)
```

替换为:

```python
def apply_chrome(slide, page_num, total, section, *,
                 bg=BG_DEEP, header='', pager='', section_prefix='',
                 section_size=11, section_color=TEXT_SECONDARY):
    """slide 装饰四件套:背景 + 网格 + HUD 角标 + 章节标。

    适合每页都套这层 chrome 的项目一次性调用。

    Args:
        bg: 背景色,默认 BG_DEEP(深色 HUD)
        header: 左上 HUD 角标文字(同 hud_corner.header)
        pager: 右下页码模板(同 hud_corner.pager)
        section_prefix: 章节标装饰前缀(同 section_label.prefix)
        section_size/color: 章节标字号/颜色
    """
    set_solid_bg(slide, bg)
    grid_bg(slide)
    hud_corner(slide, page_num, total=total, header=header, pager=pager)
    section_label(slide, section, prefix=section_prefix,
                  size=section_size, color=section_color)
```

- [ ] **Step 2: 验证导入**

```bash
cd "C:/developer/IdeaProjects/java-brain"
python -c "from tools import apply_chrome; print(hasattr(__import__('tools'), 'apply_hud_chrome'))"
```

期望:`True` / `False`(新函数存在,旧函数名不存在)。

- [ ] **Step 3: Commit**

```bash
cd "C:/developer/IdeaProjects/java-brain"
git add docs/ppt/scripts/tools.py
git commit -m "refactor(tools): rename apply_hud_chrome to apply_chrome + parametrize

All four chrome pieces (bg/header/pager/section) are now kwargs.
Generic name reflects theme-agnostic intent.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 5: 同步 `gen-ppt-v3-new.py`

**Files:**
- Modify: `docs/ppt/scripts/gen-ppt-v3-new.py:28-34`(import)+ 11 处 token 引用

- [ ] **Step 1: 改 import 块**

第 28-34 行:

```python
# Before
from tools import (
    FONT_CN, FONT_MONO,
    BG_DEEP, BG_PANEL, GRID_LINE, DIVIDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM,
    JAVA_BLUE, AI_PURPLE, HOOK_GREEN, ALERT_RED, ALERT_GOLD,
    add_text, add_rect, add_picture_with_alpha, new_presentation,
)

# After
from tools import (
    FONT_CN, FONT_MONO,
    BG_DEEP, BG_PANEL, GRID_LINE, DIVIDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM,
    PRIMARY, ACCENT, SUCCESS, DANGER, WARN,
    add_text, add_rect, add_picture_with_alpha, new_presentation,
)
```

- [ ] **Step 2: 全文替换 token**

全文 `replace_all`(5 组):

| 旧 | 新 |
|---|---|
| `JAVA_BLUE` | `PRIMARY` |
| `AI_PURPLE` | `ACCENT` |
| `HOOK_GREEN` | `SUCCESS` |
| `ALERT_RED` | `DANGER` |
| `ALERT_GOLD` | `WARN` |

**注意**:`JAVA_BLUE_DARK = T.RGBColor(...)` 是文件内 v1 风格自定义色(在 52 行附近),**不要改**。改前先 grep 一下确认只有这一处是带 `_DARK` 后缀的。

```bash
cd "C:/developer/IdeaProjects/java-brain"
grep -n "JAVA_BLUE_DARK\|JAVA_BLUE[^_]" docs/ppt/scripts/gen-ppt-v3-new.py
```

应只看到 `JAVA_BLUE_DARK` 出现。

- [ ] **Step 3: 跑 PPT 生成**

```bash
cd "C:/developer/IdeaProjects/java-brain"
python docs/ppt/scripts/gen-ppt-v3-new.py
```

期望:无报错,生成 `docs/ppt/javabrain-v3.pptx`(覆盖原文件)。

- [ ] **Step 4: 验证旧 token 零引用**

```bash
cd "C:/developer/IdeaProjects/java-brain"
grep -nE "\bJAVA_BLUE\b|\bAI_PURPLE\b|\bHOOK_GREEN\b|\bALERT_RED\b|\bALERT_GOLD\b" \
    docs/ppt/scripts/gen-ppt-v3-new.py
```

期望:零输出。

- [ ] **Step 5: Commit**

```bash
cd "C:/developer/IdeaProjects/java-brain"
git add docs/ppt/scripts/gen-ppt-v3-new.py docs/ppt/javabrain-v3.pptx
git commit -m "refactor(ppt-v3): sync token renames in gen-ppt-v3-new.py

PRIMARY/ACCENT/SUCCESS/DANGER/WARN replace JAVA_BLUE/AI_PURPLE/HOOK_GREEN/
ALERT_RED/ALERT_GOLD. JAVA_BLUE_DARK (file-local) unchanged. Regenerate
javabrain-v3.pptx to confirm visual parity.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 6: 同步 `tests/test_tools.py`

**Files:**
- Modify: `docs/ppt/tests/test_tools.py:22-34`(import)+ 12 处引用

- [ ] **Step 1: 改 import 块**

第 22-34 行:

```python
# Before
from tools import (
    BG_DEEP, BG_PANEL, GRID_LINE,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM,
    JAVA_BLUE, HOOK_GREEN, ALERT_RED, ALERT_GOLD,
    FONT_CN, FONT_MONO,
    add_text, set_text, add_rect, add_picture_with_alpha,
    apply_hud_chrome, section_label, corner_badge, add_page_number,
    kill_box, node_block, card, terminal_box, big_num,
    iso_lego, arrow_line,
    new_presentation, qa_image_check, find_dominant_bg, cover_region,
    find_media_target, replace_pptx_media, qa_pptx_images,
    preview_grid, wanx_generate, wanx_download, wanx_upload, wanx_edit,
)

# After
from tools import (
    BG_DEEP, BG_PANEL, GRID_LINE,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM,
    PRIMARY, SUCCESS, DANGER, WARN,
    FONT_CN, FONT_MONO,
    add_text, set_text, add_rect, add_picture_with_alpha,
    apply_chrome, section_label, corner_badge, add_page_number,
    kill_box, node_block, card, terminal_box, big_num,
    iso_lego, arrow_line,
    new_presentation, qa_image_check, find_dominant_bg, cover_region,
    find_media_target, replace_pptx_media, qa_pptx_images,
    preview_grid, wanx_generate, wanx_download, wanx_upload, wanx_edit,
)
```

- [ ] **Step 2: 全文替换 token + 函数名**

全文 `replace_all`(6 组):

| 旧 | 新 |
|---|---|
| `JAVA_BLUE` | `PRIMARY` |
| `HOOK_GREEN` | `SUCCESS` |
| `ALERT_RED` | `DANGER` |
| `ALERT_GOLD` | `WARN` |
| `apply_hud_chrome` | `apply_chrome` |

注:`test_tools.py` 没引用 `AI_PURPLE`,跳过。

- [ ] **Step 3: 跑 pytest**

```bash
cd "C:/developer/IdeaProjects/java-brain/docs/ppt"
python -m pytest tests/test_tools.py -v 2>&1 | tail -30
```

期望:**全部 PASS**(无 FAIL)。

- [ ] **Step 4: 验证旧名零引用**

```bash
cd "C:/developer/IdeaProjects/java-brain"
grep -nE "\bJAVA_BLUE\b|\bHOOK_GREEN\b|\bALERT_RED\b|\bALERT_GOLD\b|\bapply_hud_chrome\b" \
    docs/ppt/tests/test_tools.py
```

期望:零输出。

- [ ] **Step 5: Commit**

```bash
cd "C:/developer/IdeaProjects/java-brain"
git add docs/ppt/tests/test_tools.py
git commit -m "test(tools): sync token renames and apply_chrome in test_tools.py

PRIMARY/SUCCESS/DANGER/WARN replace old names. apply_hud_chrome ->
apply_chrome. Existing test coverage still validates behavior.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 7: 同步 `qa_ppt_text.py`

**Files:**
- Modify: `docs/ppt/scripts/qa_ppt_text.py`(第 224 行附近的字符串,可不动;待 grep 确认)

- [ ] **Step 1: grep 确认引用位置**

```bash
cd "C:/developer/IdeaProjects/java-brain"
grep -nE "\bJAVA_BLUE\b|\bAI_PURPLE\b|\bHOOK_GREEN\b|\bALERT_RED\b|\bALERT_GOLD\b|\bsection_label_v1\b|\bapply_hud_chrome\b" \
    docs/ppt/scripts/qa_ppt_text.py
```

期望:仅命中字符串字面量(如 `f"#{idx+1}: missing HOOK_GREEN accent"`,不是 token 引用)。如果全是字符串,可不动此文件。

- [ ] **Step 2(可选):改错误信息字符串**

如果 grep 出的是错误信息字符串(描述用户问题的文字),可以把它们改成像样:

```python
# Before
issues.append(f"#{idx+1}: missing HOOK_GREEN accent")

# After
issues.append(f"#{idx+1}: missing SUCCESS accent")
```

如不动,直接跳到 Step 3。

- [ ] **Step 3: 跑 QA 验证**

```bash
cd "C:/developer/IdeaProjects/java-brain"
python docs/ppt/scripts/qa_ppt_text.py docs/ppt/javabrain-v3.pptx 2>&1 | tail -20
```

期望:无 `NameError` / `ImportError`,28 项检查正常输出。

- [ ] **Step 4: Commit(若有改动)**

```bash
cd "C:/developer/IdeaProjects/java-brain"
git add docs/ppt/scripts/qa_ppt_text.py
git commit -m "refactor(qa-ppt): sync token name in error message string (optional)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

若无改动,跳过 commit。

---

## Task 8: 全量验收 + 提交

- [ ] **Step 1: 跑 6 条验收命令**

```bash
cd "C:/developer/IdeaProjects/java-brain"

# 1. tools 可导入、新名生效
python -c "from tools import PRIMARY, ACCENT, SUCCESS, DANGER, WARN; print('OK')"
# 期望: OK

# 2. 旧名应零命中(允许 test_v3_new.py 中 3 处描述性字符串)
grep -rEn '\bJAVA_BLUE\b|\bAI_PURPLE\b|\bHOOK_GREEN\b|\bALERT_RED\b|\bALERT_GOLD\b|\bsection_label_v1\b|\bapply_hud_chrome\b' \
     docs/ppt/scripts/tools.py \
     docs/ppt/scripts/gen-ppt-v3-new.py \
     docs/ppt/scripts/qa_ppt_text.py \
     docs/ppt/tests/test_tools.py
# 期望: 零输出

# 3. 重新生成 PPT
python docs/ppt/scripts/gen-ppt-v3-new.py
# 期望: 无报错, javabrain-v3.pptx 已更新

# 4. QA 仍跑通
python docs/ppt/scripts/qa_ppt_text.py docs/ppt/javabrain-v3.pptx
# 期望: 全部 28 项检查通过

# 5. tools 单元测试通过
cd docs/ppt && python -m pytest tests/test_tools.py -v
# 期望: 全部 PASS
cd ../..

# 6. (可选)v3 PPT 测试通过
cd docs/ppt && python -m pytest tests/test_v3_new.py -v
cd ../..
```

- [ ] **Step 2: 跑最终的 git status / diff 检查**

```bash
cd "C:/developer/IdeaProjects/java-brain"
git log --oneline -10
git status
```

期望:看到本次重构的 5-7 个 commit,工作区只剩与重构无关的文件(`grid-preview.py` 删除、`tools.py` 修改等若是仓库初始状态就有的则保留)。

- [ ] **Step 3: 最终汇报**

向用户总结:
- 改了哪些 token / 函数
- 同步了哪些调用方
- 验收 6 条命令的结果

完工。

---

## 自审

**1. Spec 覆盖**:
- Spec §2 颜色 token 改名 → Task 1 ✓
- Spec §3 字体值改 → Task 1 ✓
- Spec §4 注释清理 → Task 1 ✓
- Spec §5.1 `hud_corner` 参数化 → Task 2 ✓
- Spec §5.2 `section_label` 参数化 → Task 3 ✓
- Spec §5.3 删除 `section_label_v1` → Task 3 ✓
- Spec §5.4 `apply_hud_chrome → apply_chrome` → Task 4 ✓
- Spec §7.1 `gen-ppt-v3-new.py` 同步 → Task 5 ✓
- Spec §7.2 `qa_ppt_text.py` 同步 → Task 7 ✓
- Spec §7.3 `tests/test_tools.py` 同步 → Task 6 ✓
- Spec §10 验收 → Task 8 ✓

**2. 占位符扫描**:无 TBD/TODO/"implement later"。

**3. 类型/方法名一致性**:`apply_chrome` 在 Task 4 定义、在 Task 6 测试中调用,签名一致;token 新名在 Task 1 定义、在 Task 5-7 引用,一致。

**4. 风险点**:
- Task 5 Step 2 的 `JAVA_BLUE_DARK` 检查必须做 — 否则会误改。
- Task 7 是可选,实际不动也能跑通 — 注释里已说明。
- Task 1 改了颜色 token,但 `tools.py` 内部函数 `def big_num(..., color=PRIMARY, ...)` 的默认值也改了 — 这是 spec 要求的语义统一(无副作用)。

---
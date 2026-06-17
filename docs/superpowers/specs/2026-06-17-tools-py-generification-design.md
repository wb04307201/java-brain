# tools.py 通用化重构 — 设计 spec

**日期**:2026-06-17
**作者**:Claude (与用户协作)
**状态**:已批准,待写实施计划

---

## 1. 背景与目标

`docs/ppt/scripts/tools.py` 当前文件头声明自己是"跨版本(v1/v2/v3)可复用的工具函数库",但实际内容带有 JavaBrain 项目烙印 — 重命名后可被任何 PPT 项目直接复用。

**目标**:`tools.py` 成为**主题无关的中立工具库**。

**不在范围内**:
- 任何函数行为/签名变更(仅当必须为通用化让步时才改,例如 `hud_corner` 加参数)
- PPT 视觉变化(项目配色由调用方决定,工具库只提供中性默认值)
- `OUTLINE_v3.md` / 配图 prompt / `videos/` 等项目内容
- 新增测试或依赖

---

## 2. Token 重命名

颜色 token — 命名改语义、值不改、不留旧名别名:

| 旧名 | 新名 | 语义 | RGB |
|---|---|---|---|
| `JAVA_BLUE` | **`PRIMARY`** | 主色 | `0x00D9FF` |
| `AI_PURPLE` | **`ACCENT`** | 强调色 | `0xA78BFA` |
| `HOOK_GREEN` | **`SUCCESS`** | 成功 / 反衬 | `0x00FF9C` |
| `ALERT_RED` | **`DANGER`** | 警示 / 痛点 | `0xFF4D6D` |
| `ALERT_GOLD` | **`WARN`** | 警示金 / 重点 | `0xFACC15` |

**保留不动**(已为通用语义):`BG_DEEP`、`BG_PANEL`、`GRID_LINE`、`DIVIDER`、`TEXT_PRIMARY`、`TEXT_SECONDARY`、`TEXT_DIM`、`WHITE`、`BLACK`。

## 3. 字体

| 名 | 旧值 | 新值 |
|---|---|---|
| `FONT_CN` | `"阿里巴巴普惠体 3.0"` | `"Microsoft YaHei"` |
| `FONT_EN` | `"Inter"` | 不动 |
| `FONT_MONO` | `"JetBrains Mono"` | 不动 |

字体名常量名 `FONT_CN/EN/MONO` 保留不动。

## 4. 注释清理

删除带项目烙印的注释,改为纯语义描述。例如:

```python
# Before
JAVA_BLUE = RGBColor(0x00, 0xD9, 0xFF)     # 电光蓝(灵梭)
AI_PURPLE = RGBColor(0xA7, 0x8B, 0xFA)     # AI 紫(SQL 工坊)
HOOK_GREEN = RGBColor(0x00, 0xFF, 0x9C)    # 钩子青绿(杀手锏)

# After
PRIMARY = RGBColor(0x00, 0xD9, 0xFF)       # 主色
ACCENT = RGBColor(0xA7, 0x8B, 0xFA)        # 强调色
SUCCESS = RGBColor(0x00, 0xFF, 0x9C)       # 成功 / 反衬
```

## 5. 函数重写

### 5.1 `hud_corner` — 去硬编码字符串

**Before**:
```python
def hud_corner(slide, page_num, total=12):
    add_text(slide, 0.3, 0.18, 9.0, 0.3,
             "▓ JAVA / SPRING AI ▓ v1.0 ▓ SYS://OK ▓ 25.394s", ...)
    add_text(slide, 10.5, 7.15, 2.5, 0.3,
             f"[ {page_num:02d} / {total} ]   < BACK   NEXT >", ...)
```

**After**:
```python
def hud_corner(slide, page_num, total=12, *, header='', pager='[ {n:02d} / {t} ]'):
    """HUD 角标(左上 + 右下页码)。header 为空时不显示左上。"""
    if header:
        add_text(slide, 0.3, 0.18, 9.0, 0.3, header,
                 font=FONT_MONO, size=10, color=TEXT_SECONDARY,
                 align=PP_ALIGN.LEFT)
    add_text(slide, 10.5, 7.15, 2.5, 0.3,
             pager.format(n=page_num, t=total),
             font=FONT_MONO, size=10, color=TEXT_SECONDARY,
             align=PP_ALIGN.RIGHT)
```

### 5.2 `section_label` — 加强参数化

**Before**:
```python
def section_label(slide, text):
    """顶部章节标(等宽 11pt,冷灰蓝,带 ─── 装饰)。"""
    add_text(slide, 0.5, 0.55, 12.333, 0.3, text, ...)
```

**After**:
```python
def section_label(slide, text, *,
                  size=11, color=TEXT_SECONDARY,
                  prefix='', font=FONT_MONO, bold=False):
    """顶部章节标(prefix 如 '── ' 用于装饰前缀)。"""
    add_text(slide, 0.5, 0.55, 12.333, 0.3,
             f"{prefix}{text}", font=font, size=size,
             color=color, bold=bold, align=PP_ALIGN.LEFT)
```

### 5.3 `section_label_v1` — 删除

已被 `section_label` 的参数化覆盖,且无外部调用方引用(grep 验证)。

### 5.4 `apply_hud_chrome` → `apply_chrome` — 重命名 + 全参数化

**Before**:
```python
def apply_hud_chrome(slide, page_num, total, section_text) -> None:
    """v3 标准化 slide 装饰四件套..."""
    set_solid_bg(slide, BG_DEEP)
    grid_bg(slide)
    hud_corner(slide, page_num, total=total)
    section_label(slide, section_text)
```

**After**:
```python
def apply_chrome(slide, page_num, total, section, *,
                 bg=BG_DEEP, header='', pager='', section_prefix='',
                 section_size=11, section_color=TEXT_SECONDARY):
    """slide 装饰四件套:背景 + 网格 + HUD 角标 + 章节标。
    适合每页都套这层 chrome 的项目。
    """
    set_solid_bg(slide, bg)
    grid_bg(slide)
    hud_corner(slide, page_num, total=total, header=header, pager=pager)
    section_label(slide, section, prefix=section_prefix,
                  size=section_size, color=section_color)
```

## 6. 不动的函数

`add_text` / `set_text` / `add_rect` / `add_picture_with_alpha` / `set_solid_bg` / `grid_bg` / `corner_badge` / `add_page_number` / `kill_box` / `node_block` / `card` / `terminal_box` / `big_num` / `stat_card` / `feature_card` / `bullet_list` / `with_alpha` / `arrow_line` / `iso_lego` / `chip_text` / `replace_pptx_media` / `find_dominant_bg` / `cover_region` / `qa_image_check` / `qa_pptx_images` / `find_media_target` / `new_presentation` / `preview_grid` / 全部 `wanx_*` 函数 — **签名/行为完全不变**。

## 7. 调用方同步

### 7.1 `gen-ppt-v3-new.py`

**第 28-34 行 import 替换**:

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

**全文替换**(已 grep 确认出现位置):`JAVA_BLUE` → `PRIMARY`、`AI_PURPLE` → `ACCENT`、`HOOK_GREEN` → `SUCCESS`、`ALERT_RED` → `DANGER`、`ALERT_GOLD` → `WARN`。

**不动**:`JAVA_BLUE_DARK = T.RGBColor(0x00, 0x73, 0x96)`(文件内 v1 风格自定义色,不是从 tools 导入的)。

### 7.2 `qa_ppt_text.py`

仅改 token 白名单列表(grep 确认:第 224 行 `missing HOOK_GREEN accent` 是错误信息字符串,可不改;其他 token 引用待精确 grep 后逐个改)。其他逻辑不动。

### 7.3 `docs/ppt/tests/test_tools.py` —— **新增波及面**

**自审发现**:此测试文件直接 import tools 旧 token 与旧函数名,**不修复会断**。

第 22-34 行 import 替换:

```python
# Before
from tools import (
    BG_DEEP, BG_PANEL, GRID_LINE,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM,
    JAVA_BLUE, HOOK_GREEN, ALERT_RED, ALERT_GOLD,    # → 改名
    FONT_CN, FONT_MONO,
    add_text, set_text, add_rect, add_picture_with_alpha,
    apply_hud_chrome, section_label, corner_badge, add_page_number,    # → apply_hud_chrome 改 apply_chrome
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

全文 grep 替换:`JAVA_BLUE` → `PRIMARY`、`HOOK_GREEN` → `SUCCESS`、`ALERT_RED` → `DANGER`、`ALERT_GOLD` → `WARN`、`apply_hud_chrome` → `apply_chrome`(共 12 处引用,grep 验证)。

## 8. 不动的文件

- `gen-ppt.py`(旧版,自给自足 — 文件内 `JAVA_BLUE` / `AI_PURPLE` 是它自己定义的局部常量,不引用 tools)
- `gen-ppt-images.py`(只用 QA/万相函数,无 token 引用)
- `qa_image.py`(同上)
- `docs/ppt/tests/test_v3_new.py`(测试名字符串里的 `ALERT_RED` 等是描述性文字,不影响运行;不改)
- `OUTLINE_v3.md` / `videos/` / `images/`(项目内容,不是工具库)
- `qa_ppt_text.py` 中的错误信息字符串(纯文本,不是引用)

## 9. 迁移策略

**硬切** — 不保留旧名别名。

理由:调用方仅 2 个文件,grep 范围可控;不留别名避免污染通用语义。

## 10. 验收步骤

完工时按顺序跑这 6 条命令:

```bash
# 1. tools 可导入、新名生效
python -c "from tools import PRIMARY, ACCENT, SUCCESS, DANGER, WARN; print('OK')"

# 2. 旧名应零命中(允许 tests/test_v3_new.py 中 3 处描述性字符串)
grep -rEn '\bJAVA_BLUE\b|\bAI_PURPLE\b|\bHOOK_GREEN\b|\bALERT_RED\b|\bALERT_GOLD\b|\bsection_label_v1\b|\bapply_hud_chrome\b' \
     docs/ppt/scripts/tools.py \
     docs/ppt/scripts/gen-ppt-v3-new.py \
     docs/ppt/scripts/qa_ppt_text.py \
     docs/ppt/tests/test_tools.py
# 期望:零输出(或仅 qa_ppt_text.py 中 1 处错误信息字符串)

# 3. 重新生成 PPT
python docs/ppt/scripts/gen-ppt-v3-new.py
# 期望:无报错,生成 docs/ppt/javabrain-v3.pptx

# 4. QA 仍跑通
python docs/ppt/scripts/qa_ppt_text.py docs/ppt/javabrain-v3.pptx
# 期望:全部 28 项检查通过

# 5. tools 单元测试通过
cd docs/ppt && python -m pytest tests/test_tools.py -v
# 期望:全部 PASS

# 6. (可选) v3 PPT 测试通过
cd docs/ppt && python -m pytest tests/test_v3_new.py -v
```

---

## 附录 A:波及面统计

精确 grep 验证(2026-06-17):

- `tools.py`:旧 token 5 处 + `section_label_v1` 1 处 + `apply_hud_chrome` 2 处 + 文档注释 3 处 = **11 处**
- `gen-ppt-v3-new.py`:import 1 处 + 引用 11 处 = **12 处**
- `qa_ppt_text.py`:错误信息字符串 1 处(可选改) = **1 处**
- `tests/test_tools.py`:import 1 处 + `apply_hud_chrome` 2 处 + token 引用 10 处 = **13 处**
- `tests/test_v3_new.py`:测试名字符串 3 处(描述性,不改)
- `gen-ppt.py` / `gen-ppt-images.py` / `qa_image.py`:**零引用**(它们要么自给自足,要么只用 QA/万相)

## 附录 B:风险与回退

| 风险 | 缓解 |
|---|---|
| 改名漏改 → 运行时 `ImportError` | 验收命令 1 + 2 双重检查 |
| 改错调用方 → 视觉走样 | 验收命令 3 重生成 + 对比 diff |
| QA 白名单漏改 → 检查项误报 | 验收命令 4 跑通 |
| `apply_hud_chrome` / `section_label_v1` 被外部脚本隐式依赖 | 已 grep 确认仅在 tools.py 内部定义 |

回退:`git checkout HEAD -- docs/ppt/scripts/tools.py docs/ppt/scripts/gen-ppt-v3-new.py docs/ppt/scripts/qa_ppt_text.py`。
# PPT 配图存放说明

> 用途:存放 `../PPT-OUTLINE.md` 中各页所需的配图、示意图、AI 生成图。
> 命名约定:`page-<页码两位>-<主题>.png`(全部小写、英文 + 数字、连字符分隔)

## 命名示例

| 文件名 | 用途 |
|---|---|
| `page-01-cover.png` | 封面图(科技感大脑 + 数据库 + 终端) |
| `page-02-pain.png` | 痛点页(3 个红色数字 + 剪影) |
| `page-03-position.png` | 定位页(3 个乐高积木 + 锁扣组合) |
| `page-04-loom.png` | 灵梭页(6 大功能卡片配图,或 2×3 网格) |
| `page-05-forge.png` | SQL工坊页(4 个 starter 拼图 + 6 大功能) |
| `page-06-demo1.png` | 录屏 1 缩略图(分析报告 + 柱状图)— **录完视频用 ffmpeg 截帧** |
| `page-07-demo2.png` | 录屏 2 缩略图(CRUD 页面 + 38 条数据)— **录完视频用 ffmpeg 截帧** |
| `page-08-compare.png` | 实战 + 对比页(7 表拼图 + 表格) |
| `page-09-roadmap.png` | 开源 + 路线图(3 个 GitHub 卡片 + 时间线) |
| `page-10-ending.png` | 结尾页(Spring Boot 启动日志) |

## 占位 / 待补流程

1. 在 PPT-OUTLINE.md 的某页"配图建议"段后追加一行:
   ```
   ![配图占位](./images/page-XX-<主题>.png)
   ```
2. 把对应图片放到 `images/page-XX-<主题>.png`
3. PPT 排版时直接引用本目录

## AI 配图工具链(国产优先)

- 即梦(jimeng.jianying.com)— 免费额度多,中文理解好
- 通义万相(tongyi.aliyun.com/wanxiang)— 阿里出品,适合写实风
- 智谱清影 — 备选

## 录屏缩略图(ffmpeg 截帧)

第 6 页、第 7 页**不需要 AI 生成**——录完视频后用 ffmpeg 截帧,这样比 AI 生成的"假截图"更真实、更有说服力。

```bash
# 在 docs/ppt/images/ 目录下执行
# 录屏 1(90 秒):在第 5 秒截帧(AI 推理过程画面,工具调用动画)
ffmpeg -i ../videos/demo1/demo1-final.mp4 -ss 5 -vframes 1 page-06-demo1.png

# 录屏 2(100 秒):在第 60 秒截帧(CRUD 表格 + 38 条数据)
ffmpeg -i ../videos/demo2/demo2-final.mp4 -ss 60 -vframes 1 page-07-demo2.png
```

**时间点参考**:
- demo1 第 5 秒:AI 正在推理,屏幕有工具调用动画
- demo2 第 60 秒:CRUD 表格 + 38 条数据展示完毕,操作按钮齐全

如果截出来画面不好看,调整 `-ss` 参数(往前/往后挪几秒)。

如果没装 ffmpeg:`winget install Gyan.FFmpeg` 或 `choco install ffmpeg`。

视频命名与目录结构详见 [`../videos/README.md`](../videos/README.md)。

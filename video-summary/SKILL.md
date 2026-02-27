---
name: video-summary
description: |
  提取视频字幕和网页文章内容。支持：B站/YouTube 字幕 API、Jina Reader、browser-use 反爬提取、Whisper 语音转录。

  触发场景：
  - 视频转文字：B站、YouTube、抖音等视频链接
  - 文章提取：Twitter/X、微信公众号、技术博客等网页
  - 批量提取：多个视频或文章批量处理（防封锁）
  - 关键词："分析视频"、"提取文章"、"video summary"、"twitter"、"微信公众号"
---

# Video & Article Extractor

提取视频字幕和网页文章，生成结构化的中文总结和全文重写。

## 快速开始

```bash
# 单个视频/文章（自动检测类型）
python3 ~/.claude/skills/video-summary/scripts/extract.py "<URL>"
```

## 提取方法

| 内容类型 | 首选方法 | 备用方法 |
|---------|---------|---------|
| YouTube 字幕 | 字幕 API | browser-use |
| B站 字幕 | 字幕 API | - |
| Twitter/X | Jina Reader | browser-use |
| 微信公众号 | browser-use | - |
| 通用网页 | Jina Reader | browser-use |
| 无字幕视频 | Whisper (异步) | - |

## Claude 工作流程

### 第一步：提取原始内容

```bash
# 视频（可能需要异步转录）
python3 scripts/extract.py "<video_url>"

# 文章（自动检测）
python3 scripts/extract.py "<article_url>"
```

### 第二步：读取输出文件

用 Read 工具读取生成的 Markdown 文件。

### 第三步：补充元数据

根据 [OUTPUT_FORMAT.md](references/OUTPUT_FORMAT.md) 规范填写：
- `title_zh`: 中文标题
- `publish_date`: **⚠️ 发布日期（必须从 API 或页面获取，不要用提取日期）**
- `type`: 预定义类型（tutorial/news/analysis/interview/research/opinion/review/other）
- `tags`: 预定义标签，最多3个

**⚠️ 日期重要说明**：

| 字段 | 说明 |
|------|------|
| `publish_date` | 内容的原始发布时间，**必须从 API 或页面元数据获取** |
| `extracted_date` | 你提取内容的日期，仅用于记录 |

**严禁**：
- ❌ 用 extracted_date 代替 publish_date
- ❌ 文件名中使用提取日期
- ✅ 文件名必须使用 publish_date

### 第四步：生成三档总结

阅读原始内容，生成三个档次的总结：

| 档位 | 读者 | 要求 | 字数 |
|------|------|------|------|
| 入门级 | 小白/外行 | 术语通俗解释，多用类比 | ≤200字 |
| 标准级 | 从业者 | 专业但易懂，突出核心信息 | 300-500字 |
| 深入级 | 专家 | 保留术语，深度分析 | 500-800字 |

### 第五步：生成中文全文

将原始内容完整重写为流畅中文：
- 完整可独立阅读
- 不遗漏信息
- 不改原意，不加评价

### 第六步：写回文件

用 Edit 工具替换占位符：
- `{CLAUDE_BEGINNER_SUMMARY}` → 入门级总结
- `{CLAUDE_STANDARD_SUMMARY}` → 标准级总结
- `{CLAUDE_EXPERT_SUMMARY}` → 深入级总结
- `{CLAUDE_FULLTEXT}` → 中文全文

## 提取脚本

| 脚本 | 用途 |
|------|------|
| `extract.py` | 单个 URL 提取（自动检测） |
| `batch_extractor.py` | YouTube 批量字幕（5-15秒延迟，429检测） |
| `article_batch_extractor.py` | 文章批量（2-5秒延迟，自动降级） |
| `bilibili_subtitle.py` | B站字幕批量提取（需 SESSDATA） |
| `async_transcriber.py` | Whisper 转录状态检查 |
| `quality_scorer.py` | 信息质量评分计算 |

## 参考文档

- **[OUTPUT_FORMAT.md](references/OUTPUT_FORMAT.md)** — 输出结构规范（必读）
- **[METHODS.md](references/METHODS.md)** — 各种提取方法的详细说明
- **[WORKFLOW.md](references/WORKFLOW.md)** — 完整工作流程和中文重写指南
- **[BATCH.md](references/BATCH.md)** — 批量提取最佳实践

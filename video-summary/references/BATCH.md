# 批量提取最佳实践

## 防封锁策略

### YouTube 批量字幕

**脚本：** `scripts/batch_extractor.py`

**防封锁措施：**
- 会话状态持久化（`~/.cache/youtube_extractor/session.json`）
- 429 封锁检测，自动等待 5 分钟
- 每视频间 5-15 秒随机延迟
- 使用已登录浏览器会话（`--browser real`）

```bash
python3 scripts/batch_extractor.py youtube_urls.txt
```

### 文章批量提取

**脚本：** `scripts/article_batch_extractor.py`

**防封锁措施：**
- 会话状态持久化（`~/.cache/article_extractor/session.json`）
- 429/503 速率限制检测
- 每请求 2-5 秒随机延迟
- Jina Reader 失败自动降级到 browser-use

```bash
# 自动选择方法
python3 scripts/article_batch_extractor.py urls.txt

# 指定方法
python3 scripts/article_batch_extractor.py urls.txt jina
python3 scripts/article_batch_extractor.py urls.txt browser
```

### 域名自动检测

| 域名 | 首选方法 |
|------|---------|
| Twitter/X, x.com | Jina Reader |
| 微信公众号 | browser-use |
| YouTube | 字幕 API |
| B站 | 字幕 API |
| 通用网站 | Jina Reader |

## 大规模提取（378+ 篇经验）

### 核心策略：Task 并行 Subagent

使用 Claude Code 的 Task 工具并行启动多个 subagent，每个处理不同序号范围。

```python
# 同时启动 8-10 个代理
Task(
    description="Extract batch 1-20",
    prompt="提取第 1-20 篇文章...",
    subagent_type="general-purpose"
)
```

### 关键成功因素

| 因素 | 策略 |
|------|------|
| 任务分解 | 每批次 20 篇 |
| 并行执行 | 8-10 个 subagent |
| 避免重复 | 每个代理处理不同范围 |
| 统一格式 | 严格的文件命名模板 |

### 文件命名规范

```
格式: 20260218_{Source}_{Title}.md
示例: 20260218_OpenAI_GPT-5-正式发布.md
```

### 提取后检查

```bash
# 检查占位符
grep PLACEHOLDER *.md

# 检查 YAML frontmatter
grep -L "^title:" *.md
```

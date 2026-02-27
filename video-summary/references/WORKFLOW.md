# 完整工作流程

**重要**：输出格式规范详见 [OUTPUT_FORMAT.md](references/OUTPUT_FORMAT.md)

## 职责分工

- **脚本**：提取原始内容
- **Claude（你）**：补充三档总结 + 中文全文重写 + 完善元数据

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

| 字段 | 操作 |
|------|------|
| `title_zh` | 翻译标题为中文，保留专有名词 |
| `type` | 预定义类型（tutorial/news/analysis/interview/research/opinion/review/other） |
| `tags` | 预定义标签选择最多3个 |
| `quality_score` | 由 quality_scorer.py 计算 |

**类型选择指南：**
- `tutorial`: 教程教学类
- `news`: 新闻、资讯类
- `analysis`: 深度分析、报道
- `interview`: 采访、对话
- `research`: 研究、论文
- `opinion`: 观点、评论
- `review`: 评测
- `other`: 其他

### 第四步：生成三档总结

阅读原始内容，生成三个档次的总结：

| 档位 | 目标读者 | 写法要求 | 字数 |
|------|----------|----------|------|
| 入门级 | 小白/外行 | 术语通俗解释，多用类比，避免行话 | ≤200字 |
| 标准级 | 从业者 | 专业但易懂，保留关键术语，突出核心信息 | 300-500字 |
| 深入级 | 专家 | 保留所有术语，深度分析，可引用数据 | 500-800字 |

### 第五步：生成中文全文

将原始内容完整重写为流畅中文：
- 完整可独立阅读
- 不遗漏信息
- 不改原意，不加个人理解或评价

### 第六步：写回文件并重命名

用 Edit 工具替换占位符：
- `{CLAUDE_BEGINNER_SUMMARY}` → 入门级总结
- `{CLAUDE_STANDARD_SUMMARY}` → 标准级总结
- `{CLAUDE_EXPERT_SUMMARY}` → 深入级总结
- `{CLAUDE_FULLTEXT}` → 中文全文

然后按照文件名规范重命名文件。

## 输出路径

| 类型 | 路径 |
|------|------|
| 视频 | `~/Documents/video-transcribe/{日期}/` |
| 文章 | `~/Documents/articles/{日期}/` |

## 快速参考

### 文件名格式

```
{作者}_{中文标题}_【{类型}】{平台}-{日期}.md
```

### 占位符替换

```markdown
# 入门级总结
{CLAUDE_BEGINNER_SUMMARY}

# 标准级总结
{CLAUDE_STANDARD_SUMMARY}

# 深入级总结
{CLAUDE_EXPERT_SUMMARY}

# 中文全文
{CLAUDE_FULLTEXT}
```

### 预定义类型

`tutorial` | `news` | `analysis` | `interview` | `research` | `opinion` | `review` | `other`

### 预定义标签

`AI/机器学习` | `编程/开发` | `产品/设计` | `商业/创业` | `金融/投资` | `科技/数码` | `生活/健康` | `心理/成长` | `时事/新闻` | `其他`

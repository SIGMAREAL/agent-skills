# Agent Skills

[English](#english) | [中文](#中文)

---

<a id="english"></a>

## English

A collection of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) agent skills for software development workflows. Install via the [Skills CLI](https://skills.sh/).

### Skills

#### task-planner

Task planning and decomposition for auto-coding workflows. Transforms user requirements into structured development tasks with architecture docs, task lists, and automated execution.

**Install:**

```bash
npx skills add SIGMAREAL/agent-skills@task-planner
```

**Features:**

- Auto-detects project tech stack (framework, database, styling, package manager)
- Generates session-based planning files (`architecture.md`, `task.json`, `progress.md`)
- Built-in task templates for common patterns (CRUD, Auth, API, UI Component)
- Automated task execution via Claude CLI (`run-automation.sh`)
- OpenSpec integration for spec-driven development
- Testing requirements baked into every task

**Usage:**

In Claude Code, just describe what you want to build:

```
> Plan a feature for user authentication with OAuth
> Break down this project into tasks
> Create task list for the payment module
```

Or initialize manually:

```bash
python ~/.claude/skills/task-planner/scripts/init_session.py \
  /path/to/your-project \
  feature-name
```

**Workflow:**

```
Describe requirements → Auto-detect project → Generate architecture
→ Create task list → Review & adjust → Automated execution
```

**Quick reference:**

| Command | Description |
|---------|-------------|
| `init_session.py <project> <feature>` | Initialize a new planning session |
| `detect_project.py <project> --pretty` | Preview auto-detected project config |
| `detect_project.py <project> --save` | Save config to `project-config.json` |
| `setup_openspec.py <project>` | Initialize OpenSpec directory structure |
| `./auto-coding/run.sh` | Run automated task execution |

**Session structure:**

```
your-project/
└── auto-coding/
    ├── run.sh                          # Automation launcher
    ├── project-config.json             # Project config (optional)
    └── sessions/
        └── 2026-02-27-feature-name/
            ├── PRD.md                  # Product requirements
            ├── architecture.md         # System architecture
            ├── task.json               # Task list (machine-readable)
            ├── progress.md             # Progress log
            └── logs/
                └── automation.log
```

**Task templates:**

| Template | Use case |
|----------|----------|
| `crud.json` | CRUD operations, admin pages, list/detail views |
| `auth.json` | Login, registration, authentication, permissions |
| `api.json` | API endpoints, backend services |
| `ui-component.json` | Components, pages, forms, UI interactions |

For detailed documentation, see the [usage guide](task-planner/references/usage-guide.md) and [config schema](task-planner/references/project-config-schema.md).

---

#### syxma-ui

A collection of custom UI design styles. Each style is a complete design system with colors, typography, spacing, components, and implementation patterns.

**Install:**

```bash
npx skills add SIGMAREAL/agent-skills@syxma-ui
```

**Available styles:**

| Style | Description |
|-------|-------------|
| **SYXMA-minimal** | Notion-style layout, iOS system colors, Chinese-optimized. Content-first design with pill buttons, border cards, and floating capsule toggles. |
| **SYXMA-minimal-edumindai** | Education-focused variant. Green brand color (#00C06B), Inter + PingFang SC fonts. Adds gradient panels, dark panels, difficulty tags, skeleton loading, and toast notifications. |

**Usage:**

In Claude Code, reference the style when building UI:

```
> Build a dashboard using SYXMA-minimal style
> Create a landing page with SYXMA-minimal-edumindai design system
```

For detailed design specs, see the reference docs in [`syxma-ui/references/`](syxma-ui/references/).

---

#### video-summary

Extracts subtitles from videos and content from web articles, generating structured Chinese summaries and full rewrites.

**Install:**

```bash
npx skills add SIGMAREAL/agent-skills@video-summary
```

**Features:**

- Bilibili & YouTube subtitle extraction via official APIs
- Article extraction via Jina Reader (Twitter/X, WeChat, tech blogs)
- Whisper-based audio transcription for videos without subtitles
- Anti-blocking batch processing with configurable delays
- Structured output: summary, key points, full rewrite

**Supported sources:**

| Source | Method |
|--------|--------|
| YouTube | Subtitle API → browser-use fallback |
| Bilibili | Subtitle API |
| Twitter / X | Jina Reader → browser-use fallback |
| WeChat articles | Jina Reader → browser-use fallback |
| Tech blogs | Jina Reader |
| Any video (no subtitles) | Whisper transcription |

**Usage:**

In Claude Code, just paste a URL:

```
> 分析这个视频：https://www.bilibili.com/video/BV1xx...
> 提取这篇文章：https://twitter.com/...
> 批量处理这些链接：[url1, url2, url3]
```

Or use the script directly:

```bash
python3 ~/.claude/skills/video-summary/scripts/extract.py "<URL>"
```

---

### Installation

All skills are installed via the [Skills CLI](https://skills.sh/):

```bash
# Install a specific skill
npx skills add SIGMAREAL/agent-skills@task-planner
npx skills add SIGMAREAL/agent-skills@syxma-ui
npx skills add SIGMAREAL/agent-skills@video-summary

# Check for updates
npx skills check

# Update all installed skills
npx skills update
```

---

<a id="中文"></a>

## 中文

一套用于软件开发工作流的 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) Agent Skills 集合。通过 [Skills CLI](https://skills.sh/) 安装。

### Skills 列表

#### task-planner

面向自动编码工作流的任务规划与分解工具。将用户需求转化为结构化的开发任务，包含架构文档、任务列表和自动化执行。

**安装：**

```bash
npx skills add SIGMAREAL/agent-skills@task-planner
```

**功能特性：**

- 自动检测项目技术栈（框架、数据库、样式方案、包管理器）
- 生成基于 session 的规划文件（`architecture.md`、`task.json`、`progress.md`）
- 内置常见开发模式的任务模板（CRUD、认证、API、UI 组件）
- 通过 Claude CLI 自动化执行任务（`run-automation.sh`）
- 支持 OpenSpec 规范驱动开发
- 每个任务内置测试要求

**使用方式：**

在 Claude Code 中直接描述你要构建的功能：

```
> 帮我规划一个用户管理的 CRUD 功能
> 把这个项目拆解成任务列表
> 规划一个带 OAuth 的用户认证功能
```

或手动初始化：

```bash
python ~/.claude/skills/task-planner/scripts/init_session.py \
  /path/to/your-project \
  feature-name
```

**工作流程：**

```
描述需求 → 自动检测项目 → 生成架构文档 → 创建任务列表 → 审查调整 → 自动化执行
```

**命令速查：**

| 命令 | 说明 |
|------|------|
| `init_session.py <项目路径> <功能名>` | 初始化新的规划 session |
| `detect_project.py <项目路径> --pretty` | 预览自动检测的项目配置 |
| `detect_project.py <项目路径> --save` | 保存配置到 `project-config.json` |
| `setup_openspec.py <项目路径>` | 初始化 OpenSpec 目录结构 |
| `./auto-coding/run.sh` | 运行自动化任务执行 |

**Session 目录结构：**

```
your-project/
└── auto-coding/
    ├── run.sh                          # 自动化启动入口
    ├── project-config.json             # 项目配置（可选）
    └── sessions/
        └── 2026-02-27-feature-name/
            ├── PRD.md                  # 产品需求文档
            ├── architecture.md         # 系统架构文档
            ├── task.json               # 任务列表（机器可读）
            ├── progress.md             # 进度日志
            └── logs/
                └── automation.log
```

**任务模板：**

| 模板 | 适用场景 |
|------|----------|
| `crud.json` | 增删改查、管理页面、列表/详情视图 |
| `auth.json` | 登录、注册、认证、权限管理 |
| `api.json` | API 端点、后端服务 |
| `ui-component.json` | 组件、页面、表单、UI 交互 |

详细文档请参考[使用指南](task-planner/references/usage-guide.md)和[配置 Schema](task-planner/references/project-config-schema.md)。

---

#### syxma-ui

自定义 UI 设计风格集合。每种风格都是完整的设计系统，包含色彩、字体、间距、组件和实现规范。

**安装：**

```bash
npx skills add SIGMAREAL/agent-skills@syxma-ui
```

**可用风格：**

| 风格 | 说明 |
|------|------|
| **SYXMA-minimal** | Notion 风格布局，iOS 系统配色，中文阅读优化。内容优先设计，药丸按钮、边框卡片、浮动胶囊切换组。 |
| **SYXMA-minimal-edumindai** | 教育场景变体。绿色品牌色（#00C06B），Inter + PingFang SC 字体。新增渐变面板、深色面板、难度标签、骨架屏加载、Toast 通知。 |

**使用方式：**

在 Claude Code 中引用风格名称来构建 UI：

```
> 用 SYXMA-minimal 风格创建一个仪表盘
> 用 SYXMA-minimal-edumindai 风格创建一个教学管理页面
```

详细设计规范请参考 [`syxma-ui/references/`](syxma-ui/references/) 中的文档。

---

#### video-summary

视频字幕与网页文章内容提取工具，自动生成结构化中文总结和全文改写。

**安装：**

```bash
npx skills add SIGMAREAL/agent-skills@video-summary
```

**功能特性：**

- B站 / YouTube 字幕 API 直接提取
- Jina Reader 抓取文章（Twitter/X、微信公众号、技术博客）
- 无字幕视频支持 Whisper 语音转录
- 批量处理模式，内置防封锁随机延迟
- 结构化输出：摘要、核心要点、全文改写

**支持来源：**

| 来源 | 提取方式 |
|------|---------|
| YouTube | 字幕 API → browser-use 兜底 |
| B站 | 字幕 API |
| Twitter / X | Jina Reader → browser-use 兜底 |
| 微信公众号 | Jina Reader → browser-use 兜底 |
| 技术博客 | Jina Reader |
| 任意视频（无字幕） | Whisper 语音转录 |

**使用方式：**

在 Claude Code 中直接粘贴链接：

```
> 分析这个视频：https://www.bilibili.com/video/BV1xx...
> 提取这篇文章：https://twitter.com/...
> 批量处理这些链接：[url1, url2, url3]
```

或直接调用脚本：

```bash
python3 ~/.claude/skills/video-summary/scripts/extract.py "<URL>"
```

---

### 安装方式

所有 skill 通过 [Skills CLI](https://skills.sh/) 安装：

```bash
# 安装指定 skill
npx skills add SIGMAREAL/agent-skills@task-planner
npx skills add SIGMAREAL/agent-skills@syxma-ui
npx skills add SIGMAREAL/agent-skills@video-summary

# 检查更新
npx skills check

# 更新所有已安装的 skill
npx skills update
```

---

## License

MIT

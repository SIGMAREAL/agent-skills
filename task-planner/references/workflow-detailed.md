# Workflow Details

## Table of Contents

1. [File Organization](#file-organization)
2. [Initialization Script](#initialization-script)
3. [Progress.md Format](#progressmd-format)
4. [File Formats](#file-formats)

## File Organization

### Directory Structure

All auto-coding sessions are organized under `<project-root>/auto-coding/`:

```
auto-coding/
├── run.sh                               # 自动化启动入口（调用 skill 脚本）
├── sessions/
│   ├── 2026-02-25-lectures-v1.5/       # Session 目录
│   │   ├── PRD.md                      # 产品需求文档
│   │   ├── architecture.md             # 技术架构文档
│   │   ├── task.json                   # 任务列表
│   │   ├── progress.md                 # 进度记录
│   │   ├── resources/                  # 原始输入文件（PRD原稿、Figma帧数据）
│   │   └── logs/
│   │       └── automation.log          # 自动化执行日志
│   └── 2026-02-26-smart-prep-v2.1/
│       └── ...
├── project-config.json                  # 项目配置（可选，自动检测生成）
├── templates/                           # 文件模板（可选）
└── scripts/
    └── init_session.py                  # 初始化脚本
```

### Naming Conventions

**Session Directory**: `YYYY-MM-DD-{feature-name}`
- Date ensures uniqueness and chronological sorting
- Use kebab-case for feature name
- Examples: `2026-02-25-lectures-v1.5`, `2026-02-26-auth-system`

**Files**: Fixed names (no version suffixes)
- `PRD.md` - Product Requirements Document
- `architecture.md` - Technical Architecture
- `task.json` - Task List
- `progress.md` - Progress Log (chronological order)
- `logs/automation.log` - Automation Execution Log

## Initialization Script

**Before starting any planning**, initialize the session structure:

```bash
python ~/.claude/skills/task-planner/scripts/init_session.py \
  /path/to/project \
  feature-name
```

The script will:

1. **Auto-detect project configuration** (calls `detect_project.py` internally)
2. Create session directory: `auto-coding/sessions/YYYY-MM-DD-feature-name/`
3. **Generate all files from templates** (calls `generate_files.py` with detected config)
4. Return file paths as JSON for writing content

### Options

- `--generate-config` — Also save detected config to `auto-coding/project-config.json`
- `--init-openspec` — Initialize OpenSpec directory structure and spec templates (only for new projects without OpenSpec)
- If `project-config.json` already exists, it takes priority over auto-detection

### Output Example

```json
{
  "session_dir": "/path/to/project/auto-coding/sessions/2026-02-25-lectures-v1.5",
  "prd": "/path/to/project/auto-coding/sessions/2026-02-25-lectures-v1.5/PRD.md",
  "architecture": "/path/to/project/auto-coding/sessions/2026-02-25-lectures-v1.5/architecture.md",
  "task": "/path/to/project/auto-coding/sessions/2026-02-25-lectures-v1.5/task.json",
  "progress": "/path/to/project/auto-coding/sessions/2026-02-25-lectures-v1.5/progress.md",
  "automation_log": "/path/to/project/auto-coding/sessions/2026-02-25-lectures-v1.5/logs/automation.log"
}
```

## Progress.md Format

Progress entries are in **chronological order** (newest at bottom):

```markdown
# Progress - Lectures v1.5

> **Session**: 2026-02-25-lectures-v1.5
> **Start**: 2026-02-25 17:14
> **Status**: In Progress

---

## 2026-02-25 17:20 - Task: lectures-v1.5-1 ✅

### What was done
- Created color system (styles/colors.ts)
- Created spacing system (styles/spacing.ts)

### Testing
- ✅ TypeScript check passed
- ✅ Build succeeded (83 pages)

### Git Commit
- Commit: `c3648f8`
- Message: `[lectures-v1.5-1] 创建设计系统基础组件 - completed`

---

## 2026-02-25 17:45 - Task: lectures-v1.5-2 ✅

...
```

## File Formats

### architecture.md

```markdown
# [Project Name] - System Architecture

## Project Overview
[Description]

## Technology Stack
(Auto-detected or from project-config.json)
- Framework: [auto-detected]
- Language: [auto-detected]
- Database: [auto-detected]
- Styling: [auto-detected]

## Development Workflow
Following auto-coding-agent-demo:
```
选择任务 → 加载规范 → 实现功能 → 测试验证 → 更新进度 → 提交变更
```

## OpenSpec References
(Auto-detected from openspec/specs/ if available)
```

### task.json

```json
{
  "project": "Project Name - Feature Name",
  "description": "...",
  "version": "1.0.0",
  "session": "2026-02-25-feature-name",
  "meta": {
    "createdAt": "2026-02-25 17:14",
    "lastUpdated": "2026-02-25 17:14",
    "totalTasks": 5,
    "completedTasks": 0,
    "pendingTasks": 5
  },
  "tasks": [...]
}
```

**Key fields**:

- `session`: Session directory name for traceability
- `meta.createdAt`: Timestamp when session was created
- `meta.lastUpdated`: Auto-updated by automation script

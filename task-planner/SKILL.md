---
name: task-planner
description: Task planning and decomposition for auto-coding workflows. Use when users want to plan a software development project by breaking down requirements into structured tasks, generating architecture.md and task.json files that follow auto-coding-agent-demo + OpenSpec conventions. Triggers include "plan this project", "create task list", "generate architecture", "break down requirements", or when starting a new development project that will use automated task execution.
---

# Task Planner

Task planning skill for auto-coding workflows. Transforms user requirements into structured development tasks following auto-coding-agent-demo + OpenSpec conventions.

## Overview

This skill helps plan software development projects by:
1. Analyzing user requirements
2. **Auto-detecting project configuration** (tech stack, testing commands, OpenSpec)
3. **Initializing session directory structure**
4. Generating system architecture (`architecture.md`)
5. Creating structured task lists (`task.json`)
6. Following auto-coding-agent-demo best practices

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

### Initialization Script

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

**Options**:
- `--generate-config` — Also save detected config to `auto-coding/project-config.json`
- `--init-openspec` — Initialize OpenSpec directory structure and spec templates (only for new projects without OpenSpec)
- If `project-config.json` already exists, it takes priority over auto-detection

**Output Example**:

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

### Progress.md Format

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

## Workflow

### Step 1: Understand Requirements

Ask clarifying questions to understand:

- What system/feature needs to be built?
- What are the core functionalities?
- Any specific technology preferences?
- Any UI/UX requirements?

### Step 2: Initialize Session

**IMPORTANT**: Before writing any files, initialize the session structure:

```bash
python ~/.claude/skills/task-planner/scripts/init_session.py \
  <project-root> \
  <feature-name>
```

This:

1. Auto-detects project config (or loads from `project-config.json`)
2. Creates session directory: `auto-coding/sessions/YYYY-MM-DD-feature-name/`
3. Generates all files with project-specific variables (tech stack, test commands, etc.)
4. Returns file paths as JSON for subsequent writes

### Step 3: Generate Architecture

Write to `architecture.md` with:

- Project overview
- Technology stack
- Data models
- API endpoints
- Component structure
- OpenSpec references

### Step 4: Create Task List

Generate `task.json` with:

- Sequential tasks (3-7 steps each)
- Priority levels (critical/high/medium/low)
- Related OpenSpec specs
- Tags for categorization

### Step 5: User Review

Present the plan to user for:

- Confirming task scope
- Adjusting priorities
- Adding/removing tasks
- Validating approach

### Step 6: Write to Session Files

After confirmation, write content to the session directory:

- `PRD.md` - Product requirements (if applicable)
- `architecture.md` - System design document
- `task.json` - Machine-readable task list
- `progress.md` - Initial progress entry

## Task Structure

Each task must follow this format:

```json
{
  "id": "unique-task-id",
  "title": "Clear task title",
  "description": "What this task accomplishes",
  "steps": [
    "Specific step 1",
    "Specific step 2",
    "Specific step 3"
  ],
  "passes": false,
  "priority": "high",
  "tags": ["ui", "api", "database"],
  "relatedSpecs": ["openspec/specs/..."]
}
```

## Granularity Guidelines

**Task Size:**
- 3-7 steps per task
- 30-90 minutes estimated completion
- 1-3 files modified
- Single feature or component

**Task Ordering:**
1. Infrastructure/Config first
2. Data models second
3. APIs third
4. UI components fourth
5. Integration/Polish last

## Project Configuration

The skill uses a config-driven approach to adapt to any project. Configuration is loaded with the following priority:

**Priority**: `project-config.json` > auto-detection (`detect_project.py`) > default config

### Config File

Optional. Located at `<project-root>/auto-coding/project-config.json`. See [project-config-schema.md](references/project-config-schema.md) for full schema.

### Auto-Detection

If no config file exists, `detect_project.py` auto-detects:
- Package manager (pnpm/yarn/npm)
- Framework (Next.js, React, Vue, Angular, etc.)
- Database/ORM (Prisma, Drizzle, TypeORM, etc.)
- Styling (Tailwind, styled-components, etc.)
- OpenSpec domains (scans `openspec/specs/` directory)
- Testing commands (from `package.json` scripts)

### Generating a Config

```bash
python ~/.claude/skills/task-planner/scripts/detect_project.py /path/to/project --save
```

This creates `auto-coding/project-config.json` with auto-detected values you can customize.

## OpenSpec Integration

OpenSpec integration is **auto-detected** from the project. When `openspec/specs/` exists, all domains are discovered automatically and linked to tasks.

**How it works**:
1. `detect_project.py` scans `openspec/specs/*/spec.md` and builds a domain map
2. The domain map is stored in `project-config.json` under `openspec.domains`
3. When planning tasks, match task types to domain names

**Example auto-detected domains**:
```json
{
  "openspec": {
    "enabled": true,
    "domains": {
      "lectures-v3": "openspec/specs/lectures-v3/spec.md",
      "components-v3": "openspec/specs/components-v3/spec.md",
      "architecture": "openspec/specs/architecture/sse-patterns.md"
    }
  }
}
```

**Linking specs to tasks**: Match task keywords to domain names (e.g., "UI component" → `components-v3`, "API endpoint" → `architecture`).

## OpenSpec Setup

For projects that want to adopt OpenSpec but don't have it yet, use `--init-openspec` during session initialization:

```bash
python ~/.claude/skills/task-planner/scripts/init_session.py \
  /path/to/project \
  feature-name \
  --init-openspec
```

Or use the standalone script directly:

```bash
python ~/.claude/skills/task-planner/scripts/setup_openspec.py /path/to/project
```

**What it does**:

1. Checks if OpenSpec already exists (skips if it does, to avoid overwriting)
2. Creates directory structure: `openspec/specs/`, `openspec/changes/archive/`, `docs/guides/`
3. Generates spec templates based on detected project type:
   - Full-stack frameworks (Next.js, Nuxt, etc.) → `architecture`, `api`, `components` specs
   - Backend frameworks (Express, Fastify) → `architecture`, `api` specs
   - Frontend frameworks (React, Vue, etc.) → `architecture`, `components` specs
   - Projects with database/ORM → adds `data-model` spec
4. Generates `openspec/README.md` with usage instructions

**Generated structure**:

```
openspec/
├── README.md
├── specs/
│   ├── architecture/
│   │   └── spec.md
│   ├── api/              # if applicable
│   │   └── spec.md
│   ├── components/       # if applicable
│   │   └── spec.md
│   └── data-model/       # if database detected
│       └── spec.md
└── changes/
    └── archive/
```

**Important**: This only runs when explicitly requested (`--init-openspec` or direct script call). It never overwrites existing spec files.

## Testing Requirements in Tasks

**IMPORTANT**: Every task must include testing steps as the final steps. See [testing-requirements.md](references/testing-requirements.md) for complete guide:

- Mandatory testing steps for all tasks
- UI task testing with dev-browser
- API and Database task testing
- Testing step templates by task type

**Quick reference**:

- **All tasks**: End with "运行 TypeScript 检查、ESLint、Build 测试" + "更新 progress.md"
- **UI (new pages)**: Add "使用 dev-browser 测试页面" before updating progress.md
- **API**: Add "测试 API 端点（正常流程 + 错误处理）" before basic tests
- **Database**: Add "运行数据库命令（如 prisma generate）" before basic tests

## Templates

Task templates are pre-defined JSON files in `templates/` that provide standardized task structures for common development patterns.

### Available Templates

| Template | File | Use When |
|----------|------|----------|
| CRUD | `templates/crud.json` | 增删改查、管理页面、列表/详情 |
| Auth | `templates/auth.json` | 登录、注册、认证、权限 |
| API | `templates/api.json` | API 端点、接口、后端服务 |
| UI Component | `templates/ui-component.json` | 组件、页面、表单、UI |

### Template Usage

1. Match user requirement keywords to a template (see `keywords` field in each template)
2. Load the template JSON
3. Replace variable placeholders (`{{feature_name}}`, `{{resource}}`, etc.) with actual values
4. Adjust tasks as needed (add/remove steps, update priorities)
5. Set `relatedSpecs` based on project's OpenSpec domains
6. Write tasks to `task.json`

### Variable Replacement

Templates use `{{variable}}` placeholders consistent with `generate_files.py`:

- **Project variables** (auto-filled from config): `{{lint_command}}`, `{{build_command}}`, `{{type_check_command}}`
- **Template variables** (set per usage): `{{feature_name}}`, `{{resource}}`, `{{component_name}}`, `{{route_path}}`

### Custom Templates

Projects can define custom templates in `auto-coding/templates/` and register them in `project-config.json`:

```json
{
  "templates": {
    "enabled": true,
    "customTemplates": ["auto-coding/templates/my-template.json"]
  }
}
```

## Auto-Coding Workflow

After generating files, guide user to:

1. **Review** - Check architecture.md and task.json
2. **Adjust** - Modify priorities or add tasks
3. **Execute** - Run automation (see below)

### Automation Script

The automation script is managed centrally in the skill directory. Projects only need a thin launcher:

**Skill script** (full logic): `~/.claude/skills/task-planner/scripts/run-automation.sh`

**Project launcher** (thin wrapper): `auto-coding/run.sh`

```bash
# From project root - using the launcher
./auto-coding/run.sh                                              # Auto-detect latest session
./auto-coding/run.sh auto-coding/sessions/2026-02-26-feature      # Specific session
./auto-coding/run.sh auto-coding/sessions/2026-02-26-feature 5    # Run 5 tasks

# Direct skill script invocation
~/.claude/skills/task-planner/scripts/run-automation.sh /path/to/project
```

**Environment variables**:
- `CLAUDE_CMD` - Claude CLI command (default: `claude`)
- `SKIP_INIT` - Skip init.sh/setup.sh (default: `false`)
- `CLEANUP_BROWSER` - Clean up browser processes after each task (default: `true`)

**Features**:
- Auto-detects latest session if no path provided
- Loads project name from `auto-coding/project-config.json` (if exists)
- Detects init script (`init.sh` or `setup.sh`) automatically
- Cleans up dev-browser/Playwright processes after each task
- Detailed logging to `logs/automation-YYYYMMDD_HHMMSS.log`
- Counts remaining tasks and reports progress

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
\`\`\`
选择任务 → 加载规范 → 实现功能 → 测试验证 → 更新进度 → 提交变更
\`\`\`

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

## Resources

### scripts/

- `init_session.py` - Session directory initializer
- `detect_project.py` - Auto-detect project tech stack and generate config
- `generate_files.py` - Template-based file generator with variable substitution
- `setup_openspec.py` - Initialize OpenSpec directory structure and spec templates
- `run-automation.sh` - Full automation loop (Claude CLI task execution)

### templates/

- `crud.json` - CRUD 功能模板（数据模型 + API + 列表/详情 UI）
- `auth.json` - 认证系统模板（登录/注册 + 会话管理 + 权限）
- `api.json` - API 端点模板（路由 + 验证 + 业务逻辑）
- `ui-component.json` - UI 组件模板（组件 + 页面集成 + 交互优化）

### references/

- `usage-guide.md` - Complete guide for using task-planner in new projects (with FAQ)
- `project-config-schema.md` - Full configuration schema with examples
- `testing-requirements.md` - Detailed testing requirements for all task types
- `auto-coding-patterns.md` - Best practices from auto-coding-agent-demo

## Example Usage

**User:** "Plan a feature for user profile management with settings and avatar upload"

**Process:**

1. Understand requirements through Q&A
2. **Initialize session**:

   ```bash
   python ~/.claude/skills/task-planner/scripts/init_session.py \
     /Users/name/my-project \
     user-profile-v1
   ```

   Returns file paths: `auto-coding/sessions/2026-02-25-user-profile-v1/{PRD.md, architecture.md, task.json, progress.md}`

3. Generate architecture.md with:
   - Tech stack (auto-detected from project)
   - Components: ProfilePage, AvatarUploader, SettingsForm
   - OpenSpec refs (if project uses OpenSpec)

4. Generate task.json with 4-5 tasks
5. Present for user review
6. **Write to session files** (not project root)

## Best Practices

1. **Start with templates** - Match requirement to known patterns
2. **Keep tasks small** - 30-90 min, 1-3 files
3. **Order matters** - Config → Models → APIs → UI
4. **Link specs** - Always add relatedSpecs for context
5. **User confirms** - Never write files without approval

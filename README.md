# Agent Skills

A collection of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) agent skills for software development workflows. Install via the [Skills CLI](https://skills.sh/).

## Skills

### task-planner

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
> 帮我规划一个用户管理的 CRUD 功能
> Break down this project into tasks
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

### syxma-ui

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
> 用 SYXMA-minimal-edumindai 风格创建一个教学管理页面
```

For detailed design specs, see the reference docs in [`syxma-ui/references/`](syxma-ui/references/).

---

## Installation

All skills are installed via the [Skills CLI](https://skills.sh/):

```bash
# Install a specific skill
npx skills add SIGMAREAL/agent-skills@task-planner
npx skills add SIGMAREAL/agent-skills@syxma-ui

# Check for updates
npx skills check

# Update all installed skills
npx skills update
```

## License

MIT

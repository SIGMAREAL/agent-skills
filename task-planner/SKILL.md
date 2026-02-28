---
name: task-planner
description: Task planning and decomposition for auto-coding workflows. Use when users want to plan a software development project by breaking down requirements into structured tasks, generating architecture.md and task.json files that follow auto-coding-agent-demo + OpenSpec conventions. Triggers include "plan this project", "create task list", "generate architecture", "break down requirements", or when starting a new development project that will use automated task execution. Also use when users have Figma wireframes + PRD documents and want each Figma frame implemented as a page task using Figma MCP node structure as layout reference.
---

# Task Planner

Task planning skill for auto-coding workflows. Transforms user requirements into structured development tasks following auto-coding-agent-demo + OpenSpec conventions.

## Overview

This skill helps plan software development projects by:
1. Analyzing user requirements
2. Auto-detecting project configuration (tech stack, testing commands, OpenSpec)
3. Initializing session directory structure
4. Generating system architecture (`architecture.md`)
5. Creating structured task lists (`task.json`)
6. Following auto-coding-agent-demo best practices

See [references/workflow-detailed.md](references/workflow-detailed.md) for complete file organization and formats.

## Workflow

### Step 1: Understand Requirements

Ask clarifying questions to understand:
- What system/feature needs to be built?
- What are the core functionalities?
- Any specific technology preferences?
- Any UI/UX requirements?

### Step 1.5: Preserve Original Input

**MANDATORY**: Copy user's original requirements (verbatim) to `resources/init.md`. This ensures traceability and prevents information loss during planning.

### Step 2: Initialize Session

**IMPORTANT**: Before writing any files, initialize the session structure:

```bash
python ~/.claude/skills/task-planner/scripts/init_session.py \
  <project-root> \
  <feature-name>
```

This auto-detects project config, creates session directory, and generates all skeleton files. Returns file paths as JSON.

Options: `--generate-config`, `--init-openspec`

> ⚠️ Script generates skeleton templates only. Steps 3–6 fill in actual content.

### Step 3: Generate Architecture

Write to `architecture.md` with: project overview, technology stack, data models, API endpoints, component structure, OpenSpec references.

### Step 4: Create Task List

Generate `task.json` with: sequential tasks (3-7 steps each), priority levels, related OpenSpec specs, tags for categorization.

See [Task Structure](#task-structure) below.

### Step 5: User Review

Present the plan to user for: confirming task scope, adjusting priorities, adding/removing tasks, validating approach.

### Step 6: Write to Session Files

**MANDATORY**: Write actual content to ALL session files. Never leave skeleton templates empty.

Verify before finishing:
- [ ] `PRD.md` — sections 1.1-1.3, 2, 3 have real content
- [ ] `architecture.md` — sections 1, 3-5 have real content
- [ ] `task.json` — `tasks[]` has ≥1 task, `description` is not empty
- [ ] `progress.md` — initial entry written

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
    "Testing step (mandatory - see below)"
  ],
  "passes": false,
  "priority": "high",
  "tags": ["ui", "api", "database"],
  "relatedSpecs": ["openspec/specs/..."]
}
```

**Task Size**: 3-7 steps, 30-90 min, 1-3 files, single feature/component

**Task Ordering**: Infrastructure → Data models → APIs → UI → Integration

**Testing Requirements**: Every task MUST include testing steps. See [references/testing-requirements.md](references/testing-requirements.md) for:
- Mandatory testing steps for all tasks
- UI task testing with dev-browser
- API and Database task testing
- Testing step templates by task type

**Quick reference**: All tasks end with "TypeScript + ESLint + Build" + "Update progress.md". UI tasks add "dev-browser test" before that.

**UI Layout Tasks**: Before writing steps for any page layout change, read `layout.tsx` and `page.tsx` first. See [references/ui-layout-checklist.md](references/ui-layout-checklist.md).

## Automation Scripts

After planning, guide user to execute tasks:

**Command Quick Reference**:

```bash
# Serial execution (one task at a time)
./auto-coding/run.sh [session-dir] [max-tasks]

# Parallel execution (phase-based, memory-aware)
./auto-coding/run-parallel.sh [session-dir] [max-concurrency]

# Skill optimizer (session retrospective)
./auto-coding/optimize-skill.sh [session-dir]

# Multi-branch parallel (git worktrees)
./auto-coding/run-branches.sh session1:branch1 [session2:branch2 ...]

# Review loop (PM agent + auto-planning)
./auto-coding/run-review-loop.sh [--auto] [--cycles N]
```

See [references/automation-runners.md](references/automation-runners.md) for complete usage, environment variables, memory strategies, and scenario comparisons.

## Project Configuration

**Priority**: `project-config.json` > auto-detection > default config

Config file is optional at `<project-root>/auto-coding/project-config.json`. If not present, `detect_project.py` auto-detects package manager, framework, database/ORM, styling, OpenSpec domains, and testing commands.

Generate config:
```bash
python ~/.claude/skills/task-planner/scripts/detect_project.py /path/to/project --save
```

See [references/project-config-schema.md](references/project-config-schema.md) for full schema.

## OpenSpec Integration

Auto-detected from `openspec/specs/` directory. Domains are discovered and linked to tasks automatically.

For new projects adopting OpenSpec:
```bash
python ~/.claude/skills/task-planner/scripts/init_session.py \
  /path/to/project feature-name --init-openspec
```

Creates directory structure and spec templates based on detected project type.

## Templates

Task templates provide standardized structures for common patterns. See [references/templates-guide.md](references/templates-guide.md) for:
- Available templates (CRUD, Auth, API, UI Component)
- Template usage workflow
- Variable replacement
- Custom template configuration

## Resources

### scripts/

- `init_session.py` - Session directory initializer
- `detect_project.py` - Auto-detect project tech stack and generate config
- `generate_files.py` - Template-based file generator with variable substitution
- `setup_openspec.py` - Initialize OpenSpec directory structure and spec templates
- `run-automation.sh` - Serial automation loop
- `run-parallel.sh` - Parallel automation runner with memory-aware concurrency
- `skill-optimizer.sh` - *(tp-3)* Session retrospective and skill improvement generator
- `run-branch-parallel.sh` - *(tp-4)* Multi-branch parallel development with git worktrees
- `run-review-loop.sh` - *(tp-5)* PM agent + auto-planning + review loop

### templates/

- `crud.json` - CRUD 功能模板
- `auth.json` - 认证系统模板
- `api.json` - API 端点模板
- `ui-component.json` - UI 组件模板

### references/

- `usage-guide.md` - Complete guide for using task-planner in new projects (with FAQ)
- `project-config-schema.md` - Full configuration schema with examples
- `testing-requirements.md` - Detailed testing requirements for all task types
- `auto-coding-patterns.md` - Best practices from auto-coding-agent-demo
- `figma-resources-workflow.md` - Figma REST API + resources/ 文件夹工作流
- `automation-runners.md` - *(tp-1)* Detailed automation script usage and environment variables
- `workflow-detailed.md` - *(tp-1)* File organization, naming conventions, and formats
- `templates-guide.md` - *(tp-1)* Template system usage and custom templates

## Best Practices

1. **Start with templates** - Match requirement to known patterns
2. **Keep tasks small** - 30-90 min, 1-3 files
3. **Order matters** - Config → Models → APIs → UI
4. **Link specs** - Always add relatedSpecs for context
5. **User confirms** - Never write files without approval

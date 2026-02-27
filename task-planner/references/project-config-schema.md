# Project Configuration Schema

> 项目配置文件 `auto-coding/project-config.json` 的完整字段说明和使用指南。

## Overview

配置文件是**可选的**。task-planner 采用自动化优先设计：

1. **自动检测** (`detect_project.py`) 会分析项目结构并自动推导配置
2. **手动配置** 只在自动检测不准确或需要自定义时使用
3. **默认配置** 作为最终兜底

**配置优先级**: `project-config.json` > 自动检测 > 默认配置

> **建议流程**: 先运行 `--generate-config` 自动生成配置，再手动微调不准确的部分。

## Config File Location

```
<project-root>/auto-coding/project-config.json
```

配置文件不会被自动创建。需要手动或通过以下命令生成：

```bash
# 方式 1: 使用 detect_project.py 直接保存
python ~/.claude/skills/task-planner/scripts/detect_project.py /path/to/project --save

# 方式 2: 初始化 session 时附带生成配置
python ~/.claude/skills/task-planner/scripts/init_session.py /path/to/project feature-name --generate-config
```

两种方式都会在 `auto-coding/project-config.json` 创建基于自动检测结果的配置文件。

## Schema

### Top-Level Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `projectName` | string | No | `"My Project"` | 项目显示名称，用于生成文件的标题和 task.json 的 project 字段 |
| `techStack` | object | No | See below | 技术栈配置 |
| `testing` | object | No | See below | 测试命令配置 |
| `openspec` | object | No | See below | OpenSpec 集成配置 |
| `templates` | object | No | See below | 模板系统配置 |

### techStack

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `framework` | string | `""` | 主框架，含版本号。例：`"Next.js 16"`, `"React 19"`, `"Vue 3"`, `"Nuxt 3"`, `"Angular 17"` |
| `language` | string | `"TypeScript"` | 编程语言。支持 `"TypeScript"`, `"JavaScript"`, `"Flow"` |
| `database` | string | `""` | 数据库和 ORM。格式：`"数据库 (ORM)"`。例：`"PostgreSQL (Prisma)"`, `"MongoDB (Mongoose)"`, `"Supabase"` |
| `styling` | string | `""` | CSS 方案。例：`"Tailwind CSS"`, `"styled-components"`, `"CSS Modules"`, `"Sass"` |
| `packageManager` | string | `"npm"` | 包管理器。支持 `"npm"`, `"pnpm"`, `"yarn"`, `"bun"` |

**自动检测说明**：
- `framework`: 从 `package.json` 的 dependencies 检测，优先检测元框架（Next.js, Nuxt）再检测基础框架（React, Vue）
- `database`: 从 ORM 依赖检测。若使用 Prisma，会进一步解析 `schema.prisma` 中的 `datasource` 块获取精确的数据库类型
- `packageManager`: 根据 lock 文件检测，优先级 pnpm > yarn > bun > npm

### testing

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `typeCheck` | string | `"npx tsc --noEmit"` | TypeScript 类型检查命令 |
| `lint` | string | `"npm run lint"` | Lint 检查命令 |
| `build` | string | `"npm run build"` | 构建命令 |
| `uiTesting` | string | `"dev-browser"` | UI 测试工具（目前仅支持 dev-browser） |
| `databaseCommands` | string[] | `[]` | 数据库相关命令列表。例：`["prisma generate"]`, `["drizzle-kit push"]` |

**自动检测说明**：
- `lint` 和 `build`: 根据 `package.json` 中是否存在对应 scripts 和检测到的包管理器自动组合（如检测到 pnpm + 有 lint script → `"pnpm lint"`）
- `typeCheck`: 若为 TypeScript 项目则自动设置为 `"npx tsc --noEmit"`；Vue 项目会使用 `"vue-tsc --noEmit"`
- `databaseCommands`: 根据检测到的 ORM 自动添加（如 Prisma → `["prisma generate"]`）

### openspec

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `false` | 是否启用 OpenSpec 集成 |
| `domains` | object | `{}` | 域名到 spec 文件路径的映射 |

**domains 格式**:

Key 为域名（通常是 `openspec/specs/` 下的目录名），Value 为 spec 文件的相对路径。

```json
{
  "openspec": {
    "enabled": true,
    "domains": {
      "lectures-v3": "openspec/specs/lectures-v3/spec.md",
      "components-v3": "openspec/specs/components-v3/spec.md",
      "prompts": "openspec/specs/prompts/spec.md"
    }
  }
}
```

**自动检测说明**：当项目中存在 `openspec/specs/` 目录时，`detect_project.py` 会自动扫描所有子目录并查找 `spec.md` 文件。

### templates

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `true` | 是否启用模板系统 |
| `customTemplates` | string[] | `[]` | 自定义模板文件路径（相对于项目根目录） |

**自定义模板**：项目可以在 `auto-coding/templates/` 下创建自己的模板 JSON 文件，然后在此处注册。模板格式参见 `templates/README.md`。

## Template Variables

配置值会被自动转换为模板变量，用于生成 session 文件。变量使用 `{{variable}}` 格式。

### Project Variables（来源于配置）

| Variable | Source | Example |
|----------|--------|---------|
| `{{projectName}}` | `projectName` | `"EduMind AI"` |
| `{{framework}}` | `techStack.framework` | `"Next.js 16"` |
| `{{language}}` | `techStack.language` | `"TypeScript"` |
| `{{database}}` | `techStack.database` | `"PostgreSQL (Prisma)"` |
| `{{styling}}` | `techStack.styling` | `"Tailwind CSS"` |
| `{{packageManager}}` | `techStack.packageManager` | `"pnpm"` |
| `{{tech_stack_display}}` | Computed | `"Next.js 16 + TypeScript + PostgreSQL (Prisma)"` |
| `{{lint_command}}` | `testing.lint` | `"pnpm lint"` |
| `{{build_command}}` | `testing.build` | `"pnpm build"` |
| `{{type_check_command}}` | `testing.typeCheck` | `"npx tsc --noEmit"` |
| `{{ui_testing_tool}}` | `testing.uiTesting` | `"dev-browser"` |
| `{{database_commands}}` | `testing.databaseCommands` | `"prisma generate"` |
| `{{openspec_domains_table}}` | `openspec.domains` | Markdown table |

### Auto Variables（自动计算）

| Variable | Description | Example |
|----------|-------------|---------|
| `{{date}}` | 当前日期 | `"2026-02-26"` |
| `{{timestamp}}` | 当前时间戳 | `"2026-02-26 18:30"` |
| `{{feature_name}}` | CLI 传入的功能名称 | `"user-profile-v1"` |
| `{{session_name}}` | Session 目录名 | `"2026-02-26-user-profile-v1"` |

## Complete Examples

### Example 1: Next.js + Prisma + OpenSpec (Full Config)

```json
{
  "projectName": "EduMind AI",
  "techStack": {
    "framework": "Next.js 16",
    "language": "TypeScript",
    "database": "PostgreSQL (Prisma)",
    "styling": "Tailwind CSS",
    "packageManager": "pnpm"
  },
  "testing": {
    "typeCheck": "npx tsc --noEmit",
    "lint": "pnpm lint",
    "build": "pnpm build",
    "uiTesting": "dev-browser",
    "databaseCommands": ["prisma generate"]
  },
  "openspec": {
    "enabled": true,
    "domains": {
      "lectures-v3": "openspec/specs/lectures-v3/spec.md",
      "components-v3": "openspec/specs/components-v3/spec.md",
      "prompts": "openspec/specs/prompts/spec.md",
      "architecture": "openspec/specs/architecture/sse-patterns.md",
      "data-model": "openspec/specs/data-model/spec.md"
    }
  },
  "templates": {
    "enabled": true,
    "customTemplates": []
  }
}
```

### Example 2: Simple React App (Minimal Config)

```json
{
  "projectName": "My React App",
  "techStack": {
    "framework": "React 19",
    "language": "TypeScript",
    "database": "",
    "styling": "CSS Modules",
    "packageManager": "npm"
  },
  "testing": {
    "typeCheck": "npx tsc --noEmit",
    "lint": "npm run lint",
    "build": "npm run build",
    "uiTesting": "dev-browser",
    "databaseCommands": []
  },
  "openspec": {
    "enabled": false,
    "domains": {}
  }
}
```

### Example 3: Vue + Supabase (Partial Config)

只需要覆盖与默认值不同的字段：

```json
{
  "projectName": "My Vue App",
  "techStack": {
    "framework": "Vue 3",
    "database": "Supabase",
    "styling": "Tailwind CSS",
    "packageManager": "yarn"
  },
  "testing": {
    "typeCheck": "vue-tsc --noEmit",
    "lint": "yarn lint",
    "build": "yarn build",
    "databaseCommands": ["supabase db push"]
  }
}
```

> **提示**: 部分配置会与默认配置合并。未指定的字段使用默认值（如 `language` 默认为 `"TypeScript"`）。

### Example 4: Express API Backend (No UI)

```json
{
  "projectName": "Order Service",
  "techStack": {
    "framework": "Express",
    "language": "TypeScript",
    "database": "MySQL (TypeORM)",
    "styling": "",
    "packageManager": "npm"
  },
  "testing": {
    "typeCheck": "npx tsc --noEmit",
    "lint": "npm run lint",
    "build": "npm run build",
    "uiTesting": "",
    "databaseCommands": ["typeorm migration:run"]
  }
}
```

## Config Merging Behavior

配置合并遵循**深度合并**策略：

- 顶层字段：用户配置覆盖默认值
- 嵌套对象（如 `techStack`）：逐字段合并，用户指定的字段覆盖默认值，未指定的保留默认值
- 数组字段（如 `databaseCommands`）：用户配置完整替换默认值

**示例**：

```
默认: { "testing": { "lint": "npm run lint", "build": "npm run build" } }
用户: { "testing": { "lint": "pnpm lint" } }
合并: { "testing": { "lint": "pnpm lint", "build": "npm run build" } }
```

## Generating Config

### 方式 1: 直接生成并保存

```bash
python ~/.claude/skills/task-planner/scripts/detect_project.py /path/to/project --save
```

输出检测结果到 stdout，并保存到 `auto-coding/project-config.json`。

### 方式 2: 先预览再保存

```bash
# 预览检测结果（不保存）
python ~/.claude/skills/task-planner/scripts/detect_project.py /path/to/project --pretty

# 确认无误后保存
python ~/.claude/skills/task-planner/scripts/detect_project.py /path/to/project --save
```

### 方式 3: 初始化 session 时附带生成

```bash
python ~/.claude/skills/task-planner/scripts/init_session.py \
  /path/to/project \
  feature-name \
  --generate-config
```

在创建 session 的同时保存配置文件。

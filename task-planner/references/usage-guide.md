# Task Planner - Usage Guide

> 如何在新项目中使用 task-planner skill 的完整指南。

## 设计理念

task-planner 遵循 **自动化优先** 原则：

- **Python 做文件操作**: 项目检测、配置生成、session 文件创建均由 Python 脚本完成
- **AI 做规划和审查**: AI 负责需求分析、架构设计、任务分解和结果审查
- **脚本统一管理**: 所有自动化脚本集中在 `~/.claude/skills/task-planner/scripts/` 中，更新一次，所有项目受益

## 快速开始

### 1. 在新项目中使用

假设你有一个项目在 `/path/to/my-project`，想要规划一个新功能：

```bash
# Step 1: 用 Claude 开始规划（自然语言即可）
# 在 Claude Code 中说: "Plan a feature for user authentication"
# Claude 会自动调用 task-planner skill

# Step 2: 或者手动初始化 session
python ~/.claude/skills/task-planner/scripts/init_session.py \
  /path/to/my-project \
  auth-system-v1
```

init_session.py 会自动：
1. 检测项目技术栈（框架、包管理器、数据库等）
2. 创建 session 目录 `auto-coding/sessions/2026-02-26-auth-system-v1/`
3. 生成所有模板文件（PRD.md, architecture.md, task.json, progress.md）
4. 返回文件路径 JSON

### 2. 查看/修改配置

```bash
# 预览自动检测结果
python ~/.claude/skills/task-planner/scripts/detect_project.py /path/to/my-project --pretty

# 保存配置文件（可选，用于手动微调）
python ~/.claude/skills/task-planner/scripts/detect_project.py /path/to/my-project --save

# 手动编辑配置
vim /path/to/my-project/auto-coding/project-config.json
```

### 3. 运行自动化

```bash
# 使用项目启动器（推荐）
./auto-coding/run.sh

# 指定 session 和运行次数
./auto-coding/run.sh auto-coding/sessions/2026-02-26-auth-system-v1 3

# 直接使用 skill 脚本
~/.claude/skills/task-planner/scripts/run-automation.sh /path/to/my-project
```

## 完整工作流

### Phase 1: 需求分析

1. 向 Claude 描述功能需求
2. Claude 使用 task-planner 分析需求，提出澄清问题
3. 确认需求范围

### Phase 2: Session 初始化

1. Claude 调用 `init_session.py` 创建 session
2. 自动检测项目配置
3. 生成模板文件

### Phase 3: 架构和任务规划

1. Claude 填写 `architecture.md`（技术架构、数据模型、API 设计）
2. Claude 生成 `task.json`（3-7 步骤的任务列表）
3. 用户审查并调整

### Phase 4: 自动执行

1. 运行 `auto-coding/run.sh` 启动自动化
2. Claude 逐个执行任务：加载规范 → 实现 → 测试 → 提交
3. 每个任务完成后更新 `progress.md` 和 `task.json`

### Phase 5: 验收

1. 检查 `progress.md` 确认所有任务完成
2. 检查 `task.json` 确认所有 `passes: true`
3. 运行最终构建测试

## 项目目录结构

使用 task-planner 后，项目中会新增以下目录：

```
my-project/
├── auto-coding/                          # task-planner 工作目录
│   ├── run.sh                           # 自动化启动入口
│   ├── project-config.json              # 项目配置（可选）
│   └── sessions/
│       └── 2026-02-26-auth-system-v1/   # Session 目录
│           ├── PRD.md                   # 产品需求文档
│           ├── architecture.md          # 技术架构文档
│           ├── task.json                # 任务列表
│           ├── progress.md              # 进度记录
│           └── logs/
│               └── automation.log       # 自动化日志
├── src/                                  # 原有项目代码
├── package.json
└── ...
```

## Skill 目录结构

skill 的所有核心文件位于 `~/.claude/skills/task-planner/`：

```
~/.claude/skills/task-planner/
├── SKILL.md                    # Skill 主文档（Claude 读取的入口）
├── assets/
│   ├── default-project-config.json   # 默认配置
│   └── openspec-templates/           # OpenSpec 规范模板
│       ├── README.md                 # OpenSpec README 模板
│       ├── architecture.md           # 架构规范模板
│       ├── api.md                    # API 规范模板
│       ├── components.md             # 组件规范模板
│       ├── data-model.md             # 数据模型规范模板
│       └── generic.md               # 通用规范模板
├── scripts/
│   ├── init_session.py         # Session 初始化（集成检测+生成）
│   ├── detect_project.py       # 项目自动检测
│   ├── generate_files.py       # 模板文件生成
│   ├── setup_openspec.py       # OpenSpec 初始化
│   └── run-automation.sh       # 自动化执行脚本
├── templates/
│   ├── README.md               # 模板系统说明
│   ├── crud.json               # CRUD 任务模板
│   ├── auth.json               # 认证任务模板
│   ├── api.json                # API 任务模板
│   └── ui-component.json       # UI 组件任务模板
└── references/
    ├── project-config-schema.md    # 配置 Schema 文档
    ├── usage-guide.md              # 本文档
    ├── testing-requirements.md     # 测试要求文档
    └── auto-coding-patterns.md     # 编码模式最佳实践
```

## 脚本详解

### detect_project.py

自动检测项目技术栈，返回与 `project-config.json` 兼容的 JSON。

**支持检测**：
- 包管理器: pnpm, yarn, bun, npm（根据 lock 文件）
- 框架: Next.js, Nuxt, Vue, Angular, Svelte, SvelteKit, Remix, Astro, Express, Fastify, React
- 语言: TypeScript, JavaScript, Flow
- 数据库/ORM: Prisma, Drizzle, TypeORM, Sequelize, Mongoose, MongoDB, Supabase, Firebase
- 样式: Tailwind CSS, styled-components, Emotion, Chakra UI, Mantine, Material UI, Sass
- OpenSpec: 自动扫描 `openspec/specs/` 目录

**CLI 参数**：
```bash
python detect_project.py <project-path>          # 输出 JSON 到 stdout
python detect_project.py <project-path> --pretty  # 格式化 JSON 输出
python detect_project.py <project-path> --save     # 保存到 project-config.json
```

### generate_files.py

基于配置生成 session 模板文件。使用 `{{variable}}` 占位符替换。

**生成的文件**：PRD.md, architecture.md, task.json, progress.md, logs/automation.log

**CLI 参数**：
```bash
python generate_files.py --config <config.json> --output-dir <session-dir> --feature-name <name>
```

### init_session.py

Session 初始化的统一入口。内部调用 detect_project.py 和 generate_files.py。

**CLI 参数**：
```bash
python init_session.py <project-root> <feature-name>                  # 基本用法
python init_session.py <project-root> <feature-name> --generate-config # 附带保存配置
python init_session.py <project-root> <feature-name> --init-openspec   # 附带初始化 OpenSpec
```

**配置加载优先级**：
1. `auto-coding/project-config.json`（若存在）
2. 自动检测（`detect_project.py`）
3. 默认配置（`assets/default-project-config.json`）

### run-automation.sh

自动化执行脚本。循环执行 task.json 中的未完成任务。

**使用方式**：
```bash
# 通过项目启动器（推荐）
./auto-coding/run.sh [session-path] [run-count]

# 直接调用
~/.claude/skills/task-planner/scripts/run-automation.sh <project-root> [session-path] [run-count]
```

**环境变量**：
| 变量 | 默认值 | 说明 |
|------|--------|------|
| `CLAUDE_CMD` | `claude` | Claude CLI 命令 |
| `SKIP_INIT` | `false` | 跳过项目初始化脚本 |
| `CLEANUP_BROWSER` | `true` | 每个任务后清理浏览器进程 |

## 脚本统一管理的好处

task-planner 将所有自动化脚本集中在 `~/.claude/skills/task-planner/scripts/` 中管理：

1. **一次更新，所有项目受益**: 修复 `run-automation.sh` 中的 bug，所有使用该 skill 的项目自动使用新版本
2. **项目代码保持简洁**: 项目中只需要一个 24 行的 `auto-coding/run.sh` 启动入口
3. **统一的最佳实践**: 所有项目共享相同的任务执行逻辑、日志格式、错误处理
4. **无依赖冲突**: 脚本仅使用 Python 标准库和 bash，不需要额外安装依赖

## OpenSpec 集成

如果你的项目使用 [OpenSpec](https://github.com/Fission-AI/OpenSpec) 规范驱动开发：

1. **自动发现**: `detect_project.py` 会自动扫描 `openspec/specs/` 目录
2. **任务关联**: task.json 中的 `relatedSpecs` 字段关联到对应的 spec 文件
3. **规范优先**: 实现功能前先阅读相关 spec，代码遵循规范定义

不使用 OpenSpec 的项目可以忽略此功能，`openspec.enabled` 默认为 `false`。

### 初始化 OpenSpec

对于新项目想要引入 OpenSpec 规范驱动开发，可以使用 `--init-openspec` 参数：

```bash
# 在初始化 session 时同时初始化 OpenSpec
python ~/.claude/skills/task-planner/scripts/init_session.py \
  /path/to/my-project \
  feature-name \
  --init-openspec

# 或直接使用 setup_openspec.py
python ~/.claude/skills/task-planner/scripts/setup_openspec.py /path/to/my-project
```

**自动生成的内容**：

根据检测到的项目类型，自动生成不同的 spec 模板：

| 项目类型 | 生成的 specs |
|----------|-------------|
| Full-stack (Next.js, Nuxt 等) | architecture, api, components |
| Backend (Express, Fastify) | architecture, api |
| Frontend (React, Vue 等) | architecture, components |
| 有数据库/ORM | 额外添加 data-model |

**安全机制**：
- 如果项目已有 `openspec/` 目录，默认跳过（不覆盖）
- 不会覆盖已有的 spec 文件
- 使用 `--force` 参数可强制重新初始化目录结构

### setup_openspec.py

独立的 OpenSpec 初始化脚本。

**CLI 参数**：
```bash
python setup_openspec.py <project-path>                  # 基本初始化
python setup_openspec.py <project-path> --force           # 强制重新初始化
python setup_openspec.py <project-path> --config <file>   # 指定配置文件
```

## 模板系统

task-planner 提供 4 个内置任务模板，覆盖常见开发场景：

| 模板 | 场景 | 任务数 |
|------|------|--------|
| `crud.json` | 增删改查、管理页面 | 4 |
| `auth.json` | 登录、注册、权限 | 4 |
| `api.json` | API 端点、后端服务 | 3 |
| `ui-component.json` | 组件、页面、表单 | 3 |

### 使用模板

Claude 在规划任务时会自动匹配合适的模板。你也可以在请求中指定：

> "使用 CRUD 模板规划用户管理功能"

### 自定义模板

项目可以创建自己的模板：

1. 在 `auto-coding/templates/` 下创建 JSON 文件
2. 在 `project-config.json` 中注册：
   ```json
   {
     "templates": {
       "customTemplates": ["auto-coding/templates/my-template.json"]
     }
   }
   ```

模板 JSON 格式参见 `templates/README.md`。

---

## FAQ

### 基础使用

**Q: 我需要手动创建 `project-config.json` 吗？**

A: 不需要。task-planner 会自动检测项目配置。只有当自动检测结果不准确时，才需要手动创建或修改配置文件。建议先运行 `--save` 生成配置，再手动微调。

**Q: 不使用 OpenSpec 可以用 task-planner 吗？**

A: 可以。OpenSpec 是可选功能。不使用时 `openspec.enabled` 默认为 `false`，不影响其他功能。

**Q: task-planner 支持哪些编程语言的项目？**

A: 目前自动检测主要针对 JavaScript/TypeScript 生态（Node.js 项目），通过分析 `package.json` 获取信息。对于其他语言的项目，可以手动创建 `project-config.json` 配置。

**Q: 可以在同一个项目中创建多个 session 吗？**

A: 可以。每个 session 是独立的功能开发周期，有独立的 task.json 和 progress.md。不同 session 之间互不干扰。

### 配置问题

**Q: 自动检测的框架版本不对怎么办？**

A: 运行 `--save` 生成配置文件后，手动编辑 `auto-coding/project-config.json` 中的 `techStack.framework` 字段。下次初始化 session 时会优先使用手动配置。

**Q: 我的项目使用 monorepo（Turborepo/Nx），怎么配置？**

A: 在每个 package/app 的根目录下分别运行 `detect_project.py`，或手动创建针对特定 package 的配置文件。当前不支持 monorepo 级别的自动检测。

**Q: `databaseCommands` 的命令是在什么时候执行的？**

A: 这些命令会被写入 task.json 的测试步骤中。在自动化执行时，Claude 会在修改 schema 的任务中运行这些命令（如 `prisma generate`）来更新客户端类型。

**Q: 我的测试命令不是标准的 `npm run lint` 格式怎么办？**

A: 手动配置 `testing` 对象中的命令。例如使用 vitest 的项目可以设置 `"test": "npx vitest run"`。支持任意命令字符串。

### 自动化执行

**Q: `run-automation.sh` 执行任务失败了怎么办？**

A: 检查 `logs/automation.log` 查看详细日志。常见原因：
1. 构建失败 — 检查代码错误
2. 测试不通过 — 查看具体失败项
3. Claude CLI 超时 — 增加超时时间或拆分任务

失败的任务会保持 `passes: false`，下次运行会重试。

**Q: 如何跳过项目初始化（`init.sh`）？**

A: 设置环境变量 `SKIP_INIT=true`：
```bash
SKIP_INIT=true ./auto-coding/run.sh
```

**Q: 可以并行执行多个任务吗？**

A: 目前不支持。任务按顺序执行，确保依赖关系正确。每个任务完成并提交后，才会开始下一个。

**Q: 自动化脚本会修改我的 git 历史吗？**

A: 每个任务完成后会创建一个新的 git commit（包含代码变更 + task.json 更新 + progress.md 更新）。不会修改已有的 commit 历史。

### 故障排查

**Q: `setup_openspec.py` 跳过了初始化，但我想重新生成**

A: 如果项目已有 `openspec/` 目录，脚本默认跳过。使用 `--force` 参数强制重新初始化目录结构（不会覆盖已有的 spec 文件）：
```bash
python setup_openspec.py /path/to/project --force
```

**Q: 生成的 spec 模板不适合我的项目类型**

A: spec 模板是起点，不是最终版本。你可以直接编辑生成的 `spec.md` 文件，删除不需要的部分，添加项目特有的 requirements 和 scenarios。也可以删除不适用的 spec 目录。

**Q: `detect_project.py` 报错 "No such file or directory"**

A: 确认传入的项目路径是正确的绝对路径或相对路径。脚本需要项目根目录中存在 `package.json` 才能进行完整检测。

**Q: `init_session.py` 报错 "Invalid feature name"**

A: 功能名称必须使用 kebab-case 格式（小写字母、数字、连字符、点号）。例：`user-profile-v1`, `auth-system`, `api-v2.0`。不支持空格、下划线或中文。

**Q: 生成的文件中有未替换的 `{{variable}}`**

A: 检查配置文件中对应字段是否为空字符串。空字符串会被直接替换（变量消失），但如果变量名拼写错误则不会被替换。确认 `generate_files.py` 支持该变量（参见 project-config-schema.md 的 Template Variables 部分）。

**Q: `run-automation.sh` 提示 "claude: command not found"**

A: 确认已安装 Claude CLI 并在 PATH 中。或通过环境变量指定：
```bash
CLAUDE_CMD=/path/to/claude ./auto-coding/run.sh
```

**Q: 更新了 skill 脚本后项目没有使用新版本**

A: 项目中的 `auto-coding/run.sh` 是一个 thin wrapper，直接调用 `~/.claude/skills/task-planner/scripts/run-automation.sh`。更新 skill 中的脚本后，所有项目会立即使用新版本，无需任何额外操作。如果仍有问题，检查 `auto-coding/run.sh` 中的路径是否正确。

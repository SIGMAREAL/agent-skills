# Testing Requirements for Tasks

**IMPORTANT**: Every task must include testing steps as the final steps. The testing requirements vary by task type.

> **Note**: Testing commands are project-specific and defined in `auto-coding/project-config.json` under the `testing` key. The commands below use placeholder names — refer to your project's `progress.md` Testing Commands Reference table for actual commands.

## Mandatory Testing Steps (All Tasks)

**Last 1-2 steps of every task must be**:

```json
{
  "steps": [
    "...(implementation steps)...",
    "运行 TypeScript 检查、Lint、Build 测试",
    "更新 progress.md 记录测试结果"
  ]
}
```

**Testing commands** (from project config):
- **Type Check**: `testing.typeCheck` (e.g., `npx tsc --noEmit`, `vue-tsc --noEmit`)
- **Lint**: `testing.lint` (e.g., `pnpm lint`, `npm run lint`, `yarn lint`)
- **Build**: `testing.build` (e.g., `pnpm build`, `npm run build`)

## UI Task Testing (New/Modified Pages)

For tasks involving **new pages, components, or UI changes**, add these steps:

```json
{
  "id": "ui-task-example",
  "title": "Feature UI component",
  "steps": [
    "Create page/component file",
    "Implement layout and interactions",
    "Add loading and error states",
    "运行 TypeScript、Lint、Build 测试",
    "使用 dev-browser 测试页面",
    "更新 progress.md 记录测试结果和截图路径"
  ]
}
```

### dev-browser Testing Guide

**测试步骤详解**:

```markdown
使用 dev-browser 测试页面：
1. 启动 dev-browser 服务器（如未运行）
2. 导航到 http://localhost:3000/[页面路径]
3. 验证页面正确加载（标题、URL、内容）
4. 测试交互功能（按钮、链接、表单）
5. 截图保存到 ~/.claude/skills/dev-browser/tmp/
6. 记录截图路径到 progress.md
```

**测试模板**:

```typescript
// 在任务步骤中描述为：
"使用 dev-browser 测试：导航页面 → 验证加载 → 测试交互 → 截图"

// 实际执行时的代码：
cd ~/.claude/skills/dev-browser && npx tsx <<'EOF'
import { connect, waitForPageLoad } from "@/client.js";

const client = await connect();
const page = await client.page("test-[task-id]");

await page.goto("http://localhost:3000/[path]");
await waitForPageLoad(page);

console.log("Title:", await page.title());
await page.screenshot({ path: "tmp/[task-id]-result.png" });

// 测试交互
const snapshot = await client.getAISnapshot("test-[task-id]");
// ... 点击、输入等操作

await client.disconnect();
EOF
```

## API Task Testing

For tasks involving **API endpoints**:

```json
{
  "steps": [
    "...(implementation steps)...",
    "测试 API 端点（正常流程 + 错误处理）",
    "运行 TypeScript、Lint、Build 测试",
    "更新 progress.md"
  ]
}
```

## Database Task Testing

For tasks involving **schema changes** (Prisma, Drizzle, TypeORM, etc.):

```json
{
  "steps": [
    "...(implementation steps)...",
    "运行数据库客户端生成命令（参见 testing.databaseCommands）",
    "运行 TypeScript、Lint、Build 测试",
    "更新 progress.md"
  ]
}
```

## Testing Step Templates by Task Type

| Task Type | Final Testing Steps |
|-----------|---------------------|
| **UI (新页面/组件)** | `"运行测试"`, `"dev-browser 浏览器测试"`, `"更新 progress.md"` |
| **UI (小修改)** | `"运行测试"`, `"更新 progress.md"` |
| **API** | `"测试 API 端点"`, `"运行测试"`, `"更新 progress.md"` |
| **Database** | `"运行数据库命令"`, `"运行测试"`, `"更新 progress.md"` |
| **其他** | `"运行测试"`, `"更新 progress.md"` |

**Note**: "运行测试" = TypeScript check (`testing.typeCheck`) + Lint (`testing.lint`) + Build (`testing.build`)

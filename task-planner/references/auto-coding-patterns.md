# Auto-Coding Patterns

## Task Granularity Rules

### Size Guidelines
- **3-7 steps per task** - Enough to be meaningful, small enough to complete in one session
- **30-90 minutes estimated completion** - Single sitting work
- **1-3 files modified** - Focused change set
- **Single feature or component** - Clear scope boundary

### Examples

**Good (5 steps, focused):**
```json
{
  "id": "login-page",
  "title": "登录页面实现",
  "steps": [
    "创建 app/login/page.tsx",
    "创建 LoginForm 组件",
    "实现邮箱+密码登录",
    "添加错误处理",
    "登录成功后跳转"
  ]
}
```

**Bad (too big):**
```json
{
  "id": "auth-system",
  "title": "完整认证系统",
  "steps": [
    "实现登录、注册、找回密码、OAuth、2FA...",
    "..."
  ]
}
```

## Task Ordering

### Dependency Chain
1. **Infrastructure/Config** - Dependencies, env vars, configs
2. **Data Models** - Database schemas, types
3. **API Layer** - Endpoints, business logic
4. **UI Components** - Pages, components
5. **Integration/Polish** - Error handling, loading states, tests

### Example Flow
```
Task 1: Install Supabase client (infra)
Task 2: Create database schema (data)
Task 3: Create auth API routes (API)
Task 4: Build login page (UI)
Task 5: Add auth protection (integration)
```

## Testing Requirements

### Mandatory Checks

Testing commands come from the project's `auto-coding/project-config.json`:
- `testing.lint` - Lint check (e.g., `pnpm lint`, `npm run lint`)
- `testing.build` - Build verification (e.g., `pnpm build`, `npm run build`)
- `testing.typeCheck` - TypeScript check (e.g., `npx tsc --noEmit`)

### UI Changes

- Browser testing with dev-browser skill
- Screenshot verification
- Interaction testing (clicks, form fills, navigation)

### API Changes
- Endpoint testing
- Error case handling
- Response format validation

## Commit Rules

### Single Commit Per Task
```bash
git add .
git commit -m "[task-id] Task description - completed"
```

### Must Include
- All code changes
- task.json update (passes: true)
- progress.txt entry

### Never Do
- Multiple commits for one task
- Commit without testing
- Mark passes: true if incomplete

# Figma + Resources Workflow

完整指南：使用 Figma 低保真原型图 + PRD 文档驱动自动化开发。

## 目录

1. [适用场景](#适用场景)
2. [Session 目录结构](#session-目录结构)
3. [准备阶段（用户操作）](#准备阶段用户操作)
4. [规划阶段（task-planner 操作）](#规划阶段task-planner-操作)
5. [task.json 任务格式](#taskjson-任务格式)
6. [执行阶段说明](#执行阶段说明)
7. [最佳实践](#最佳实践)

---

## 适用场景

以下情况使用此工作流：

- 有 Figma 低保真原型图，每个 frame 对应一个待实现页面
- 有独立 PRD 文档（Word/飞书/Markdown，内容可杂乱无序）
- 需要获取 Figma 帧节点结构作为布局参考
- 不使用截图，通过结构化节点数据理解布局

---

## Session 目录结构

```
auto-coding/sessions/YYYY-MM-DD-feature-name/
├── PRD.md                  # 整理后的产品需求（由 task-planner 从 resources/ 合成）
├── architecture.md         # 技术架构（含组件层次，基于 Figma 帧结构分析）
├── task.json               # 任务列表（每个任务含 figmaFrameId）
├── progress.md             # 进度记录
├── resources/              # 原始输入文件（由 init_session.py 自动创建）
│   ├── README.md           # 目录说明（自动生成）
│   ├── figma-frames.json   # Figma 帧节点数据（task-planner 规划时通过 REST API 生成）
│   └── *.md / *.txt        # 用户手动放置的原始 PRD 文档
└── logs/
    └── automation.log
```

---

## 准备阶段（用户操作）

**Step 1**: 运行 init_session.py 创建 session

```bash
python ~/.claude/skills/task-planner/scripts/init_session.py \
  /path/to/project \
  feature-name
```

此命令会自动创建 `resources/` 目录及其 README.md。

**Step 2**: 将原始 PRD/需求文档放入 `resources/`

```
resources/
├── 01-overview.md      # 功能概述（可直接粘贴飞书内容）
├── 02-flow.md          # 用户流程和交互说明
└── 03-constraints.md   # 技术约束和边界条件
```

建议加数字前缀确保阅读顺序，内容可混乱，task-planner 会重新整理。

**Step 3**: 提供 Figma 信息

告知 task-planner：
- Figma 文件 ID（如 `o84V8gz2EZzmAhYhOKDyHN`，从文件 URL 中提取）
- Figma PAT Token（Personal Access Token）

frame ID 不需要提前准备，task-planner 会从文件结构中自动发现。

---

## 规划阶段（task-planner 操作）

### 1. 读取 resources/

阅读 `resources/` 下所有文档，理解功能需求和约束条件。

### 2. 获取 Figma 帧结构（REST API）

使用 Figma REST API 获取帧节点数据，**不依赖 Figma MCP，Figma 可以关闭**。

**Step 2a：发现所有帧 ID**

```bash
curl "https://api.figma.com/v1/files/{fileId}?depth=2" \
  -H "X-Figma-Token: {PAT_TOKEN}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for page in data['document']['children']:
    print(f'Page: {page[\"name\"]} ({page[\"id\"]})')
    for child in page.get('children', []):
        print(f'  Frame: {child[\"name\"]} ({child[\"id\"]})')
"
```

输出示例：
```
Page: Components (1:3)
  Frame: 讲义生成配置-锁定教学范围 (1:3534)
  Frame: 讲义生成配置-设定教学策略 (1:3616)
  Frame: 历史讲义 (8:1101)
```

根据需求确定需要实现的帧 ID（可向用户确认），或由用户直接提供 Figma 帧链接（从 URL 中提取 `node-id` 参数，`-` 替换为 `:`）。

**Step 2b：批量获取帧节点结构**

```bash
# 多个帧用逗号分隔，节点 ID 用冒号格式（1:3534,1:3616,1:3769）
curl "https://api.figma.com/v1/files/{fileId}/nodes?ids={id1},{id2},{id3}" \
  -H "X-Figma-Token: {PAT_TOKEN}" | python3 -c "
import json, sys

def print_tree(node, depth=0, max_depth=3):
    if depth > max_depth: return
    prefix = '  ' * depth
    ntype = node.get('type', '')
    name = node.get('name', '')
    nid = node.get('id', '')
    bounds = node.get('absoluteBoundingBox', {})
    w, h = int(bounds.get('width', 0)), int(bounds.get('height', 0))
    chars = f' \"{node[\"characters\"][:40]}\"' if ntype == 'TEXT' else ''
    print(f'{prefix}[{ntype}] {name} ({nid}) [{w}x{h}]{chars}')
    for child in node.get('children', []):
        print_tree(child, depth+1, max_depth)

data = json.load(sys.stdin)
for node_id, node_data in data['nodes'].items():
    doc = node_data['document']
    print(f'\n=== {doc[\"name\"]} ({node_id}) ===')
    for child in doc.get('children', []):
        print_tree(child, 1)
"
```

**PAT Token 来源**：
- 从 `~/.claude.json` 的 figma MCP args 中提取（`--figma-api-key=figd_...`）
- 或由用户在对话中提供

**Figma URL 中提取帧 ID**：
- URL 格式：`...?node-id=1-3534&...`
- 对应节点 ID：`1:3534`（将 `-` 替换为 `:`）

### 3. 保存 figma-frames.json

将节点数据处理后保存到 `resources/figma-frames.json`：

```json
{
  "fileId": "o84V8gz2EZzmAhYhOKDyHN",
  "fetchedAt": "2026-02-27",
  "frames": {
    "1:3534": {
      "figmaNodeId": "1:3534",
      "figmaUrl": "https://www.figma.com/design/...",
      "name": "讲义生成配置-锁定教学范围",
      "size": { "w": 1728, "h": 1117 },
      "layout": { ... }
    }
  }
}
```

**保存完成后 Figma 可以关闭**，执行阶段不再需要 Figma。

### 4. 合成 PRD.md

基于 `resources/` 原始文档重新整理，输出结构化的 PRD：

```markdown
# PRD: [Feature Name]

## 功能概述
[从原始文档提炼的清晰描述]

## 页面清单
| 帧ID    | 页面名称     | 核心功能         |
|---------|-------------|-----------------|
| 1:3534  | 锁定教学范围 | 选择年级/学科/章节 |

## 业务逻辑
[从原始文档中提取的规则和约束]
```

### 5. 生成 architecture.md

基于 Figma 帧节点分析组件层次，识别可复用组件：

- 提取每个帧的顶层结构（导航栏、主体区域、底部操作区）
- 识别跨帧复用的组件（如配置表单、选择器等）
- 定义组件目录结构

### 6. 生成 task.json

每个 Figma 帧（或功能模块）对应一个任务，含 `figmaFrameId` 字段（见下节）。

---

## task.json 任务格式

### 扩展字段说明

Figma 页面任务需包含两个额外字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `figmaFileId` | string | Figma 文件 ID |
| `figmaFrameId` | string | 帧节点 ID（如 `1:3534`） |

这两个字段均为可选，不影响无 Figma 的普通任务。

### 任务示例

```json
{
  "id": "ui-page-1",
  "title": "实现讲义生成配置页面（锁定教学范围）",
  "figmaFileId": "o84V8gz2EZzmAhYhOKDyHN",
  "figmaFrameId": "1:3534",
  "description": "实现讲义生成的第一步配置页面",
  "steps": [
    "阅读 resources/figma-frames.json 中 1:3534 帧的节点结构，分析布局层次",
    "阅读 PRD.md 中对应页面的需求描述",
    "在 app/ 下创建对应页面文件，按照 Figma 帧的布局层次实现",
    "复用项目现有设计系统，视觉风格保持一致",
    "运行 pnpm build 确认构建成功",
    "更新 progress.md"
  ],
  "passes": false,
  "priority": "high",
  "tags": ["ui", "figma", "page"],
  "relatedSpecs": ["auto-coding/sessions/YYYY-MM-DD-feature/PRD.md"]
}
```

**注意**：steps 中不需要"调用 Figma API"——数据已在规划阶段保存到 `figma-frames.json`，执行时直接读取即可。

---

## 执行阶段说明

每个任务执行时，Claude 读取 `figma-frames.json` 中缓存的节点数据作为布局参考，**无需 Figma 打开或 MCP 连接**。

**布局参考原则**（非像素还原）：
- 节点层次 → 组件嵌套结构
- 相对尺寸比例 → flex/grid 布局
- 元素排列顺序 → DOM 结构
- 文字内容 → 占位文案

**视觉风格**：跟随项目现有设计系统，不从 Figma 低保真中提取颜色或精确尺寸。

**不使用截图**：始终通过节点树数据理解布局，节点树比图片提供更精确的结构信息。

---

## 最佳实践

1. **文档命名加序号**: `01-overview.md`, `02-flow.md`，确保阅读顺序
2. **figma-frames.json 不要手动编辑**: 由 task-planner 在规划阶段通过 REST API 自动生成
3. **规划完成即可关闭 Figma**: 执行阶段完全依赖 figma-frames.json，无需保持 Figma 打开
4. **设计更新后重新规划**: Figma 帧更新时，重新运行规划阶段获取最新节点数据
5. **任务粒度**：每个任务聚焦 1-2 个文件，避免单任务过大
6. **resources/ 内容只读**: 规划完成后，不在 resources/ 中修改原始文档（以便追溯）

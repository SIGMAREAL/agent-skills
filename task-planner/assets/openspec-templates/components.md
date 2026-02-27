# Components Specification - {{projectName}}

> 组件规范，定义 UI 组件的行为、属性和交互模式。

## Purpose

定义 {{projectName}} 的 UI 组件规范，确保组件设计一致、可复用、可测试。

## Component Conventions

- **样式方案**: {{styling}}
- **组件库**: [待定义]
- **命名规则**: PascalCase (组件), camelCase (props/hooks)
- **文件结构**: 每个组件一个目录，包含组件文件、类型定义

## Requirements

### REQ-COMP-001: 组件可访问性

所有交互组件 MUST 符合基本的可访问性要求。

#### Scenario: 键盘导航

```gherkin
GIVEN 用户使用键盘导航
WHEN 焦点到达交互组件
THEN 组件 MUST 有可见的焦点指示
AND MUST 支持 Enter/Space 键触发操作
```

#### Scenario: 语义化标签

```gherkin
GIVEN 组件渲染到页面
THEN MUST 使用语义化 HTML 标签
AND 交互元素 MUST 有 aria-label 或关联标签
```

### REQ-COMP-002: 响应式设计

所有页面级组件 MUST 支持响应式布局。

#### Scenario: 移动端适配

```gherkin
GIVEN 用户在移动设备上访问
WHEN 视口宽度 < 768px
THEN 布局 MUST 自动调整为移动端友好的排列
AND 交互元素 MUST 有足够的触摸区域 (>= 44px)
```

### REQ-COMP-003: 加载状态

异步操作相关组件 MUST 显示加载状态。

#### Scenario: 数据加载中

```gherkin
GIVEN 组件需要加载远程数据
WHEN 数据正在加载
THEN MUST 显示加载指示器
AND SHOULD 禁用可能导致重复请求的交互元素
```

## Component Catalog

> 在此定义项目的核心组件，包括 props、行为和使用示例。

### [组件名称]

**Props**:
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| - | - | - | - |

**Behavior**:
- [描述组件行为]

## Notes

- 本规范创建于 {{date}}
- 新增组件前请先在此添加规范定义
- 修改前请创建变更提案 (openspec/changes/)

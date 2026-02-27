# Architecture Specification - {{projectName}}

> 系统架构规范，定义核心架构决策和技术约束。

## Purpose

定义 {{projectName}} 的系统架构，确保所有开发活动遵循统一的技术规范和设计模式。

## Technology Stack

| 层级 | 技术 |
|------|------|
| 框架 | {{framework}} |
| 语言 | {{language}} |
| 数据库 | {{database}} |
| 样式 | {{styling}} |

## Architecture Decisions

### ADR-001: [架构决策标题]

**Status**: Proposed
**Date**: {{date}}

**Context**: [描述决策背景和问题]

**Decision**: [描述决策内容]

**Consequences**: [描述决策的影响]

## Requirements

### REQ-ARCH-001: 目录结构

项目 MUST 遵循以下目录结构约定。

#### Scenario: 标准目录布局

```gherkin
GIVEN 项目根目录
THEN 应包含以下核心目录
AND 每个目录的职责清晰分离
```

### REQ-ARCH-002: 错误处理模式

系统 MUST 使用统一的错误处理模式。

#### Scenario: API 错误响应

```gherkin
GIVEN API 端点发生错误
WHEN 错误被捕获
THEN MUST 返回统一格式的错误响应
AND 错误信息 SHOULD 包含可操作的描述
```

## Notes

- 本规范创建于 {{date}}
- 根据项目发展持续更新
- 修改前请创建变更提案 (openspec/changes/)

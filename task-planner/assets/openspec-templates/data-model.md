# Data Model Specification - {{projectName}}

> 数据模型规范，定义数据库 schema、关系和约束。

## Purpose

定义 {{projectName}} 的数据模型规范，确保数据库设计满足业务需求并保持数据完整性。

## Database

- **数据库**: {{database}}
- **命名规则**: snake_case (表名、字段名)
- **主键**: 所有表 MUST 有主键
- **时间戳**: 所有表 SHOULD 有 `created_at` 和 `updated_at` 字段

## Requirements

### REQ-DATA-001: 数据完整性

所有数据表 MUST 定义适当的约束以确保数据完整性。

#### Scenario: 必填字段

```gherkin
GIVEN 数据表中定义了必填字段
WHEN 插入或更新记录时缺少必填字段
THEN 数据库 MUST 拒绝操作
AND MUST 返回明确的约束违反错误
```

#### Scenario: 外键关系

```gherkin
GIVEN 两个表之间存在外键关系
WHEN 尝试删除被引用的记录
THEN MUST 根据级联策略处理（CASCADE/RESTRICT/SET NULL）
AND 不应产生孤立数据
```

### REQ-DATA-002: 索引策略

频繁查询的字段 SHOULD 建立索引。

#### Scenario: 查询性能

```gherkin
GIVEN 表中有大量数据
WHEN 执行按常用字段过滤的查询
THEN 查询 SHOULD 使用索引
AND 响应时间 SHOULD 在可接受范围内
```

## Models

> 在此定义项目的核心数据模型。

### [模型名称]

**表名**: `[table_name]`

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID/Int | PK | 主键 |
| created_at | DateTime | NOT NULL, DEFAULT now() | 创建时间 |
| updated_at | DateTime | NOT NULL | 更新时间 |

**关系**:
- [描述与其他模型的关系]

**索引**:
- [描述索引策略]

## Notes

- 本规范创建于 {{date}}
- 修改 schema 前请先更新此规范
- 修改前请创建变更提案 (openspec/changes/)

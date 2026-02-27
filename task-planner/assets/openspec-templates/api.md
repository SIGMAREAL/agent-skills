# API Specification - {{projectName}}

> API 端点规范，定义路由、请求/响应格式和行为契约。

## Purpose

定义 {{projectName}} 的 API 接口规范，确保所有端点遵循一致的设计模式和行为约定。

## API Conventions

- **Base Path**: `/api`
- **Response Format**: JSON (`{ success: boolean, data?: any, error?: string }`)
- **Authentication**: [待定义]
- **Versioning**: [待定义]

## Requirements

### REQ-API-001: 统一响应格式

所有 API 端点 MUST 返回统一格式的 JSON 响应。

#### Scenario: 成功响应

```gherkin
GIVEN 客户端发送有效请求
WHEN API 处理成功
THEN MUST 返回 HTTP 200
AND 响应 body MUST 包含 { "success": true, "data": ... }
```

#### Scenario: 错误响应

```gherkin
GIVEN 客户端发送无效请求
WHEN API 处理失败
THEN MUST 返回适当的 HTTP 状态码
AND 响应 body MUST 包含 { "success": false, "error": "描述信息" }
```

### REQ-API-002: 输入验证

所有 API 端点 MUST 验证输入参数。

#### Scenario: 缺少必填参数

```gherkin
GIVEN 客户端发送请求
WHEN 缺少必填参数
THEN MUST 返回 HTTP 400
AND 错误信息 SHOULD 指明缺少的参数名称
```

## Endpoints

> 按功能域组织 API 端点，在此添加具体的端点定义。

### [域名称]

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/[resource]` | 获取列表 |
| POST | `/api/[resource]` | 创建记录 |
| GET | `/api/[resource]/[id]` | 获取详情 |
| PUT | `/api/[resource]/[id]` | 更新记录 |
| DELETE | `/api/[resource]/[id]` | 删除记录 |

## Notes

- 本规范创建于 {{date}}
- 新增端点前请先更新此规范
- 修改前请创建变更提案 (openspec/changes/)

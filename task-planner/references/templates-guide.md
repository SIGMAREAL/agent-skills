# Templates Guide

## Table of Contents

1. [Overview](#overview)
2. [Available Templates](#available-templates)
3. [Template Usage](#template-usage)
4. [Variable Replacement](#variable-replacement)
5. [Custom Templates](#custom-templates)

## Overview

Task templates are pre-defined JSON files in `templates/` that provide standardized task structures for common development patterns.

## Available Templates

| Template | File | Use When |
|----------|------|----------|
| CRUD | `templates/crud.json` | 增删改查、管理页面、列表/详情 |
| Auth | `templates/auth.json` | 登录、注册、认证、权限 |
| API | `templates/api.json` | API 端点、接口、后端服务 |
| UI Component | `templates/ui-component.json` | 组件、页面、表单、UI |

## Template Usage

1. Match user requirement keywords to a template (see `keywords` field in each template)
2. Load the template JSON
3. Replace variable placeholders (`{{feature_name}}`, `{{resource}}`, etc.) with actual values
4. Adjust tasks as needed (add/remove steps, update priorities)
5. Set `relatedSpecs` based on project's OpenSpec domains
6. Write tasks to `task.json`

## Variable Replacement

Templates use `{{variable}}` placeholders consistent with `generate_files.py`:

- **Project variables** (auto-filled from config): `{{lint_command}}`, `{{build_command}}`, `{{type_check_command}}`
- **Template variables** (set per usage): `{{feature_name}}`, `{{resource}}`, `{{component_name}}`, `{{route_path}}`

## Custom Templates

Projects can define custom templates in `auto-coding/templates/` and register them in `project-config.json`:

```json
{
  "templates": {
    "enabled": true,
    "customTemplates": ["auto-coding/templates/my-template.json"]
  }
}
```

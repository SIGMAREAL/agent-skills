# OpenSpec - {{projectName}}

> 规范驱动开发 (Specification-Driven Development) with [OpenSpec](https://github.com/Fission-AI/OpenSpec)

## 什么是 OpenSpec？

OpenSpec 是一种规范驱动开发方法，通过 **先写规范，再写代码** 的方式确保：

- 功能行为有明确的契约定义
- 变更历史可追溯
- 团队对系统行为有统一理解

## 目录结构

```
openspec/
├── README.md                   # 本文件
├── specs/                      # 规范文件（系统当前状态）
│   ├── architecture/
│   │   └── spec.md             # 架构规范
│   ├── api/
│   │   └── spec.md             # API 规范
│   ├── components/
│   │   └── spec.md             # 组件规范
│   └── data-model/
│       └── spec.md             # 数据模型规范
├── changes/                    # 变更记录
│   └── archive/                # 已完成的变更归档
│       └── YYYY-MM-DD-change-name/
│           ├── proposal.md     # 变更提案
│           └── tasks.md        # 任务分解
└── ...

docs/
└── guides/                     # 用户指南和教程
    └── ...
```

## 核心概念

### 三层文档结构

| 层级 | 路径 | 作用 |
|------|------|------|
| **Specs** | `openspec/specs/` | 系统当前状态的行为契约 |
| **Changes** | `openspec/changes/archive/` | 变更历史记录 |
| **Guides** | `docs/guides/` | 用户指南和教程 |

### 行为规范 (Gherkin 格式)

每个 spec 使用 Gherkin 格式描述行为：

```gherkin
GIVEN 用户在登录页面
WHEN 输入正确的用户名和密码
THEN 应跳转到首页
AND 显示欢迎消息
```

### RFC 2119 关键词

| 关键词 | 含义 |
|--------|------|
| **MUST** | 必须实现，不可协商 |
| **SHOULD** | 强烈建议，有充分理由时可例外 |
| **MAY** | 可选实现 |

## 工作流

### 新功能开发

```
1. 阅读相关 spec → 理解现有规范
2. 创建变更提案 → openspec/changes/archive/YYYY-MM-DD-feature/proposal.md
3. 更新 spec → 添加新的 requirements 和 scenarios
4. 分解任务 → openspec/changes/archive/YYYY-MM-DD-feature/tasks.md
5. 实施开发 → 代码遵循 spec 定义
6. 验证完成 → 对照 spec 验收
```

### 修改现有功能

```
1. 查阅 spec → 理解当前行为定义
2. 创建变更记录 → 记录为什么要改
3. 更新 spec → 修改 requirements/scenarios
4. 实施变更 → 代码反映新的 spec
5. 验证完成 → 确保新旧行为都正确
```

## 快速上手

1. **查看规范**: 浏览 `openspec/specs/` 下的 spec.md 文件
2. **理解格式**: 每个 spec 包含 Purpose、Requirements、Scenarios
3. **开发前阅读**: 实现功能前先阅读相关 spec
4. **保持同步**: 代码变更时同步更新对应的 spec

## 参考

- [OpenSpec 项目](https://github.com/Fission-AI/OpenSpec)
- [Gherkin 格式](https://cucumber.io/docs/gherkin/)
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119)

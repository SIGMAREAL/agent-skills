#!/usr/bin/env python3
"""
Session File Generator

根据项目配置自动生成 session 模板文件（architecture.md, task.json, progress.md, PRD.md）。
支持变量替换：{{projectName}}, {{framework}}, {{lint_command}} 等。

Usage:
    python generate_files.py --config config.json --output-dir /path/to/session
    python generate_files.py --config config.json --output-dir /path/to/session --feature-name my-feature

Example:
    python generate_files.py \
      --config /path/to/project-config.json \
      --output-dir /path/to/project/auto-coding/sessions/2026-02-26-feature
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str) -> Dict[str, Any]:
    """加载项目配置文件"""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_default_config() -> Dict[str, Any]:
    """加载默认配置"""
    default_path = Path(__file__).parent.parent / "assets" / "default-project-config.json"
    if default_path.exists():
        with open(default_path, "r", encoding="utf-8") as f:
            return json.load(f)
    # Inline fallback if asset file is missing
    return {
        "projectName": "My Project",
        "techStack": {
            "framework": "",
            "language": "TypeScript",
            "database": "",
            "styling": "",
            "packageManager": "npm",
        },
        "testing": {
            "typeCheck": "npx tsc --noEmit",
            "lint": "npm run lint",
            "build": "npm run build",
            "uiTesting": "dev-browser",
            "databaseCommands": [],
        },
        "openspec": {"enabled": False, "domains": {}},
        "templates": {"enabled": True, "customTemplates": []},
    }


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """递归合并配置（override 中非空值覆盖 base）"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        elif value not in (None, "", [], {}):
            result[key] = value
    return result


def build_variables(config: Dict[str, Any], feature_name: str, session_name: str) -> Dict[str, str]:
    """从配置构建模板变量映射"""
    tech = config.get("techStack", {})
    testing = config.get("testing", {})
    openspec = config.get("openspec", {})

    # Build tech stack display string
    tech_parts = []
    if tech.get("framework"):
        tech_parts.append(tech["framework"])
    if tech.get("language"):
        tech_parts.append(tech["language"])
    if tech.get("database"):
        tech_parts.append(tech["database"])
    if tech.get("styling"):
        tech_parts.append(tech["styling"])
    tech_stack_display = " + ".join(tech_parts) if tech_parts else "Not specified"

    # Build OpenSpec domains table
    openspec_table = ""
    if openspec.get("enabled") and openspec.get("domains"):
        rows = []
        for domain, spec_path in openspec["domains"].items():
            rows.append(f"| {domain} | `{spec_path}` |")
        openspec_table = "| Domain | Spec Path |\n|--------|----------|\n" + "\n".join(rows)
    else:
        openspec_table = "OpenSpec not configured for this project."

    # Build database commands string
    db_commands = testing.get("databaseCommands", [])
    db_commands_str = ", ".join(db_commands) if db_commands else "None"

    return {
        "{{projectName}}": config.get("projectName", "My Project"),
        "{{feature_name}}": feature_name,
        "{{session_name}}": session_name,
        "{{framework}}": tech.get("framework", ""),
        "{{language}}": tech.get("language", "TypeScript"),
        "{{database}}": tech.get("database", ""),
        "{{styling}}": tech.get("styling", ""),
        "{{packageManager}}": tech.get("packageManager", "npm"),
        "{{tech_stack_display}}": tech_stack_display,
        "{{lint_command}}": testing.get("lint", "npm run lint"),
        "{{build_command}}": testing.get("build", "npm run build"),
        "{{type_check_command}}": testing.get("typeCheck", "npx tsc --noEmit"),
        "{{ui_testing_tool}}": testing.get("uiTesting", "dev-browser"),
        "{{database_commands}}": db_commands_str,
        "{{openspec_enabled}}": str(openspec.get("enabled", False)),
        "{{openspec_domains_table}}": openspec_table,
        "{{date}}": datetime.now().strftime("%Y-%m-%d"),
        "{{timestamp}}": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def apply_variables(template: str, variables: Dict[str, str]) -> str:
    """将模板中的占位符替换为实际值"""
    result = template
    for key, value in variables.items():
        result = result.replace(key, value)
    return result


def generate_prd(variables: Dict[str, str]) -> str:
    """生成 PRD.md 模板"""
    template = """# {{feature_name}} - 产品需求文档 (PRD)

> **Project**: {{projectName}}
> **Session**: {{session_name}}
> **日期**: {{date}}
> **状态**: 规划中

---

## 1. 文档概述

### 1.1 背景


### 1.2 目标


### 1.3 范围

| 包含 | 不包含 |
|------|--------|
|      |        |

---

## 2. 用户流程



---

## 3. 功能需求



---

## 4. 非功能需求

### 4.1 性能要求

### 4.2 兼容性

---

## 5. 附录

### 5.1 术语表

| 术语 | 说明 |
|------|------|
|      |      |
"""
    return apply_variables(template, variables)


def generate_architecture(variables: Dict[str, str]) -> str:
    """生成 architecture.md 模板"""
    template = """# {{feature_name}} - System Architecture

> **Project**: {{projectName}}
> **Session**: {{session_name}}
> **日期**: {{date}}

---

## 1. Project Overview

### 1.1 Architecture Goals


### 1.2 Core Principles

- **组件复用**:
- **设计一致**:
- **渐进增强**:

---

## 2. Technology Stack

| Layer | Technology |
|-------|-----------|
| Framework | {{framework}} |
| Language | {{language}} |
| Database | {{database}} |
| Styling | {{styling}} |
| Package Manager | {{packageManager}} |

---

## 3. Application Architecture



---

## 4. Data Models



---

## 5. API Design



---

## 6. Development Workflow

Following auto-coding-agent-demo:
```
选择任务 → 加载规范 → 实现功能 → 测试验证 → 更新进度 → 提交变更
```

### Testing Commands

| Check | Command |
|-------|---------|
| Type Check | `{{type_check_command}}` |
| Lint | `{{lint_command}}` |
| Build | `{{build_command}}` |
| UI Testing | `{{ui_testing_tool}}` |

---

## 7. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
|      |        |            |
"""
    return apply_variables(template, variables)


def generate_task_json(config: Dict[str, Any], feature_name: str, session_name: str) -> str:
    """生成 task.json 模板"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    project_name = config.get("projectName", "My Project")

    task_content = {
        "project": f"{project_name} - {feature_name}",
        "description": "",
        "version": "1.0.0",
        "session": session_name,
        "meta": {
            "createdAt": timestamp,
            "lastUpdated": timestamp,
            "totalTasks": 0,
            "completedTasks": 0,
            "pendingTasks": 0,
        },
        "tasks": [],
    }
    return json.dumps(task_content, indent=2, ensure_ascii=False)


def generate_progress(variables: Dict[str, str]) -> str:
    """生成 progress.md 模板"""
    template = """# Progress - {{feature_name}}

> **Project**: {{projectName}}
> **Session**: {{session_name}}
> **Start**: {{timestamp}}
> **Status**: In Progress

---

## Testing Commands Reference

| Check | Command |
|-------|---------|
| Type Check | `{{type_check_command}}` |
| Lint | `{{lint_command}}` |
| Build | `{{build_command}}` |
| UI Testing | `{{ui_testing_tool}}` |

---

## Session Started

准备开始开发...

---
"""
    return apply_variables(template, variables)


def generate_files(config: Dict[str, Any], output_dir: str, feature_name: str) -> Dict[str, str]:
    """
    生成所有 session 文件

    Args:
        config: 项目配置
        output_dir: session 输出目录
        feature_name: 功能名称

    Returns:
        生成的文件路径字典
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    logs_path = output_path / "logs"
    logs_path.mkdir(exist_ok=True)

    session_name = output_path.name
    variables = build_variables(config, feature_name, session_name)

    files = {}

    # PRD.md
    prd_path = output_path / "PRD.md"
    prd_path.write_text(generate_prd(variables), encoding="utf-8")
    files["prd"] = str(prd_path)

    # architecture.md
    arch_path = output_path / "architecture.md"
    arch_path.write_text(generate_architecture(variables), encoding="utf-8")
    files["architecture"] = str(arch_path)

    # task.json
    task_path = output_path / "task.json"
    task_path.write_text(generate_task_json(config, feature_name, session_name), encoding="utf-8")
    files["task"] = str(task_path)

    # progress.md
    progress_path = output_path / "progress.md"
    progress_path.write_text(generate_progress(variables), encoding="utf-8")
    files["progress"] = str(progress_path)

    # automation.log
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    log_path = logs_path / "automation.log"
    log_path.write_text(f"# Automation Log - {session_name}\n\nStarted: {timestamp}\n\n", encoding="utf-8")
    files["automation_log"] = str(log_path)

    files["session_dir"] = str(output_path)
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Generate session template files from project config"
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to project config JSON file",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Path to session output directory",
    )
    parser.add_argument(
        "--feature-name",
        default="",
        help="Feature name (defaults to output directory name)",
    )
    args = parser.parse_args()

    try:
        # Load and merge config
        default_config = load_default_config()
        user_config = load_config(args.config)
        config = merge_configs(default_config, user_config)

        # Determine feature name
        feature_name = args.feature_name or Path(args.output_dir).name

        # Generate files
        files = generate_files(config, args.output_dir, feature_name)

        # Output result
        print(json.dumps(files, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

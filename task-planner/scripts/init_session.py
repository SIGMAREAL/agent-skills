#!/usr/bin/env python3
"""
Auto-Coding Session Initializer

自动创建开发 session 的目录结构和必需文件。
集成 detect_project.py（自动检测）和 generate_files.py（模板生成）。

配置加载优先级: project-config.json > 自动检测 > 默认配置

Usage:
    python init_session.py <project-root> <feature-name>
    python init_session.py <project-root> <feature-name> --generate-config
    python init_session.py <project-root> <feature-name> --init-openspec

Example:
    python init_session.py /path/to/my-project user-profile-v1
    python init_session.py /path/to/my-project auth-system --generate-config
    python init_session.py /path/to/my-project auth-system --init-openspec
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Import sibling scripts
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from detect_project import detect_project
from generate_files import generate_files, load_default_config, merge_configs
from setup_openspec import setup_openspec


def load_project_config(project_root: Path) -> Dict[str, Any]:
    """
    加载项目配置，按优先级: project-config.json > 自动检测 > 默认配置

    Args:
        project_root: 项目根目录路径

    Returns:
        合并后的配置字典
    """
    default_config = load_default_config()
    config_path = project_root / "auto-coding" / "project-config.json"

    if config_path.exists():
        # Priority 1: project-config.json exists, use it
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
        config = merge_configs(default_config, user_config)
        config["_source"] = "project-config.json"
    else:
        # Priority 2: Auto-detect from project
        try:
            detected_config = detect_project(str(project_root))
            config = merge_configs(default_config, detected_config)
            config["_source"] = "auto-detected"
        except Exception:
            # Priority 3: Fallback to default config
            config = default_config
            config["_source"] = "default"

    return config


def create_session(
    project_root: str,
    feature_name: str,
    generate_config: bool = False,
    init_openspec: bool = False,
) -> Dict[str, Any]:
    """
    创建 session 目录结构并生成所有文件

    Args:
        project_root: 项目根目录路径
        feature_name: 功能名称（kebab-case）
        generate_config: 是否保存检测到的配置到 project-config.json
        init_openspec: 是否初始化 OpenSpec 目录结构和 spec 模板

    Returns:
        包含所有文件路径和配置来源的字典
    """
    # Validate feature_name format (kebab-case)
    if not all(c.isalnum() or c in '-.' for c in feature_name):
        raise ValueError(f"Invalid feature name: {feature_name}. Use kebab-case (e.g., 'user-profile-v1')")

    project_path = Path(project_root).resolve()
    if not project_path.exists():
        raise FileNotFoundError(f"Project root not found: {project_root}")

    # Generate session directory name
    today = datetime.now().strftime("%Y-%m-%d")
    session_name = f"{today}-{feature_name}"

    # Session path
    session_path = project_path / "auto-coding" / "sessions" / session_name

    # Load config (priority: project-config.json > auto-detect > default)
    config = load_project_config(project_path)
    config_source = config.pop("_source", "unknown")

    # Optionally save config
    if generate_config:
        config_save_path = project_path / "auto-coding" / "project-config.json"
        config_save_path.parent.mkdir(parents=True, exist_ok=True)
        # Don't save _source field
        save_config = {k: v for k, v in config.items() if not k.startswith("_")}
        config_save_path.write_text(
            json.dumps(save_config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    # Generate all session files using generate_files.py
    files = generate_files(config, str(session_path), feature_name)

    # Create resources/ directory for raw input files (PRD docs, Figma data, etc.)
    resources_dir = session_path / "resources"
    resources_dir.mkdir(parents=True, exist_ok=True)
    resources_readme_content = (
        "# Session Resources\n\n"
        "将原始输入文件放入此目录：\n\n"
        "- `*.md` / `*.txt` — 原始 PRD、需求文档（可混乱，task-planner 会重新整理）\n"
        "- `figma-frames.json` — Figma MCP 节点数据（由 task-planner 规划阶段自动生成）\n\n"
        "**注意**: 此目录的文件不会直接放入 PRD.md，"
        "task-planner 会阅读后重新整理。\n"
    )
    (resources_dir / "README.md").write_text(resources_readme_content, encoding="utf-8")

    # Create resources/init.md template for capturing original user requirements
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    init_md_content = (
        f"# 原始需求\n\n"
        f"> **Session**: {session_name}\n"
        f"> **初始化时间**: {now}\n\n"
        f"---\n\n"
        f"## 用户原始输入\n\n"
        f"[在此粘贴用户的原始需求，包括所有细节和上下文]\n\n"
        f"## 补充材料\n\n"
        f"[相关参考资料、截图说明、链接等]\n"
    )
    init_md_path = resources_dir / "init.md"
    init_md_path.write_text(init_md_content, encoding="utf-8")

    files["resources_dir"] = str(resources_dir)
    files["init_md"] = str(init_md_path)

    # Add metadata
    files["config_source"] = config_source
    files["config"] = {
        "projectName": config.get("projectName", ""),
        "framework": config.get("techStack", {}).get("framework", ""),
        "packageManager": config.get("techStack", {}).get("packageManager", ""),
    }

    if generate_config:
        files["config_saved_to"] = str(config_save_path)

    # Optionally initialize OpenSpec
    if init_openspec:
        openspec_result = setup_openspec(
            str(project_path), config=config, force=False
        )
        files["openspec"] = openspec_result

    return files


def main():
    parser = argparse.ArgumentParser(
        description="Initialize auto-coding session with auto-detected project config"
    )
    parser.add_argument(
        "project_root",
        help="Path to the project root directory",
    )
    parser.add_argument(
        "feature_name",
        help="Feature name in kebab-case (e.g., 'user-profile-v1')",
    )
    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Save detected config to auto-coding/project-config.json",
    )
    parser.add_argument(
        "--init-openspec",
        action="store_true",
        help="Initialize OpenSpec directory structure and spec templates",
    )
    args = parser.parse_args()

    try:
        files = create_session(
            args.project_root,
            args.feature_name,
            args.generate_config,
            args.init_openspec,
        )

        # Output JSON (for Claude to parse)
        print(json.dumps(files, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

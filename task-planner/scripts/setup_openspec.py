#!/usr/bin/env python3
"""
OpenSpec Setup Script

为项目自动初始化 OpenSpec 目录结构和基础 spec 文件。
根据项目类型（检测到的框架和数据库）生成合适的模板。

仅在用户明确指定时才初始化，避免覆盖现有配置。

Usage:
    python setup_openspec.py <project-root>
    python setup_openspec.py <project-root> --force
    python setup_openspec.py <project-root> --config <config.json>

Examples:
    python setup_openspec.py /path/to/my-project
    python setup_openspec.py /path/to/my-project --force  # 覆盖现有配置
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import sibling scripts
SCRIPTS_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPTS_DIR.parent / "assets"
TEMPLATES_DIR = ASSETS_DIR / "openspec-templates"

sys.path.insert(0, str(SCRIPTS_DIR))


def check_openspec_exists(project_root: Path) -> bool:
    """检测项目中是否已有 openspec/ 目录"""
    openspec_dir = project_root / "openspec"
    return openspec_dir.exists() and (openspec_dir / "specs").exists()


def load_template(template_name: str) -> str:
    """加载 OpenSpec 模板文件"""
    template_path = TEMPLATES_DIR / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")


def get_applicable_specs(config: Dict[str, Any]) -> List[str]:
    """
    根据项目配置确定应该生成哪些 spec 模板

    Returns:
        模板文件名列表（不含扩展名）
    """
    specs = ["architecture"]  # 始终生成 architecture spec

    framework = config.get("techStack", {}).get("framework", "")
    database = config.get("techStack", {}).get("database", "")

    # 框架相关 spec
    framework_lower = framework.lower()
    if any(kw in framework_lower for kw in ["next", "nuxt", "remix", "sveltekit", "astro"]):
        # Full-stack frameworks: need both API and components
        specs.append("api")
        specs.append("components")
    elif any(kw in framework_lower for kw in ["express", "fastify"]):
        # Backend frameworks: API only
        specs.append("api")
    elif any(kw in framework_lower for kw in ["react", "vue", "angular", "svelte"]):
        # Frontend frameworks: components only
        specs.append("components")

    # 数据库相关 spec
    if database:
        specs.append("data-model")

    return specs


def apply_template_variables(content: str, config: Dict[str, Any]) -> str:
    """替换模板中的变量占位符"""
    project_name = config.get("projectName", "My Project")
    framework = config.get("techStack", {}).get("framework", "")
    language = config.get("techStack", {}).get("language", "TypeScript")
    database = config.get("techStack", {}).get("database", "")
    styling = config.get("techStack", {}).get("styling", "")
    date = datetime.now().strftime("%Y-%m-%d")

    replacements = {
        "{{projectName}}": project_name,
        "{{framework}}": framework or "N/A",
        "{{language}}": language or "N/A",
        "{{database}}": database or "N/A",
        "{{styling}}": styling or "N/A",
        "{{date}}": date,
    }

    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    return content


def create_openspec_structure(project_root: Path) -> List[str]:
    """
    创建 OpenSpec 目录结构

    Returns:
        创建的目录列表
    """
    dirs = [
        project_root / "openspec" / "specs",
        project_root / "openspec" / "changes" / "archive",
        project_root / "docs" / "guides",
    ]

    created = []
    for d in dirs:
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            created.append(str(d.relative_to(project_root)))

    return created


def generate_spec_templates(
    project_root: Path, config: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    根据项目类型生成 spec 模板文件

    Returns:
        生成的文件列表 [{path, domain}]
    """
    specs = get_applicable_specs(config)
    generated = []

    for spec_name in specs:
        spec_dir = project_root / "openspec" / "specs" / spec_name
        spec_file = spec_dir / "spec.md"

        # 不覆盖已有的 spec 文件
        if spec_file.exists():
            continue

        # 加载模板
        template_filename = f"{spec_name}.md"
        try:
            content = load_template(template_filename)
        except FileNotFoundError:
            # 如果没有对应模板，使用通用模板
            content = load_template("generic.md")
            content = content.replace("{{domain_name}}", spec_name)

        # 替换变量
        content = apply_template_variables(content, config)

        # 写入文件
        spec_dir.mkdir(parents=True, exist_ok=True)
        spec_file.write_text(content, encoding="utf-8")

        generated.append({
            "path": str(spec_file.relative_to(project_root)),
            "domain": spec_name,
        })

    return generated


def generate_readme(project_root: Path, config: Dict[str, Any]) -> Optional[str]:
    """
    生成 openspec/README.md

    Returns:
        README 文件的相对路径，如果已存在则返回 None
    """
    readme_path = project_root / "openspec" / "README.md"
    if readme_path.exists():
        return None

    try:
        content = load_template("README.md")
    except FileNotFoundError:
        # 内联 fallback
        content = _generate_fallback_readme(config)

    content = apply_template_variables(content, config)
    readme_path.write_text(content, encoding="utf-8")

    return str(readme_path.relative_to(project_root))


def _generate_fallback_readme(config: Dict[str, Any]) -> str:
    """生成 fallback README 内容"""
    return """# OpenSpec - {{projectName}}

> 规范驱动开发 (Specification-Driven Development)

## 目录结构

```
openspec/
├── README.md           # 本文件
├── specs/              # 规范文件
│   └── {domain}/
│       └── spec.md     # 域规范
└── changes/
    └── archive/        # 变更归档
```

## 使用方法

1. 在 `specs/` 下创建域规范
2. 使用 Gherkin 格式描述行为
3. 开发前先阅读相关 spec
4. 变更通过 `changes/` 追踪

详见: https://github.com/Fission-AI/OpenSpec
"""


def setup_openspec(
    project_root: str,
    config: Optional[Dict[str, Any]] = None,
    force: bool = False,
) -> Dict[str, Any]:
    """
    为项目初始化 OpenSpec 目录结构和基础 spec 文件

    Args:
        project_root: 项目根目录路径
        config: 项目配置（如果为 None，尝试自动检测）
        force: 是否强制初始化（覆盖现有配置）

    Returns:
        初始化结果字典
    """
    root = Path(project_root).resolve()
    if not root.exists():
        raise FileNotFoundError(f"Project root not found: {project_root}")

    # 检查是否已有 OpenSpec
    already_exists = check_openspec_exists(root)
    if already_exists and not force:
        return {
            "status": "skipped",
            "reason": "OpenSpec already exists. Use --force to reinitialize.",
            "openspec_dir": str(root / "openspec"),
        }

    # 加载配置
    if config is None:
        try:
            from detect_project import detect_project
            config = detect_project(project_root)
        except Exception:
            config = {
                "projectName": root.name.replace("-", " ").replace("_", " ").title(),
                "techStack": {},
            }

    # 创建目录结构
    created_dirs = create_openspec_structure(root)

    # 生成 spec 模板
    generated_specs = generate_spec_templates(root, config)

    # 生成 README
    readme_path = generate_readme(root, config)

    result = {
        "status": "initialized",
        "openspec_dir": str(root / "openspec"),
        "created_dirs": created_dirs,
        "generated_specs": generated_specs,
        "readme": readme_path,
        "already_existed": already_exists,
    }

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Initialize OpenSpec directory structure and spec templates"
    )
    parser.add_argument(
        "project_root",
        help="Path to the project root directory",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force initialization even if OpenSpec already exists",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to project config JSON file (optional, auto-detects if not provided)",
    )
    args = parser.parse_args()

    try:
        config = None
        if args.config:
            with open(args.config, "r", encoding="utf-8") as f:
                config = json.load(f)

        result = setup_openspec(args.project_root, config=config, force=args.force)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

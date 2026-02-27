#!/usr/bin/env python3
"""
Project Auto-Detector

自动检测项目技术栈、包管理器、测试命令等，返回与 project-config.json 兼容的 JSON 配置。

Usage:
    python detect_project.py <project-root>
    python detect_project.py <project-root> --pretty
    python detect_project.py <project-root> --save

Examples:
    python detect_project.py /path/to/my-project
    python detect_project.py /path/to/my-project --save   # 保存到 auto-coding/project-config.json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional


def detect_package_manager(project_root: Path) -> str:
    """检测包管理器（pnpm > yarn > npm）"""
    if (project_root / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (project_root / "yarn.lock").exists():
        return "yarn"
    if (project_root / "bun.lockb").exists():
        return "bun"
    # package-lock.json or fallback
    return "npm"


def load_package_json(project_root: Path) -> Optional[Dict[str, Any]]:
    """加载 package.json"""
    pkg_path = project_root / "package.json"
    if not pkg_path.exists():
        return None
    with open(pkg_path, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_framework(pkg: Dict[str, Any]) -> str:
    """从 dependencies/devDependencies 检测框架"""
    all_deps = {}
    all_deps.update(pkg.get("dependencies", {}))
    all_deps.update(pkg.get("devDependencies", {}))

    # Next.js
    if "next" in all_deps:
        version = all_deps["next"].lstrip("^~>=<")
        major = version.split(".")[0] if version else ""
        return f"Next.js {major}" if major else "Next.js"

    # Nuxt
    if "nuxt" in all_deps:
        version = all_deps["nuxt"].lstrip("^~>=<")
        major = version.split(".")[0] if version else ""
        return f"Nuxt {major}" if major else "Nuxt"

    # Vue
    if "vue" in all_deps:
        version = all_deps["vue"].lstrip("^~>=<")
        major = version.split(".")[0] if version else ""
        return f"Vue {major}" if major else "Vue"

    # Angular
    if "@angular/core" in all_deps:
        version = all_deps["@angular/core"].lstrip("^~>=<")
        major = version.split(".")[0] if version else ""
        return f"Angular {major}" if major else "Angular"

    # Svelte / SvelteKit
    if "@sveltejs/kit" in all_deps:
        return "SvelteKit"
    if "svelte" in all_deps:
        return "Svelte"

    # Remix
    if "@remix-run/react" in all_deps:
        return "Remix"

    # Astro
    if "astro" in all_deps:
        return "Astro"

    # Express
    if "express" in all_deps:
        return "Express"

    # Fastify
    if "fastify" in all_deps:
        return "Fastify"

    # React (standalone, after checking meta-frameworks)
    if "react" in all_deps:
        version = all_deps["react"].lstrip("^~>=<")
        major = version.split(".")[0] if version else ""
        return f"React {major}" if major else "React"

    return ""


def detect_language(project_root: Path, pkg: Dict[str, Any]) -> str:
    """检测编程语言"""
    all_deps = {}
    all_deps.update(pkg.get("dependencies", {}))
    all_deps.update(pkg.get("devDependencies", {}))

    if "typescript" in all_deps or (project_root / "tsconfig.json").exists():
        return "TypeScript"

    # Check for Flow
    if (project_root / ".flowconfig").exists():
        return "Flow"

    return "JavaScript"


def detect_database(pkg: Dict[str, Any], project_root: Path) -> str:
    """检测数据库和 ORM"""
    all_deps = {}
    all_deps.update(pkg.get("dependencies", {}))
    all_deps.update(pkg.get("devDependencies", {}))

    parts: List[str] = []

    # Detect ORM / database client
    if "prisma" in all_deps or "@prisma/client" in all_deps:
        # Try to detect database type from schema.prisma
        db_type = _detect_prisma_provider(project_root)
        if db_type:
            parts.append(f"{db_type} (Prisma)")
        else:
            parts.append("Prisma")
    elif "drizzle-orm" in all_deps:
        parts.append("Drizzle ORM")
    elif "typeorm" in all_deps:
        parts.append("TypeORM")
    elif "sequelize" in all_deps:
        parts.append("Sequelize")
    elif "mongoose" in all_deps:
        parts.append("MongoDB (Mongoose)")
    elif "mongodb" in all_deps:
        parts.append("MongoDB")

    # Detect Supabase
    if "@supabase/supabase-js" in all_deps:
        parts.append("Supabase")

    # Detect Firebase
    if "firebase" in all_deps or "firebase-admin" in all_deps:
        if not parts:
            parts.append("Firebase")

    return " + ".join(parts) if parts else ""


def _detect_prisma_provider(project_root: Path) -> str:
    """从 schema.prisma 的 datasource 块检测数据库 provider"""
    schema_path = project_root / "prisma" / "schema.prisma"
    if not schema_path.exists():
        return ""

    try:
        content = schema_path.read_text(encoding="utf-8")
        # Only look for provider inside datasource block
        in_datasource = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("datasource "):
                in_datasource = True
                continue
            if in_datasource and stripped == "}":
                break
            if in_datasource and stripped.startswith("provider") and "=" in stripped:
                value = stripped.split("=", 1)[1].strip().strip('"').strip("'")
                provider_map = {
                    "postgresql": "PostgreSQL",
                    "postgres": "PostgreSQL",
                    "mysql": "MySQL",
                    "sqlite": "SQLite",
                    "sqlserver": "SQL Server",
                    "mongodb": "MongoDB",
                    "cockroachdb": "CockroachDB",
                }
                return provider_map.get(value, "")
    except Exception:
        pass
    return ""


def detect_styling(pkg: Dict[str, Any]) -> str:
    """检测 CSS/样式方案"""
    all_deps = {}
    all_deps.update(pkg.get("dependencies", {}))
    all_deps.update(pkg.get("devDependencies", {}))

    parts: List[str] = []

    if "tailwindcss" in all_deps:
        parts.append("Tailwind CSS")
    if "styled-components" in all_deps:
        parts.append("styled-components")
    if "@emotion/react" in all_deps or "@emotion/styled" in all_deps:
        parts.append("Emotion")
    if "@chakra-ui/react" in all_deps:
        parts.append("Chakra UI")
    if "@mantine/core" in all_deps:
        parts.append("Mantine")
    if "@mui/material" in all_deps:
        parts.append("Material UI")
    if "sass" in all_deps or "node-sass" in all_deps:
        parts.append("Sass")

    return " + ".join(parts) if parts else ""


def detect_testing_commands(pkg: Dict[str, Any], package_manager: str, language: str) -> Dict[str, Any]:
    """检测测试相关命令"""
    scripts = pkg.get("scripts", {})
    all_deps = {}
    all_deps.update(pkg.get("dependencies", {}))
    all_deps.update(pkg.get("devDependencies", {}))

    run_cmd = f"{package_manager} run" if package_manager != "npm" else "npm run"
    # pnpm allows shorthand: pnpm lint instead of pnpm run lint
    if package_manager == "pnpm":
        run_cmd = "pnpm"

    # Type check
    type_check = ""
    if language == "TypeScript":
        if "vue" in all_deps or "nuxt" in all_deps:
            type_check = "vue-tsc --noEmit"
        else:
            type_check = "npx tsc --noEmit"

    # Lint
    lint = ""
    if "lint" in scripts:
        lint = f"{run_cmd} lint"
    elif "eslint" in scripts:
        lint = f"{run_cmd} eslint"

    # Build
    build = ""
    if "build" in scripts:
        build = f"{run_cmd} build"

    # UI testing - default to dev-browser
    ui_testing = "dev-browser"

    # Database commands
    db_commands: List[str] = []
    if "prisma" in all_deps or "@prisma/client" in all_deps:
        db_commands.append("prisma generate")
    if "db:generate" in scripts:
        pass  # Already covered by prisma generate
    if "db:push" in scripts:
        db_commands.append(f"{run_cmd} db:push")

    return {
        "typeCheck": type_check,
        "lint": lint,
        "build": build,
        "uiTesting": ui_testing,
        "databaseCommands": db_commands,
    }


def detect_openspec(project_root: Path) -> Dict[str, Any]:
    """扫描 OpenSpec 目录结构"""
    openspec_root = project_root / "openspec"
    if not openspec_root.exists():
        return {"enabled": False, "domains": {}}

    specs_dir = openspec_root / "specs"
    if not specs_dir.exists():
        return {"enabled": True, "domains": {}}

    domains: Dict[str, str] = {}
    for spec_dir in sorted(specs_dir.iterdir()):
        if spec_dir.is_dir():
            spec_file = spec_dir / "spec.md"
            if spec_file.exists():
                # Use relative path from project root
                rel_path = spec_file.relative_to(project_root)
                domains[spec_dir.name] = str(rel_path)

    return {
        "enabled": True,
        "domains": domains,
    }


def detect_project_name(pkg: Optional[Dict[str, Any]], project_root: Path) -> str:
    """检测项目名称"""
    if pkg:
        name = pkg.get("name", "")
        if name:
            # Convert kebab-case to Title Case for display
            return name.replace("-", " ").replace("_", " ").title()
    return project_root.name.replace("-", " ").replace("_", " ").title()


def detect_project(project_root: str) -> Dict[str, Any]:
    """
    自动检测项目配置

    Args:
        project_root: 项目根目录路径

    Returns:
        与 project-config.json 兼容的配置字典
    """
    root = Path(project_root).resolve()
    if not root.exists():
        raise FileNotFoundError(f"Project root not found: {project_root}")

    # Load package.json
    pkg = load_package_json(root)

    # Detect package manager first (needed by other detectors)
    package_manager = detect_package_manager(root)

    if pkg:
        framework = detect_framework(pkg)
        language = detect_language(root, pkg)
        database = detect_database(pkg, root)
        styling = detect_styling(pkg)
        testing = detect_testing_commands(pkg, package_manager, language)
        project_name = detect_project_name(pkg, root)
    else:
        framework = ""
        language = ""
        database = ""
        styling = ""
        testing = {
            "typeCheck": "",
            "lint": "",
            "build": "",
            "uiTesting": "dev-browser",
            "databaseCommands": [],
        }
        project_name = detect_project_name(None, root)

    # Detect OpenSpec
    openspec = detect_openspec(root)

    config = {
        "projectName": project_name,
        "techStack": {
            "framework": framework,
            "language": language,
            "database": database,
            "styling": styling,
            "packageManager": package_manager,
        },
        "testing": testing,
        "openspec": openspec,
        "templates": {
            "enabled": True,
            "customTemplates": [],
        },
    }

    return config


def main():
    parser = argparse.ArgumentParser(
        description="Auto-detect project tech stack and generate compatible config"
    )
    parser.add_argument(
        "project_root",
        help="Path to the project root directory",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (default: compact)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save detected config to auto-coding/project-config.json",
    )
    args = parser.parse_args()

    try:
        config = detect_project(args.project_root)

        indent = 2 if args.pretty else None
        output = json.dumps(config, indent=indent, ensure_ascii=False)

        if args.save:
            save_path = Path(args.project_root) / "auto-coding" / "project-config.json"
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_text(
                json.dumps(config, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(json.dumps({
                "config": config,
                "saved_to": str(save_path),
            }, indent=2, ensure_ascii=False))
        else:
            print(output)

    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

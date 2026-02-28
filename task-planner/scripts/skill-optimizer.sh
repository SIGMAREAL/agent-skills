#!/bin/bash
# =============================================================================
# skill-optimizer.sh - Session 回顾与 Skill 改进建议生成器
# =============================================================================
# 本脚本在 session 完成后自动收集数据，调用 Claude 分析 skill 使用中的问题，
# 生成结构化改进建议文件，帮助 skill 持续进化。
#
# 使用方法: skill-optimizer.sh <project-root> [session-dir]
# 示例:
#   skill-optimizer.sh /path/to/project
#   skill-optimizer.sh /path/to/project auto-coding/sessions/2026-02-28-feature
#
# 环境变量:
#   CLAUDE_CMD      - Claude CLI 命令（默认: claude）
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Defaults from environment
CLAUDE_CMD="${CLAUDE_CMD:-claude}"

# =============================================================================
# Argument parsing
# =============================================================================

PROJECT_ROOT=""
SESSION_DIR=""

print_usage() {
    echo "Usage: $0 <project-root> [session-dir]"
    echo ""
    echo "Arguments:"
    echo "  project-root   项目根目录路径（必须）"
    echo "  session-dir    Session 目录路径（可选，默认自动检测最新）"
    echo ""
    echo "Examples:"
    echo "  $0 /path/to/project"
    echo "  $0 /path/to/project auto-coding/sessions/2026-02-28-feature"
    echo ""
    echo "Environment Variables:"
    echo "  CLAUDE_CMD       Claude CLI 命令（默认: claude）"
}

if [ -z "$1" ]; then
    echo -e "${RED}[ERROR]${NC} 缺少 project-root 参数"
    print_usage
    exit 1
fi

PROJECT_ROOT="$(cd "$1" && pwd)"

if [ ! -d "$PROJECT_ROOT" ]; then
    echo -e "${RED}[ERROR]${NC} 项目目录不存在: $1"
    exit 1
fi

# Parse session path
if [ -n "$2" ]; then
    if [[ "$2" = /* ]]; then
        SESSION_DIR="$2"
    else
        SESSION_DIR="$PROJECT_ROOT/$2"
    fi
else
    # Auto-detect latest session
    if [ -d "$PROJECT_ROOT/auto-coding/sessions" ]; then
        SESSION_DIR=$(ls -dt "$PROJECT_ROOT/auto-coding/sessions"/*/ 2>/dev/null | head -1 | sed 's:/*$::')
        if [ -z "$SESSION_DIR" ]; then
            echo -e "${RED}[ERROR]${NC} 没有找到 auto-coding/sessions 目录下的 session"
            echo "请提供 session 路径"
            exit 1
        fi
        echo -e "${BLUE}[INFO]${NC} 自动检测到最新 session: $SESSION_DIR"
    else
        echo -e "${RED}[ERROR]${NC} auto-coding/sessions 目录不存在"
        exit 1
    fi
fi

# Validate session directory
if [ ! -d "$SESSION_DIR" ]; then
    echo -e "${RED}[ERROR]${NC} Session 目录不存在: $SESSION_DIR"
    exit 1
fi

if [ ! -f "$SESSION_DIR/task.json" ]; then
    echo -e "${RED}[ERROR]${NC} task.json 不存在: $SESSION_DIR/task.json"
    exit 1
fi

log() {
    local level=$1
    local message=$2

    case $level in
        INFO)
            echo -e "${BLUE}[INFO]${NC} ${message}"
            ;;
        SUCCESS)
            echo -e "${GREEN}[SUCCESS]${NC} ${message}"
            ;;
        WARNING)
            echo -e "${YELLOW}[WARNING]${NC} ${message}"
            ;;
        ERROR)
            echo -e "${RED}[ERROR]${NC} ${message}"
            ;;
    esac
}

# =============================================================================
# Data collection
# =============================================================================

log INFO "开始收集 session 数据..."

SESSION_NAME=$(basename "$SESSION_DIR")
TASK_JSON="$SESSION_DIR/task.json"
PROGRESS_FILE="$SESSION_DIR/progress.md"
INIT_MD="$SESSION_DIR/resources/init.md"
LOG_DIR="$SESSION_DIR/logs"

# Collect progress.md content
PROGRESS_CONTENT=""
if [ -f "$PROGRESS_FILE" ]; then
    PROGRESS_CONTENT=$(cat "$PROGRESS_FILE")
    log INFO "已读取 progress.md ($(wc -l < "$PROGRESS_FILE") 行)"
else
    log WARNING "progress.md 不存在"
fi

# Collect task.json statistics
TASK_STATS=""
if command -v python3 &> /dev/null; then
    TASK_STATS=$(python3 -c "
import json, sys
with open('$TASK_JSON', 'r') as f:
    data = json.load(f)
    total = len(data.get('tasks', []))
    completed = sum(1 for t in data.get('tasks', []) if t.get('passes', False))
    blocked = sum(1 for t in data.get('tasks', []) if not t.get('passes', False))
    print(f'总任务数: {total}, 已完成: {completed}, 阻塞/失败: {blocked}')
" 2>&1)
    log INFO "任务统计: $TASK_STATS"
else
    log WARNING "无法统计 task.json（需要 python3）"
fi

# Collect latest log tail
LATEST_LOG=""
if [ -d "$LOG_DIR" ]; then
    LATEST_LOG_FILE=$(ls -t "$LOG_DIR"/*.log 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG_FILE" ]; then
        LATEST_LOG=$(tail -50 "$LATEST_LOG_FILE")
        log INFO "已读取最新日志末尾 50 行: $(basename "$LATEST_LOG_FILE")"
    fi
fi

# Collect init.md if exists
INIT_CONTENT=""
if [ -f "$INIT_MD" ]; then
    INIT_CONTENT=$(cat "$INIT_MD")
    log INFO "已读取 resources/init.md"
fi

# =============================================================================
# Build analysis prompt
# =============================================================================

log INFO "构建 Claude 分析提示词..."

PROMPT="你是 task-planner skill 的改进分析专家。请根据以下 session 执行数据，分析 skill 使用过程中出现的问题，并提出改进建议。

## Session 信息
- **Session 名称**: $SESSION_NAME
- **任务统计**: $TASK_STATS

## 原始需求（init.md）
\`\`\`
$INIT_CONTENT
\`\`\`

## 执行进度（progress.md）
\`\`\`
$PROGRESS_CONTENT
\`\`\`

## 最新日志（末尾 50 行）
\`\`\`
$LATEST_LOG
\`\`\`

---

## 分析要求

请按以下固定格式输出分析结果：

# Skill 改进分析 - $SESSION_NAME

## 出现的问题
[列出在 session 执行过程中遇到的具体问题，如：提示词理解错误、脚本执行失败、缺少必要指引等]

## 提示词歧义点
[指出 SKILL.md 中哪些描述可能导致 AI 误解或多种解读，需要更明确的表达]

## 可脚本化的工作
[识别哪些重复性、确定性的工作可以用脚本自动化，而不是每次让 AI 重新编写]

## 建议改进
[具体的改进建议，分为以下三个子类别]

### SKILL.md 改动
[具体需要修改 SKILL.md 的哪些章节，如何修改]

### 新增/修改脚本
[建议新增或修改哪些脚本文件，实现什么功能]

### 新增 reference
[是否需要新增 references/ 下的文档，包含哪些详细信息]

---

请保持分析客观、具体、可执行。如果某个分类没有内容，请写 '无'。"

# =============================================================================
# Ensure skill-improvements directory exists
# =============================================================================

IMPROVEMENTS_DIR="$SKILL_DIR/skill-improvements"
mkdir -p "$IMPROVEMENTS_DIR"

# =============================================================================
# Call Claude to analyze
# =============================================================================

OUTPUT_DATE=$(date +%Y-%m-%d)
OUTPUT_FILE="$IMPROVEMENTS_DIR/${OUTPUT_DATE}-${SESSION_NAME}.md"

log INFO "调用 Claude 进行分析..."

if ! $CLAUDE_CMD -p --dangerously-skip-permissions "$PROMPT" > "$OUTPUT_FILE" 2>&1; then
    log ERROR "Claude 调用失败"
    exit 1
fi

log SUCCESS "分析完成！输出文件: $OUTPUT_FILE"
echo -e "${CYAN}查看结果:${NC} cat $OUTPUT_FILE"

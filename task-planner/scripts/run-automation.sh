#!/bin/bash
# =============================================================================
# run-automation.sh - 通用全自动任务执行脚本（Session 版）
# =============================================================================
# 本脚本实现无人干预的连续任务执行，支持 auto-coding session 目录。
# 与具体项目解耦，通过 project-config.json 获取项目特定配置。
#
# 使用方法: run-automation.sh <project-root> [session路径] [运行次数]
# 示例:
#   run-automation.sh /path/to/project auto-coding/sessions/2026-02-26-feature 5
#   run-automation.sh /path/to/project auto-coding/sessions/2026-02-26-feature
#   run-automation.sh /path/to/project   (自动检测最新session)
#
# 环境变量:
#   CLAUDE_CMD      - Claude CLI 命令（默认: claude）
#   SKIP_INIT       - 跳过初始化脚本（默认: false）
#   CLEANUP_BROWSER - 是否清理浏览器进程（默认: true）
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
SKIP_INIT="${SKIP_INIT:-false}"
CLEANUP_BROWSER="${CLEANUP_BROWSER:-true}"

# =============================================================================
# Argument parsing
# =============================================================================

PROJECT_ROOT=""
SESSION_DIR=""
TOTAL_RUNS=""

print_usage() {
    echo "Usage: $0 <project-root> [session-path] [run-count]"
    echo ""
    echo "Arguments:"
    echo "  project-root   项目根目录路径（必须）"
    echo "  session-path   Session 目录路径（可选，相对于 project-root 或绝对路径）"
    echo "  run-count      运行次数（可选，默认无限）"
    echo ""
    echo "Examples:"
    echo "  $0 /path/to/project"
    echo "  $0 /path/to/project auto-coding/sessions/2026-02-26-feature"
    echo "  $0 /path/to/project auto-coding/sessions/2026-02-26-feature 5"
    echo ""
    echo "Environment Variables:"
    echo "  CLAUDE_CMD       Claude CLI 命令（默认: claude）"
    echo "  SKIP_INIT        跳过初始化脚本（默认: false）"
    echo "  CLEANUP_BROWSER  是否清理浏览器进程（默认: true）"
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

# Change to project root
cd "$PROJECT_ROOT"

# Parse session path
if [ -n "$2" ] && ! [[ "$2" =~ ^[0-9]+$ ]]; then
    # Second arg is a session path
    if [[ "$2" = /* ]]; then
        SESSION_DIR="$2"
    else
        SESSION_DIR="$PROJECT_ROOT/$2"
    fi
    if [ -n "$3" ]; then
        TOTAL_RUNS="$3"
    else
        TOTAL_RUNS="unlimited"
    fi
elif [ -n "$2" ] && [[ "$2" =~ ^[0-9]+$ ]]; then
    # Second arg is a number (run count), auto-detect session
    TOTAL_RUNS="$2"
else
    TOTAL_RUNS="unlimited"
fi

# Auto-detect session if not provided
if [ -z "$SESSION_DIR" ]; then
    if [ -d "auto-coding/sessions" ]; then
        SESSION_DIR=$(ls -dt auto-coding/sessions/*/ 2>/dev/null | head -1 | sed 's:/*$::')
        if [ -z "$SESSION_DIR" ]; then
            echo -e "${RED}[ERROR]${NC} 没有找到 auto-coding/sessions 目录下的 session"
            echo "请提供 session 路径"
            exit 1
        fi
        # Make absolute
        SESSION_DIR="$PROJECT_ROOT/$SESSION_DIR"
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

# =============================================================================
# Setup paths and logging
# =============================================================================

TASK_JSON="$SESSION_DIR/task.json"
PROGRESS_FILE="$SESSION_DIR/progress.md"
LOG_DIR="$SESSION_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/automation-$(date +%Y%m%d_%H%M%S).log"

# Load project config (optional)
PROJECT_CONFIG="$PROJECT_ROOT/auto-coding/project-config.json"
PROJECT_NAME="$(basename "$PROJECT_ROOT")"
INIT_SCRIPT=""

if [ -f "$PROJECT_CONFIG" ]; then
    # Try to extract project name from config
    if command -v python3 &> /dev/null; then
        PROJECT_NAME=$(python3 -c "
import json, sys
try:
    with open('$PROJECT_CONFIG') as f:
        config = json.load(f)
    print(config.get('projectName', '$PROJECT_NAME'))
except:
    print('$PROJECT_NAME')
" 2>/dev/null || echo "$PROJECT_NAME")
    fi
fi

# Detect init script
if [ -f "./init.sh" ]; then
    INIT_SCRIPT="./init.sh"
elif [ -f "./setup.sh" ]; then
    INIT_SCRIPT="./setup.sh"
fi

# =============================================================================
# Utility functions
# =============================================================================

log() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" >> "$LOG_FILE"

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
        PROGRESS)
            echo -e "${CYAN}[PROGRESS]${NC} ${message}"
            ;;
    esac
}

count_remaining_tasks() {
    if [ -f "$TASK_JSON" ]; then
        local count=$(grep -c '"passes": false' "$TASK_JSON" 2>/dev/null || echo "0")
        echo "$count"
    else
        echo "0"
    fi
}

# Clean up browser processes left by dev-browser/playwright testing
# IMPORTANT: This runs AFTER log writing is complete to avoid interfering with output
cleanup_browsers() {
    if [ "$CLEANUP_BROWSER" != "true" ]; then
        return
    fi

    log "INFO" "清理测试浏览器进程..."

    # Kill dev-browser server by exact path match
    if pgrep -f "\.claude/skills/dev-browser/server\.sh" > /dev/null 2>&1; then
        pkill -f "\.claude/skills/dev-browser/server\.sh" 2>/dev/null || true
        log "INFO" "已终止 dev-browser server"
    fi

    # Kill Chromium processes ONLY if they contain playwright AND chromium in path
    if pgrep -f "playwright.*chromium" > /dev/null 2>&1; then
        pkill -f "playwright.*chromium" 2>/dev/null || true
        log "INFO" "已终止 Playwright Chromium 进程"
    fi

    # Kill Chrome processes ONLY if they're clearly from Playwright
    if pgrep -f "chrome.*--enable-automation.*playwright" > /dev/null 2>&1; then
        pkill -f "chrome.*--enable-automation.*playwright" 2>/dev/null || true
        log "INFO" "已终止 Playwright Chrome 进程"
    fi

    # Clean up old screenshot files (more than 1 day old)
    if [ -d "$HOME/.claude/skills/dev-browser/tmp" ]; then
        find "$HOME/.claude/skills/dev-browser/tmp" -name "*.png" -mtime +1 -delete 2>/dev/null || true
    fi

    log "INFO" "浏览器清理完成"
}

# =============================================================================
# Main execution
# =============================================================================

# Banner
echo ""
echo "========================================"
echo "  Auto-Coding - 全自动任务执行器"
echo "  Project: $PROJECT_NAME"
echo "========================================"
echo ""

log "INFO" "Project: $PROJECT_ROOT"
log "INFO" "Session: $SESSION_DIR"
log "INFO" "Task JSON: $TASK_JSON"
log "INFO" "Progress: $PROGRESS_FILE"
log "INFO" "日志文件: $LOG_FILE"

# Initialize environment
echo ""
log "PROGRESS" "Step 1: 初始化环境..."
if [ "$SKIP_INIT" != "true" ] && [ -n "$INIT_SCRIPT" ]; then
    $INIT_SCRIPT || {
        log "ERROR" "初始化失败: $INIT_SCRIPT"
        exit 1
    }
elif [ "$SKIP_INIT" = "true" ]; then
    log "INFO" "跳过初始化（SKIP_INIT=true）"
else
    log "WARNING" "没有找到初始化脚本（init.sh 或 setup.sh），跳过初始化"
fi

# Display run mode
if [ "$TOTAL_RUNS" = "unlimited" ]; then
    log "INFO" "模式: 执行所有任务直到完成"
else
    log "INFO" "模式: 执行 $TOTAL_RUNS 个任务"
fi

# Initial task count
INITIAL_TASKS=$(count_remaining_tasks)
log "INFO" "初始待完成任务数: $INITIAL_TASKS"

if [ "$INITIAL_TASKS" -eq 0 ]; then
    log "SUCCESS" "✅ 所有任务已完成！"
    exit 0
fi

# Make relative paths for prompt (cleaner output)
REL_SESSION_DIR=$(python3 -c "
import os
print(os.path.relpath('$SESSION_DIR', '$PROJECT_ROOT'))
" 2>/dev/null || basename "$SESSION_DIR")

REL_TASK_JSON="$REL_SESSION_DIR/task.json"
REL_PROGRESS="$REL_SESSION_DIR/progress.md"

# Main loop
current_run=0
while true; do
    current_run=$((current_run + 1))

    # Check if we've reached the limit
    if [ "$TOTAL_RUNS" != "unlimited" ] && [ $current_run -gt $TOTAL_RUNS ]; then
        log "SUCCESS" "✅ 已达到指定运行次数 ($TOTAL_RUNS)"
        break
    fi

    echo ""
    echo "========================================"
    log "PROGRESS" "任务 #$current_run"
    echo "========================================"

    # Check remaining tasks
    REMAINING=$(count_remaining_tasks)

    if [ "$REMAINING" -eq 0 ]; then
        log "SUCCESS" "✅ 所有任务已完成！"
        break
    fi

    log "INFO" "剩余任务数: $REMAINING"

    # Create prompt file for this run
    PROMPT_FILE=$(mktemp)
    cat > "$PROMPT_FILE" << PROMPT_EOF
你正在运行 ${PROJECT_NAME} 全自动工作流。

请严格按照 CLAUDE.md 中的 "全自动 Agent 工作流" 执行：

1. **Step 1**: 环境应该已初始化（由 run-automation.sh 完成）
2. **Step 2**: 读取 ${REL_TASK_JSON}，选择下一个 \`passes: false\` 的任务，并阅读其 \`relatedSpecs\` 中的 OpenSpec 规范
3. **Step 3**: 实现任务（严格遵循规范）
4. **Step 4**: 测试验证（pnpm lint + pnpm build + 浏览器测试如果需要）
5. **Step 5**: 更新 ${REL_PROGRESS}
6. **Step 6**: 提交所有变更（代码 + progress.md + task.json），使用 Co-authored-by

**重要规则**：
- 只完成一个任务
- 如果遇到阻塞（需要人工决策、API 密钥缺失等），停止并清晰报告
- 所有测试通过后才标记 task.json 的 passes 为 true
- 使用 git commit -m "..." -m "Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>"

完成后报告：
- 完成的任务 ID 和标题
- 修改的文件列表
- 测试结果
- 是否成功提交
PROMPT_EOF

    # Run Claude with the prompt
    log "INFO" "启动 Claude Code 执行任务..."

    if command -v "$CLAUDE_CMD" &> /dev/null; then
        if "$CLAUDE_CMD" -p --dangerously-skip-permissions < "$PROMPT_FILE" 2>&1 | tee -a "$LOG_FILE"; then
            log "SUCCESS" "任务 #$current_run 完成"
        else
            log "WARNING" "任务 #$current_run 异常退出，代码 $?"
        fi
    else
        log "ERROR" "Claude Code CLI 未安装（命令: $CLAUDE_CMD）"
        rm -f "$PROMPT_FILE"
        exit 1
    fi

    # Clean up
    rm -f "$PROMPT_FILE"

    # Check remaining after this run
    REMAINING_AFTER=$(count_remaining_tasks)
    COMPLETED=$((REMAINING - REMAINING_AFTER))

    if [ "$COMPLETED" -gt 0 ]; then
        log "SUCCESS" "本任务完成，剩余 $REMAINING_AFTER 个任务"
    else
        log "WARNING" "没有检测到任务完成，可能遇到阻塞"
    fi

    # Add separator in log BEFORE cleanup to ensure log is complete
    echo "" >> "$LOG_FILE"
    echo "----------------------------------------" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"

    # Clean up browser processes after each task
    cleanup_browsers

    # Small delay between runs
    if [ "$REMAINING_AFTER" -gt 0 ]; then
        log "INFO" "等待 3 秒后继续下一个任务..."
        sleep 3
    fi
done

# Final summary
echo ""
echo "========================================"
log "SUCCESS" "🏁 自动化执行完成！"
echo "========================================"

FINAL_REMAINING=$(count_remaining_tasks)
TOTAL_COMPLETED=$((INITIAL_TASKS - FINAL_REMAINING))

log "INFO" "执行统计:"
log "INFO" "  - 项目: $PROJECT_NAME"
log "INFO" "  - 总运行次数: $current_run"
log "INFO" "  - 完成任务数: $TOTAL_COMPLETED"
log "INFO" "  - 剩余任务数: $FINAL_REMAINING"
log "INFO" "  - 日志文件: $LOG_FILE"

if [ "$FINAL_REMAINING" -eq 0 ]; then
    log "SUCCESS" "🎉 所有任务已顺利完成！"
else
    log "WARNING" "⏸️  还有 $FINAL_REMAINING 个任务待完成"
    log "INFO" "运行 $0 $PROJECT_ROOT $SESSION_DIR 继续执行"
fi

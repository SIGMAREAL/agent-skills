#!/bin/bash
# =============================================================================
# run-branch-parallel.sh - 多分支并行开发脚本（task-planner skill）
# =============================================================================
# 支持同时在多个 git 分支上并行开发不同 session，使用 git worktree
# 隔离各分支工作区，监控所有进程并输出汇总报告
#
# 使用方法: run-branch-parallel.sh <project-root> <session1:branch1> [<session2:branch2> ...]
# 示例:
#   run-branch-parallel.sh /path/to/project auto-coding/sessions/2026-02-28-feature-a:feature-a
#   run-branch-parallel.sh /path/to-project \
#       auto-coding/sessions/2026-02-28-feature-a:feature-a \
#       auto-coding/sessions/2026-02-28-feature-b:feature-b
#
# 参数说明:
#   project-root    项目根目录路径（必须）
#   session:branch  Session 路径和分支名对，用冒号分隔（至少需要1对）
#
# 环境变量:
#   CLAUDE_CMD  - Claude CLI 命令（默认: claude）
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# =============================================================================
# Defaults
# =============================================================================

CLAUDE_CMD="${CLAUDE_CMD:-claude}"
SKILL_SCRIPT="$SCRIPT_DIR/run-automation.sh"

# =============================================================================
# Logging
# =============================================================================

log() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case $level in
        INFO)    echo -e "${BLUE}[INFO]${NC} ${message}" >&2 ;;
        SUCCESS) echo -e "${GREEN}[SUCCESS]${NC} ${message}" >&2 ;;
        WARNING) echo -e "${YELLOW}[WARNING]${NC} ${message}" >&2 ;;
        ERROR)   echo -e "${RED}[ERROR]${NC} ${message}" >&2 ;;
        BRANCH)  echo -e "${MAGENTA}[BRANCH]${NC} ${message}" >&2 ;;
        STATUS)  echo -e "${CYAN}[STATUS]${NC} ${message}" >&2 ;;
    esac
}

# =============================================================================
# Argument parsing
# =============================================================================

print_usage() {
    echo "Usage: $0 <project-root> <session1:branch1> [<session2:branch2> ...]"
    echo ""
    echo "Arguments:"
    echo "  project-root    项目根目录路径（必须）"
    echo "  session:branch  Session 路径和分支名对（至少需要1对）"
    echo ""
    echo "示例:"
    echo "  $0 /path/to/project auto-coding/sessions/2026-02-28-feature-a:feature-a"
    echo "  $0 /path/to/project \\"
    echo "      auto-coding/sessions/2026-02-28-feature-a:feature-a \\"
    echo "      auto-coding/sessions/2026-02-28-feature-b:feature-b"
    echo ""
    echo "说明:"
    echo "  - 每个分支使用独立的 git worktree 隔离工作区"
    echo "  - 分支不存在时会自动创建"
    echo "  - worktree 位置: <project-root>/.claude/worktrees/<branch-name>"
    echo "  - 执行完成后可使用: git worktree remove .claude/worktrees/<branch-name>"
    echo ""
    echo "环境变量:"
    echo "  CLAUDE_CMD  Claude CLI 命令（默认: claude）"
}

if [ -z "$1" ]; then
    log "ERROR" "缺少 project-root 参数"
    print_usage
    exit 1
fi

PROJECT_ROOT="$(cd "$1" && pwd)"
if [ ! -d "$PROJECT_ROOT" ]; then
    log "ERROR" "项目目录不存在: $1"
    exit 1
fi

# Verify it's a git repository
if ! git -C "$PROJECT_ROOT" status >/dev/null 2>&1; then
    log "ERROR" "不是有效的 git 仓库: $PROJECT_ROOT"
    exit 1
fi

shift

# Parse session:branch pairs
if [ $# -lt 1 ]; then
    log "ERROR" "至少需要一个 session:branch 对"
    print_usage
    exit 1
fi

declare -a SESSION_BRANCHES
declare -a SESSION_NAMES
declare -a BRANCH_NAMES
declare -a WORKTREE_PATHS
declare -a PIDS
declare -a LOG_FILES

for pair in "$@"; do
    IFS=: read -r session branch <<< "$pair"
    if [ -z "$session" ] || [ -z "$branch" ]; then
        log "ERROR" "无效的 session:branch 格式: $pair"
        exit 1
    fi

    # Resolve session path
    if [[ "$session" = /* ]]; then
        SESSION_DIR="$session"
    else
        SESSION_DIR="$PROJECT_ROOT/$session"
    fi

    if [ ! -d "$SESSION_DIR" ]; then
        log "ERROR" "Session 目录不存在: $SESSION_DIR"
        exit 1
    fi

    TASK_JSON="$SESSION_DIR/task.json"
    if [ ! -f "$TASK_JSON" ]; then
        log "ERROR" "task.json 不存在: $TASK_JSON"
        exit 1
    fi

    # Check if branch exists, create if not
    if ! git -C "$PROJECT_ROOT" branch --list "$branch" | grep -q "$branch"; then
        log "INFO" "创建新分支: $branch"
        git -C "$PROJECT_ROOT" branch "$branch"
    fi

    # Create safe branch name (replace / with -)
    BRANCH_SAFE="${branch//\//-}"

    # Create worktree if not exists
    WORKTREE_DIR="$PROJECT_ROOT/.claude/worktrees/$BRANCH_SAFE"
    if [ ! -d "$WORKTREE_DIR" ]; then
        log "INFO" "创建 worktree: $WORKTREE_DIR (branch: $branch)"
        mkdir -p "$PROJECT_ROOT/.claude"
        git -C "$PROJECT_ROOT" worktree add "$WORKTREE_DIR" "$branch" 2>/dev/null || true
    fi

    # Store info
    SESSION_BRANCHES+=("$pair")
    SESSION_NAMES+=("$SESSION_DIR")
    BRANCH_NAMES+=("$branch")
    WORKTREE_PATHS+=("$WORKTREE_DIR")
done

log "INFO" "共 ${#SESSION_BRANCHES[@]} 个分支准备并行执行"
for i in "${!SESSION_BRANCHES[@]}"; do
    log "INFO" "  [$((i+1))] ${BRANCH_NAMES[$i]} <- ${SESSION_NAMES[$i]}"
done

# =============================================================================
# Execute sessions in parallel
# =============================================================================

# Create logs directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_BASE_DIR="$PROJECT_ROOT/.claude/logs/branch-parallel-$TIMESTAMP"
mkdir -p "$LOG_BASE_DIR"

for i in "${!SESSION_BRANCHES[@]}"; do
    BRANCH="${BRANCH_NAMES[$i]}"
    SESSION_DIR="${SESSION_NAMES[$i]}"
    WORKTREE_DIR="${WORKTREE_PATHS[$i]}"
    LOG_FILE="$LOG_BASE_DIR/branch-${BRANCH//\//--}.log"

    LOG_FILES+=("$LOG_FILE")

    log "INFO" "启动分支 $BRANCH (worktree: $WORKTREE_DIR)"

    # Run in background
    (
        cd "$WORKTREE_DIR"
        bash "$SKILL_SCRIPT" "$WORKTREE_DIR" "$SESSION_DIR" > "$LOG_FILE" 2>&1
        echo $? > "$LOG_FILE.exitcode"
    ) &

    PIDS+=($!)
done

# =============================================================================
# Monitor processes
# =============================================================================

log "INFO" "所有分支已启动，开始监控..."
echo ""

while true; do
    # Check status of all PIDs
    local still_running=()
    local completed_count=0

    for i in "${!PIDS[@]}"; do
        local pid="${PIDS[$i]}"
        local branch="${BRANCH_NAMES[$i]}"

        if kill -0 "$pid" 2>/dev/null; then
            still_running+=("$i")
        else
            ((completed_count++)) || true
        fi
    done

    local total=${#PIDS[@]}
    log "STATUS" "活跃: ${#still_running[@]}/$total"

    # Check if all completed
    if [ ${#still_running[@]} -eq 0 ]; then
        break
    fi

    sleep 10
done

# Wait for all processes to finish completely
wait "${PIDS[@]}" 2>/dev/null || true

echo ""
log "INFO" "所有分支执行完成"

# =============================================================================
# Collect results
# =============================================================================

echo ""
log "INFO" "========================================"
log "INFO" "汇总报告"
log "INFO" "========================================"

for i in "${!SESSION_BRANCHES[@]}"; do
    BRANCH="${BRANCH_NAMES[$i]}"
    SESSION_DIR="${SESSION_NAMES[$i]}"
    WORKTREE_DIR="${WORKTREE_PATHS[$i]}"
    LOG_FILE="${LOG_FILES[$i]}"
    EXIT_CODE_FILE="$LOG_FILE.exitcode"

    # Get exit code
    EXIT_CODE=0
    if [ -f "$EXIT_CODE_FILE" ]; then
        EXIT_CODE=$(cat "$EXIT_CODE_FILE")
    fi

    # Read task.json stats
    TOTAL=$(python3 -c "
import json
try:
    with open('$SESSION_DIR/task.json') as f:
        data = json.load(f)
    print(data.get('meta', {}).get('totalTasks', 0))
except:
    print(0)
" 2>/dev/null || echo "0")

    COMPLETED=$(python3 -c "
import json
try:
    with open('$SESSION_DIR/task.json') as f:
        data = json.load(f)
    print(data.get('meta', {}).get('completedTasks', 0))
except:
    print(0)
" 2>/dev/null || echo "0")

    if [ "$EXIT_CODE" -eq 0 ]; then
        log "SUCCESS" "[$BRANCH] 完成: $COMPLETED/$TOTAL 任务"
    else
        log "ERROR" "[$BRANCH] 异常 (exit=$EXIT_CODE): $COMPLETED/$TOTAL 任务"
        echo "  日志: $LOG_FILE"
    fi
done

echo ""
log "INFO" "========================================"
log "INFO" "清理 worktree（可选）"
log "INFO" "========================================"
echo "执行以下命令清理 worktree："
for i in "${!SESSION_BRANCHES[@]}"; do
    BRANCH="${BRANCH_NAMES[$i]}"
    BRANCH_SAFE="${BRANCH//\//-}"
    echo "  git -C $PROJECT_ROOT worktree remove .claude/worktrees/$BRANCH_SAFE"
done
echo "或者删除全部："
echo "  rm -rf $PROJECT_ROOT/.claude/worktrees"

echo ""
log "INFO" "日志目录: $LOG_BASE_DIR"

# Exit with error if any branch failed
for i in "${!SESSION_BRANCHES[@]}"; do
    LOG_FILE="${LOG_FILES[$i]}"
    EXIT_CODE_FILE="$LOG_FILE.exitcode"
    if [ -f "$EXIT_CODE_FILE" ]; then
        EXIT_CODE=$(cat "$EXIT_CODE_FILE")
        if [ "$EXIT_CODE" -ne 0 ]; then
            exit "$EXIT_CODE"
        fi
    fi
done

exit 0

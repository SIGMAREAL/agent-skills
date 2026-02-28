#!/bin/bash
# =============================================================================
# run-parallel.sh - 并行执行版自动化任务脚本（task-planner skill）
# =============================================================================
# 读取 task.json，按 phase 顺序执行任务：
#   - parallel: false → 顺序执行（一个接一个）
#   - parallel: true  → 并行执行（实时检测内存，动态调整并发数）
#
# 使用方法: run-parallel.sh <project-root> [session路径] [max-batch-size]
# 示例:
#   run-parallel.sh /path/to/project                                           # 自动检测最新 session，最大并发=3
#   run-parallel.sh /path/to/project auto-coding/sessions/2026-02-27-feature   # 指定 session
#   run-parallel.sh /path/to/project auto-coding/sessions/2026-02-27-feature 4 # 最大并发=4
#
# 内存动态调整策略（macOS vm_stat）：
#   可用内存 >= 8GB  → 使用 MAX_BATCH_SIZE
#   可用内存 4~8GB   → 使用 MAX_BATCH_SIZE / 2（最少1）
#   可用内存 2~4GB   → 固定 1（顺序）
#   可用内存 < 2GB   → 暂停等待，直到内存恢复
#
# 环境变量:
#   CLAUDE_CMD      - Claude CLI 命令（默认: claude）
#   MAX_BATCH_SIZE  - 最大并发数上限（默认: 3，也可作为第3参数传入）
#   MEM_PAUSE_GB    - 低于此值暂停（默认: 2）
#   MEM_SINGLE_GB   - 低于此值限为1并发（默认: 4）
#   MEM_FULL_GB     - 高于此值使用最大并发（默认: 8）
#   CLEANUP_BROWSER - 是否清理浏览器进程（默认: true）
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
CLEANUP_BROWSER="${CLEANUP_BROWSER:-true}"
MEM_PAUSE_GB="${MEM_PAUSE_GB:-2}"
MEM_SINGLE_GB="${MEM_SINGLE_GB:-4}"
MEM_FULL_GB="${MEM_FULL_GB:-8}"

# =============================================================================
# Argument parsing
# =============================================================================

print_usage() {
    echo "Usage: $0 <project-root> [session-path] [max-batch-size]"
    echo ""
    echo "Arguments:"
    echo "  project-root     项目根目录路径（必须）"
    echo "  session-path     Session 路径（可选，相对或绝对路径）"
    echo "  max-batch-size   最大并发数（可选，默认 3）"
    echo ""
    echo "Environment Variables:"
    echo "  CLAUDE_CMD       Claude CLI 命令（默认: claude）"
    echo "  MAX_BATCH_SIZE   最大并发上限（默认: 3）"
    echo "  MEM_PAUSE_GB     内存低于此值暂停 GB（默认: 2）"
    echo "  MEM_SINGLE_GB    内存低于此值串行 GB（默认: 4）"
    echo "  MEM_FULL_GB      内存高于此值全速 GB（默认: 8）"
    echo "  CLEANUP_BROWSER  清理浏览器进程（默认: true）"
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

SESSION_ARG="$2"
MAX_BATCH_SIZE_ARG="$3"

# Set MAX_BATCH_SIZE: env var > 3rd arg > default 3
if [ -n "$MAX_BATCH_SIZE_ARG" ] && [[ "$MAX_BATCH_SIZE_ARG" =~ ^[0-9]+$ ]]; then
    MAX_BATCH_SIZE="$MAX_BATCH_SIZE_ARG"
elif [ -n "${MAX_BATCH_SIZE}" ] && [[ "${MAX_BATCH_SIZE}" =~ ^[0-9]+$ ]]; then
    MAX_BATCH_SIZE="${MAX_BATCH_SIZE}"
else
    MAX_BATCH_SIZE=3
fi

# Resolve session directory
if [ -n "$SESSION_ARG" ]; then
    if [[ "$SESSION_ARG" = /* ]]; then
        SESSION_DIR="$SESSION_ARG"
    else
        SESSION_DIR="$PROJECT_ROOT/$SESSION_ARG"
    fi
else
    # Auto-detect latest session
    if [ -d "$PROJECT_ROOT/auto-coding/sessions" ]; then
        SESSION_DIR=$(ls -dt "$PROJECT_ROOT/auto-coding/sessions"/*/ 2>/dev/null | head -1 | sed 's:/*$::')
        if [ -z "$SESSION_DIR" ]; then
            echo -e "${RED}[ERROR]${NC} auto-coding/sessions 目录下没有找到 session"
            exit 1
        fi
        echo -e "${BLUE}[INFO]${NC} 自动检测到最新 session: $SESSION_DIR"
    else
        echo -e "${RED}[ERROR]${NC} auto-coding/sessions 目录不存在"
        exit 1
    fi
fi

if [ ! -d "$SESSION_DIR" ]; then
    echo -e "${RED}[ERROR]${NC} Session 目录不存在: $SESSION_DIR"
    exit 1
fi

TASK_JSON="$SESSION_DIR/task.json"
PROGRESS_FILE="$SESSION_DIR/progress.md"
LOG_DIR="$SESSION_DIR/logs"
mkdir -p "$LOG_DIR"
MAIN_LOG="$LOG_DIR/parallel-$(date +%Y%m%d_%H%M%S).log"

if [ ! -f "$TASK_JSON" ]; then
    echo -e "${RED}[ERROR]${NC} task.json 不存在: $TASK_JSON"
    exit 1
fi

# Relative paths for prompts (relative to project root)
REL_TASK_JSON=$(python3 -c "
import os
print(os.path.relpath('$TASK_JSON', '$PROJECT_ROOT'))
")
REL_PROGRESS=$(python3 -c "
import os
print(os.path.relpath('$PROGRESS_FILE', '$PROJECT_ROOT'))
")

# Session name for commit messages
SESSION_NAME="$(basename "$SESSION_DIR")"

# Project name from config or directory name
PROJECT_NAME="$(basename "$PROJECT_ROOT")"
PROJECT_CONFIG="$PROJECT_ROOT/auto-coding/project-config.json"
if [ -f "$PROJECT_CONFIG" ]; then
    PROJECT_NAME=$(python3 -c "
import json
try:
    with open('$PROJECT_CONFIG') as f:
        config = json.load(f)
    print(config.get('projectName', '$PROJECT_NAME'))
except:
    print('$PROJECT_NAME')
" 2>/dev/null || echo "$PROJECT_NAME")
fi

cd "$PROJECT_ROOT"

# =============================================================================
# Logging
# =============================================================================

log() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" >> "$MAIN_LOG"

    case $level in
        INFO)    echo -e "${BLUE}[INFO]${NC} ${message}" >&2 ;;
        SUCCESS) echo -e "${GREEN}[SUCCESS]${NC} ${message}" >&2 ;;
        WARNING) echo -e "${YELLOW}[WARNING]${NC} ${message}" >&2 ;;
        ERROR)   echo -e "${RED}[ERROR]${NC} ${message}" >&2 ;;
        PHASE)   echo -e "${MAGENTA}[PHASE]${NC} ${message}" >&2 ;;
        BATCH)   echo -e "${CYAN}[BATCH]${NC} ${message}" >&2 ;;
    esac
}

# =============================================================================
# Memory monitoring (macOS)
# =============================================================================

get_free_mem_gb() {
    local page_size
    page_size=$(pagesize 2>/dev/null || echo 4096)
    local free_pages
    free_pages=$(vm_stat 2>/dev/null | awk '
        /Pages free/        { gsub(/\./,"",$3); free+=$3 }
        /Pages inactive/    { gsub(/\./,"",$3); free+=$3 }
        END { print free }
    ')
    if [ -z "$free_pages" ] || [ "$free_pages" -eq 0 ]; then
        echo 99  # 无法检测时保守返回大值
        return
    fi
    python3 -c "print(int($free_pages * $page_size / 1024 / 1024 / 1024))"
}

calc_batch_size() {
    local free_gb
    free_gb=$(get_free_mem_gb)
    local result

    if [ "$free_gb" -ge "$MEM_FULL_GB" ]; then
        result=$MAX_BATCH_SIZE
        log "INFO" "  内存充足 (${free_gb}GB 可用) → 并发 ${result}"
    elif [ "$free_gb" -ge "$MEM_SINGLE_GB" ]; then
        result=$(( MAX_BATCH_SIZE / 2 ))
        [ "$result" -lt 1 ] && result=1
        log "WARNING" "  内存偏低 (${free_gb}GB 可用) → 降至并发 ${result}"
    elif [ "$free_gb" -ge "$MEM_PAUSE_GB" ]; then
        result=1
        log "WARNING" "  内存紧张 (${free_gb}GB 可用) → 强制串行 (并发=1)"
    else
        result=0
        log "ERROR" "  内存严重不足 (${free_gb}GB 可用，阈值 ${MEM_PAUSE_GB}GB) → 暂停"
    fi
    echo "$result"
}

wait_for_memory() {
    local wait_secs=30
    local total_waited=0
    local max_wait=300
    while true; do
        local free_gb
        free_gb=$(get_free_mem_gb)
        if [ "$free_gb" -ge "$MEM_PAUSE_GB" ]; then
            break
        fi
        log "WARNING" "  内存不足 (${free_gb}GB)，等待 ${wait_secs}s 后重试... (已等 ${total_waited}s)"
        sleep "$wait_secs"
        total_waited=$((total_waited + wait_secs))
        if [ "$total_waited" -ge "$max_wait" ]; then
            log "ERROR" "  等待超时 (${max_wait}s)，强制继续（并发=1）"
            break
        fi
    done
}

# =============================================================================
# Task utilities
# =============================================================================

get_phase_tasks() {
    local phase=$1
    local parallel_filter=$2  # "true", "false", or "any"

    python3 << PYEOF
import json
with open('$TASK_JSON') as f:
    data = json.load(f)

tasks = data.get('tasks', [])
result = []
for t in tasks:
    if t.get('passes', False):
        continue
    if t.get('phase', 1) != $phase:
        continue
    p = str(t.get('parallel', False)).lower()
    if '$parallel_filter' == 'any':
        result.append(t['id'])
    elif '$parallel_filter' == 'true' and p == 'true':
        result.append(t['id'])
    elif '$parallel_filter' == 'false' and p == 'false':
        result.append(t['id'])

print(' '.join(result))
PYEOF
}

get_task_info() {
    local task_id=$1
    python3 << PYEOF
import json
with open('$TASK_JSON') as f:
    data = json.load(f)
for t in data.get('tasks', []):
    if t['id'] == '$task_id':
        title = t.get('title', '')
        desc = t.get('description', '')
        print(f"{title}|||{desc}")
        break
PYEOF
}

is_task_done() {
    local task_id=$1
    python3 -c "
import json
with open('$TASK_JSON') as f:
    data = json.load(f)
for t in data.get('tasks', []):
    if t['id'] == '$task_id':
        print('true' if t.get('passes', False) else 'false')
        break
" 2>/dev/null || echo "false"
}

count_remaining() {
    python3 -c "
import json
with open('$TASK_JSON') as f:
    data = json.load(f)
print(sum(1 for t in data.get('tasks', []) if not t.get('passes', False)))
" 2>/dev/null || echo "0"
}

# 获取 task.json 中所有未完成任务的 phase 值（升序去重）
get_all_phases() {
    python3 -c "
import json
with open('$TASK_JSON') as f:
    data = json.load(f)
phases = sorted(set(t.get('phase', 1) for t in data.get('tasks', []) if not t.get('passes', False)))
print(' '.join(str(p) for p in phases))
" 2>/dev/null || echo "1"
}

sync_meta() {
    python3 << PYEOF
import json, datetime
with open('$TASK_JSON') as f:
    data = json.load(f)
tasks = data.get('tasks', [])
completed = sum(1 for t in tasks if t.get('passes', False))
data['meta']['completedTasks'] = completed
data['meta']['pendingTasks'] = len(tasks) - completed
data['meta']['lastUpdated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
with open('$TASK_JSON', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
PYEOF
}

# =============================================================================
# Browser cleanup
# =============================================================================

cleanup_browsers() {
    if [ "$CLEANUP_BROWSER" != "true" ]; then return; fi
    if pgrep -f "\.claude/skills/dev-browser/server\.sh" > /dev/null 2>&1; then
        pkill -f "\.claude/skills/dev-browser/server\.sh" 2>/dev/null || true
    fi
    if pgrep -f "playwright.*chromium" > /dev/null 2>&1; then
        pkill -f "playwright.*chromium" 2>/dev/null || true
    fi
}

# =============================================================================
# Run a single task (sequential / foreground)
# =============================================================================

run_task_sequential() {
    local task_id=$1
    local task_info=$(get_task_info "$task_id")
    local task_title=$(echo "$task_info" | cut -d'|' -f1)

    log "INFO" "▶ 顺序执行任务: $task_id - $task_title"

    PROMPT_FILE=$(mktemp)
    cat > "$PROMPT_FILE" << PROMPT_EOF
你正在运行 ${PROJECT_NAME} 自动化工作流。请执行以下特定任务：

**任务 ID**: ${task_id}
**任务标题**: ${task_title}

请读取 ${REL_TASK_JSON} 中 id 为 "${task_id}" 的任务的完整 steps 字段，按步骤严格执行。

执行规则：
1. 严格按照任务 steps 中每个步骤执行（步骤中有 git commit 才提交，否则不提交）
2. 所有测试通过后将 ${REL_TASK_JSON} 中此任务的 passes 设为 true
3. 在 ${REL_PROGRESS} 中**追加**完成记录（不覆盖，使用 ## 标题 + 日期）
4. 如遇阻塞（环境问题、API 缺失等），在 progress.md 记录阻塞原因并停止

完成后报告：任务 ID、修改的文件列表、测试结果。
PROMPT_EOF

    local task_log="$LOG_DIR/task-${task_id}-$(date +%H%M%S).log"
    if "$CLAUDE_CMD" -p --dangerously-skip-permissions < "$PROMPT_FILE" 2>&1 | tee -a "$task_log" >> "$MAIN_LOG"; then
        log "SUCCESS" "✅ 任务完成: $task_id"
        sync_meta
    else
        log "WARNING" "⚠️  任务异常退出: $task_id (exit code $?)"
    fi
    rm -f "$PROMPT_FILE"
    cleanup_browsers
}

# =============================================================================
# Run a task in background (parallel)
# =============================================================================

run_task_background() {
    local task_id=$1
    local task_info=$(get_task_info "$task_id")
    local task_title=$(echo "$task_info" | cut -d'|' -f1)

    log "INFO" "  ⚡ 后台启动: $task_id - $task_title"

    PROMPT_FILE=$(mktemp)
    cat > "$PROMPT_FILE" << PROMPT_EOF
你正在运行 ${PROJECT_NAME} 自动化工作流。请执行以下特定任务：

**任务 ID**: ${task_id}
**任务标题**: ${task_title}

请读取 ${REL_TASK_JSON} 中 id 为 "${task_id}" 的任务的完整 steps 字段，按步骤严格执行。

执行规则：
1. 严格按照任务 steps 中每个步骤执行
2. 注意：steps 中明确说明 **不要执行 git commit** 的并行任务，请跳过 git commit 步骤
3. 所有步骤完成后将 ${REL_TASK_JSON} 中此任务的 passes 设为 true
4. 在 ${REL_PROGRESS} 中**追加**完成记录（每个任务用 ## 标题 + 任务 ID 区分，不覆盖其他任务记录）
5. 如遇阻塞，在 progress.md 记录阻塞原因并停止

完成后输出：TASK_DONE: ${task_id}
PROMPT_EOF

    local task_log="$LOG_DIR/task-${task_id}-$(date +%H%M%S).log"
    (
        "$CLAUDE_CMD" -p --dangerously-skip-permissions "$(cat "$PROMPT_FILE")" \
            > "$task_log" 2>&1
        rm -f "$PROMPT_FILE"
    ) &
    local bg_pid=$!
    echo "$bg_pid"
}

# =============================================================================
# Dynamic process pool for parallel tasks
# =============================================================================

run_parallel_dynamic() {
    local phase=$1
    shift
    local all_tasks=("$@")
    local total=${#all_tasks[@]}
    local next_idx=0
    local active_pids=()
    local completed=0
    local failed_tasks=()

    log "INFO" "Phase ${phase} 进程池模式：共 ${total} 个任务，最大并发 ${MAX_BATCH_SIZE}"
    log "INFO" "内存阈值: 暂停<${MEM_PAUSE_GB}GB / 串行<${MEM_SINGLE_GB}GB / 全速>=${MEM_FULL_GB}GB"

    while true; do
        # 收割已完成的进程
        local still_running=()
        for entry in "${active_pids[@]}"; do
            local pid="${entry%%:*}"
            local tid="${entry##*:}"
            if kill -0 "$pid" 2>/dev/null; then
                still_running+=("$entry")
            else
                wait "$pid" 2>/dev/null && rc=0 || rc=$?
                if [ "$rc" -eq 0 ]; then
                    log "SUCCESS" "✅ 完成: $tid  [活跃: $((${#still_running[@]})) / 剩余: $((total - next_idx))]"
                    sync_meta
                else
                    log "WARNING" "⚠️  异常退出: $tid (rc=$rc)"
                    failed_tasks+=("$tid")
                fi
                ((completed++)) || true
            fi
        done
        active_pids=("${still_running[@]}")

        # 检查是否全部完成
        if [ ${#active_pids[@]} -eq 0 ] && [ "$next_idx" -ge "$total" ]; then
            break
        fi

        # 检测内存，确定当前允许的并发上限
        wait_for_memory
        local cur_max
        cur_max=$(calc_batch_size)
        [ "$cur_max" -lt 1 ] && cur_max=1

        # 补充新任务，直到达到并发上限或任务耗尽
        while [ ${#active_pids[@]} -lt "$cur_max" ] && [ "$next_idx" -lt "$total" ]; do
            local task_id="${all_tasks[$next_idx]}"
            ((next_idx++)) || true

            local pid
            pid=$(run_task_background "$task_id")
            active_pids+=("$pid:$task_id")
            log "INFO" "⚡ 启动: $task_id  [活跃: ${#active_pids[@]}/${cur_max}  已完成: ${completed}/${total}]"
            sleep 1
        done

        sleep 3
    done

    cleanup_browsers

    if [ ${#failed_tasks[@]} -gt 0 ]; then
        log "WARNING" "Phase ${phase} 异常任务: ${failed_tasks[*]}"
    fi
    log "INFO" "Phase ${phase} 进程池完成，共执行 ${completed} 个任务"
}

# =============================================================================
# Process a phase
# =============================================================================

process_phase() {
    local phase=$1
    local phase_name=${2:-"Phase $phase"}

    log "PHASE" "========================================"
    log "PHASE" "Phase ${phase}: ${phase_name}"
    log "PHASE" "========================================"

    # 顺序任务
    local seq_tasks_str=$(get_phase_tasks "$phase" "false")
    if [ -n "$seq_tasks_str" ]; then
        log "INFO" "Phase ${phase} 顺序任务: $seq_tasks_str"
        for task_id in $seq_tasks_str; do
            if [ "$(is_task_done "$task_id")" = "true" ]; then
                log "INFO" "  跳过已完成: $task_id"
                continue
            fi
            run_task_sequential "$task_id"
        done
    else
        log "INFO" "Phase ${phase} 无顺序任务"
    fi

    # 并行任务
    local par_tasks_str=$(get_phase_tasks "$phase" "true")
    if [ -n "$par_tasks_str" ]; then
        local par_tasks=()
        for task_id in $par_tasks_str; do
            if [ "$(is_task_done "$task_id")" = "true" ]; then
                log "INFO" "  跳过已完成: $task_id"
                continue
            fi
            par_tasks+=("$task_id")
        done

        if [ ${#par_tasks[@]} -gt 0 ]; then
            run_parallel_dynamic "$phase" "${par_tasks[@]}"
        else
            log "INFO" "Phase ${phase} 所有并行任务已完成"
        fi
    else
        log "INFO" "Phase ${phase} 无并行任务"
    fi
}

# =============================================================================
# Batch git commit after a phase
# =============================================================================

do_batch_commit() {
    local phase=$1
    log "INFO" "Phase ${phase} 批量提交已修改的文件..."
    if git -C "$PROJECT_ROOT" diff --quiet && git -C "$PROJECT_ROOT" diff --cached --quiet; then
        log "INFO" "  没有待提交的修改，跳过"
        return
    fi
    git -C "$PROJECT_ROOT" add -A
    git -C "$PROJECT_ROOT" commit \
        -m "[$SESSION_NAME] Phase ${phase} 批量提交 - batch commit" \
        -m "Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>" \
        2>&1 | tee -a "$MAIN_LOG" || true
    log "SUCCESS" "Phase ${phase} 批量提交完成"
}

# =============================================================================
# Main
# =============================================================================

echo ""
echo -e "${MAGENTA}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║  Auto-Coding Parallel Runner                                ║${NC}"
echo -e "${MAGENTA}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
log "INFO" "项目: $PROJECT_NAME"
log "INFO" "Session: $SESSION_DIR"
log "INFO" "task.json: $REL_TASK_JSON"
log "INFO" "最大并发: $MAX_BATCH_SIZE（实际并发由内存动态决定）"
log "INFO" "内存策略: 暂停<${MEM_PAUSE_GB}GB / 串行<${MEM_SINGLE_GB}GB / 全速>=${MEM_FULL_GB}GB"
log "INFO" "日志: $MAIN_LOG"
echo ""

REMAINING=$(count_remaining)
log "INFO" "待执行任务数: $REMAINING"
echo ""

if [ "$REMAINING" -eq 0 ]; then
    log "SUCCESS" "所有任务已完成！"
    exit 0
fi

# 动态检测所有 phase，按顺序执行
ALL_PHASES=$(get_all_phases)
log "INFO" "检测到 phases: $ALL_PHASES"

for phase in $ALL_PHASES; do
    process_phase "$phase"
    do_batch_commit "$phase"
done

echo ""
REMAINING_FINAL=$(count_remaining)
if [ "$REMAINING_FINAL" -eq 0 ]; then
    log "SUCCESS" "🎉 所有任务完成！Session: $SESSION_NAME"
else
    log "WARNING" "⚠️  仍有 $REMAINING_FINAL 个任务未完成，请检查日志: $MAIN_LOG"
fi
echo ""

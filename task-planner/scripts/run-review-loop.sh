#!/bin/bash
# =============================================================================
# run-review-loop.sh - 自驱项目改进闭环
# =============================================================================
# 实现完整的自驱改进闭环：
# 1. inbox/ 接收用户随时投入的需求材料
# 2. PM Agent 扮演产品经理整合分析
# 3. 自动创建并执行 session
# 4. Result Reviewer 评估结果
# 5. 支持循环迭代
#
# 使用方法: run-review-loop.sh <project-root> [--auto] [--cycles N]
# 示例:
#   run-review-loop.sh /path/to/project              # 手动模式，处理一个 session 后停止
#   run-review-loop.sh /path/to/project --auto       # 自动模式，按 config.json 配置循环
#   run-review-loop.sh /path/to/project --auto --cycles 5
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

# Log function
log() {
    echo -e "${CYAN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $*"
}

# Defaults
CLAUDE_CMD="${CLAUDE_CMD:-claude}"

# =============================================================================
# Argument parsing
# =============================================================================

PROJECT_ROOT=""
AUTO_MODE=false
MAX_CYCLES=""

print_usage() {
    echo "Usage: $0 <project-root> [--auto] [--cycles N]"
    echo ""
    echo "Arguments:"
    echo "  project-root   项目根目录路径（必须）"
    echo "  --auto         自动模式，按配置循环执行"
    echo "  --cycles N     最大循环次数（覆盖 config.json）"
    echo ""
    echo "Examples:"
    echo "  $0 /path/to/project"
    echo "  $0 /path/to/project --auto"
    echo "  $0 /path/to/project --auto --cycles 5"
    echo ""
    echo "Environment Variables:"
    echo "  CLAUDE_CMD       Claude CLI 命令（默认: claude）"
}

# Check for --help first
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    print_usage
    exit 0
fi

if [ -z "$1" ]; then
    echo -e "${RED}[ERROR]${NC} 缺少 project-root 参数"
    print_usage
    exit 1
fi

PROJECT_ROOT="$(cd "$1" && pwd)"
shift

# Parse options
while [ $# -gt 0 ]; do
    case "$1" in
        --auto)
            AUTO_MODE=true
            shift
            ;;
        --cycles)
            if [ -z "$2" ] || ! [[ "$2" =~ ^[0-9]+$ ]]; then
                echo -e "${RED}[ERROR]${NC} --cycles 需要一个数字参数"
                exit 1
            fi
            MAX_CYCLES="$2"
            shift 2
            ;;
        --help)
            print_usage
            exit 0
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} 未知参数: $1"
            print_usage
            exit 1
            ;;
    esac
done

if [ ! -d "$PROJECT_ROOT" ]; then
    echo -e "${RED}[ERROR]${NC} 项目目录不存在: $PROJECT_ROOT"
    exit 1
fi

# =============================================================================
# Configuration
# =============================================================================

CONFIG_FILE="$PROJECT_ROOT/auto-coding/review-loop/config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}[ERROR]${NC} 配置文件不存在: $CONFIG_FILE"
    echo "请先创建 auto-coding/review-loop/config.json"
    exit 1
fi

log "读取配置: $CONFIG_FILE"

# Parse config using python
CONFIG_MODE=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['mode'])")
CONFIG_MAX_LOOPS=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['maxAutoLoops'])")
CONFIG_CODEBASE=$(python3 -c "import json; print(' '.join(json.load(open('$CONFIG_FILE'))['focus']['codebase']))")
CONFIG_SESSION_LIMIT=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['focus']['sessionHistoryLimit'])")
CONFIG_RUNNER=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['runner'])")
CONFIG_MAX_TASKS=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['maxTasksPerSession'])")
CONFIG_PAUSE=$(python3 -c "import json; print(str(json.load(open('$CONFIG_FILE'))['pauseForReview']).lower())")

# Override with command line
if [ -n "$MAX_CYCLES" ]; then
    CONFIG_MAX_LOOPS="$MAX_CYCLES"
fi

if [ "$AUTO_MODE" = true ]; then
    CONFIG_MODE="auto"
fi

log "模式: $CONFIG_MODE, 最大循环: $CONFIG_MAX_LOOPS"

# =============================================================================
# Main Loop
# =============================================================================

CYCLE_NUM=1

# Determine next cycle number
HISTORY_DIR="$PROJECT_ROOT/auto-coding/review-loop/history"
mkdir -p "$HISTORY_DIR"

if [ -d "$HISTORY_DIR" ]; then
    LAST_CYCLE=$(find "$HISTORY_DIR" -maxdepth 1 -type d -name "????-??-??-???" | sort | tail -1 | xargs basename | grep -oE '[0-9]{3}$' || echo "000")
    CYCLE_NUM=$((10#$LAST_CYCLE + 1))
fi

CYCLE_NUM_PADDED=$(printf "%03d" $CYCLE_NUM)

while true; do
    log "${GREEN}========================================${NC}"
    log "${GREEN}开始 Cycle $CYCLE_NUM_PADDED${NC}"
    log "${GREEN}========================================${NC}"

    # Create cycle directory
    DATE_PREFIX=$(date '+%Y-%m-%d')
    CYCLE_DIR="$HISTORY_DIR/$DATE_PREFIX-$CYCLE_NUM_PADDED"
    mkdir -p "$CYCLE_DIR"

    log "Cycle 目录: $CYCLE_DIR"

    # =============================================================================
    # Step 1: Collect context
    # =============================================================================

    log "${BLUE}[1/7]${NC} 收集上下文..."

    # Collect inbox files
    INBOX_DIR="$PROJECT_ROOT/auto-coding/inbox"
    INBOX_FILES=$(find "$INBOX_DIR" -maxdepth 1 -type f \( -name "*.md" -o -name "*.txt" \) 2>/dev/null || true)
    INBOX_COUNT=$(echo "$INBOX_FILES" | grep -c . || echo 0)

    log "Inbox 未处理文件: $INBOX_COUNT"

    if [ "$INBOX_COUNT" -eq 0 ]; then
        log "INFO" "Inbox 为空，PM Agent 将基于 codebase + sessions 历史自主规划"
    fi

    # Collect recent sessions
    SESSIONS_DIR="$PROJECT_ROOT/auto-coding/sessions"
    RECENT_SESSIONS=$(find "$SESSIONS_DIR" -maxdepth 1 -type d -name "????-??-??-*" | sort -r | head -n "$CONFIG_SESSION_LIMIT" || true)

    log "最近 $CONFIG_SESSION_LIMIT 个 sessions"

    # Collect codebase structure
    CODEBASE_STRUCTURE=""
    for dir in $CONFIG_CODEBASE; do
        if [ -d "$PROJECT_ROOT/$dir" ]; then
            CODEBASE_STRUCTURE="$CODEBASE_STRUCTURE\n\n### $dir\n"
            CODEBASE_STRUCTURE="$CODEBASE_STRUCTURE$(cd "$PROJECT_ROOT" && find "$dir" -type f -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" | head -50 || true)"
        fi
    done

    # =============================================================================
    # Step 2: PM Agent analysis
    # =============================================================================

    log "${BLUE}[2/7]${NC} PM Agent 分析需求..."

    # Build PM prompt
    PM_PROMPT="你是一个经验丰富但克制的产品经理（PM Agent）。你的任务是分析项目需求，规划最高优先级的 session。

## 输入上下文

### Inbox 需求文件

"

    # Add inbox files content
    for file in $INBOX_FILES; do
        PM_PROMPT="$PM_PROMPT

---
文件: $(basename "$file")
---
$(cat "$file")

"
    done

    PM_PROMPT="$PM_PROMPT

### 最近的 Sessions 进度

"

    # Add recent sessions summary
    for session_dir in $RECENT_SESSIONS; do
        if [ -f "$session_dir/progress.md" ]; then
            PM_PROMPT="$PM_PROMPT

---
Session: $(basename "$session_dir")
---
$(head -100 "$session_dir/progress.md")

"
        fi
    done

    PM_PROMPT="$PM_PROMPT

### 代码库结构

$CODEBASE_STRUCTURE

## 你的任务

1. **分析需求**: 整合 inbox 中的需求，识别最高优先级和影响力的功能
2. **克制原则**: 每次只规划 1-2 个最重要的 session，避免过度规划
3. **输出两个文件**:

   a) **pm-analysis.md** - 你的分析过程和决策依据
      - 需求整合和优先级排序
      - 为什么选择这个 session
      - 预期影响和风险

   b) **session-plan.md** - 具体的 session 创建方案
      - 必须包含: SESSION_NAME: xxxx （一行，session 名称，格式 YYYY-MM-DD-feature-name）
      - Session 目标和范围
      - 关键技术决策
      - 建议的任务数量（最多 $CONFIG_MAX_TASKS 个）

请输出这两个文件的内容，使用 markdown 文件分隔符。

---pm-analysis.md---
[pm-analysis.md 内容]

---session-plan.md---
[session-plan.md 内容]
"

    log "调用 Claude PM Agent..."

    PM_OUTPUT=$("$CLAUDE_CMD" -p --dangerously-skip-permissions "$PM_PROMPT" 2>&1)

    # Extract pm-analysis.md
    echo "$PM_OUTPUT" | sed -n '/---pm-analysis.md---/,/---session-plan.md---/p' | sed '1d;$d' > "$CYCLE_DIR/pm-analysis.md"

    # Extract session-plan.md
    echo "$PM_OUTPUT" | sed -n '/---session-plan.md---/,$p' | sed '1d' > "$CYCLE_DIR/session-plan.md"

    log "${GREEN}✓${NC} PM 分析完成: $CYCLE_DIR/pm-analysis.md"
    log "${GREEN}✓${NC} Session 方案: $CYCLE_DIR/session-plan.md"

    # =============================================================================
    # Step 3: Review pause (optional)
    # =============================================================================

    if [ "$CONFIG_PAUSE" = "true" ]; then
        log "${BLUE}[3/7]${NC} 等待人工确认..."
        echo ""
        cat "$CYCLE_DIR/pm-analysis.md"
        echo ""
        echo -e "${YELLOW}按 Enter 继续执行，或按 Ctrl+C 取消...${NC}"
        read -r
    else
        log "${BLUE}[3/7]${NC} 跳过人工确认（config.pauseForReview=false）"
    fi

    # =============================================================================
    # Step 4: Extract session name and create session
    # =============================================================================

    log "${BLUE}[4/7]${NC} 创建 Session..."

    SESSION_NAME=$(grep -i 'SESSION_NAME' "$CYCLE_DIR/session-plan.md" | head -1 | sed 's/.*SESSION_NAME[^:]*:[[:space:]]*//' | tr -d ' *\r' || true)

    if [ -z "$SESSION_NAME" ]; then
        echo -e "${RED}[ERROR]${NC} 无法从 session-plan.md 中提取 SESSION_NAME"
        echo "请确保文件包含 'SESSION_NAME: xxxx' 行"
        exit 1
    fi

    # init_session.py 会自动加 YYYY-MM-DD- 前缀，去掉 PM Agent 可能携带的日期前缀
    SESSION_NAME=$(echo "$SESSION_NAME" | sed 's/^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-//')

    log "Session 名称: $SESSION_NAME"

    # Call init_session.py
    INIT_OUTPUT=$(python3 "$SCRIPT_DIR/init_session.py" "$PROJECT_ROOT" "$SESSION_NAME" 2>&1)
    SESSION_PATH=$(echo "$INIT_OUTPUT" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('session_dir', ''))" || true)

    if [ -z "$SESSION_PATH" ] || [ ! -d "$SESSION_PATH" ]; then
        echo -e "${RED}[ERROR]${NC} Session 创建失败"
        echo "$INIT_OUTPUT"
        exit 1
    fi

    log "${GREEN}✓${NC} Session 创建: $SESSION_PATH"

    # Copy session-plan to session resources
    cp "$CYCLE_DIR/session-plan.md" "$SESSION_PATH/resources/"
    cp "$CYCLE_DIR/pm-analysis.md" "$SESSION_PATH/resources/"

    # =============================================================================
    # Step 5: Planner Agent fills task.json
    # =============================================================================

    log "${BLUE}[5/7]${NC} Planner Agent 填写 task.json..."

    PLANNER_PROMPT_FILE=$(mktemp)
    cat > "$PLANNER_PROMPT_FILE" << PROMPT_EOF
你是一个任务规划专家（Planner Agent）。请完成以下任务：

1. 读取 PM 分析: $CYCLE_DIR/pm-analysis.md
2. 读取 Session 方案: $CYCLE_DIR/session-plan.md
3. 读取现有 task.json 骨架: $SESSION_PATH/task.json
4. 用 Write 工具将完整填好的 task.json 写入到: $SESSION_PATH/task.json

task.json 格式要求（必须严格遵守）：
- 保留 meta、project、description、session 字段
- tasks 数组最多 $CONFIG_MAX_TASKS 个任务
- 每个 task 必须包含：id、title、description、phase（数字）、parallel（布尔）、passes（false）、priority、tags（数组）、relatedSpecs（数组）、steps（字符串数组，每步包含具体命令和验证标准）
- 输出纯 JSON，直接用 Write 工具写文件，不要说明或解释
PROMPT_EOF

    "$CLAUDE_CMD" -p --dangerously-skip-permissions < "$PLANNER_PROMPT_FILE" > "$CYCLE_DIR/planner-output.log" 2>&1
    rm -f "$PLANNER_PROMPT_FILE"

    # Validate JSON
    if ! python3 -c "import json; json.load(open('$SESSION_PATH/task.json'))" 2>/dev/null; then
        echo -e "${RED}[ERROR]${NC} task.json 格式无效"
        cat "$SESSION_PATH/task.json"
        exit 1
    fi

    log "${GREEN}✓${NC} task.json 已填写"

    # =============================================================================
    # Step 6: Execute session
    # =============================================================================

    log "${BLUE}[6/7]${NC} 执行 Session..."

    # Determine runner
    RUNNER_SCRIPT=""
    if [ "$CONFIG_RUNNER" = "auto" ]; then
        # Check if any task has parallel:true
        HAS_PARALLEL=$(python3 -c "import json; tasks=json.load(open('$SESSION_PATH/task.json'))['tasks']; print('true' if any(t.get('parallel', False) for t in tasks) else 'false')")
        if [ "$HAS_PARALLEL" = "true" ]; then
            RUNNER_SCRIPT="$SCRIPT_DIR/run-parallel.sh"
            log "检测到 parallel 任务，使用 run-parallel.sh"
        else
            RUNNER_SCRIPT="$SCRIPT_DIR/run-automation.sh"
            log "无 parallel 任务，使用 run-automation.sh"
        fi
    elif [ "$CONFIG_RUNNER" = "parallel" ]; then
        RUNNER_SCRIPT="$SCRIPT_DIR/run-parallel.sh"
    else
        RUNNER_SCRIPT="$SCRIPT_DIR/run-automation.sh"
    fi

    log "运行: $RUNNER_SCRIPT"

    bash "$RUNNER_SCRIPT" "$PROJECT_ROOT" "$SESSION_PATH" || true

    log "${GREEN}✓${NC} Session 执行完成"

    # =============================================================================
    # Step 7: Result Reviewer
    # =============================================================================

    log "${BLUE}[7/7]${NC} Result Reviewer 评估结果..."

    REVIEWER_PROMPT="你是一个结果评审专家（Result Reviewer）。请评估 session 的执行结果。

## Session Progress
$(cat "$SESSION_PATH/progress.md" 2>/dev/null || echo "无 progress.md")

## Task Status
$(python3 -c "import json; data=json.load(open('$SESSION_PATH/task.json')); tasks=data['tasks']; print('Total:', len(tasks)); print('Completed:', sum(1 for t in tasks if t.get('passes', False))); print('Pending:', sum(1 for t in tasks if not t.get('passes', False)))")

## 你的任务

评估 session 的完成情况和质量，输出 result.md，包含：

1. **完成度评估**: 完成率、阻塞任务分析
2. **质量评估**: 代码质量、测试覆盖
3. **问题总结**: 遇到的主要问题
4. **改进建议**: 下一步建议和优化方向

直接输出 result.md 的内容。
"

    RESULT_MD=$("$CLAUDE_CMD" -p --dangerously-skip-permissions "$REVIEWER_PROMPT" 2>&1)
    echo "$RESULT_MD" > "$CYCLE_DIR/result.md"

    log "${GREEN}✓${NC} 结果评估: $CYCLE_DIR/result.md"

    # =============================================================================
    # Step 8: Move processed inbox files
    # =============================================================================

    log "移动已处理的 inbox 文件..."

    PROCESSED_DIR="$INBOX_DIR/processed/$DATE_PREFIX-$CYCLE_NUM_PADDED"
    mkdir -p "$PROCESSED_DIR"

    for file in $INBOX_FILES; do
        mv "$file" "$PROCESSED_DIR/"
        log "  移动: $(basename "$file") -> $PROCESSED_DIR/"
    done

    # =============================================================================
    # Check if should continue
    # =============================================================================

    log "${GREEN}========================================${NC}"
    log "${GREEN}Cycle $CYCLE_NUM_PADDED 完成${NC}"
    log "${GREEN}========================================${NC}"

    if [ "$CONFIG_MODE" != "auto" ]; then
        log "手动模式，退出"
        break
    fi

    if [ "$CYCLE_NUM" -ge "$CONFIG_MAX_LOOPS" ]; then
        log "已达最大循环次数 $CONFIG_MAX_LOOPS，退出"
        break
    fi

    CYCLE_NUM=$((CYCLE_NUM + 1))
    CYCLE_NUM_PADDED=$(printf "%03d" $CYCLE_NUM)

    log "继续下一轮..."
    sleep 2
done

log "${GREEN}========================================${NC}"
log "${GREEN}Review Loop 完成${NC}"
log "${GREEN}========================================${NC}"
log "查看历史记录: $HISTORY_DIR"

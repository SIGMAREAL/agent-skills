# Automation Runners

## Table of Contents

1. [Overview](#overview)
2. [Serial Runner (run-automation.sh)](#serial-runner-run-automationsh)
3. [Parallel Runner (run-parallel.sh)](#parallel-runner-run-parallelsh)
4. [Memory-Aware Concurrency](#memory-aware-concurrency)
5. [Known Behaviors](#known-behaviors)
6. [Usage Scenarios](#usage-scenarios)
7. [Environment Variables](#environment-variables)

## Overview

Two execution scripts are managed centrally in the skill directory. Projects only need thin launchers.

## Serial Runner (run-automation.sh)

每次执行一个任务，适合任务数量少或不需要并行的 session。

**Skill script**: `~/.claude/skills/task-planner/scripts/run-automation.sh`
**Project launcher**: `auto-coding/run.sh`

### Usage

```bash
./auto-coding/run.sh                                              # Auto-detect latest session
./auto-coding/run.sh auto-coding/sessions/2026-02-26-feature      # Specific session
./auto-coding/run.sh auto-coding/sessions/2026-02-26-feature 5    # Run at most 5 tasks
```

### Environment Variables

- `CLAUDE_CMD` - Claude CLI command (default: `claude`)
- `SKIP_INIT` - Skip init.sh/setup.sh (default: `false`)
- `CLEANUP_BROWSER` - Clean up browser processes after each task (default: `true`)

## Parallel Runner (run-parallel.sh)

按 phase 执行任务，同一 phase 内的 `parallel: true` 任务并发运行；`parallel: false` 串行执行。macOS 动态内存感知，自动调整并发数。

**Skill script**: `~/.claude/skills/task-planner/scripts/run-parallel.sh`
**Project launcher**: `auto-coding/run-parallel.sh`

### Usage

```bash
./auto-coding/run-parallel.sh                                             # Auto-detect latest session, concurrency=3
./auto-coding/run-parallel.sh auto-coding/sessions/2026-02-27-feature     # Specific session
./auto-coding/run-parallel.sh auto-coding/sessions/2026-02-27-feature 4   # Max concurrency=4
```

### task.json 字段（并行任务需要）

```json
{
  "id": "task-1",
  "phase": 1,          // 执行阶段（整数，按升序执行）
  "parallel": false,   // true=并行执行；false=顺序执行
  "passes": false
}
```

### 执行顺序

1. 从 task.json 自动检测所有未完成任务的 phase（升序）
2. 每个 phase 内：先执行所有 `parallel: false` 任务（串行），再执行所有 `parallel: true` 任务（并发池）
3. 每个 phase 结束后自动批量 git commit 未提交的修改
4. 并行任务的 steps 中应注明"不要执行 git commit"，由 phase 结束的批量提交统一处理

### Environment Variables

- `CLAUDE_CMD` - Claude CLI command (default: `claude`)
- `MAX_BATCH_SIZE` - Max concurrency (default: `3`)
- `MEM_PAUSE_GB` - Pause threshold GB (default: `2`)
- `MEM_SINGLE_GB` - Serial threshold GB (default: `4`)
- `MEM_FULL_GB` - Full-speed threshold GB (default: `8`)
- `CLEANUP_BROWSER` - Clean up browser processes (default: `true`)

## Memory-Aware Concurrency

内存动态调整策略（macOS）:

| 可用内存 | 并发数 |
|---------|--------|
| ≥ 8GB | MAX_BATCH_SIZE（默认3）|
| 4~8GB | MAX_BATCH_SIZE / 2（最少1）|
| 2~4GB | 强制串行（1）|
| < 2GB | 暂停等待（最多5分钟）|

## Known Behaviors

- `wait $pid` 在进程已被回收时返回 rc=127（假警告），任务实际已完成
- 并行任务通过 `-p "prompt"` 传递（而非 stdin），避免 stdin 竞争
- 日志写入 `logs/parallel-YYYYMMDD_HHMMSS.log`，每个任务单独 `logs/task-{id}-{time}.log`

## Usage Scenarios

| 场景 | 推荐脚本 |
|------|---------|
| 任务较少（< 10个），无 phase 划分 | `run.sh`（串行）|
| 任务较多，有明确并行组（如组件批量审查）| `run-parallel.sh`（并行）|
| task.json 中全部 `parallel: false` | 两者效果相同，`run.sh` 更简单 |

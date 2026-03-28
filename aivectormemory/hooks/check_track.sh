#!/usr/bin/env bash
# AIVectorMemory PreToolUse Hook (Edit|Write)
# 检查1：当前项目是否有活跃的 track issue（没有则阻断文件修改）
# 检查2：如果活跃 issue 关联了 spec 任务且有待执行子任务，必须有 in_progress 的子任务

DB_PATH="$HOME/.aivectormemory/memory.db"

# 数据库不存在则放行（首次使用）
if [ ! -f "$DB_PATH" ]; then
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

# 定义 SQL 执行函数：统一使用 python3 参数化查询防止 SQL 注入
# 用法：run_sql "SELECT ... WHERE col=?" "param1" "param2" ...
run_sql() {
  local sql="$1"
  shift
  python3 -c "import sqlite3,sys;c=sqlite3.connect(sys.argv[1]);r=c.execute(sys.argv[2],tuple(sys.argv[3:])).fetchone();print(r[0] if r else '');c.close()" "$DB_PATH" "$sql" "$@" 2>/dev/null
}

# === 检查1：是否有活跃的 track issue ===
COUNT=$(run_sql "SELECT COUNT(*) FROM issues WHERE project_dir=? AND status IN ('pending','in_progress');" "$PROJECT_DIR")

if [ $? -ne 0 ] || [ -z "$COUNT" ]; then
  exit 0
fi

if [ "$COUNT" -eq 0 ]; then
  echo "⚠️ 当前项目没有活跃的 track issue。请先调用 track(action: create) 记录问题后再修改代码。" >&2
  exit 2
fi

# === 检查2：spec 任务 in_progress 检查 ===
# 仅当活跃 issue 有 feature_id 且该 feature 有 pending 子任务时生效
FEATURE_ID=$(run_sql "SELECT feature_id FROM issues WHERE project_dir=? AND status IN ('pending','in_progress') AND feature_id != '' AND feature_id IS NOT NULL LIMIT 1;" "$PROJECT_DIR")

if [ -n "$FEATURE_ID" ]; then
  PENDING_TASKS=$(run_sql "SELECT COUNT(*) FROM tasks WHERE project_dir=? AND feature_id=? AND status='pending' AND parent_id!=0;" "$PROJECT_DIR" "$FEATURE_ID")

  if [ "$PENDING_TASKS" -gt 0 ] 2>/dev/null; then
    IN_PROGRESS=$(run_sql "SELECT COUNT(*) FROM tasks WHERE project_dir=? AND feature_id=? AND status='in_progress' AND parent_id!=0;" "$PROJECT_DIR" "$FEATURE_ID")

    if [ "$IN_PROGRESS" -eq 0 ] 2>/dev/null; then
      echo "⚠️ spec 任务 [$FEATURE_ID] 有待执行的子任务但没有 in_progress 的子任务。请先调用 task(action: update, task_id: X, status: in_progress) 标记当前正在执行的子任务后再修改代码。" >&2
      exit 2
    fi
  fi
fi

exit 0

"""AIVectorMemory PreToolUse Hook (Edit|Write)

检查1：当前项目是否有活跃的 track issue（没有则阻断文件修改）
检查2：如果活跃 issue 关联了 spec 任务且有待执行子任务，必须有 in_progress 的子任务

用法: python3 -m aivectormemory.hooks.check_track
stdin: JSON（tool_input.file_path 等）
exit 0: 放行  exit 2: 阻断
"""
import os
import sqlite3
import sys
from pathlib import Path

from aivectormemory.hooks._common import read_stdin, get_project_dir, block
from aivectormemory.hooks._messages import get_message


def _db_path() -> Path:
    return Path.home() / ".aivectormemory" / "memory.db"


def _query_one(conn: sqlite3.Connection, sql: str, params: tuple) -> str | None:
    row = conn.execute(sql, params).fetchone()
    return str(row[0]) if row else None


def main() -> int:
    db = _db_path()
    if not db.exists():
        return 0  # 首次使用，放行

    _ = read_stdin()  # 消费 stdin（部分 IDE 要求读完）
    project_dir = get_project_dir()

    try:
        conn = sqlite3.connect(str(db))
    except Exception:
        return 0  # 数据库打开失败，放行

    try:
        # 检查1：是否有活跃的 track issue
        count = _query_one(
            conn,
            "SELECT COUNT(*) FROM issues WHERE project_dir=? AND status IN ('pending','in_progress')",
            (project_dir,),
        )
        if count is None or int(count) == 0:
            return block(get_message("no_track_issue"))

        # 检查2：spec 任务 in_progress 检查
        feature_id = _query_one(
            conn,
            "SELECT feature_id FROM issues WHERE project_dir=? AND status IN ('pending','in_progress') AND feature_id != '' AND feature_id IS NOT NULL LIMIT 1",
            (project_dir,),
        )
        if feature_id:
            pending = _query_one(
                conn,
                "SELECT COUNT(*) FROM tasks WHERE project_dir=? AND feature_id=? AND status='pending' AND parent_id!=0",
                (project_dir, feature_id),
            )
            if pending and int(pending) > 0:
                in_progress = _query_one(
                    conn,
                    "SELECT COUNT(*) FROM tasks WHERE project_dir=? AND feature_id=? AND status='in_progress' AND parent_id!=0",
                    (project_dir, feature_id),
                )
                if not in_progress or int(in_progress) == 0:
                    return block(get_message("no_in_progress_task", feature_id=feature_id))
    except Exception:
        return 0  # SQL 异常放行
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())

"""AIVectorMemory PreToolUse Hook (Edit|Write)

检查1：当前项目是否有活跃的 track issue（没有则阻断代码文件修改）
检查2：如果活跃 issue 关联了 spec 任务且有待执行子任务，必须有 in_progress 的子任务

非代码文件（.md/.sh/.json/.yaml/.toml/.css/.html/.txt/.cfg/.ini/.env/.sql 等）直接放行。

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

# 非代码文件扩展名，直接放行
NON_CODE_EXTS = {
    ".md", ".sh", ".bash", ".zsh", ".fish",
    ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".env",
    ".txt", ".csv", ".log", ".sql",
    ".html", ".css", ".svg", ".xml",
    ".dockerfile", ".gitignore", ".editorconfig",
}


def _db_path() -> Path:
    return Path.home() / ".aivectormemory" / "memory.db"


def _query_one(conn: sqlite3.Connection, sql: str, params: tuple) -> str | None:
    row = conn.execute(sql, params).fetchone()
    return str(row[0]) if row else None


def _get_file_path(data: dict) -> str:
    """从 stdin JSON 中提取文件路径"""
    tool_input = data.get("tool_input", {})
    return tool_input.get("file_path", "") or tool_input.get("path", "")


def main() -> int:
    db = _db_path()
    if not db.exists():
        return 0  # 首次使用，放行

    data = read_stdin()
    project_dir = get_project_dir()

    # 检查文件扩展名，非代码文件直接放行
    file_path = _get_file_path(data)
    if file_path:
        ext = Path(file_path).suffix.lower()
        if ext in NON_CODE_EXTS or not ext:
            return 0

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

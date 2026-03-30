"""过期记忆自动归档清理 — T13"""
import logging
import time
from datetime import datetime, timedelta, timezone

from aivectormemory.config import CLEANUP_DAYS

logger = logging.getLogger(__name__)

_last_cleanup: float = 0


def maybe_cleanup(conn, project_dir: str) -> None:
    """节流入口：每小时最多触发一次清理"""
    global _last_cleanup
    now = time.time()
    if now - _last_cleanup < 3600:
        return
    _last_cleanup = now
    try:
        cleanup_expired_memories(conn, project_dir)
    except Exception:
        logger.exception("cleanup_expired_memories failed")


def cleanup_expired_memories(conn, project_dir: str) -> int:
    """清理过期记忆：tier=short_term AND importance < 0.1 AND last_accessed_at > CLEANUP_DAYS 天

    返回归档记录总数。
    """
    threshold = datetime.now(timezone.utc) - timedelta(days=CLEANUP_DAYS)
    threshold_str = threshold.isoformat()
    now_str = datetime.now(timezone.utc).isoformat()
    total_archived = 0

    table_configs = [
        {
            "table": "memories",
            "scope": "project",
            "fts": "fts_memories",
            "vec": "vec_memories",
            "tag": "memory_tags",
            "extra_where": " AND project_dir = ?",
            "extra_params": [project_dir],
        },
        {
            "table": "user_memories",
            "scope": "user",
            "fts": "fts_user_memories",
            "vec": "vec_user_memories",
            "tag": "user_memory_tags",
            "extra_where": "",
            "extra_params": [],
        },
    ]

    for cfg in table_configs:
        table = cfg["table"]
        params = [threshold_str] + cfg["extra_params"]
        expired = conn.execute(
            f"SELECT * FROM {table} WHERE tier = 'short_term' AND importance < 0.1 "
            f"AND last_accessed_at < ? AND last_accessed_at != ''{cfg['extra_where']}",
            params,
        ).fetchall()

        if not expired:
            continue

        for row in expired:
            row_dict = dict(row)
            mid = row_dict["id"]

            # 插入 memories_archive
            conn.execute(
                """INSERT OR IGNORE INTO memories_archive
                   (id, content, scope, session_id, project_dir, source,
                    tier, access_count, last_accessed_at, importance, summary,
                    archived_at, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    mid,
                    row_dict.get("content", ""),
                    cfg["scope"] if cfg["scope"] == "user" else row_dict.get("scope", "project"),
                    row_dict.get("session_id", 0),
                    row_dict.get("project_dir", ""),
                    row_dict.get("source", "manual"),
                    row_dict.get("tier", "short_term"),
                    row_dict.get("access_count", 0),
                    row_dict.get("last_accessed_at", ""),
                    row_dict.get("importance", 0.5),
                    row_dict.get("summary", ""),
                    now_str,
                    row_dict.get("created_at", now_str),
                    row_dict.get("updated_at", now_str),
                ],
            )

            # 清理关联数据：FTS5 → relations → vec → tags → 原表
            conn.execute(f"DELETE FROM {cfg['fts']} WHERE id = ?", [mid])
            conn.execute(
                "DELETE FROM memory_relations WHERE memory_id = ? OR related_id = ?",
                [mid, mid],
            )
            conn.execute(f"DELETE FROM {cfg['vec']} WHERE id = ?", [mid])
            conn.execute(f"DELETE FROM {cfg['tag']} WHERE memory_id = ?", [mid])
            conn.execute(f"DELETE FROM {table} WHERE id = ?", [mid])

            total_archived += 1

        conn.commit()

    if total_archived:
        logger.info("Archived %d expired memories", total_archived)
    return total_archived

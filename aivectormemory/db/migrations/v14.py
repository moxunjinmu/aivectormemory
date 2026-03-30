"""v14: Smart Memory Engine P1 — memories_archive 表 + tier/summary 字段"""


def _has_column(conn, table: str, column: str) -> bool:
    """检查表是否已有指定列"""
    cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any((c[1] if isinstance(c, tuple) else c["name"]) == column for c in cols)


def _add_tier_summary(conn, table: str):
    """为 memories / user_memories 添加 tier 和 summary 字段"""
    if not _has_column(conn, table, "tier"):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN tier TEXT NOT NULL DEFAULT 'short_term'")
    if not _has_column(conn, table, "summary"):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN summary TEXT")


def _backfill_tier(conn, table: str):
    """access_count >= 3 的记忆提升为 long_term"""
    conn.execute(f"UPDATE {table} SET tier = 'long_term' WHERE access_count >= 3")


def upgrade(conn, **_):
    # 1. 创建 memories_archive 表
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories_archive (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            scope TEXT NOT NULL DEFAULT 'project',
            session_id INTEGER,
            project_dir TEXT,
            source TEXT DEFAULT 'manual',
            tier TEXT NOT NULL DEFAULT 'short_term',
            access_count INTEGER NOT NULL DEFAULT 0,
            last_accessed_at TEXT,
            importance REAL NOT NULL DEFAULT 0.5,
            summary TEXT,
            archived_at TEXT NOT NULL DEFAULT (datetime('now')),
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # 2. ALTER TABLE 加 tier + summary 字段
    for table in ("memories", "user_memories"):
        _add_tier_summary(conn, table)

    # 3. 回填 tier
    for table in ("memories", "user_memories"):
        _backfill_tier(conn, table)

    # 4. 创建 tier 索引
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_tier ON memories(tier)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_user_memories_tier ON user_memories(tier)")

    conn.commit()

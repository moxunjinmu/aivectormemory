"""v13: Smart Memory Engine P0 — 新增字段 + FTS5 + memory_relations"""

import jieba


def _tokenize_for_fts(content: str) -> str:
    """jieba 分词后空格拼接，供 FTS5 unicode61 分词器索引"""
    return ' '.join(jieba.cut(content))


def _add_columns(conn, table: str):
    """为 memories / user_memories 添加 access_count, last_accessed_at, importance"""
    conn.execute(f"ALTER TABLE {table} ADD COLUMN access_count INTEGER NOT NULL DEFAULT 0")
    conn.execute(f"ALTER TABLE {table} ADD COLUMN last_accessed_at TEXT NOT NULL DEFAULT ''")
    conn.execute(f"ALTER TABLE {table} ADD COLUMN importance REAL NOT NULL DEFAULT 0.5")


def _backfill_last_accessed(conn, table: str):
    """回填 last_accessed_at 为 created_at"""
    conn.execute(f"UPDATE {table} SET last_accessed_at = created_at WHERE last_accessed_at = ''")


def _populate_fts(conn, src_table: str, fts_table: str):
    """遍历源表所有记录，jieba 分词后插入 FTS5 表"""
    rows = conn.execute(f"SELECT id, content FROM {src_table}").fetchall()
    for row in rows:
        mid = row[0] if isinstance(row, tuple) else row["id"]
        content = row[1] if isinstance(row, tuple) else row["content"]
        tokenized = _tokenize_for_fts(content)
        conn.execute(f"INSERT INTO {fts_table}(id, content) VALUES (?, ?)", (mid, tokenized))


def upgrade(conn, **_):
    # 1. 创建 FTS5 虚拟表
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS fts_memories USING fts5(
            id UNINDEXED, content, tokenize='unicode61'
        )
    """)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS fts_user_memories USING fts5(
            id UNINDEXED, content, tokenize='unicode61'
        )
    """)

    # 2. 创建 memory_relations 表和索引
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memory_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_id TEXT NOT NULL,
            related_id TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            scope TEXT NOT NULL DEFAULT 'project',
            created_at TEXT NOT NULL,
            UNIQUE(memory_id, related_id, relation_type)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_relations_memory ON memory_relations(memory_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_relations_related ON memory_relations(related_id)")

    # 3. ALTER TABLE 加字段
    for table in ("memories", "user_memories"):
        _add_columns(conn, table)

    # 4. 回填 last_accessed_at
    for table in ("memories", "user_memories"):
        _backfill_last_accessed(conn, table)

    # 5. 遍历分词填充 FTS5
    _populate_fts(conn, "memories", "fts_memories")
    _populate_fts(conn, "user_memories", "fts_user_memories")

    conn.commit()

from aivectormemory.config import MODEL_DIMENSION

SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL DEFAULT 0
)"""

MEMORIES_TABLE = """
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '[]',
    scope TEXT NOT NULL DEFAULT 'project',
    source TEXT NOT NULL DEFAULT 'manual',
    project_dir TEXT NOT NULL DEFAULT '',
    session_id INTEGER NOT NULL DEFAULT 0,
    tier TEXT NOT NULL DEFAULT 'short_term' CHECK(tier IN ('short_term', 'long_term')),
    summary TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)"""

VEC_MEMORIES_TABLE = f"""
CREATE VIRTUAL TABLE IF NOT EXISTS vec_memories USING vec0(
    id TEXT PRIMARY KEY,
    embedding FLOAT[{MODEL_DIMENSION}]
)"""

SESSION_STATE_TABLE = """
CREATE TABLE IF NOT EXISTS session_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_dir TEXT NOT NULL DEFAULT '',
    is_blocked INTEGER NOT NULL DEFAULT 0,
    block_reason TEXT NOT NULL DEFAULT '',
    next_step TEXT NOT NULL DEFAULT '',
    current_task TEXT NOT NULL DEFAULT '',
    progress TEXT NOT NULL DEFAULT '[]',
    recent_changes TEXT NOT NULL DEFAULT '[]',
    pending TEXT NOT NULL DEFAULT '[]',
    updated_at TEXT NOT NULL,
    UNIQUE(project_dir)
)"""

ISSUES_TABLE = """
CREATE TABLE IF NOT EXISTS issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_dir TEXT NOT NULL DEFAULT '',
    issue_number INTEGER NOT NULL,
    date TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    content TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '[]',
    description TEXT NOT NULL DEFAULT '',
    investigation TEXT NOT NULL DEFAULT '',
    root_cause TEXT NOT NULL DEFAULT '',
    solution TEXT NOT NULL DEFAULT '',
    files_changed TEXT NOT NULL DEFAULT '[]',
    test_result TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    feature_id TEXT NOT NULL DEFAULT '',
    parent_id INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)"""

ISSUES_ARCHIVE_TABLE = """
CREATE TABLE IF NOT EXISTS issues_archive (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_dir TEXT NOT NULL DEFAULT '',
    issue_number INTEGER NOT NULL,
    date TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '[]',
    description TEXT NOT NULL DEFAULT '',
    investigation TEXT NOT NULL DEFAULT '',
    root_cause TEXT NOT NULL DEFAULT '',
    solution TEXT NOT NULL DEFAULT '',
    files_changed TEXT NOT NULL DEFAULT '[]',
    test_result TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    feature_id TEXT NOT NULL DEFAULT '',
    parent_id INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT '',
    original_issue_id INTEGER NOT NULL DEFAULT 0,
    archived_at TEXT NOT NULL,
    created_at TEXT NOT NULL
)"""

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_memories_project ON memories(project_dir)",
    "CREATE INDEX IF NOT EXISTS idx_memories_scope ON memories(scope)",
    "CREATE INDEX IF NOT EXISTS idx_memories_tags ON memories(tags)",
    "CREATE INDEX IF NOT EXISTS idx_issues_date ON issues(date)",
    "CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status)",
    "CREATE INDEX IF NOT EXISTS idx_issues_project ON issues(project_dir)",
    "CREATE INDEX IF NOT EXISTS idx_issues_archive_project ON issues_archive(project_dir)",
    "CREATE INDEX IF NOT EXISTS idx_issues_archive_date ON issues_archive(date)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_dir)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_feature ON tasks(feature_id)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)",
    "CREATE INDEX IF NOT EXISTS idx_memories_source ON memories(source)",
    "CREATE INDEX IF NOT EXISTS idx_user_memories_tags ON user_memories(tags)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_archive_project ON tasks_archive(project_dir)",
    "CREATE INDEX IF NOT EXISTS idx_tasks_archive_feature ON tasks_archive(feature_id)",
    "CREATE INDEX IF NOT EXISTS idx_memory_tags_tag ON memory_tags(tag)",
    "CREATE INDEX IF NOT EXISTS idx_user_memory_tags_tag ON user_memory_tags(tag)",
    "CREATE INDEX IF NOT EXISTS idx_memory_relations_memory ON memory_relations(memory_id)",
    "CREATE INDEX IF NOT EXISTS idx_memory_relations_related ON memory_relations(related_id)",
    "CREATE INDEX IF NOT EXISTS idx_memories_tier ON memories(tier)",
    "CREATE INDEX IF NOT EXISTS idx_user_memories_tier ON user_memories(tier)",
]

TASKS_TABLE = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_dir TEXT NOT NULL DEFAULT '',
    feature_id TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    sort_order INTEGER NOT NULL DEFAULT 0,
    parent_id INTEGER NOT NULL DEFAULT 0,
    task_type TEXT NOT NULL DEFAULT 'manual',
    metadata TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)"""

USER_MEMORIES_TABLE = """
CREATE TABLE IF NOT EXISTS user_memories (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '[]',
    source TEXT NOT NULL DEFAULT 'manual',
    session_id INTEGER NOT NULL DEFAULT 0,
    tier TEXT NOT NULL DEFAULT 'short_term' CHECK(tier IN ('short_term', 'long_term')),
    summary TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)"""

VEC_USER_MEMORIES_TABLE = f"""
CREATE VIRTUAL TABLE IF NOT EXISTS vec_user_memories USING vec0(
    id TEXT PRIMARY KEY,
    embedding FLOAT[{MODEL_DIMENSION}]
)"""

VEC_ISSUES_ARCHIVE_TABLE = f"""
CREATE VIRTUAL TABLE IF NOT EXISTS vec_issues_archive USING vec0(
    id INTEGER PRIMARY KEY,
    embedding FLOAT[{MODEL_DIMENSION}]
)"""

TASKS_ARCHIVE_TABLE = """
CREATE TABLE IF NOT EXISTS tasks_archive (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_dir TEXT NOT NULL DEFAULT '',
    feature_id TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    sort_order INTEGER NOT NULL DEFAULT 0,
    parent_id INTEGER NOT NULL DEFAULT 0,
    task_type TEXT NOT NULL DEFAULT 'manual',
    metadata TEXT NOT NULL DEFAULT '{}',
    original_task_id INTEGER NOT NULL DEFAULT 0,
    archived_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)"""

MEMORY_TAGS_TABLE = """
CREATE TABLE IF NOT EXISTS memory_tags (
    memory_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (memory_id, tag)
)"""

USER_MEMORY_TAGS_TABLE = """
CREATE TABLE IF NOT EXISTS user_memory_tags (
    memory_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (memory_id, tag)
)"""

USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_login TEXT
)"""

FTS_MEMORIES_TABLE = """
CREATE VIRTUAL TABLE IF NOT EXISTS fts_memories USING fts5(
    id UNINDEXED,
    content,
    tokenize='unicode61'
)"""

FTS_USER_MEMORIES_TABLE = """
CREATE VIRTUAL TABLE IF NOT EXISTS fts_user_memories USING fts5(
    id UNINDEXED,
    content,
    tokenize='unicode61'
)"""

MEMORIES_ARCHIVE_TABLE = """
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
)"""

MEMORY_RELATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS memory_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id TEXT NOT NULL,
    related_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    scope TEXT NOT NULL DEFAULT 'project',
    created_at TEXT NOT NULL,
    UNIQUE(memory_id, related_id, relation_type)
)"""

ALL_TABLES = [SCHEMA_VERSION_TABLE, MEMORIES_TABLE, VEC_MEMORIES_TABLE, SESSION_STATE_TABLE, ISSUES_TABLE, ISSUES_ARCHIVE_TABLE, TASKS_TABLE, USER_MEMORIES_TABLE, VEC_USER_MEMORIES_TABLE, VEC_ISSUES_ARCHIVE_TABLE, TASKS_ARCHIVE_TABLE, MEMORY_TAGS_TABLE, USER_MEMORY_TAGS_TABLE, USERS_TABLE, FTS_MEMORIES_TABLE, FTS_USER_MEMORIES_TABLE, MEMORY_RELATIONS_TABLE, MEMORIES_ARCHIVE_TABLE]

CURRENT_SCHEMA_VERSION = 14


def _get_schema_version(conn) -> int:
    row = conn.execute("SELECT version FROM schema_version").fetchone()
    if row:
        return row[0] if isinstance(row, tuple) else row["version"]
    conn.execute("INSERT INTO schema_version (version) VALUES (0)")
    conn.commit()
    return 0


def _set_schema_version(conn, version: int):
    conn.execute("UPDATE schema_version SET version=?", (version,))


def init_db(conn, engine=None):
    for sql in ALL_TABLES:
        conn.execute(sql)

    ver = _get_schema_version(conn)

    if ver < CURRENT_SCHEMA_VERSION:
        from .migrations import MIGRATIONS
        for ver_num in range(ver + 1, CURRENT_SCHEMA_VERSION + 1):
            fn = MIGRATIONS.get(ver_num)
            if fn:
                fn(conn, engine=engine)

    for sql in INDEXES:
        conn.execute(sql)

    if ver < CURRENT_SCHEMA_VERSION:
        _set_schema_version(conn, CURRENT_SCHEMA_VERSION)
    conn.commit()

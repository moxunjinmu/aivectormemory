"""v15: 代码知识图谱 — graph_nodes + graph_edges 表"""


def upgrade(conn, **_):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS graph_nodes (
            id TEXT PRIMARY KEY,
            project_dir TEXT NOT NULL,
            name TEXT NOT NULL,
            entity_type TEXT NOT NULL CHECK(entity_type IN ('function','class','module','api','table','variable')),
            file_path TEXT DEFAULT '',
            line_number INTEGER DEFAULT 0,
            description TEXT DEFAULT '',
            memory_id TEXT DEFAULT '',
            file_mtime TEXT DEFAULT '',
            metadata TEXT DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(project_dir, name, entity_type, file_path)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS graph_edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL REFERENCES graph_nodes(id),
            target_id TEXT NOT NULL REFERENCES graph_nodes(id),
            relation TEXT NOT NULL CHECK(relation IN ('calls','depends_on','data_flow','contains','implements','reads','writes')),
            label TEXT DEFAULT '',
            metadata TEXT DEFAULT '{}',
            created_at TEXT NOT NULL,
            UNIQUE(source_id, target_id, relation)
        )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_graph_nodes_project ON graph_nodes(project_dir)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_graph_nodes_name ON graph_nodes(name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_graph_nodes_type ON graph_nodes(entity_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_graph_nodes_file ON graph_nodes(file_path)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_graph_edges_source ON graph_edges(source_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_graph_edges_target ON graph_edges(target_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_graph_edges_relation ON graph_edges(relation)")

    conn.commit()

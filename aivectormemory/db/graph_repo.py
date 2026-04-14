import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from aivectormemory.utils import now_iso


_UUID_RE = re.compile(r'^[0-9a-f]{12}$')


class GraphRepo:
    """代码知识图谱：节点/边 CRUD + BFS 遍历 + stale 检测"""

    def __init__(self, conn: sqlite3.Connection, project_dir: str):
        self.conn = conn
        self.project_dir = project_dir

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_uuid(ref: str) -> bool:
        return bool(_UUID_RE.match(ref))

    @staticmethod
    def normalize_file_path(file_path: str, project_dir: str) -> str:
        if not file_path:
            return ""
        path = file_path.replace("\\", "/")
        prefix = project_dir.replace("\\", "/")
        if not prefix.endswith("/"):
            prefix += "/"
        if path.startswith(prefix):
            path = path[len(prefix):]
        return path

    def _get_file_mtime(self, file_path: str) -> str:
        if not file_path:
            return ""
        full_path = Path(self.project_dir) / file_path
        if not full_path.exists():
            return ""
        return datetime.fromtimestamp(
            full_path.stat().st_mtime, tz=timezone.utc
        ).isoformat()

    def resolve_node(self, ref: str, project_dir: str | None = None) -> str:
        if self._is_uuid(ref):
            return ref
        pd = project_dir or self.project_dir
        rows = self.conn.execute(
            "SELECT id FROM graph_nodes WHERE name = ? AND project_dir = ?",
            [ref, pd]
        ).fetchall()
        if len(rows) == 1:
            return rows[0]["id"] if isinstance(rows[0], sqlite3.Row) else rows[0][0]
        if not rows:
            raise ValueError(f"节点 '{ref}' 不存在")
        raise ValueError(f"节点 '{ref}' 有多个匹配，请用 ID 指定")

    def _check_stale(self, node: dict) -> dict:
        node = dict(node)
        file_path = node.get("file_path", "")
        if not file_path:
            node["stale"] = False
            return node

        full_path = Path(self.project_dir) / file_path
        if not full_path.exists():
            node["stale"] = True
            node["stale_reason"] = "file_not_found"
            return node

        current_mtime = datetime.fromtimestamp(
            full_path.stat().st_mtime, tz=timezone.utc
        ).isoformat()
        stored_mtime = node.get("file_mtime", "")
        node["stale"] = (stored_mtime != current_mtime)
        if node["stale"]:
            node["stale_reason"] = "file_modified"
        return node

    def _row_to_dict(self, row) -> dict:
        return dict(row) if isinstance(row, sqlite3.Row) else row

    # ------------------------------------------------------------------
    # Node CRUD
    # ------------------------------------------------------------------

    def upsert_node(self, name: str, entity_type: str, file_path: str = "",
                    line_number: int = 0, description: str = "",
                    memory_id: str = "", metadata: dict | None = None) -> dict:
        file_path = self.normalize_file_path(file_path, self.project_dir)
        file_mtime = self._get_file_mtime(file_path)
        now = now_iso()
        node_id = uuid.uuid4().hex[:12]

        self.conn.execute("""
            INSERT INTO graph_nodes (id, project_dir, name, entity_type, file_path,
                line_number, description, memory_id, file_mtime, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_dir, name, entity_type, file_path) DO UPDATE SET
                line_number = excluded.line_number,
                description = excluded.description,
                memory_id = excluded.memory_id,
                file_mtime = excluded.file_mtime,
                metadata = excluded.metadata,
                updated_at = excluded.updated_at
        """, [node_id, self.project_dir, name, entity_type, file_path,
              line_number, description, memory_id, file_mtime,
              json.dumps(metadata or {}), now, now])
        self.conn.commit()

        row = self.conn.execute(
            "SELECT id FROM graph_nodes WHERE project_dir = ? AND name = ? AND entity_type = ? AND file_path = ?",
            [self.project_dir, name, entity_type, file_path]
        ).fetchone()
        actual_id = row["id"] if isinstance(row, sqlite3.Row) else row[0]
        return {"id": actual_id, "name": name, "entity_type": entity_type}

    def get_node(self, node_id: str) -> dict | None:
        row = self.conn.execute("SELECT * FROM graph_nodes WHERE id = ?", [node_id]).fetchone()
        return self._row_to_dict(row) if row else None

    # ------------------------------------------------------------------
    # Edge CRUD
    # ------------------------------------------------------------------

    def insert_edge(self, source: str, target: str, relation: str,
                    label: str = "", metadata: dict | None = None) -> dict:
        source_id = self.resolve_node(source)
        target_id = self.resolve_node(target)
        now = now_iso()

        self.conn.execute("""
            INSERT OR IGNORE INTO graph_edges (source_id, target_id, relation, label, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [source_id, target_id, relation, label, json.dumps(metadata or {}), now])
        self.conn.commit()

        row = self.conn.execute(
            "SELECT id FROM graph_edges WHERE source_id = ? AND target_id = ? AND relation = ?",
            [source_id, target_id, relation]
        ).fetchone()
        edge_id = row["id"] if isinstance(row, sqlite3.Row) else row[0]
        return {"id": edge_id, "source_id": source_id, "target_id": target_id, "relation": relation}

    # ------------------------------------------------------------------
    # Remove
    # ------------------------------------------------------------------

    def remove_node(self, node_id: str):
        self.conn.execute("DELETE FROM graph_edges WHERE source_id = ? OR target_id = ?", [node_id, node_id])
        self.conn.execute("DELETE FROM graph_nodes WHERE id = ?", [node_id])
        self.conn.commit()

    def remove_edge(self, edge_id: int):
        self.conn.execute("DELETE FROM graph_edges WHERE id = ?", [edge_id])
        self.conn.commit()

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def query_nodes(self, name: str | None = None, entity_type: str | None = None,
                    file_path: str | None = None) -> list[dict]:
        conditions = ["project_dir = ?"]
        params: list = [self.project_dir]

        if name:
            conditions.append("name LIKE ?")
            params.append(f"%{name}%")
        if entity_type:
            conditions.append("entity_type = ?")
            params.append(entity_type)
        if file_path:
            fp = self.normalize_file_path(file_path, self.project_dir)
            conditions.append("file_path LIKE ?")
            params.append(f"%{fp}%")

        sql = f"SELECT * FROM graph_nodes WHERE {' AND '.join(conditions)} ORDER BY name"
        rows = self.conn.execute(sql, params).fetchall()
        return [self._check_stale(self._row_to_dict(r)) for r in rows]

    # ------------------------------------------------------------------
    # Trace (BFS)
    # ------------------------------------------------------------------

    def _get_edges(self, node_id: str, relation: str | None, direction: str) -> list[dict]:
        conditions = []
        params: list = []

        if direction == "down":
            conditions.append("source_id = ?")
            params.append(node_id)
        elif direction == "up":
            conditions.append("target_id = ?")
            params.append(node_id)
        else:  # both
            conditions.append("(source_id = ? OR target_id = ?)")
            params.extend([node_id, node_id])

        if relation:
            conditions.append("relation = ?")
            params.append(relation)

        sql = f"SELECT * FROM graph_edges WHERE {' AND '.join(conditions)}"
        return [self._row_to_dict(r) for r in self.conn.execute(sql, params).fetchall()]

    def trace(self, start: str, relation: str | None = None, direction: str = "down",
              max_depth: int = 3, cross_project: bool = False) -> dict:
        start_id = self.resolve_node(start)
        start_node = self.get_node(start_id)
        if not start_node:
            raise ValueError(f"起始节点 '{start}' 不存在")

        visited = {start_id}
        queue = [(start_id, 0)]
        result_nodes = [self._check_stale(start_node)]
        result_edges = []

        while queue:
            current_id, depth = queue.pop(0)
            if depth >= max_depth:
                continue

            edges = self._get_edges(current_id, relation, direction)
            for edge in edges:
                if direction == "up":
                    next_id = edge["source_id"]
                elif direction == "down":
                    next_id = edge["target_id"]
                else:
                    next_id = edge["target_id"] if edge["source_id"] == current_id else edge["source_id"]

                if next_id in visited:
                    continue

                node = self.get_node(next_id)
                if not node:
                    continue
                if not cross_project and node["project_dir"] != self.project_dir:
                    continue

                visited.add(next_id)
                result_nodes.append(self._check_stale(node))
                result_edges.append(edge)
                queue.append((next_id, depth + 1))

        return {"nodes": result_nodes, "edges": result_edges}

    # ------------------------------------------------------------------
    # Batch
    # ------------------------------------------------------------------

    def batch_upsert(self, nodes: list[dict], edges: list[dict]) -> dict:
        created_nodes = []
        created_edges = []
        name_to_id: dict[str, str] = {}

        for n in nodes:
            result = self.upsert_node(
                name=n["name"],
                entity_type=n.get("entity_type", "function"),
                file_path=n.get("file_path", ""),
                line_number=n.get("line_number", 0),
                description=n.get("description", ""),
                memory_id=n.get("memory_id", ""),
                metadata=n.get("metadata"),
            )
            created_nodes.append(result)
            name_to_id[n["name"]] = result["id"]

        for e in edges:
            source_ref = e["source"]
            target_ref = e["target"]
            # 优先从同批次节点名称解析
            if source_ref in name_to_id:
                source_ref = name_to_id[source_ref]
            if target_ref in name_to_id:
                target_ref = name_to_id[target_ref]

            result = self.insert_edge(
                source=source_ref,
                target=target_ref,
                relation=e["relation"],
                label=e.get("label", ""),
                metadata=e.get("metadata"),
            )
            created_edges.append(result)

        return {"nodes": created_nodes, "edges": created_edges}

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def refresh(self, file_path: str | None = None) -> list[dict]:
        conditions = ["project_dir = ?"]
        params: list = [self.project_dir]

        if file_path:
            fp = self.normalize_file_path(file_path, self.project_dir)
            conditions.append("file_path LIKE ?")
            params.append(f"%{fp}%")

        sql = f"SELECT * FROM graph_nodes WHERE {' AND '.join(conditions)}"
        rows = self.conn.execute(sql, params).fetchall()

        stale_nodes = []
        for r in rows:
            node = self._check_stale(self._row_to_dict(r))
            if node.get("stale"):
                stale_nodes.append(node)
        return stale_nodes

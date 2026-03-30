import json
import sqlite3
import uuid
from typing import Any

from aivectormemory.utils import now_iso

import jieba


def tokenize_for_fts(content: str) -> str:
    """jieba 分词后用空格连接，供 FTS5 索引"""
    return ' '.join(jieba.cut(content))


class BaseRepo:
    """所有 Repo 的基类"""

    def __init__(self, conn: sqlite3.Connection, project_dir: str = ""):
        self.conn = conn
        self.project_dir = project_dir

    def _now(self) -> str:
        return now_iso()

    def _commit(self) -> None:
        from aivectormemory.db.connection import _in_transaction
        if not _in_transaction:
            self.conn.commit()


class BaseMemoryRepo(BaseRepo):
    """MemoryRepo 和 UserMemoryRepo 的公共基类"""

    TABLE = ""
    VEC_TABLE = ""
    TAG_TABLE = ""

    def _sync_tags(self, mid: str, tags: list[str]) -> None:
        self.conn.execute(f"DELETE FROM {self.TAG_TABLE} WHERE memory_id=?", (mid,))
        if tags:
            self.conn.executemany(
                f"INSERT OR IGNORE INTO {self.TAG_TABLE} (memory_id, tag) VALUES (?,?)",
                [(mid, t) for t in tags])

    def insert(self, content: str, tags: list[str], session_id: int,
               embedding: list[float], dedup_threshold: float = 0.95,
               source: str = "manual", **extra) -> dict:
        from aivectormemory.config import CONFLICT_THRESHOLD
        from aivectormemory.summarizer import generate_summary
        import aivectormemory.db.connection as _conn_mod
        was_in_transaction = _conn_mod._in_transaction
        if not was_in_transaction:
            self.conn.execute("BEGIN IMMEDIATE")
            _conn_mod._in_transaction = True
        try:
            action, dup_id, conflict_ids = self._check_similar(embedding, dedup_threshold, CONFLICT_THRESHOLD)
            if action == "update":
                result = self._update_existing(dup_id, content, tags, session_id, embedding)
            else:
                now = self._now()
                mid = uuid.uuid4().hex[:12]
                cols, vals = self._build_insert(mid, content, tags, source, session_id, now, extra)
                placeholders = ",".join("?" * len(vals))
                self.conn.execute(f"INSERT INTO {self.TABLE} ({cols}) VALUES ({placeholders})", vals)
                self.conn.execute(f"INSERT INTO {self.VEC_TABLE} (id, embedding) VALUES (?,?)", (mid, json.dumps(embedding)))
                self._sync_tags(mid, tags)
                # T3.1: FTS5 同步
                fts_table = f"fts_{self.TABLE}"
                tokenized = tokenize_for_fts(content)
                self.conn.execute(f"INSERT INTO {fts_table}(id, content) VALUES (?, ?)", [mid, tokenized])
                # T6.2: 矛盾检测 — 创建 supersedes 关系 + 降低旧记忆 importance
                if conflict_ids:
                    self._create_supersedes_relations(self.conn, mid, conflict_ids)
                    self._reduce_importance(self.conn, conflict_ids, self.TABLE)
                # T15.3: 自动摘要
                summary = generate_summary(content)
                if summary:
                    try:
                        self.conn.execute(f"UPDATE {self.TABLE} SET summary=? WHERE id=?", [summary, mid])
                    except Exception:
                        pass  # v14 迁移前 summary 字段不存在
                # T14: 自动建立 related 关系（tag 重叠 >= 2）
                self._build_relations(mid, tags)
                result = {"id": mid, "action": "created"}
            if not was_in_transaction:
                self.conn.commit()
            return result
        except Exception:
            if not was_in_transaction:
                self.conn.rollback()
            raise
        finally:
            if not was_in_transaction:
                _conn_mod._in_transaction = False

    def _build_insert(self, mid: str, content: str, tags: list[str], source: str,
                       session_id: int, now: str, extra: dict[str, Any]) -> tuple[str, list]:
        """子类覆盖以添加额外字段"""
        raise NotImplementedError

    def _update_existing(self, mid: str, content: str, tags: list[str],
                         session_id: int, embedding: list[float]) -> dict:
        """更新已有记忆（始终在 insert() 的事务内调用）"""
        from aivectormemory.summarizer import generate_summary
        now = self._now()
        self.conn.execute(
            f"UPDATE {self.TABLE} SET content=?, tags=?, session_id=?, updated_at=? WHERE id=?",
            (content, json.dumps(tags, ensure_ascii=False), session_id, now, mid))
        self.conn.execute(f"DELETE FROM {self.VEC_TABLE} WHERE id=?", (mid,))
        self.conn.execute(f"INSERT INTO {self.VEC_TABLE} (id, embedding) VALUES (?,?)", (mid, json.dumps(embedding)))
        self._sync_tags(mid, tags)
        # T3.2: FTS5 同步
        fts_table = f"fts_{self.TABLE}"
        self.conn.execute(f"DELETE FROM {fts_table} WHERE id = ?", [mid])
        tokenized = tokenize_for_fts(content)
        self.conn.execute(f"INSERT INTO {fts_table}(id, content) VALUES (?, ?)", [mid, tokenized])
        # T15.3: 自动摘要 — 更新时重新生成
        summary = generate_summary(content)
        try:
            self.conn.execute(f"UPDATE {self.TABLE} SET summary=? WHERE id=?", [summary or '', mid])
        except Exception:
            pass  # v14 迁移前 summary 字段不存在
        return {"id": mid, "action": "updated"}

    def _check_similar(self, embedding: list[float], dedup_threshold: float,
                       conflict_threshold: float) -> tuple[str, str | None, list[str]]:
        """返回 (action, dup_id, conflict_ids)"""
        rows = self.conn.execute(
            f"SELECT id, distance FROM {self.VEC_TABLE} WHERE embedding MATCH ? AND k = 5",
            (json.dumps(embedding),)
        ).fetchall()
        conflicts = []
        for r in rows:
            if not self._is_same_scope(r["id"]):
                continue
            similarity = 1 - (r["distance"] ** 2) / 2
            if similarity >= dedup_threshold:
                return ("update", r["id"], [])
            if similarity >= conflict_threshold:
                conflicts.append(r["id"])
        return ("insert", None, conflicts)

    def _create_supersedes_relations(self, conn, new_id: str, conflict_ids: list[str]) -> None:
        db_scope = 'user' if self.TABLE == 'user_memories' else 'project'
        now = self._now()
        for old_id in conflict_ids:
            conn.execute(
                "INSERT OR IGNORE INTO memory_relations(memory_id, related_id, relation_type, scope, created_at) VALUES (?, ?, 'supersedes', ?, ?)",
                [new_id, old_id, db_scope, now]
            )

    def _reduce_importance(self, conn, conflict_ids: list[str], table: str) -> None:
        for old_id in conflict_ids:
            conn.execute(
                f"UPDATE {table} SET importance = importance * 0.3 WHERE id = ?",
                [old_id]
            )

    def _build_relations(self, new_id: str, tags: list[str]) -> None:
        """tag 重叠 >= 2 时建立 related 关系，每条记忆最多 10 条"""
        if len(tags) < 2:
            return

        scope = 'user' if self.TABLE == 'user_memories' else 'project'
        placeholders = ','.join('?' * len(tags))
        rows = self.conn.execute(f"""
            SELECT mt.memory_id, COUNT(*) as overlap
            FROM {self.TAG_TABLE} mt
            WHERE mt.tag IN ({placeholders})
            AND mt.memory_id != ?
            GROUP BY mt.memory_id
            HAVING overlap >= 2
            ORDER BY overlap DESC
            LIMIT 10
        """, tags + [new_id]).fetchall()

        now = self._now()
        for row in rows:
            related_id = row[0] if isinstance(row, tuple) else row['memory_id']
            self.conn.execute(
                "INSERT OR IGNORE INTO memory_relations(memory_id, related_id, relation_type, scope, created_at) VALUES (?, ?, 'related', ?, ?)",
                [new_id, related_id, scope, now]
            )

    def _is_same_scope(self, mid: str) -> bool:
        """子类覆盖：MemoryRepo 需检查 project_dir，UserMemoryRepo 直接返回 True"""
        return True

    def search_by_vector(self, embedding: list[float], top_k: int = 5, **filters) -> list[dict]:
        multiplier = 3
        while multiplier <= 10:
            k = top_k * multiplier
            rows = self.conn.execute(
                f"SELECT id, distance FROM {self.VEC_TABLE} WHERE embedding MATCH ? AND k = ?",
                (json.dumps(embedding), k)
            ).fetchall()
            results = self._filter_and_collect(rows, top_k, filters)
            if len(results) >= top_k or multiplier >= 10:
                return results
            multiplier += 2
        return results

    def _filter_and_collect(self, rows: list, top_k: int, filters: dict) -> list[dict]:
        results = []
        for r in rows:
            row = self.conn.execute(f"SELECT * FROM {self.TABLE} WHERE id=?", (r["id"],)).fetchone()
            if not row:
                continue
            d = dict(row)
            if not self._match_filters(d, filters):
                continue
            d["distance"] = r["distance"]
            results.append(d)
            if len(results) >= top_k:
                break
        return results

    def _match_filters(self, mem: dict, filters: dict) -> bool:
        """子类覆盖以添加过滤逻辑"""
        tier = filters.get("tier")
        if tier and mem.get("tier", "short_term") != tier:
            return False
        return True

    def search_by_vector_with_tags(self, embedding: list[float], tags: list[str],
                                    top_k: int = 5, **filters) -> list[dict]:
        import numpy as np
        tier = filters.pop("tier", None)
        candidates = self.list_by_tags(tags, limit=1000, tags_mode="any", **filters)
        # T12: tier 过滤
        if tier:
            candidates = [c for c in candidates if c.get("tier", "short_term") == tier]
        if not candidates:
            return []
        query_vec = np.array(embedding, dtype=np.float32)
        final = []
        for mem in candidates:
            row = self.conn.execute(f"SELECT embedding FROM {self.VEC_TABLE} WHERE id=?", (mem["id"],)).fetchone()
            if not row:
                continue
            raw = row["embedding"]
            vec = np.frombuffer(raw, dtype=np.float32) if isinstance(raw, (bytes, memoryview)) else np.array(json.loads(raw), dtype=np.float32)
            cos_sim = float(np.dot(query_vec, vec) / (np.linalg.norm(query_vec) * np.linalg.norm(vec) + 1e-9))
            d = dict(mem)
            d["distance"] = float(np.sqrt(2 * (1 - cos_sim)))
            final.append(d)
        final.sort(key=lambda x: x["distance"])
        return final[:top_k]

    def delete(self, mid: str) -> bool:
        cur = self.conn.execute(f"DELETE FROM {self.TABLE} WHERE id=?", (mid,))
        self.conn.execute(f"DELETE FROM {self.VEC_TABLE} WHERE id=?", (mid,))
        if self.TAG_TABLE:
            self.conn.execute(f"DELETE FROM {self.TAG_TABLE} WHERE memory_id=?", (mid,))
        # T3.3: FTS5 同步清理
        fts_table = f"fts_{self.TABLE}"
        self.conn.execute(f"DELETE FROM {fts_table} WHERE id = ?", [mid])
        # T8: memory_relations 级联清理
        self.conn.execute("DELETE FROM memory_relations WHERE memory_id = ? OR related_id = ?", [mid, mid])
        self._commit()
        return cur.rowcount > 0

    def get_by_id(self, mid: str) -> dict | None:
        row = self.conn.execute(f"SELECT * FROM {self.TABLE} WHERE id=?", (mid,)).fetchone()
        return dict(row) if row else None

    def list_by_tags(self, tags: list[str], limit: int = 100, **filters) -> list[dict]:
        """子类覆盖"""
        raise NotImplementedError

    def get_tag_counts(self, **filters) -> dict[str, int]:
        """子类覆盖"""
        raise NotImplementedError

    def get_ids_with_tag(self, tag: str, **filters) -> list[dict]:
        """子类覆盖"""
        raise NotImplementedError

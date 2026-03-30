from datetime import datetime, timezone

import jieba

from aivectormemory.config import DEFAULT_TOP_K
from aivectormemory.db.memory_repo import MemoryRepo
from aivectormemory.db.user_memory_repo import UserMemoryRepo
from aivectormemory.db.issue_repo import IssueRepo
from aivectormemory.errors import success_response
from aivectormemory.utils import distance_to_similarity
from aivectormemory.i18n.responses import to_json
from aivectormemory.scoring import composite_score
from aivectormemory.utils import normalize_tags


BRIEF_KEYS = {"content", "tags"}


def _to_brief(rows):
    result = []
    for r in rows:
        # T15.4: brief 模式下用 summary 替代完整 content
        if r.get('summary'):
            r = dict(r)
            r['content'] = r['summary']
        result.append({k: r[k] for k in BRIEF_KEYS if k in r})
    return result


def _add_similarity(rows):
    results = []
    for r in rows:
        distance = r.pop("distance", 0)
        r["similarity"] = distance_to_similarity(distance)
        results.append(r)
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# FTS5 full-text search
# ---------------------------------------------------------------------------

def fts_search(conn, query: str, scope: str, top_k: int = 20, tier: str | None = None) -> list[dict]:
    """FTS5 full-text search, returns [{id, content, ...}, ...]"""
    fts_table = "fts_user_memories" if scope == "user" else "fts_memories"
    main_table = "user_memories" if scope == "user" else "memories"
    tokenized = " ".join(jieba.cut(query))
    try:
        sql = (f"SELECT m.* FROM {main_table} m "
               f"JOIN {fts_table} f ON f.id = m.id "
               f"WHERE {fts_table} MATCH ?")
        params: list = [tokenized]
        if tier:
            sql += " AND m.tier = ?"
            params.append(tier)
        sql += " ORDER BY rank LIMIT ?"
        params.append(top_k)
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Reciprocal Rank Fusion
# ---------------------------------------------------------------------------

def rrf_merge(vec_results: list[dict], fts_results: list[dict], k: int = 60) -> list[dict]:
    """RRF merge vector search and FTS5 search results."""
    scores: dict[str, float] = {}
    all_items: dict[str, dict] = {}

    for rank, item in enumerate(vec_results):
        mid = item["id"]
        scores[mid] = scores.get(mid, 0) + 1.0 / (k + rank + 1)
        all_items[mid] = item

    for rank, item in enumerate(fts_results):
        mid = item["id"]
        scores[mid] = scores.get(mid, 0) + 1.0 / (k + rank + 1)
        if mid not in all_items:
            all_items[mid] = item

    sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
    result = []
    for mid in sorted_ids:
        item = all_items[mid]
        item["rrf_score"] = scores[mid]
        result.append(item)
    return result


# ---------------------------------------------------------------------------
# Composite scoring + access tracking
# ---------------------------------------------------------------------------

def _apply_composite_score(merged: list[dict], conn, table: str):
    """Apply composite_score() to merged results and sort in-place."""
    if not merged:
        return
    max_ac_row = conn.execute(f"SELECT MAX(access_count) FROM {table}").fetchone()
    max_ac = (max_ac_row[0] if max_ac_row and max_ac_row[0] else 1)

    for m in merged:
        m["score"] = composite_score(
            similarity=m.get("rrf_score", m.get("similarity", 0.5)),
            last_accessed_at=m.get("last_accessed_at") or m.get("created_at", ""),
            access_count=m.get("access_count", 0),
            max_access_count=max_ac,
            importance=m.get("importance", 0.5),
        )
    merged.sort(key=lambda x: x["score"], reverse=True)


def _update_access(conn, table: str, results: list[dict]):
    """Batch update access_count / last_accessed_at for returned results, auto-promote to long_term."""
    if not results:
        return
    now = datetime.now(timezone.utc).isoformat()
    for m in results:
        conn.execute(
            f"UPDATE {table} SET access_count = access_count + 1, last_accessed_at = ? WHERE id = ?",
            [now, m["id"]],
        )
        # T12.3: 自动晋升 — access_count+1 后 >= 3 且当前 short_term → long_term
        conn.execute(
            f"UPDATE {table} SET tier = 'long_term' WHERE id = ? AND access_count >= 3 AND tier = 'short_term'",
            [m["id"]],
        )
    conn.commit()


# ---------------------------------------------------------------------------
# Relation expansion (1-hop related) — T14
# ---------------------------------------------------------------------------

def _expand_relations(conn, memory_ids: list[str], scope: str) -> list[dict]:
    """沿 related 关系扩展 1 跳，返回关联记忆"""
    if not memory_ids:
        return []

    db_scope = 'user' if scope == 'user' else 'project'
    table = 'user_memories' if scope == 'user' else 'memories'
    ph = ','.join('?' * len(memory_ids))

    rows = conn.execute(f"""
        SELECT DISTINCT m.* FROM {table} m
        JOIN memory_relations r ON (
            (r.related_id = m.id AND r.memory_id IN ({ph}))
            OR (r.memory_id = m.id AND r.related_id IN ({ph}))
        )
        WHERE r.relation_type = 'related' AND r.scope = ?
        AND m.id NOT IN ({ph})
    """, memory_ids + memory_ids + [db_scope] + memory_ids).fetchall()

    return [dict(r) for r in rows]


def _apply_expand_relations(conn, results: list[dict], scope: str, top_k: int) -> list[dict]:
    """对结果集应用关系扩展：score * 0.7 衰减合并"""
    hit_ids = [m['id'] for m in results]
    scopes = ['user', 'project'] if scope == 'all' else [scope]
    related: list[dict] = []
    for s in scopes:
        related.extend(_expand_relations(conn, hit_ids, s))

    for m in related:
        m['score'] = m.get('score', 0.5) * 0.7
        m['_from_relation'] = True
    results.extend(related)
    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    return results[:top_k]


# ---------------------------------------------------------------------------
# Superseded filtering
# ---------------------------------------------------------------------------

def _load_superseded_ids(conn, scope: str) -> set[str]:
    """Load IDs of memories that have been superseded."""
    db_scope = "user" if scope == "user" else "project"
    rows = conn.execute(
        "SELECT DISTINCT related_id FROM memory_relations WHERE relation_type = 'supersedes' AND scope = ?",
        [db_scope],
    ).fetchall()
    return {r[0] for r in rows}


# ---------------------------------------------------------------------------
# Main handler
# ---------------------------------------------------------------------------

def handle_recall(args, *, cm, engine, **_):
    source = args.get("source")

    if source == "experience":
        return _recall_experience(args, cm=cm, engine=engine)

    scope = args.get("scope", "all")
    query = args.get("query")
    tags = normalize_tags(args.get("tags"))
    top_k = min(max(int(args.get("top_k", DEFAULT_TOP_K)), 1), 100)
    brief = args.get("brief", False)
    tags_mode = args.get("tags_mode", "any" if query and tags else "all")
    exclude_superseded = args.get("exclude_superseded", True)
    tier = args.get("tier")  # T12: 指定搜索层级
    expand_relations = args.get("expand_relations", False)  # T14: 关系扩展

    if scope == "user":
        rows = _query_user(cm, engine, query, tags, top_k, source, tags_mode, exclude_superseded, tier)
    elif scope == "project":
        rows = _query_project(cm, engine, query, tags, top_k, source, tags_mode, exclude_superseded, tier)
    else:
        rows = _query_all(cm, engine, query, tags, top_k, source, tags_mode, exclude_superseded, tier)

    # T14: 关系扩展
    if expand_relations:
        rows = _apply_expand_relations(cm.conn, rows, scope, top_k)

    return to_json(success_response(memories=_to_brief(rows) if brief else rows))


def _query_user(cm, engine, query, tags, top_k, source, tags_mode="all", exclude_superseded=True, tier=None):
    repo = UserMemoryRepo(cm.conn)
    return _query_scope(cm, engine, repo, query, tags, top_k, source, tags_mode, exclude_superseded, tier,
                        table="user_memories", scope="user")


def _search_tier(cm, engine, repo, query, tags, top_k, tier, exclude_superseded, table, scope, filters=None):
    """统一的分层搜索：同时适用于 user_memories 和 memories"""
    embedding = engine.encode(query)
    if tags:
        kw = filters or {}
        kw["tier"] = tier
        vec = _add_similarity(repo.search_by_vector_with_tags(embedding, tags, top_k=top_k * 2, **kw))
    else:
        vec = _add_similarity(repo.search_by_vector(embedding, top_k=top_k * 2, tier=tier) if not filters
                              else repo.search_by_vector(embedding, top_k=top_k * 2, **{**filters, "tier": tier}))

    fts = fts_search(cm.conn, query, scope=scope, top_k=top_k * 2, tier=tier)
    merged = rrf_merge(vec, fts)

    if exclude_superseded:
        superseded_ids = _load_superseded_ids(cm.conn, scope)
        if superseded_ids:
            merged = [m for m in merged if m["id"] not in superseded_ids]

    _apply_composite_score(merged, cm.conn, table)
    return merged[:top_k]


def _query_scope(cm, engine, repo, query, tags, top_k, source, tags_mode, exclude_superseded, tier, table, scope):
    """统一的 scope 查询逻辑"""
    filters = {"scope": scope, "project_dir": cm.project_dir, "source": source} if scope == "project" else None
    if not query:
        if not tags:
            raise ValueError("query or tags is required")
        if scope == "project":
            rows = repo.list_by_tags(tags, scope="project", project_dir=cm.project_dir, limit=top_k, source=source, tags_mode=tags_mode)
        else:
            rows = repo.list_by_tags(tags, limit=top_k, source=source, tags_mode=tags_mode)
        for r in rows:
            r["similarity"] = 1.0
        if tier:
            rows = [r for r in rows if r.get("tier", "short_term") == tier]
        return rows

    tiers_to_search = [tier] if tier else ["long_term", "short_term"]
    final = []
    for t in tiers_to_search:
        remaining = top_k - len(final)
        if remaining <= 0:
            break
        tier_filters = {**filters, "tier": t} if filters else None
        tier_results = _search_tier(cm, engine, repo, query, tags, remaining, t, exclude_superseded,
                                    table, scope, filters=filters)
        final.extend(tier_results)

    _update_access(cm.conn, table, final)
    return final


def _query_project(cm, engine, query, tags, top_k, source, tags_mode="all", exclude_superseded=True, tier=None):
    repo = MemoryRepo(cm.conn, cm.project_dir)
    return _query_scope(cm, engine, repo, query, tags, top_k, source, tags_mode, exclude_superseded, tier,
                        table="memories", scope="project")


def _query_all(cm, engine, query, tags, top_k, source, tags_mode="all", exclude_superseded=True, tier=None):
    proj = _query_project(cm, engine, query, tags, top_k, source, tags_mode, exclude_superseded, tier)
    user = _query_user(cm, engine, query, tags, top_k, source, tags_mode, exclude_superseded, tier)
    merged = proj + user
    merged.sort(key=lambda x: x.get("score", x.get("similarity", 0)), reverse=True)
    return merged[:top_k]


def _recall_experience(args, *, cm, engine):
    query = args.get("query")
    if not query:
        raise ValueError("query is required for source=experience")
    top_k = min(max(int(args.get("top_k", DEFAULT_TOP_K)), 1), 100)
    brief = args.get("brief", False)

    embedding = engine.encode(query)
    issue_repo = IssueRepo(cm.conn, cm.project_dir, engine=engine)
    rows = issue_repo.search_archive_by_vector(embedding, top_k=top_k)

    results = []
    for r in rows:
        content = f"{r['title']}\n根因：{r['root_cause'] or ''}\n方案：{r['solution'] or ''}"
        results.append({
            "id": r["id"],
            "content": content,
            "tags": ["经验"],
            "similarity": r["similarity"],
        })
    return to_json(success_response(memories=_to_brief(results) if brief else results))

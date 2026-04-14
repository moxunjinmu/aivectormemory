from aivectormemory.db.graph_repo import GraphRepo


def get_graph(cm, params, pdir):
    """获取全量节点和边，供前端图谱渲染"""
    repo = GraphRepo(cm.conn, pdir)
    entity_type = params.get("entity_type", [None])[0]
    name = params.get("name", [None])[0]
    nodes = repo.query_nodes(name=name, entity_type=entity_type)
    node_ids = {n["id"] for n in nodes}
    rows = cm.conn.execute(
        "SELECT * FROM graph_edges WHERE source_id IN "
        f"({','.join('?' * len(node_ids))}) OR target_id IN "
        f"({','.join('?' * len(node_ids))})",
        list(node_ids) + list(node_ids)
    ).fetchall() if node_ids else []
    edges = [dict(r) if hasattr(r, "keys") else r for r in rows]
    return {"nodes": nodes, "edges": edges, "node_count": len(nodes), "edge_count": len(edges)}


def get_graph_stats(cm, pdir):
    """图谱统计：按实体类型分组计数"""
    conn = cm.conn
    node_rows = conn.execute(
        "SELECT entity_type, COUNT(*) as count FROM graph_nodes WHERE project_dir = ? GROUP BY entity_type",
        [pdir]
    ).fetchall()
    edge_rows = conn.execute(
        "SELECT relation, COUNT(*) as count FROM graph_edges e "
        "JOIN graph_nodes n ON e.source_id = n.id WHERE n.project_dir = ? GROUP BY relation",
        [pdir]
    ).fetchall()
    total_nodes = sum(r["count"] if hasattr(r, "keys") else r[1] for r in node_rows)
    total_edges = sum(r["count"] if hasattr(r, "keys") else r[1] for r in edge_rows)
    return {
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "by_type": {(r["entity_type"] if hasattr(r, "keys") else r[0]): (r["count"] if hasattr(r, "keys") else r[1]) for r in node_rows},
        "by_relation": {(r["relation"] if hasattr(r, "keys") else r[0]): (r["count"] if hasattr(r, "keys") else r[1]) for r in edge_rows},
    }


def trace_graph(cm, params, pdir, node_ref):
    """从指定节点 trace 遍历"""
    repo = GraphRepo(cm.conn, pdir)
    direction = params.get("direction", ["both"])[0]
    max_depth = int(params.get("max_depth", ["3"])[0])
    max_depth = max(1, min(5, max_depth))
    try:
        result = repo.trace(start=node_ref, direction=direction, max_depth=max_depth)
        return result
    except ValueError as e:
        return {"error": str(e)}

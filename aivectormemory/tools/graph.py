from aivectormemory.db.graph_repo import GraphRepo
from aivectormemory.errors import success_response
from aivectormemory.i18n.responses import to_json


def handle_graph(args, *, cm, **_):
    action = args.get("action")
    repo = GraphRepo(cm.conn, cm.project_dir)

    if action == "add_node":
        result = repo.upsert_node(
            name=args["name"],
            entity_type=args["entity_type"],
            file_path=args.get("file_path", ""),
            line_number=args.get("line_number", 0),
            description=args.get("description", ""),
            memory_id=args.get("memory_id", ""),
            metadata=args.get("metadata"),
        )
        return to_json(success_response(node=result))

    if action == "add_edge":
        result = repo.insert_edge(
            source=args["source"],
            target=args["target"],
            relation=args["relation"],
            label=args.get("label", ""),
            metadata=args.get("metadata"),
        )
        return to_json(success_response(edge=result))

    if action == "remove":
        node_id = args.get("node_id")
        edge_id = args.get("edge_id")
        if node_id:
            repo.remove_node(node_id)
            return to_json(success_response(removed="node", id=node_id))
        if edge_id:
            repo.remove_edge(int(edge_id))
            return to_json(success_response(removed="edge", id=edge_id))
        raise ValueError("remove 需要 node_id 或 edge_id")

    if action == "query":
        nodes = repo.query_nodes(
            name=args.get("name"),
            entity_type=args.get("entity_type"),
            file_path=args.get("file_path"),
        )
        return to_json(success_response(nodes=nodes, count=len(nodes)))

    if action == "trace":
        result = repo.trace(
            start=args["start"],
            relation=args.get("relation"),
            direction=args.get("direction", "down"),
            max_depth=min(max(int(args.get("max_depth", 3)), 1), 5),
            cross_project=args.get("cross_project", False),
        )
        return to_json(success_response(**result))

    if action == "batch":
        with cm.transaction():
            result = repo.batch_upsert(
                nodes=args.get("nodes", []),
                edges=args.get("edges", []),
            )
        return to_json(success_response(**result))

    if action == "refresh":
        stale_nodes = repo.refresh(file_path=args.get("file_path"))
        return to_json(success_response(stale_nodes=stale_nodes, count=len(stale_nodes)))

    raise ValueError(f"未知 action: {action}")

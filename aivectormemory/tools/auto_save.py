from aivectormemory.config import DEDUP_THRESHOLD
from aivectormemory.db.memory_repo import MemoryRepo
from aivectormemory.db.user_memory_repo import UserMemoryRepo
from aivectormemory.i18n.responses import fmt
from aivectormemory.tools.keywords import enrich_tags
from aivectormemory.utils import normalize_tags, contains_project_path


def handle_auto_save(args, *, cm, engine, session_id, **_):
    items = normalize_tags(args.get("preferences")) or []
    if not items:
        return fmt("auto_save.empty")

    user_repo = UserMemoryRepo(cm.conn)
    project_repo = MemoryRepo(cm.conn, cm.project_dir)
    saved = []
    with cm.transaction():
        for item in items:
            if not item or not isinstance(item, str):
                continue
            item = item[:5000] if len(item) > 5000 else item
            embedding = engine.encode(item)
            tags = ["preference"] + (normalize_tags(args.get("extra_tags")) or [])
            # 自动从 item 提取关键词补充到 tags
            enrich_tags(tags, item)
            # 含项目路径的偏好降级为项目记忆
            if contains_project_path(item):
                result = project_repo.insert(item, tags, "project", session_id, embedding, DEDUP_THRESHOLD, source="auto_save")
            else:
                result = user_repo.insert(item, tags, session_id, embedding, DEDUP_THRESHOLD, source="auto_save")
            saved.append({"id": result["id"], "action": result["action"], "category": "preferences"})

    return fmt("auto_save", count=len(saved))

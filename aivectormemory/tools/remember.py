from aivectormemory.config import DEDUP_THRESHOLD
from aivectormemory.db.memory_repo import MemoryRepo
from aivectormemory.db.user_memory_repo import UserMemoryRepo
from aivectormemory.i18n.responses import fmt
from aivectormemory.tools.keywords import enrich_tags
from aivectormemory.utils import validate_content, validate_tags, contains_project_path


def handle_remember(args, *, cm, engine, session_id, **_):
    content = validate_content(args.get("content", ""))
    tags = validate_tags(args.get("tags", []))
    scope = args.get("scope", "project")

    # 含项目路径的内容禁止存为全局记忆，自动降级为项目记忆
    if scope == "user" and contains_project_path(content):
        scope = "project"

    if len(content) > 5000:
        content = content[:5000]

    # 自动从 content 提取关键词补充到 tags
    enrich_tags(tags, content)

    embedding = engine.encode(content)

    if scope == "user":
        repo = UserMemoryRepo(cm.conn)
        result = repo.insert(content, tags, session_id, embedding, DEDUP_THRESHOLD)
    else:
        repo = MemoryRepo(cm.conn, cm.project_dir)
        result = repo.insert(content, tags, scope, session_id, embedding, DEDUP_THRESHOLD)

    return fmt(f"remember.{result['action']}", id=result["id"], tags=tags)

from aivectormemory.db.issue_repo import IssueRepo
from aivectormemory.db.task_repo import TaskRepo


def get_issues(cm, params, pdir):
    date = params.get("date", [None])[0]
    status = params.get("status", [None])[0]
    keyword = params.get("keyword", [None])[0]
    try:
        limit = int(params.get("limit", [20])[0])
    except (ValueError, TypeError):
        limit = 20
    try:
        offset = int(params.get("offset", [0])[0])
    except (ValueError, TypeError):
        offset = 0
    limit = max(1, min(limit, 500))
    offset = max(0, min(offset, 100000))
    repo = IssueRepo(cm.conn, pdir)
    if status == "archived":
        issues, total = repo.list_archived(date=date, limit=limit, offset=offset, keyword=keyword)
    elif status == "all":
        issues, total = repo.list_all(date=date, limit=limit, offset=offset, keyword=keyword)
    elif status:
        issues, total = repo.list_by_date(date=date, status=status, limit=limit, offset=offset, keyword=keyword)
    else:
        issues, total = repo.list_by_date(date=date, limit=limit, offset=offset, keyword=keyword)
    task_repo = TaskRepo(cm.conn, pdir)
    fids = list({i.get("feature_id", "") for i in issues if i.get("feature_id")})
    progress_map = task_repo.get_task_progress_batch(fids) if fids else {}
    for issue in issues:
        fid = issue.get("feature_id", "")
        if fid and fid in progress_map:
            issue["task_progress"] = progress_map[fid]
    return {"issues": issues, "total": total}


def put_issue(handler, cm, iid, pdir):
    from aivectormemory.web.api import _read_body
    body = _read_body(handler)
    repo = IssueRepo(cm.conn, pdir)
    old = repo.get_by_id(iid)
    if not old:
        return {"error": "not found"}
    fields = {k: body[k] for k in ("title", "status", "content",
              "description", "investigation", "root_cause", "solution",
              "files_changed", "test_result", "notes", "feature_id") if k in body}
    result = repo.update(iid, **fields)
    if not result:
        return {"error": "not found"}
    return result


def post_issue(handler, cm, pdir):
    from aivectormemory.web.api import _read_body
    body = _read_body(handler)
    title = body.get("title", "").strip()
    if not title:
        return {"error": "title required"}
    content = body.get("content", "")
    from datetime import date
    d = body.get("date", date.today().isoformat())

    repo = IssueRepo(cm.conn, pdir)
    parent_id = body.get("parent_id", 0)
    result = repo.create(d, title, content, parent_id=parent_id)
    if result.get("deduplicated"):
        return result

    return result


def delete_issue(handler, cm, iid, pdir, params, is_archived=False):
    action = params.get("action", ["delete"])[0]
    repo = IssueRepo(cm.conn, pdir)

    if action == "archive":
        result = repo.archive(iid)
        if not result:
            return {"error": "not found"}
        return result

    if is_archived:
        result = repo.delete_archived(iid)
    else:
        result = repo.delete(iid)
    if not result:
        return {"error": "not found"}
    return result

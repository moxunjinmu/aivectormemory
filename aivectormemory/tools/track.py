import json
from datetime import date
from aivectormemory.db.issue_repo import IssueRepo
from aivectormemory.errors import success_response


def handle_track(args, *, cm, **_):
    action = args.get("action")
    if not action:
        raise ValueError("action is required")

    repo = IssueRepo(cm.conn, cm.project_dir)
    today = date.today().isoformat()

    if action == "create":
        title = args.get("title")
        if not title:
            raise ValueError("title is required for create")
        d = args.get("date", today)
        result = repo.create(d, title, args.get("content", ""), args.get("memory_id", ""))
        return json.dumps(success_response(**result))

    elif action == "update":
        issue_id = args.get("issue_id")
        if not issue_id:
            raise ValueError("issue_id is required for update")
        fields = {k: args[k] for k in ("title", "status", "content", "memory_id") if k in args}
        result = repo.update(issue_id, **fields)
        if not result:
            raise ValueError(f"Issue {issue_id} not found")
        return json.dumps(success_response(issue=result))

    elif action == "archive":
        issue_id = args.get("issue_id")
        if not issue_id:
            raise ValueError("issue_id is required for archive")
        content = args.get("content")
        if content:
            repo.update(issue_id, content=content)
        result = repo.archive(issue_id)
        if not result:
            raise ValueError(f"Issue {issue_id} not found")
        return json.dumps(success_response(**result))

    elif action == "list":
        d = args.get("date")
        status = args.get("status")
        include_archived = args.get("include_archived", False)
        issues = repo.list_by_date(date=d, status=status)
        if include_archived:
            archived = repo.list_archived(date=d)
            issues = issues + archived
        return json.dumps(success_response(issues=issues))

    else:
        raise ValueError(f"Unknown action: {action}")

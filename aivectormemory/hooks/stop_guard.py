"""AIVectorMemory Stop Hook

检查 7 项：1) 手动操作词  2) 前端测试  3) 后端测试  4) commit前测试
          5) grep副作用检查  6) track update  7) status设阻塞

用法: python3 -m aivectormemory.hooks.stop_guard
stdin: JSON（transcript_path）
exit 0: 放行  exit 2: 阻断
"""
import json
import os
import sys
from pathlib import Path

from aivectormemory.hooks._common import read_stdin, get_transcript_path, block
from aivectormemory.hooks._messages import get_message

FRONTEND_EXTS = {".ts", ".tsx", ".js", ".jsx", ".vue", ".css", ".html", ".svelte"}
BACKEND_EXTS = {".py", ".go", ".rs", ".java", ".rb", ".php", ".swift", ".kt"}

MANUAL_WORDS = [
    "手动", "刷新浏览器", "请用户", "请自行", "你需要打开",
    "你需要访问", "你需要刷新", "请手动", "用户需要", "请你自己",
    # English equivalents
    "manually", "refresh the browser", "please open", "you need to open",
    "please refresh", "user should",
]

BYPASS_FRONTEND = "此改动不影响前端"
BYPASS_BACKEND = "此改动不影响后端"
BYPASS_FRONTEND_EN = "this change does not affect the frontend"
BYPASS_BACKEND_EN = "this change does not affect the backend"


def main() -> int:
    data = read_stdin()
    transcript_path = get_transcript_path(data)
    if not transcript_path or not Path(transcript_path).exists():
        return 0

    messages = []
    with open(transcript_path) as f:
        for line in f:
            try:
                messages.append(json.loads(line))
            except Exception:
                pass

    # 找最后一条 user 消息（当前轮次起点）
    last_user_idx = -1
    for i, msg in enumerate(messages):
        if msg.get("role") == "user":
            last_user_idx = i
    if last_user_idx == -1:
        return 0

    frontend_edited = False
    backend_edited = False
    playwright_used = False
    backend_test_used = False
    git_committed = False
    has_manual_words = False
    has_bypass_frontend = False
    has_bypass_backend = False
    test_before_commit = False
    grep_used = False          # G2: 副作用检查
    track_updated = False      # G4: track update 调用
    status_blocked = False     # H: status 设阻塞

    for msg in messages[last_user_idx + 1:]:
        if msg.get("role") != "assistant":
            continue
        content = msg.get("content", [])
        if isinstance(content, str):
            for w in MANUAL_WORDS:
                if w in content:
                    has_manual_words = True
            if BYPASS_FRONTEND in content or BYPASS_FRONTEND_EN in content.lower():
                has_bypass_frontend = True
            if BYPASS_BACKEND in content or BYPASS_BACKEND_EN in content.lower():
                has_bypass_backend = True
            continue
        for blk in content:
            if blk.get("type") == "text":
                text = blk.get("text", "")
                for w in MANUAL_WORDS:
                    if w in text:
                        has_manual_words = True
                if BYPASS_FRONTEND in text or BYPASS_FRONTEND_EN in text.lower():
                    has_bypass_frontend = True
                if BYPASS_BACKEND in text or BYPASS_BACKEND_EN in text.lower():
                    has_bypass_backend = True
            if blk.get("type") == "tool_use":
                name = blk.get("name", "")
                inp = blk.get("input", {})
                if name in ("Edit", "Write"):
                    fp = inp.get("file_path", "")
                    ext = os.path.splitext(fp)[1].lower()
                    if ext in FRONTEND_EXTS:
                        frontend_edited = True
                    if ext in BACKEND_EXTS:
                        backend_edited = True
                if "playwright" in name and ("navigate" in name or "snapshot" in name):
                    playwright_used = True
                if name == "Bash":
                    cmd = inp.get("command", "")
                    if "pytest" in cmd or "curl " in cmd or "curl\n" in cmd:
                        backend_test_used = True
                        if not git_committed:
                            test_before_commit = True
                    if "git commit" in cmd or "git add" in cmd:
                        git_committed = True
                # G2: grep 副作用检查
                if name == "Grep" or (name == "Bash" and "grep " in inp.get("command", "")):
                    grep_used = True
                # G4: track update
                if name == "mcp__aivectormemory__track":
                    action = inp.get("action", "")
                    if action == "update":
                        track_updated = True
                # H: status 设阻塞
                if name == "mcp__aivectormemory__status":
                    state = inp.get("state", {})
                    if isinstance(state, dict) and state.get("is_blocked") is True:
                        status_blocked = True

    errors = []

    if has_manual_words:
        errors.append(get_message("manual_words_detected"))
    if frontend_edited and not playwright_used and not has_bypass_frontend:
        errors.append(get_message("frontend_no_playwright"))
    if backend_edited and not backend_test_used and not has_bypass_backend:
        errors.append(get_message("backend_no_test"))
    if git_committed and (frontend_edited or backend_edited) and not test_before_commit:
        errors.append(get_message("commit_before_test"))

    any_code_edited = frontend_edited or backend_edited
    any_test_done = playwright_used or backend_test_used

    # 检查5: 代码修改后未 grep 检查副作用
    if any_code_edited and not grep_used:
        errors.append(get_message("no_grep_after_edit"))

    # 检查6: 代码修改后未 track update
    if any_code_edited and not track_updated:
        errors.append(get_message("no_track_update_after_edit"))

    # 检查7: 代码修改 + 测试完成 但未设阻塞
    if any_code_edited and any_test_done and not status_blocked:
        errors.append(get_message("no_status_blocked"))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

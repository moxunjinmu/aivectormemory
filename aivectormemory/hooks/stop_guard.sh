#!/usr/bin/env bash
# AIVectorMemory Stop Hook
# 检查：1) 改了代码文件但没跑测试  2) 回复含"手动操作"类违规词  3) git commit 前未测试

INPUT=$(cat)
TRANSCRIPT=$(python3 -c "import sys,json;print(json.load(sys.stdin).get('transcript_path',''))" <<< "$INPUT" 2>/dev/null)

[ -z "$TRANSCRIPT" ] || [ ! -f "$TRANSCRIPT" ] && exit 0

python3 - "$TRANSCRIPT" << 'PYEOF'
import json, sys, os

transcript_path = sys.argv[1]
messages = []
with open(transcript_path) as f:
    for line in f:
        try:
            messages.append(json.loads(line))
        except Exception:
            pass

# 找到最后一条 user 消息的位置（当前轮次起点）
last_user_idx = -1
for i, msg in enumerate(messages):
    if msg.get("role") == "user":
        last_user_idx = i

if last_user_idx == -1:
    sys.exit(0)

# 文件扩展名分类
FRONTEND_EXTS = {".ts", ".tsx", ".js", ".jsx", ".vue", ".css", ".html", ".svelte"}
BACKEND_EXTS = {".py", ".go", ".rs", ".java", ".rb", ".php", ".swift", ".kt"}
CODE_EXTS = FRONTEND_EXTS | BACKEND_EXTS

MANUAL_WORDS = [
    "手动", "刷新浏览器", "请用户", "请自行", "你需要打开",
    "你需要访问", "你需要刷新", "请手动", "用户需要", "请你自己",
]
BYPASS_FRONTEND = "此改动不影响前端"
BYPASS_BACKEND = "此改动不影响后端"

frontend_edited = False
backend_edited = False
playwright_used = False
backend_test_used = False  # pytest / curl
git_committed = False
has_manual_words = False
has_bypass_frontend = False
has_bypass_backend = False
test_before_commit = False  # 测试在 commit 之前发生

for msg in messages[last_user_idx + 1:]:
    if msg.get("role") != "assistant":
        continue
    content = msg.get("content", [])
    if isinstance(content, str):
        text = content
        for w in MANUAL_WORDS:
            if w in text:
                has_manual_words = True
        if BYPASS_FRONTEND in text:
            has_bypass_frontend = True
        if BYPASS_BACKEND in text:
            has_bypass_backend = True
        continue
    for block in content:
        if block.get("type") == "text":
            text = block.get("text", "")
            for w in MANUAL_WORDS:
                if w in text:
                    has_manual_words = True
            if BYPASS_FRONTEND in text:
                has_bypass_frontend = True
            if BYPASS_BACKEND in text:
                has_bypass_backend = True
        if block.get("type") == "tool_use":
            name = block.get("name", "")
            inp = block.get("input", {})
            # 检测代码编辑
            if name in ("Edit", "Write"):
                fp = inp.get("file_path", "")
                ext = os.path.splitext(fp)[1].lower()
                if ext in FRONTEND_EXTS:
                    frontend_edited = True
                if ext in BACKEND_EXTS:
                    backend_edited = True
            # 检测 Playwright 测试
            if "playwright" in name and ("navigate" in name or "snapshot" in name):
                playwright_used = True
            # 检测后端测试（pytest / curl）
            if name == "Bash":
                cmd = inp.get("command", "")
                if "pytest" in cmd or "curl " in cmd or "curl\n" in cmd:
                    backend_test_used = True
                    if not git_committed:
                        test_before_commit = True
                # 检测 git commit
                if "git commit" in cmd or "git add" in cmd:
                    git_committed = True

any_code_edited = frontend_edited or backend_edited
any_test_done = playwright_used or backend_test_used

errors = []

# 检查1：手动操作词
if has_manual_words:
    errors.append("⚠️ 回复中包含让用户手动操作的内容（手动/刷新浏览器/请用户等）。禁止让用户手动操作，请自行使用 Playwright MCP 或 curl/pytest 完成验证。")

# 检查2：前端代码修改但没用 Playwright
if frontend_edited and not playwright_used and not has_bypass_frontend:
    errors.append("⚠️ 前端代码已修改但未使用 Playwright MCP 验证。影响前端 → browser_navigate + browser_snapshot 验证；不影响 → 明确说明「此改动不影响前端」及理由。")

# 检查3：后端代码修改但没跑测试
if backend_edited and not backend_test_used and not has_bypass_backend:
    errors.append("⚠️ 后端代码已修改但未运行测试（pytest/curl）。请先运行测试验证功能正常。不影响后端 → 明确说明「此改动不影响后端」及理由。")

# 检查4：git commit 但测试不在 commit 之前
if git_committed and any_code_edited and not test_before_commit:
    errors.append("⚠️ 检测到 git commit 但在提交前未运行测试。必须先完成 G1-G4 检查清单，测试通过后才能提交。")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(2)

sys.exit(0)
PYEOF

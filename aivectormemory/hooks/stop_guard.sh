#!/usr/bin/env bash
# AIVectorMemory Stop Hook
# 检查：1) 改了代码文件但没用 Playwright 验证  2) 回复含"手动操作"类违规词

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

CODE_EXTS = {".py", ".go", ".ts", ".tsx", ".js", ".jsx", ".vue", ".css", ".html", ".svelte", ".rs", ".java", ".rb", ".php", ".swift", ".kt"}
MANUAL_WORDS = ["手动", "刷新浏览器", "请用户", "请自行", "你需要打开", "你需要访问", "你需要刷新"]
BYPASS_PHRASE = "此改动不影响前端"

code_edited = False
playwright_used = False
has_manual_words = False
has_bypass = False

for msg in messages[last_user_idx + 1:]:
    if msg.get("role") != "assistant":
        continue
    content = msg.get("content", [])
    if isinstance(content, str):
        text = content
        for w in MANUAL_WORDS:
            if w in text:
                has_manual_words = True
        if BYPASS_PHRASE in text:
            has_bypass = True
        continue
    for block in content:
        if block.get("type") == "text":
            text = block.get("text", "")
            for w in MANUAL_WORDS:
                if w in text:
                    has_manual_words = True
            if BYPASS_PHRASE in text:
                has_bypass = True
        if block.get("type") == "tool_use":
            name = block.get("name", "")
            inp = block.get("input", {})
            if name in ("Edit", "Write"):
                fp = inp.get("file_path", "")
                ext = os.path.splitext(fp)[1].lower()
                if ext in CODE_EXTS:
                    code_edited = True
            if "playwright" in name and ("navigate" in name or "snapshot" in name):
                playwright_used = True

errors = []
if has_manual_words:
    errors.append("⚠️ 回复中包含让用户手动操作的内容（手动/刷新浏览器/请用户等）。禁止让用户手动操作，请自行使用 Playwright MCP 完成验证。")
if code_edited and not playwright_used and not has_bypass:
    errors.append("⚠️ 代码文件已修改但未使用 Playwright MCP 验证页面效果。请判断：此改动是否影响前端页面？影响 → 用 ToolSearch 加载 Playwright MCP，执行 browser_navigate + browser_snapshot 验证。不影响 → 在回复中明确说明「此改动不影响前端页面」及理由。")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(2)

sys.exit(0)
PYEOF

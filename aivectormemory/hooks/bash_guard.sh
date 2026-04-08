#!/usr/bin/env bash
# AIVectorMemory PreToolUse Hook (Bash)
# 拦截危险命令：open http / python3 -c 多行 / $(...)+管道 / mysql -e 多语句 / 部署命令
# git commit/push 不在此拦截 — 由 steering 规则约束 + stop_guard 事后兜底

INPUT=$(cat)
COMMAND=$(python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('tool_input',{}).get('command',''))" <<< "$INPUT" 2>/dev/null)

[ -z "$COMMAND" ] && exit 0

# 1. 拦截 open http:// / open https://
if echo "$COMMAND" | grep -qE '^\s*open\s+https?://'; then
  echo "⚠️ 禁止使用 open 命令打开浏览器。请使用 Playwright MCP（ToolSearch 加载后 browser_navigate）进行前端测试。" >&2
  exit 2
fi

# 2. 拦截 python3 -c 多行（含换行符）
if echo "$COMMAND" | grep -qE 'python3?\s+-c\s+'; then
  NEWLINES=$(printf '%s' "$COMMAND" | tr -cd '\n' | wc -c)
  if [ "$NEWLINES" -gt 1 ]; then
    echo "⚠️ 禁止 python3 -c 执行多行脚本（超过2行）。请写成 .py 文件用 python3 xxx.py 执行。" >&2
    exit 2
  fi
fi

# 3. 拦截 $(...) + 管道组合
if echo "$COMMAND" | grep -qE '\$\(.*\)\s*\|'; then
  echo "⚠️ 禁止 \$(…) + 管道组合，可能导致 IDE 卡死。请拆成多步独立执行。" >&2
  exit 2
fi

# 4. 拦截 mysql -e 多条语句
if echo "$COMMAND" | grep -qE 'mysql.*-e\s*["\x27].*;\s*.+;'; then
  echo "⚠️ 禁止 MySQL -e 执行多条语句。请写入 .sql 文件用 < data/xxx.sql 执行。" >&2
  exit 2
fi

# 5. 拦截部署命令（不可逆操作，硬阻断）
if echo "$COMMAND" | grep -qE 'sshpass\s.*\s(deploy|restart|docker|systemctl)|ssh\s.*\s(deploy|restart|docker|systemctl)|docker\s+(compose\s+up|restart)|systemctl\s+restart|kubectl\s+(apply|rollout|set)'; then
  echo "⚠️ 禁止自行部署。必须用户明确指示后才能执行部署操作。" >&2
  exit 2
fi

exit 0

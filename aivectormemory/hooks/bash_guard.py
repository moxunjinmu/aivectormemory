"""AIVectorMemory PreToolUse Hook (Bash)

拦截危险命令：open http / python3 -c 多行 / $(...)+管道 / mysql -e 多语句 / 部署命令
git commit/push 不在此拦截 — 由 steering 规则约束 + stop_guard 事后兜底

用法: python3 -m aivectormemory.hooks.bash_guard
stdin: Claude Code / Cursor / Windsurf / Codex / Copilot / Gemini 传入的 JSON
exit 0: 放行  exit 2: 阻断（stderr 消息反馈给 AI）
"""
import re
import sys

from aivectormemory.hooks._common import read_stdin, get_command, block
from aivectormemory.hooks._messages import get_message


def main() -> int:
    data = read_stdin()
    cmd = get_command(data)
    if not cmd:
        return 0

    # 1. open http:// / https://
    if re.search(r"^\s*open\s+https?://", cmd):
        return block(get_message("open_http_blocked"))

    # 2. python3 -c 多行（超过 2 行）
    if re.search(r"python3?\s+-c\s+", cmd) and cmd.count("\n") > 1:
        return block(get_message("python_multiline_blocked"))

    # 3. $(...) + 管道组合
    if re.search(r"\$\(.*\)\s*\|", cmd):
        return block(get_message("subshell_pipe_blocked"))

    # 4. mysql -e 多条语句
    if re.search(r"mysql.*-e\s*[\"'].*;\s*.+;", cmd):
        return block(get_message("mysql_multi_blocked"))

    # 5. 部署命令（不可逆操作，硬阻断）
    deploy_pattern = (
        r"sshpass\s.*\s(deploy|restart|docker|systemctl)"
        r"|ssh\s.*\s(deploy|restart|docker|systemctl)"
        r"|docker\s+(compose\s+up|restart)"
        r"|systemctl\s+restart"
        r"|kubectl\s+(apply|rollout|set)"
    )
    if re.search(deploy_pattern, cmd):
        return block(get_message("deploy_blocked"))

    return 0


if __name__ == "__main__":
    sys.exit(main())

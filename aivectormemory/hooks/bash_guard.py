"""AIVectorMemory PreToolUse Hook (Bash)

拦截毁灭性删除命令：rm -rf / | rm -rf ~ | rm -rf *

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

    # rm -rf 毁灭性删除（/, ~, *, /*, ~/）
    # 匹配: rm -rf / | rm -rf ~ | rm -rf * | rm -rf /* | rm -rf ~/
    # 不匹配: rm -rf ./build | rm -rf ~/Documents | rm -rf /tmp/xxx
    if re.search(r"\brm\s+-[a-zA-Z]*(rf|fr)[a-zA-Z]*\s+(/\*|/\s|/$|~\s|~$|~/\s|~/$|\*\s|\*$)", cmd):
        return block(get_message("rm_rf_blocked"))

    return 0


if __name__ == "__main__":
    sys.exit(main())

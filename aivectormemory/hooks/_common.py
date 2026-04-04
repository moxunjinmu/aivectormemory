"""AIVectorMemory Hooks — 跨 IDE 共享工具函数

兼容 Claude Code / Cursor / Windsurf / Kiro / OpenCode / Codex / Copilot / Gemini CLI
的 stdin JSON 格式差异。
"""
import json
import os
import sys


def read_stdin() -> dict:
    """读取 stdin JSON 输入，解析失败返回空 dict"""
    try:
        return json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        return {}


def get_command(data: dict) -> str:
    """提取 Bash/Shell 命令，兼容所有 IDE 格式

    - Claude Code / Cursor / Codex / Copilot(VSCode): tool_input.command
    - Windsurf: tool_info.command_line
    - Copilot(Cloud): toolArgs JSON string → command
    - Gemini CLI: tool_input.command (同 Claude Code)
    """
    # Claude Code / Cursor / Codex / Gemini
    cmd = data.get("tool_input", {}).get("command", "")
    if cmd:
        return cmd
    # Windsurf
    cmd = data.get("tool_info", {}).get("command_line", "")
    if cmd:
        return cmd
    # Copilot Cloud (toolArgs is JSON string)
    tool_args = data.get("toolArgs", "")
    if tool_args and isinstance(tool_args, str):
        try:
            args = json.loads(tool_args)
            cmd = args.get("command", "")
            if cmd:
                return cmd
        except (json.JSONDecodeError, ValueError):
            pass
    return ""


def get_file_path(data: dict) -> str:
    """提取文件路径，兼容所有 IDE 格式"""
    # Claude Code / Cursor / Codex / Gemini
    fp = data.get("tool_input", {}).get("file_path", "")
    if fp:
        return fp
    # Windsurf
    fp = data.get("tool_info", {}).get("file_path", "")
    if fp:
        return fp
    # Copilot Cloud
    tool_args = data.get("toolArgs", "")
    if tool_args and isinstance(tool_args, str):
        try:
            args = json.loads(tool_args)
            fp = args.get("file_path", args.get("filePath", ""))
            if fp:
                return fp
        except (json.JSONDecodeError, ValueError):
            pass
    return ""


def get_transcript_path(data: dict) -> str:
    """提取 transcript 路径"""
    return data.get("transcript_path", "")


def get_project_dir() -> str:
    """获取项目目录（优先环境变量，fallback 到 cwd）"""
    return os.environ.get("PROJECT_DIR", os.getcwd())


def block(message: str) -> int:
    """输出阻断消息到 stderr，返回退出码 2"""
    print(message, file=sys.stderr)
    return 2

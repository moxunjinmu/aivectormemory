"""aivectormemory install - 交互式为当前项目配置 MCP + Steering 规则"""
import json
import os
import re
import sys
from pathlib import Path
from aivectormemory.i18n import get_steering, get_workflow_prompt, get_compact_recovery_hints

# (IDE名, MCP配置路径, MCP格式, 是否全局, Steering路径, Steering写入方式, Hooks目录)
# steering_mode: "file"=独立文件 "append"=追加到已有文件 None=不写Steering
# hooks_dir: lambda返回hooks目录路径, None=不支持hooks
IDES = [
    ("Kiro",           lambda root: root / ".kiro/settings/mcp.json",  "standard", False,
     lambda root: root / ".kiro/steering/aivectormemory.md", "file",
     lambda root: root / ".kiro/hooks"),
    ("Cursor",         lambda root: root / ".cursor/mcp.json",         "standard", False,
     lambda root: root / ".cursor/rules/aivectormemory.md", "file",
     lambda root: root / ".cursor"),
    ("Claude Code",    lambda root: root / ".mcp.json",                "standard", False,
     lambda root: root / "CLAUDE.md", "append",
     lambda root: root / ".claude"),
    ("Windsurf",       lambda root: root / ".windsurf/mcp.json",       "windsurf", False,
     lambda root: root / ".windsurf/rules/aivectormemory.md", "file",
     lambda root: root / ".windsurf"),
    ("VSCode",         lambda root: root / ".vscode/mcp.json",         "vscode", False,
     lambda root: root / ".github/copilot-instructions.md", "append",
     lambda root: root / ".claude"),
    ("Trae",           lambda root: root / ".trae/mcp.json",           "standard", False,
     lambda root: root / ".trae/rules/aivectormemory.md", "file", None),
    ("OpenCode",       lambda root: root / "opencode.json",            "opencode", False,
     lambda root: root / "AGENTS.md", "append",
     lambda root: root / ".opencode/plugins"),
    ("Codex",          lambda root: root / ".codex/config.toml",       "codex", False,
     lambda root: root / "AGENTS.md", "append", None),
    ("Antigravity",    lambda root: Path.home() / ".gemini/antigravity/mcp_config.json", "basic", True,
     lambda root: root / "GEMINI.md", "file", None),
    ("Copilot",        lambda root: root / ".github/copilot/mcp.json",  "basic", False,
     lambda root: root / ".github/copilot-instructions.md", "append", None),
]

RUNNERS = [
    ("python -m aivectormemory（pip/pipx 安装）", lambda pdir: (sys.executable, ["-m", "aivectormemory", "--project-dir", pdir])),
    ("uvx aivectormemory（无需安装）", lambda pdir: ("uvx", ["aivectormemory@latest", "--project-dir", pdir])),
]


STEERING_MARKER = "<!-- aivectormemory-steering -->"
CODEX_MCP_START_MARKER = "# >>> aivectormemory mcp >>>"
CODEX_MCP_END_MARKER = "# <<< aivectormemory mcp <<<"
DEFAULT_SERVER_NAME = "aivectormemory"
LEGACY_SERVER_NAMES = ("devmemory",)
AUTO_APPROVE_TOOLS = ["remember", "recall", "forget", "status", "track", "task", "readme", "auto_save"]

PLAYWRIGHT_SERVER_NAME = "playwright"
PLAYWRIGHT_MCP_VERSION = "0.0.68"
PLAYWRIGHT_ARGS = ["-y", f"@playwright/mcp@{PLAYWRIGHT_MCP_VERSION}", "--browser", "chromium"]


def _build_playwright_config(fmt: str) -> dict:
    cfg = _build_config("npx", PLAYWRIGHT_ARGS, fmt)
    for k in ("autoApprove", "alwaysAllow", "env"):
        cfg.pop(k, None)
    return cfg


def _has_npx() -> bool:
    """检测系统是否有 npx"""
    import shutil
    return shutil.which("npx") is not None


def _cleanup_legacy_playwright(root: Path) -> None:
    """清理旧版 install 无条件写入的 playwright 配置（仅清除含 @playwright/mcp 的，不碰用户自定义）"""
    for _label, path_fn, fmt, _is_global, *_ in IDES:
        if fmt == "codex":
            continue
        filepath = path_fn(root)
        if not filepath.exists():
            continue
        try:
            config = json.loads(filepath.read_text("utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        key = _root_key(fmt)
        pw = config.get(key, {}).get(PLAYWRIGHT_SERVER_NAME)
        if pw is None:
            continue
        if "@playwright/mcp" not in json.dumps(pw):
            continue
        del config[key][PLAYWRIGHT_SERVER_NAME]
        filepath.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  ⚠ 已清理旧版遗留的 Playwright 配置 → {filepath.name}")


HOOKS_CONFIGS = [
    {
        "filename": "dev-workflow-check.kiro.hook",
        "content": {
            "name": "开发流程检查",
            "version": "1.0.0",
            "description": "每次收到用户消息时，检查核心原则、问题处理原则、自测要求",
            "when": {"type": "promptSubmit"},
            "then": {
                "type": "askAgent",
                "prompt": "",  # 占位，_write_hooks 时动态填充
            },
        },
    },
    {
        "filename": "pre-tool-use-check.kiro.hook",
        "content": {
            "name": "代码修改前检查 track issue",
            "version": "1.0.0",
            "description": "Edit/Write 工具执行前，检查当前项目是否有活跃的 track issue，没有则拒绝执行",
            "when": {"type": "preToolUse", "toolTypes": ["write"]},
            "then": {
                "type": "runCommand",
                "command": "",  # 占位，install 时动态填充
            },
        },
    },
]


def _check_track_script_path() -> Path:
    """返回包内 check_track.sh 的路径"""
    return Path(__file__).parent / "hooks" / "check_track.sh"


CLAUDE_CODE_HOOKS_CONFIG = {
    "hooks": {
        "PreToolUse": [
            {
                "matcher": "Edit|Write",
                "hooks": [
                    {
                        "type": "command",
                        "command": "",  # 占位，install 时动态填充 check_track.sh 路径
                        "timeout": 10,
                    }
                ]
            }
        ],
        "UserPromptSubmit": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": "",  # 占位，install 时动态填充 inject-workflow-rules.sh 路径
                    }
                ]
            }
        ],
        "SessionStart": [
            {
                "matcher": "startup|compact|resume|clear",
                "hooks": [
                    {
                        "type": "command",
                        "command": "",  # 占位，install 时动态填充 compact-recovery.sh 路径
                    }
                ]
            }
        ]
    }
}

CURSOR_HOOKS_CONFIG = {
    "version": 1,
    "hooks": {
        "preToolUse": [
            {
                "matcher": "edit|write",
                "command": "",  # 占位，install 时动态填充实际路径
                "timeout": 10,
            }
        ]
    }
}

WINDSURF_HOOKS_CONFIG = {
    "hooks": {
        "pre_write_code": [
            {
                "command": "",  # 占位，install 时动态填充实际路径
                "show_output": True,
            }
        ]
    }
}


OPENCODE_PLUGIN_TEMPLATE = """\
// AIVectorMemory plugin for OpenCode (@opencode-ai/plugin)
// - experimental.chat.system.transform: 注入开发规则到 system prompt
// - tool.execute.before: 检查 Edit/Write 前是否有活跃 track issue
import { execFileSync } from "child_process";
import { homedir } from "os";
import { existsSync } from "fs";
import { join } from "path";

const DB_PATH = join(homedir(), ".aivectormemory", "memory.db");

const DEV_WORKFLOW_RULES = `<ADDITIONAL_INSTRUCTIONS>
__DEV_WORKFLOW_RULES__</ADDITIONAL_INSTRUCTIONS>`;

function hasActiveIssues(projectDir) {
  if (!existsSync(DB_PATH)) return true;
  try {
    const result = execFileSync("python3", [
      "-c",
      "import sqlite3,sys;c=sqlite3.connect(sys.argv[1]);print(c.execute('SELECT COUNT(*) FROM issues WHERE project_dir=? AND status IN (?,?)',(sys.argv[2],'pending','in_progress')).fetchone()[0]);c.close()",
      DB_PATH,
      projectDir,
    ], { encoding: "utf-8", timeout: 5000 }).trim();
    return parseInt(result, 10) > 0;
  } catch {
    return true;
  }
}

export default async ({ project }) => ({
  "experimental.chat.system.transform": async (_input, output) => {
    output.system.push(DEV_WORKFLOW_RULES);
  },
  "tool.execute.before": async ({ tool, sessionID }, output) => {
    if (tool !== "Edit" && tool !== "Write" && tool !== "edit" && tool !== "write") return;
    const projectDir = project?.path || process.cwd();
    if (!hasActiveIssues(projectDir)) {
      output.args = {
        ...output.args,
        __blocked: "当前项目没有活跃的 track issue。请先调用 track(action: create) 记录问题后再修改代码。",
      };
    }
  },
});
"""


def _build_opencode_plugin_content(lang: str = None) -> str:
    """动态生成 OpenCode 插件内容，从 i18n 模块加载"""
    js_rules = get_workflow_prompt(lang).replace('`', '\\`').replace('${', '\\${')
    return OPENCODE_PLUGIN_TEMPLATE.replace('__DEV_WORKFLOW_RULES__', js_rules)


def _copy_check_track_script(target_dir: Path) -> tuple[Path, bool]:
    """复制 check_track.sh 到目标目录，返回 (目标路径, 是否有变更)"""
    import shutil
    target_dir.mkdir(parents=True, exist_ok=True)
    src = _check_track_script_path()
    dst = target_dir / "check_track.sh"
    if not dst.exists() or dst.read_text("utf-8") != src.read_text("utf-8"):
        shutil.copy2(src, dst)
        dst.chmod(0o755)
        return dst, True
    return dst, False


def _build_claude_code_hooks(check_script_path: str, inject_script_path: str, compact_recovery_path: str) -> dict:
    """构建 Claude Code hooks 配置，填充实际脚本路径"""
    import copy
    cfg = copy.deepcopy(CLAUDE_CODE_HOOKS_CONFIG)
    cfg["hooks"]["PreToolUse"][0]["hooks"][0]["command"] = check_script_path
    cfg["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"] = inject_script_path
    cfg["hooks"]["SessionStart"][0]["hooks"][0]["command"] = compact_recovery_path
    return cfg


def _write_inject_workflow_script(target_dir: Path, lang: str | None = None) -> tuple[Path, bool]:
    """生成 inject-workflow-rules.sh，只包含指定语言的 workflow prompt（直接 cat 输出）"""
    from aivectormemory.settings import get_language
    if lang is None:
        lang = get_language()
    target_dir.mkdir(parents=True, exist_ok=True)
    dst = target_dir / "inject-workflow-rules.sh"
    prompt = get_workflow_prompt(lang)
    parts = ["#!/bin/bash", "cat <<'AIVECTORMEMORY_EOF'", prompt, "AIVECTORMEMORY_EOF"]
    content = "\n".join(parts) + "\n"
    if dst.exists() and dst.read_text("utf-8") == content:
        return dst, False
    dst.write_text(content, encoding="utf-8")
    dst.chmod(0o755)
    return dst, True


def _write_compact_recovery_script(target_dir: Path, lang: str | None = None) -> tuple[Path, bool]:
    """生成 compact-recovery.sh，上下文压缩后重新注入关键规则（CLAUDE.md 始终自动加载，无需重复注入）"""
    from aivectormemory.settings import get_language
    if lang is None:
        lang = get_language()
    header, footer = get_compact_recovery_hints(lang)
    target_dir.mkdir(parents=True, exist_ok=True)
    dst = target_dir / "compact-recovery.sh"
    # footer 可能含 \n，bash echo 双引号内的换行会正常输出
    content = f"""#!/bin/bash
# compact-recovery: re-inject critical rules after context compression (CLAUDE.md auto-loaded)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "{header}"
echo ""
sed '1d;/^cat <<.*AIVECTORMEMORY_EOF/d;/^AIVECTORMEMORY_EOF$/d' "$SCRIPT_DIR/inject-workflow-rules.sh"
echo ""
echo "{footer}"
"""
    if dst.exists() and dst.read_text("utf-8") == content:
        return dst, False
    dst.write_text(content, encoding="utf-8")
    dst.chmod(0o755)
    return dst, True


def _write_claude_code_hooks(hooks_dir: Path, lang: str | None = None) -> list[str]:
    """写入 Claude Code hooks 到 .claude/settings.json"""
    results = []
    hooks_dir.mkdir(parents=True, exist_ok=True)
    script_dir = hooks_dir / "hooks"
    # 复制 check_track.sh
    check_path, check_changed = _copy_check_track_script(script_dir)
    results.append(f"{'✓ 已同步' if check_changed else '- 无变更'}  Script: .claude/hooks/check_track.sh")
    # 生成 inject-workflow-rules.sh
    inject_path, inject_changed = _write_inject_workflow_script(script_dir, lang=lang)
    results.append(f"{'✓ 已同步' if inject_changed else '- 无变更'}  Script: .claude/hooks/inject-workflow-rules.sh")
    # 生成 compact-recovery.sh
    compact_path, compact_changed = _write_compact_recovery_script(script_dir, lang=lang)
    results.append(f"{'✓ 已同步' if compact_changed else '- 无变更'}  Script: .claude/hooks/compact-recovery.sh")
    # 构建配置
    new_hooks_cfg = _build_claude_code_hooks(str(check_path), str(inject_path), str(compact_path))
    filepath = hooks_dir / "settings.json"
    config = {}
    if filepath.exists():
        try:
            config = json.loads(filepath.read_text("utf-8"))
        except (json.JSONDecodeError, OSError):
            config = {}
    existing = config.get("hooks", {})
    new_hooks = new_hooks_cfg["hooks"]
    hook_keys = ["PreToolUse", "UserPromptSubmit", "SessionStart"]
    changed = any(existing.get(k) != new_hooks.get(k) for k in hook_keys)
    # 清理旧的 Stop hook
    has_old_stop = "Stop" in existing
    if changed or has_old_stop:
        config.setdefault("hooks", {})
        for k in hook_keys:
            config["hooks"][k] = new_hooks[k]
        config["hooks"].pop("Stop", None)
        config["hooks"].pop("TaskCompleted", None)
    # 写入 permissions.allow（MCP 工具通配符 + 基础工具自动授权）
    required_perms = [f"mcp__{DEFAULT_SERVER_NAME}__*", f"mcp__{PLAYWRIGHT_SERVER_NAME}__*", "Bash(*)", "Edit(*)", "Write(*)", "Read(*)", "Glob(*)", "Grep(*)"]
    # 清理旧的逐条 MCP 权限（被通配符覆盖）
    old_mcp_prefixes = (f"mcp__{DEFAULT_SERVER_NAME}__", f"mcp__{PLAYWRIGHT_SERVER_NAME}__")
    if "permissions" in config and "allow" in config["permissions"]:
        config["permissions"]["allow"] = [p for p in config["permissions"]["allow"] if not any(p.startswith(prefix) and not p.endswith("*") for prefix in old_mcp_prefixes)]
    existing_perms = set(config.get("permissions", {}).get("allow", []))
    missing = [p for p in required_perms if p not in existing_perms]
    if missing:
        config.setdefault("permissions", {}).setdefault("allow", [])
        config["permissions"]["allow"].extend(missing)
        changed = True
        results.append(f"✓ 已写入  Permissions: {len(missing)} 条规则（MCP 工具 + Bash）")
    else:
        results.append("- 无变更  Permissions: 已全部授权")
    if changed or has_old_stop:
        filepath.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        results.append(f"✓ 已生成  Hook: .claude/settings.json ({' + '.join(hook_keys)})")
    else:
        results.append(f"- 无变更  Hook: .claude/settings.json ({' + '.join(hook_keys)})")
    return results


def _build_cursor_hooks(script_path: str) -> dict:
    """构建 Cursor hooks 配置，填充实际脚本路径"""
    import copy
    cfg = copy.deepcopy(CURSOR_HOOKS_CONFIG)
    cfg["hooks"]["preToolUse"][0]["command"] = script_path
    return cfg


def _write_cursor_hooks(hooks_dir: Path) -> list[str]:
    """写入 Cursor hooks 到 .cursor/hooks.json"""
    results = []
    hooks_dir.mkdir(parents=True, exist_ok=True)
    # 复制检查脚本
    script_dir = hooks_dir / "hooks"
    script_path, script_changed = _copy_check_track_script(script_dir)
    results.append(f"{'✓ 已同步' if script_changed else '- 无变更'}  Script: .cursor/hooks/check_track.sh")
    # 构建配置
    new_cfg = _build_cursor_hooks(str(script_path))
    filepath = hooks_dir / "hooks.json"
    config = {}
    if filepath.exists():
        try:
            config = json.loads(filepath.read_text("utf-8"))
        except (json.JSONDecodeError, OSError):
            config = {}
    existing_hooks = config.get("hooks", {})
    new_hooks = new_cfg["hooks"]
    changed = existing_hooks.get("preToolUse") != new_hooks.get("preToolUse")
    # 清理旧的 beforeSubmitPrompt hook（如果存在）
    has_old_hooks = "beforeSubmitPrompt" in existing_hooks
    if changed or has_old_hooks:
        config["version"] = new_cfg["version"]
        config.setdefault("hooks", {})
        config["hooks"]["preToolUse"] = new_hooks["preToolUse"]
        config["hooks"].pop("beforeSubmitPrompt", None)
        filepath.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        results.append("✓ 已生成  Hook: .cursor/hooks.json (preToolUse)")
    else:
        results.append("- 无变更  Hook: .cursor/hooks.json (preToolUse)")
    return results


def _build_windsurf_hooks(script_path: str) -> dict:
    """构建 Windsurf hooks 配置，填充实际脚本路径"""
    import copy
    cfg = copy.deepcopy(WINDSURF_HOOKS_CONFIG)
    cfg["hooks"]["pre_write_code"][0]["command"] = script_path
    return cfg


def _write_windsurf_hooks(hooks_dir: Path) -> list[str]:
    """写入 Windsurf hooks 到 .windsurf/hooks.json"""
    results = []
    hooks_dir.mkdir(parents=True, exist_ok=True)
    # 复制检查脚本
    script_dir = hooks_dir / "hooks"
    script_path, script_changed = _copy_check_track_script(script_dir)
    results.append(f"{'✓ 已同步' if script_changed else '- 无变更'}  Script: .windsurf/hooks/check_track.sh")
    # 构建配置
    new_cfg = _build_windsurf_hooks(str(script_path))
    filepath = hooks_dir / "hooks.json"
    config = {}
    if filepath.exists():
        try:
            config = json.loads(filepath.read_text("utf-8"))
        except (json.JSONDecodeError, OSError):
            config = {}
    existing_hooks = config.get("hooks", {})
    new_hooks = new_cfg["hooks"]
    changed = existing_hooks.get("pre_write_code") != new_hooks.get("pre_write_code")
    if changed:
        config.setdefault("hooks", {})
        config["hooks"]["pre_write_code"] = new_hooks["pre_write_code"]
        filepath.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        results.append("✓ 已生成  Hook: .windsurf/hooks.json (pre_write_code)")
    else:
        results.append("- 无变更  Hook: .windsurf/hooks.json (pre_write_code)")
    return results


def _write_opencode_plugins(plugins_dir: Path, lang: str = None) -> list[str]:
    """写入 OpenCode 插件文件，返回变更列表"""
    results = []
    plugins_dir.mkdir(parents=True, exist_ok=True)
    # 确保 .opencode/package.json 包含 "type": "module"（ESM 插件必需）
    opencode_dir = plugins_dir.parent
    pkg_path = opencode_dir / "package.json"
    pkg_expected = {"type": "module", "dependencies": {"@opencode-ai/plugin": "1.2.10"}}
    pkg_changed = False
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text("utf-8"))
            if pkg.get("type") != "module":
                pkg["type"] = "module"
                pkg_changed = True
            if pkg.get("dependencies", {}).get("@opencode-ai/plugin") != "1.2.10":
                pkg.setdefault("dependencies", {})["@opencode-ai/plugin"] = "1.2.10"
                pkg_changed = True
            if pkg_changed:
                pkg_path.write_text(json.dumps(pkg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except (json.JSONDecodeError, OSError):
            pkg_path.write_text(json.dumps(pkg_expected, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            pkg_changed = True
    else:
        pkg_path.write_text(json.dumps(pkg_expected, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        pkg_changed = True
    results.append(f"{'✓ 已更新' if pkg_changed else '- 无变更'}  package.json (type: module)")
    # 写入插件文件
    plugin_content = _build_opencode_plugin_content(lang)
    filepath = plugins_dir / "aivectormemory-pre-tool-check.js"
    if filepath.exists() and filepath.read_text("utf-8").strip() == plugin_content.strip():
        results.append("- 无变更  Plugin: aivectormemory-pre-tool-check.js")
    else:
        filepath.write_text(plugin_content, encoding="utf-8")
        results.append("✓ 已生成  Plugin: aivectormemory-pre-tool-check.js")
    return results


def _write_hooks(hooks_dir: Path, lang: str = None) -> list[str]:
    """写入 hook 文件到指定目录（Kiro），返回变更列表"""
    import copy
    results = []
    hooks_dir.mkdir(parents=True, exist_ok=True)
    # 复制 check_track.sh 到 hooks 目录
    script_path, script_changed = _copy_check_track_script(hooks_dir)
    results.append(f"{'✓ 已同步' if script_changed else '- 无变更'}  Script: check_track.sh")
    for hook in HOOKS_CONFIGS:
        content = copy.deepcopy(hook["content"])
        # 动态填充
        if hook["filename"] == "dev-workflow-check.kiro.hook":
            content["then"]["prompt"] = get_workflow_prompt(lang)
        elif hook["filename"] == "pre-tool-use-check.kiro.hook":
            content["then"]["command"] = str(script_path)
        filepath = hooks_dir / hook["filename"]
        new_content = json.dumps(content, indent=2, ensure_ascii=False) + "\n"
        if filepath.exists():
            existing = filepath.read_text("utf-8")
            if existing.strip() == new_content.strip():
                results.append(f"- 无变更  Hook: {hook['filename']}")
                continue
        filepath.write_text(new_content, encoding="utf-8")
        results.append(f"✓ 已生成  Hook: {hook['filename']}")
    return results


SPECS_PATH_MAP = {
    "Kiro": ".kiro/specs/{feature_id}/",
    "Cursor": ".cursor/specs/{feature_id}/",
    "Windsurf": ".windsurf/specs/{feature_id}/",
    "Trae": ".trae/specs/{feature_id}/",
}
SPECS_PATH_DEFAULT = "docs/specs/{feature_id}/（项目根目录）"

# 有每消息注入机制的 IDE，steering 不写入 DEV_WORKFLOW_PROMPT（避免重复）
PER_MSG_INJECTION_IDES = {"Kiro", "OpenCode", "Claude Code"}


def _write_steering(filepath: Path, mode: str, ide_name: str = "", include_workflow: bool = True, lang: str = None) -> bool:
    raw = get_steering(lang).strip()
    specs_path = SPECS_PATH_MAP.get(ide_name, SPECS_PATH_DEFAULT)
    content = raw.replace("{specs_path}", specs_path)
    if include_workflow:
        # 语言无关：在第一个章节标题前插入 workflow prompt
        anchor = "---\n\n## "
        idx = content.find(anchor)
        if idx != -1:
            rest = content[idx + len(anchor):]  # "⚠️ IDENTITY..." 或 "⚠️ 1. ..."
            workflow = get_workflow_prompt(lang).strip()
            content = content[:idx] + f"---\n\n{workflow}\n\n---\n\n## " + rest
    if mode == "file":
        START = STEERING_MARKER
        END = "<!-- /aivectormemory-steering -->"
        block = f"{START}\n{content}\n{END}"
        if filepath.exists():
            existing = filepath.read_text("utf-8")
            if START in existing and END in existing:
                start_idx = existing.index(START)
                end_idx = existing.index(END) + len(END)
                old_block = existing[start_idx:end_idx]
                if old_block.strip() == block.strip():
                    return False
                updated = existing[:start_idx] + block + existing[end_idx:]
                filepath.write_text(updated, encoding="utf-8")
                return True
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(block + "\n", encoding="utf-8")
        return True
    if mode == "append":
        existing = filepath.read_text("utf-8") if filepath.exists() else ""
        block = f"\n{STEERING_MARKER}\n{content}\n"
        if STEERING_MARKER in existing:
            start = existing.index(STEERING_MARKER)
            next_marker = existing.find("\n<!-- ", start + len(STEERING_MARKER))
            end = next_marker if next_marker != -1 else len(existing)
            old_block = existing[start:end]
            new_block = f"{STEERING_MARKER}\n{content}\n"
            if old_block.strip() == new_block.strip():
                return False
            updated = existing[:start] + new_block + existing[end:]
            filepath.write_text(updated, encoding="utf-8")
            return True
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(block)
        return True
    return False


def _build_env_block() -> dict:
    env_block = {}
    hf_endpoint = os.environ.get("HF_ENDPOINT", "")
    if hf_endpoint:
        env_block["HF_ENDPOINT"] = hf_endpoint
    return env_block


def _root_key(fmt: str) -> str:
    return {"opencode": "mcp", "vscode": "servers"}.get(fmt, "mcpServers")


def _build_config(cmd: str, args: list[str], fmt: str) -> dict:
    env_block = _build_env_block()
    if fmt == "opencode":
        cfg = {"type": "local", "command": [cmd] + args, "enabled": True}
    elif fmt == "vscode":
        cfg = {"type": "stdio", "command": cmd, "args": args}
    elif fmt == "windsurf":
        cfg = {"command": cmd, "args": args, "disabled": False, "alwaysAllow": AUTO_APPROVE_TOOLS}
    elif fmt == "basic":
        cfg = {"command": cmd, "args": args}
    else:  # standard (Claude Code, Kiro)
        cfg = {"command": cmd, "args": args, "disabled": False, "autoApprove": AUTO_APPROVE_TOOLS}
    if env_block:
        cfg["env"] = env_block
    return cfg


def _build_codex_config_block(cmd: str, args: list[str], server_name: str = DEFAULT_SERVER_NAME) -> str:
    lines = [
        f"[mcp_servers.{server_name}]",
        f"command = {json.dumps(cmd, ensure_ascii=False)}",
        f"args = {json.dumps(args, ensure_ascii=False)}",
    ]
    env_block = _build_env_block()
    if env_block:
        lines.append("")
        lines.append(f"[mcp_servers.{server_name}.env]")
        for key, value in env_block.items():
            lines.append(f"{key} = {json.dumps(value, ensure_ascii=False)}")
    return "\n".join(lines)


def _strip_codex_managed_block(content: str) -> str:
    start = content.find(CODEX_MCP_START_MARKER)
    if start == -1:
        return content
    end = content.find(CODEX_MCP_END_MARKER, start)
    if end == -1:
        return content[:start]
    end += len(CODEX_MCP_END_MARKER)
    if end < len(content) and content[end] == "\n":
        end += 1
    return content[:start] + content[end:]


def _strip_codex_server_sections(content: str, server_names: tuple[str, ...]) -> str:
    lines = content.splitlines(keepends=True)
    section_prefixes = tuple(f"mcp_servers.{name}" for name in server_names)
    kept = []
    skipping = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1].strip()
            if any(section == prefix or section.startswith(f"{prefix}.") for prefix in section_prefixes):
                skipping = True
                continue
            skipping = False
        if not skipping:
            kept.append(line)
    return "".join(kept)


def _normalize_toml_content(content: str) -> str:
    stripped = content.strip()
    if not stripped:
        return ""
    normalized_lines = []
    previous_blank = False
    for line in stripped.splitlines():
        current = line.rstrip()
        is_blank = current == ""
        if is_blank and previous_blank:
            continue
        normalized_lines.append(current)
        previous_blank = is_blank
    return "\n".join(normalized_lines) + "\n"


def _merge_codex_config(filepath: Path, server_name: str, server_block: str) -> bool:
    existing = filepath.read_text("utf-8") if filepath.exists() else ""
    all_server_names = (server_name,) + LEGACY_SERVER_NAMES
    cleaned = _strip_codex_managed_block(existing)
    cleaned = _strip_codex_server_sections(cleaned, all_server_names)
    cleaned = _normalize_toml_content(cleaned)
    managed_block = (
        f"{CODEX_MCP_START_MARKER}\n"
        f"{server_block}\n"
        f"{CODEX_MCP_END_MARKER}\n"
    )
    updated = f"{cleaned}\n{managed_block}" if cleaned else managed_block
    if existing.strip() == updated.strip():
        return False
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(updated, encoding="utf-8")
    return True


def _merge_config(filepath: Path, key: str, server_name: str, server_config: dict) -> bool:
    config = {}
    if filepath.exists():
        try:
            config = json.loads(filepath.read_text("utf-8"))
        except (json.JSONDecodeError, OSError):
            config = {}
    config.setdefault(key, {})
    if server_name in config[key] and config[key][server_name] == server_config:
        return False
    config[key][server_name] = server_config
    for old_key in LEGACY_SERVER_NAMES:
        if old_key in config[key] and old_key != server_name:
            del config[key][old_key]
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return True


def _config_has_server(filepath: Path, fmt: str, server_name: str = DEFAULT_SERVER_NAME) -> bool:
    if not filepath.exists():
        return False
    server_names = (server_name,) + LEGACY_SERVER_NAMES
    if fmt == "codex":
        pattern = "|".join(re.escape(name) for name in server_names)
        try:
            content = filepath.read_text("utf-8")
        except OSError:
            return False
        return bool(re.search(rf"(?m)^\s*\[mcp_servers\.({pattern})\]\s*$", content))
    try:
        config = json.loads(filepath.read_text("utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    key = _root_key(fmt)
    servers = config.get(key, {})
    return any(name in servers for name in server_names)


def _detect_installed_ide_names(root: Path) -> set[str]:
    installed = set()
    for name, path_fn, fmt, *_ in IDES:
        filepath = path_fn(root)
        if filepath and _config_has_server(filepath, fmt):
            installed.add(name)
    return installed


def _should_include_workflow(root: Path, steering_path: Path, active_ide_names: set[str]) -> bool:
    shared_ides = set()
    for name, _, _, _, steering_fn, steering_mode, _ in IDES:
        if name not in active_ide_names or not steering_fn or not steering_mode:
            continue
        if steering_fn(root) == steering_path:
            shared_ides.add(name)
    if not shared_ides:
        return True
    return any(name not in PER_MSG_INJECTION_IDES for name in shared_ides)


def _choose(prompt: str, options: list[tuple], allow_all: bool = False) -> list | None:
    for i, (label, *_) in enumerate(options, 1):
        print(f"  {i}. {label}")
    if allow_all:
        print(f"  a. 全部安装")
    print()
    choice = input(f"{prompt}: ").strip().lower()
    if not choice:
        return None
    if allow_all and choice == "a":
        return list(range(len(options)))
    nums = {int(p.strip()) - 1 for p in choice.split(",") if p.strip().isdigit()}
    selected = [i for i in nums if 0 <= i < len(options)]
    return selected or None


def run_install(project_dir: str | None = None):
    pdir = str(Path(project_dir or ".").resolve()).replace("\\", "/")
    print(f"项目目录: {pdir}\n")

    # 0. 清理旧版遗留的 playwright 配置
    _cleanup_legacy_playwright(Path(pdir))

    # 1. 选择启动方式
    print("启动方式：")
    runner_indices = _choose("选择启动方式 [1]", RUNNERS)
    if runner_indices is None:
        runner_indices = [0]  # 默认 pip/pipx
    cmd, args = RUNNERS[runner_indices[0]][1](pdir)
    print(f"  → {cmd} {' '.join(args)}\n")

    # 2. 选择语言
    from aivectormemory.settings import SUPPORTED_LANGS, get_language, set_language
    lang_labels = {
        "zh-CN": "简体中文", "zh-TW": "繁體中文", "en": "English",
        "es": "Español", "de": "Deutsch", "fr": "Français", "ja": "日本語",
    }
    current_lang = get_language()
    lang_options = [(f"{lang_labels.get(l, l)}{' (当前)' if l == current_lang else ''}", l) for l in SUPPORTED_LANGS]
    print("AI 规则语言：")
    lang_indices = _choose("选择语言 [当前]", lang_options)
    if lang_indices is not None:
        selected_lang = lang_options[lang_indices[0]][1]
    else:
        selected_lang = current_lang
    if selected_lang != current_lang:
        set_language(selected_lang)
    print(f"  → {lang_labels.get(selected_lang, selected_lang)}\n")

    # 3. 选择 IDE
    print("支持的 IDE：")
    valid_ides = []
    for name, path_fn, fmt, is_global, steering_fn, steering_mode, hooks_fn in IDES:
        p = path_fn(Path(pdir))
        if p is None:
            continue
        tag = " (全局)" if is_global else ""
        valid_ides.append((f"{name}{tag}", name, path_fn, fmt, steering_fn, steering_mode, hooks_fn))

    ide_indices = _choose("选择 IDE（编号，逗号分隔多选，a=全部）", valid_ides, allow_all=True)
    if ide_indices is None:
        print("未选择，退出")
        return

    # 4. 是否安装 Playwright MCP
    install_playwright = False
    if _has_npx():
        pw_choice = input("\n是否同时配置 Playwright MCP？(y/N): ").strip().lower()
        install_playwright = pw_choice in ("y", "yes")
    print()

    # 5. 写入配置
    print()
    root = Path(pdir)
    selected_ide_names = {valid_ides[idx][1] for idx in ide_indices}
    active_ide_names = _detect_installed_ide_names(root) | selected_ide_names
    for idx in ide_indices:
        label, ide_name, path_fn, fmt, steering_fn, steering_mode, hooks_fn = valid_ides[idx]
        filepath = path_fn(root)
        if filepath is None:
            continue
        if fmt == "codex":
            server_block = _build_codex_config_block(cmd, args)
            changed = _merge_codex_config(filepath, DEFAULT_SERVER_NAME, server_block)
        else:
            server_config = _build_config(cmd, args, fmt)
            key = _root_key(fmt)
            changed = _merge_config(filepath, key, DEFAULT_SERVER_NAME, server_config)
            # Playwright MCP：仅在用户选择安装且配置中不存在时写入
            if install_playwright and not _config_has_server(filepath, fmt, PLAYWRIGHT_SERVER_NAME):
                pw_changed = _merge_config(filepath, key, PLAYWRIGHT_SERVER_NAME, _build_playwright_config(fmt))
                changed = changed or pw_changed
        status = "✓ 已更新" if changed else "- 无变更"
        print(f"  {status}  {label} MCP 配置")

        # 4. 写入 Steering 规则
        if steering_fn and steering_mode:
            steering_path = steering_fn(root)
            include_workflow = _should_include_workflow(root, steering_path, active_ide_names)
            s_changed = _write_steering(steering_path, steering_mode, ide_name, include_workflow, lang=selected_lang)
            s_status = "✓ 已生成" if s_changed else "- 无变更"
            print(f"  {s_status}  {label} Steering 规则 → {steering_path.relative_to(root)}")

        # 5. 写入 Hooks / Plugins
        if hooks_fn:
            hooks_dir = hooks_fn(root)
            hooks_dir_str = str(hooks_dir)
            if hooks_dir_str.endswith(".opencode/plugins"):
                hook_results = _write_opencode_plugins(hooks_dir, lang=selected_lang)
            elif hooks_dir_str.endswith(".claude"):
                hook_results = _write_claude_code_hooks(hooks_dir, lang=selected_lang)
            elif hooks_dir_str.endswith(".cursor"):
                hook_results = _write_cursor_hooks(hooks_dir)
            elif hooks_dir_str.endswith(".windsurf"):
                hook_results = _write_windsurf_hooks(hooks_dir)
            else:
                hook_results = _write_hooks(hooks_dir, lang=selected_lang)
            for r in hook_results:
                print(f"  {r}")

    if "Codex" in selected_ide_names:
        print("\n提示：Codex 只有在项目被标记为 trusted project 后才会加载 .codex/config.toml。")
        print("      AGENTS.md 会继续作为项目指令被发现；若机器上已存在同名全局 MCP，未信任前仍可能优先命中全局配置。")

    # Playwright 浏览器安装
    print("\nPlaywright 浏览器测试支持：")
    pw_choice = input("是否安装 Playwright Chromium 浏览器？[Y/n]: ").strip().lower()
    if pw_choice != "n":
        import subprocess
        try:
            subprocess.run(["npx", "-y", f"@playwright/mcp@{PLAYWRIGHT_MCP_VERSION}", "--help"], capture_output=True, timeout=30)
            subprocess.run(["npx", "playwright", "install", "chromium"], timeout=120)
            print("  ✓ Chromium 浏览器安装完成")
        except Exception as e:
            print(f"  ⚠️  安装失败: {e}")
            print(f"  手动安装: npx playwright install chromium")
    else:
        print("  - 跳过（可稍后运行: npx playwright install chromium）")

    print("\n安装完成，重启 IDE 即可使用")

    # 6. 注册项目到数据库（Web 看板可见）
    try:
        from aivectormemory.db.connection import ConnectionManager
        from aivectormemory.db.schema import init_db
        cm = ConnectionManager(pdir)
        init_db(cm.conn)
        from datetime import datetime
        now = datetime.now().astimezone().isoformat()
        cm.conn.execute(
            "INSERT OR IGNORE INTO session_state (project_dir, is_blocked, block_reason, next_step, current_task, progress, recent_changes, pending, updated_at) VALUES (?,0,'','','','[]','[]','[]',?)",
            (pdir, now)
        )
        cm.conn.commit()
        cm.close()
    except Exception as e:
        print(f"\n⚠️  项目注册到数据库失败（Web 看板可能不显示此项目）: {e}")


# ---------------------------------------------------------------------------
# Uninstall
# ---------------------------------------------------------------------------

def _remove_mcp_server(filepath: Path, fmt: str) -> list[str]:
    """从 MCP 配置文件中移除 aivectormemory + playwright server 条目"""
    results = []
    if not filepath.exists():
        return results
    server_names = (DEFAULT_SERVER_NAME,) + LEGACY_SERVER_NAMES
    all_names = server_names + (PLAYWRIGHT_SERVER_NAME,)

    if fmt == "codex":
        content = filepath.read_text("utf-8")
        original = content
        content = _strip_codex_managed_block(content)
        content = _strip_codex_server_sections(content, all_names)
        content = _normalize_toml_content(content)
        if content != original:
            if content.strip():
                filepath.write_text(content, encoding="utf-8")
            else:
                _safe_unlink(filepath)
            results.append(f"✓ 已移除  MCP: {filepath.name}")
        else:
            results.append(f"- 无变更  MCP: {filepath.name}")
        return results

    try:
        config = json.loads(filepath.read_text("utf-8"))
    except (json.JSONDecodeError, OSError):
        return results
    key = _root_key(fmt)
    servers = config.get(key, {})
    removed = []
    for name in all_names:
        if name in servers:
            del servers[name]
            removed.append(name)
    if removed:
        if not servers and key in config:
            del config[key]
        if config:
            filepath.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        else:
            _safe_unlink(filepath)
        results.append(f"✓ 已移除  MCP: {filepath.name} ({', '.join(removed)})")
    else:
        results.append(f"- 无变更  MCP: {filepath.name}")
    return results


def _remove_steering(filepath: Path, mode: str) -> list[str]:
    """移除 steering 规则"""
    results = []
    if not filepath.exists():
        return results
    if mode == "file":
        content = filepath.read_text("utf-8")
        if STEERING_MARKER in content:
            _safe_unlink(filepath)
            results.append(f"✓ 已删除  Steering: {filepath.name}")
        else:
            results.append(f"- 跳过    Steering: {filepath.name}（非 AIVectorMemory 生成）")
    elif mode == "append":
        content = filepath.read_text("utf-8")
        if STEERING_MARKER not in content:
            results.append(f"- 无变更  Steering: {filepath.name}")
            return results
        start = content.index(STEERING_MARKER)
        next_marker = content.find("\n<!-- ", start + len(STEERING_MARKER))
        end = next_marker if next_marker != -1 else len(content)
        updated = content[:start].rstrip() + content[end:]
        updated = updated.strip() + "\n" if updated.strip() else ""
        if updated:
            filepath.write_text(updated, encoding="utf-8")
            results.append(f"✓ 已移除  Steering: {filepath.name}（保留其他内容）")
        else:
            _safe_unlink(filepath)
            results.append(f"✓ 已删除  Steering: {filepath.name}（已空）")
    return results


def _remove_kiro_hooks(hooks_dir: Path) -> list[str]:
    """移除 Kiro hooks"""
    results = []
    targets = ["dev-workflow-check.kiro.hook", "pre-tool-use-check.kiro.hook", "check_track.sh"]
    for name in targets:
        f = hooks_dir / name
        if f.exists() and _safe_unlink(f):
            results.append(f"✓ 已删除  Hook: {name}")
    return results


def _remove_claude_code_hooks(hooks_dir: Path) -> list[str]:
    """移除 Claude Code hooks + scripts + permissions"""
    results = []
    # 删除脚本
    script_dir = hooks_dir / "hooks"
    for name in ["check_track.sh", "inject-workflow-rules.sh", "compact-recovery.sh"]:
        f = script_dir / name
        if f.exists() and _safe_unlink(f):
            results.append(f"✓ 已删除  Script: .claude/hooks/{name}")
    if script_dir.exists() and not any(script_dir.iterdir()):
        script_dir.rmdir()
    # 清理 settings.json
    settings = hooks_dir / "settings.json"
    if not settings.exists():
        return results
    try:
        config = json.loads(settings.read_text("utf-8"))
    except (json.JSONDecodeError, OSError):
        return results
    changed = False
    # 移除 hooks 段
    for key in ["PreToolUse", "UserPromptSubmit", "SessionStart", "Stop", "TaskCompleted"]:
        if key in config.get("hooks", {}):
            del config["hooks"][key]
            changed = True
    if not config.get("hooks"):
        config.pop("hooks", None)
    # 移除 permissions
    mcp_prefixes = (f"mcp__{DEFAULT_SERVER_NAME}__", f"mcp__{PLAYWRIGHT_SERVER_NAME}__")
    if "permissions" in config and "allow" in config["permissions"]:
        before = len(config["permissions"]["allow"])
        config["permissions"]["allow"] = [
            p for p in config["permissions"]["allow"]
            if not any(p.startswith(prefix) for prefix in mcp_prefixes)
        ]
        if len(config["permissions"]["allow"]) < before:
            changed = True
        if not config["permissions"]["allow"]:
            del config["permissions"]["allow"]
        if not config.get("permissions"):
            del config["permissions"]
    if changed:
        if config:
            settings.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        else:
            _safe_unlink(settings)
        results.append("✓ 已清理  .claude/settings.json (hooks + permissions)")
    return results


def _remove_cursor_hooks(hooks_dir: Path) -> list[str]:
    """移除 Cursor hooks"""
    results = []
    # 删除脚本
    script_dir = hooks_dir / "hooks"
    f = script_dir / "check_track.sh"
    if f.exists() and _safe_unlink(f):
        results.append("✓ 已删除  Script: .cursor/hooks/check_track.sh")
    if script_dir.exists() and not any(script_dir.iterdir()):
        script_dir.rmdir()
    # 清理 hooks.json
    filepath = hooks_dir / "hooks.json"
    if not filepath.exists():
        return results
    try:
        config = json.loads(filepath.read_text("utf-8"))
    except (json.JSONDecodeError, OSError):
        return results
    changed = False
    for key in ["preToolUse", "beforeSubmitPrompt"]:
        if key in config.get("hooks", {}):
            del config["hooks"][key]
            changed = True
    if not config.get("hooks"):
        config.pop("hooks", None)
    if changed:
        if config:
            filepath.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        else:
            _safe_unlink(filepath)
        results.append("✓ 已清理  .cursor/hooks.json")
    return results


def _remove_windsurf_hooks(hooks_dir: Path) -> list[str]:
    """移除 Windsurf hooks"""
    results = []
    script_dir = hooks_dir / "hooks"
    f = script_dir / "check_track.sh"
    if f.exists() and _safe_unlink(f):
        results.append("✓ 已删除  Script: .windsurf/hooks/check_track.sh")
    if script_dir.exists() and not any(script_dir.iterdir()):
        script_dir.rmdir()
    filepath = hooks_dir / "hooks.json"
    if not filepath.exists():
        return results
    try:
        config = json.loads(filepath.read_text("utf-8"))
    except (json.JSONDecodeError, OSError):
        return results
    changed = False
    if "pre_write_code" in config.get("hooks", {}):
        del config["hooks"]["pre_write_code"]
        changed = True
    if not config.get("hooks"):
        config.pop("hooks", None)
    if changed:
        if config:
            filepath.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        else:
            _safe_unlink(filepath)
        results.append("✓ 已清理  .windsurf/hooks.json")
    return results


def _remove_opencode_plugins(plugins_dir: Path) -> list[str]:
    """移除 OpenCode 插件"""
    results = []
    f = plugins_dir / "aivectormemory-pre-tool-check.js"
    if f.exists() and _safe_unlink(f):
        results.append("✓ 已删除  Plugin: aivectormemory-pre-tool-check.js")
    return results


_HOOKS_REMOVER_BY_SUFFIX = {
    ".kiro/hooks":        _remove_kiro_hooks,
    ".claude":            _remove_claude_code_hooks,
    ".cursor":            _remove_cursor_hooks,
    ".windsurf":          _remove_windsurf_hooks,
    ".opencode/plugins":  _remove_opencode_plugins,
}


def _find_hooks_remover(hooks_dir: Path):
    """根据 hooks 目录路径后缀匹配 remover 函数"""
    path_str = str(hooks_dir)
    for suffix, remover in _HOOKS_REMOVER_BY_SUFFIX.items():
        if path_str.endswith(suffix):
            return remover
    return None


def _safe_unlink(filepath: Path) -> bool:
    """安全删除文件，Windows 文件锁定时打印警告"""
    try:
        filepath.unlink()
        return True
    except OSError as e:
        print(f"  ⚠️  无法删除 {filepath.name}: {e}")
        return False


def run_uninstall(project_dir: str | None = None):
    """从当前项目卸载 AIVectorMemory 的所有 IDE 配置"""
    pdir = str(Path(project_dir or os.getcwd()).resolve())
    root = Path(pdir)
    print(f"项目目录: {pdir}\n")

    installed = _detect_installed_ide_names(root)
    if not installed:
        print("未检测到已安装的 IDE 配置，无需卸载。")
        return

    print(f"检测到已安装: {', '.join(sorted(installed))}\n")

    cleaned_hooks_dirs: set[str] = set()  # 防止共享目录重复清理

    for name, path_fn, fmt, is_global, steering_fn, steering_mode, hooks_fn in IDES:
        if name not in installed:
            continue
        print(f"── {name} ──")
        # 1. 移除 MCP 配置（全局配置跳过）
        if is_global:
            mcp_path = path_fn(root)
            print(f"  ⚠️  跳过全局 MCP 配置: {mcp_path}")
            print(f"       如需移除请手动编辑: {mcp_path}")
        else:
            mcp_path = path_fn(root)
            if mcp_path:
                for r in _remove_mcp_server(mcp_path, fmt):
                    print(f"  {r}")
        # 2. 移除 Steering
        if steering_fn and steering_mode:
            steering_path = steering_fn(root)
            for r in _remove_steering(steering_path, steering_mode):
                print(f"  {r}")
        # 3. 移除 Hooks（根据路径后缀匹配 remover，防止共享目录重复清理）
        if hooks_fn:
            hooks_dir = hooks_fn(root)
            hooks_key = str(hooks_dir)
            if hooks_key not in cleaned_hooks_dirs:
                remover = _find_hooks_remover(hooks_dir)
                if remover:
                    for r in remover(hooks_dir):
                        print(f"  {r}")
                    cleaned_hooks_dirs.add(hooks_key)
        print()

    print("✓ 卸载完成（记忆数据已保留，如需清除请手动删除 ~/.aivectormemory/）")

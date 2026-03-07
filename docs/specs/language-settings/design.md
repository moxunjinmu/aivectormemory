# 语言设置统一 - 设计文档

## 1. 架构概览

```
桌面端/看板/CLI 选择语言
        │
        ▼
~/.aivectormemory/settings.json  ← 全局语言配置（唯一数据源）
        │
        ├──▶ 动态 hook（运行时读取）
        │     ├─ Claude Code: inject-workflow-rules.sh → 读 settings.json → 输出对应语言
        │     ├─ Kiro: dev-workflow-check.kiro.hook（静态，install 时生成）
        │     ├─ Cursor: rules 文件（静态，install 时生成）
        │     ├─ Windsurf: rules 文件（静态，install 时生成）
        │     └─ OpenCode: plugin JS（静态，install 时生成）
        │
        └──▶ 静态文件（install 或语言切换时重新生成）
              ├─ CLAUDE.md（append 模式）
              ├─ AGENTS.md（append 模式）
              ├─ .kiro/steering/aivectormemory.md
              ├─ .cursor/rules/aivectormemory.md
              ├─ .windsurf/rules/aivectormemory.md
              ├─ .trae/rules/aivectormemory.md
              └─ .github/copilot-instructions.md
```

## 2. 全局语言配置（F1）

### 2.1 存储位置

`~/.aivectormemory/settings.json`

```json
{
  "language": "zh-CN"
}
```

### 2.2 读写 API

新建 `aivectormemory/settings.py`：

```python
SETTINGS_PATH = Path.home() / ".aivectormemory" / "settings.json"
DEFAULT_LANG = "zh-CN"

def get_language() -> str:
    """读取全局语言设置，不存在则返回默认值"""

def set_language(lang: str) -> None:
    """写入语言设置到 settings.json（保留其他字段）"""
```

## 3. i18n 翻译模块（F5）

### 3.1 目录结构

```
aivectormemory/i18n/
├── __init__.py          # get_steering(lang), get_workflow_prompt(lang)
└── rules/
    ├── __init__.py
    ├── zh_CN.py         # STEERING_CONTENT, DEV_WORKFLOW_PROMPT（基准，从 install.py 迁移）
    ├── zh_TW.py
    ├── en.py
    ├── es.py
    ├── de.py
    ├── fr.py
    └── ja.py
```

### 3.2 翻译文件格式

每个语言文件导出两个常量：

```python
# aivectormemory/i18n/rules/en.py
STEERING_CONTENT = """# AIVectorMemory - Workflow Rules
---
## 1. New Session Startup (must follow order)
...
"""

DEV_WORKFLOW_PROMPT = (
    "## ⚠️ IDENTITY & TONE\n\n"
    "- Role: You are a Senior Engineer and Data Scientist\n"
    "- Language: **Always reply in English**...\n"
    ...
)
```

### 3.3 加载 API

```python
# aivectormemory/i18n/__init__.py
def get_steering(lang: str = None) -> str:
    """返回指定语言的 STEERING_CONTENT，lang 为 None 时从 settings.json 读取"""

def get_workflow_prompt(lang: str = None) -> str:
    """返回指定语言的 DEV_WORKFLOW_PROMPT"""

LANG_MODULE_MAP = {
    "zh-CN": "zh_CN", "zh-TW": "zh_TW", "en": "en",
    "es": "es", "de": "de", "fr": "fr", "ja": "ja",
}
```

## 4. install.py 改造（F3）

### 4.1 去除硬编码

- 删除 `install.py` 中的 `STEERING_CONTENT` 和 `DEV_WORKFLOW_PROMPT` 常量
- 所有引用改为调用 `from aivectormemory.i18n import get_steering, get_workflow_prompt`
- `_write_steering()` 接收 `lang` 参数：

```python
def _write_steering(filepath, mode, ide_name="", include_workflow=True, lang=None):
    content = get_steering(lang)  # 从 i18n 加载
    if include_workflow:
        workflow = get_workflow_prompt(lang)
        # 注入 workflow 到 content
    ...
```

### 4.2 install 流程增加语言选择

在 IDE 选择之后、MCP 配置之前，增加语言选择步骤：

```
请选择 AI 回复语言 / Choose AI response language:
1. 简体中文 (zh-CN)
2. 繁體中文 (zh-TW)
3. English (en)
4. Español (es)
5. Deutsch (de)
6. Français (fr)
7. 日本語 (ja)
```

选择后调用 `set_language(lang)` 写入全局配置。

## 5. 动态 hook 改造（F2）

### 5.1 inject-workflow-rules.sh

改造 `_write_inject_workflow_script()`，生成的 bash 脚本从静态 heredoc 改为动态读取：

```bash
#!/bin/bash
# 读取语言设置
SETTINGS="$HOME/.aivectormemory/settings.json"
if [ -f "$SETTINGS" ]; then
    LANG_CODE=$(python3 -c "import json; print(json.load(open('$SETTINGS')).get('language','zh-CN'))" 2>/dev/null)
else
    LANG_CODE="zh-CN"
fi
# 输出对应语言的规则
python3 -m aivectormemory.i18n.rules --lang "$LANG_CODE" --type workflow 2>/dev/null
```

或更高效的方案——预生成所有语言的 heredoc，用 case 分支选择：

```bash
#!/bin/bash
SETTINGS="$HOME/.aivectormemory/settings.json"
LANG="zh-CN"
if [ -f "$SETTINGS" ]; then
    # 轻量 JSON 解析，不依赖 python
    LANG=$(grep -o '"language"[[:space:]]*:[[:space:]]*"[^"]*"' "$SETTINGS" | head -1 | sed 's/.*"language"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    [ -z "$LANG" ] && LANG="zh-CN"
fi
case "$LANG" in
    zh-CN) cat <<'EOF_ZH_CN'
...中文规则...
EOF_ZH_CN
    ;;
    en) cat <<'EOF_EN'
...English rules...
EOF_EN
    ;;
    *) cat <<'EOF_DEFAULT'
...中文规则（默认）...
EOF_DEFAULT
    ;;
esac
```

**选择方案 B（case 分支）**：
- 优点：纯 bash，无 Python 依赖，启动快（< 10ms）
- 缺点：脚本体积较大（所有语言内嵌），install 时需要重新生成
- 但 hook 脚本本来就是 install 时生成的，每次语言切换也会重新生成，所以可接受

### 5.2 Kiro hook

Kiro 的 `dev-workflow-check.kiro.hook` 是静态 JSON（askAgent prompt），无法运行时动态读取。方案：install 时按语言生成对应文本。语言切换时重新生成。

### 5.3 OpenCode plugin

`aivectormemory-pre-tool-check.js` 中的 `DEV_WORKFLOW_RULES` 也是静态文本。方案同 Kiro：install 时按语言生成，语言切换时重新生成。

## 6. 桌面端语言切换联动（F4）

### 6.1 Go 后端新增 API

桌面端 Go 后端新增方法：

```go
// SetLanguage 设置语言并更新所有已安装项目的规则文件
func (a *App) SetLanguage(lang string) error {
    // 1. 写入 ~/.aivectormemory/settings.json
    // 2. 调用 Python: python3 -m aivectormemory regenerate --lang <lang>
    //    → 遍历数据库中已注册项目，重新生成 steering + hooks
}
```

### 6.2 Python regenerate 命令

新增 CLI 子命令 `aivectormemory regenerate --lang <lang>`：

```python
def regenerate(lang: str):
    """遍历已注册项目，重新生成静态规则文件"""
    set_language(lang)
    projects = get_all_registered_projects()  # 从数据库读取
    for project in projects:
        # 检测项目安装了哪些 IDE 配置
        # 重新执行 _write_steering() 和 _write_hooks() 等
```

### 6.3 前端联动

桌面端 Vue 前端切换语言时：
1. 调用 `SetLanguage(lang)` → Go → Python regenerate
2. 同时更新 UI 语言（已有逻辑）

## 7. 看板联动（F6）

Web 看板设置页面修改语言时：
1. 调用 API `POST /api/settings/language` → 写入 settings.json
2. 触发 regenerate 逻辑（与桌面端共用同一 Python 函数）

## 8. 数据流总结

| 触发场景 | 动态 hook | 静态文件 |
|---------|-----------|---------|
| 新项目 install | 按当前语言生成 | 按当前语言生成 |
| 桌面端切换语言 | 下次触发自动生效（方案 B：重新生成） | 重新生成 |
| 看板切换语言 | 同上 | 重新生成 |
| CLI regenerate | 同上 | 重新生成 |

## 9. 向后兼容

- `~/.aivectormemory/settings.json` 不存在 → 默认 zh-CN
- `language` 字段为空或无效值 → 默认 zh-CN
- 旧版本 install.py 生成的静态文件不受影响（仍为中文）
- regenerate 命令可手动运行更新

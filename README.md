🌐 [简体中文](docs/README.zh-CN.md) | [繁體中文](docs/README.zh-TW.md) | English | [Español](docs/README.es.md) | [Deutsch](docs/README.de.md) | [Français](docs/README.fr.md) | [日本語](docs/README.ja.md)

<p align="center">
  <img src="docs/logo.png" alt="AIVectorMemory Logo" width="200">
</p>

<p align="center">
  <img src="docs/image.png" alt="AI Vector Memory Architecture" width="100%">
</p>
<h1 align="center">AIVectorMemory</h1>
<p align="center">
  <strong>Give your AI coding assistant a memory — Cross-session persistent memory MCP Server</strong>
</p>
<p align="center">
  <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/v/aivectormemory?color=blue&label=PyPI" alt="PyPI"></a>
  <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/pyversions/aivectormemory" alt="Python"></a>
  <a href="https://github.com/Edlineas/aivectormemory/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache_2.0-green" alt="License"></a>
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple" alt="MCP"></a>
</p>

---

> **Still using CLAUDE.md / MEMORY.md as memory?** This Markdown-file memory approach has fatal flaws: the file keeps growing, injecting everything into every session and burning massive tokens; content only supports keyword matching — search "database timeout" and you won't find "MySQL connection pool pitfall"; sharing one file across projects causes cross-contamination; there's no task tracking, so dev progress lives entirely in your head; not to mention the 200-line truncation, manual maintenance, and inability to deduplicate or merge.
>
> **AIVectorMemory is a fundamentally different approach.** Local vector database storage with semantic search for precise recall (matches even when wording differs), on-demand retrieval that loads only relevant memories (token usage drops 50%+), automatic multi-project isolation with zero interference, and built-in issue tracking + task management that lets AI fully automate your dev workflow. All data is permanently stored on your machine — zero cloud dependency, never lost when switching sessions or IDEs.

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🧠 **Cross-Session Memory** | Your AI finally remembers your project — pitfalls, decisions, conventions all persist across sessions |
| 🔍 **Hybrid Smart Search** | FTS5 full-text + vector semantic dual-path search, RRF fusion ranking + composite scoring (recency × frequency × importance), far more precise than pure vector search |
| 🐛 **Issue Tracking** | Built-in Issue Tracker — discover → investigate → fix → archive, full lifecycle. AI manages bugs automatically |
| 📋 **Task Management** | Spec → task breakdown → nested subtasks → status sync → linked archival. AI drives the complete dev workflow |
| 🚦 **Session State** | Blocking management + breakpoint resume + progress tracking, seamless handoff across sessions and context compaction |
| 🪝 **Hooks + Steering** | Auto-inject workflow rules + behavior guard hooks, consistent AI behavior guaranteed — no need to repeat instructions |
| 🧬 **Memory Evolution** | Contradiction detection auto-supersedes stale knowledge + short-term → long-term auto-promotion + 90-day auto-archive, self-evolving memory |
| 📊 **Desktop App + Web Dashboard** | Native desktop app (macOS/Windows/Linux) + Web dashboard, 3D vector network reveals knowledge connections at a glance |
| 💰 **Save 50%+ Tokens** | Stop copy-pasting project context every conversation. Semantic retrieval on demand, no more bulk injection |
| 🏠 **Fully Local** | Zero cloud dependency. ONNX local inference, no API Key, data never leaves your machine |
| 🔌 **11 IDEs Covered** | Cursor / Kiro / Claude Code / Windsurf / VSCode / Copilot / OpenCode / Trae / Codex / Antigravity / OpenClaw — one-click install & uninstall |
| 📁 **Multi-Project Isolation** | One DB for all projects, auto-isolated with zero interference, seamless project switching |
| 🔄 **Smart Dedup** | Similarity > 0.95 auto-merges updates, keeping your memory store clean — never gets messy over time |
| 🌐 **7 Languages** | 简体中文 / 繁體中文 / English / Español / Deutsch / Français / 日本語, full-stack i18n for dashboard + Steering rules |

<p align="center">
  QQ群：1085682431 &nbsp;|&nbsp; 微信：changhuibiz<br>
  共同参与项目开发加QQ群或微信交流
</p>

<p align="center">
  <img src="docs/003.png" alt="Login" width="100%">
  <br>
  <em>Login</em>
</p>

<p align="center">
  <img src="docs/001.png" alt="Project Selection" width="100%">
  <br>
  <em>Project Selection</em>
</p>

<p align="center">
  <img src="docs/002.png" alt="Overview & Vector Network" width="100%">
  <br>
  <em>Overview & Vector Network</em>
</p>

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                   AI IDE                         │
│  OpenCode / Codex / Claude Code / Cursor / ...  │
└──────────────────────┬──────────────────────────┘
                       │ MCP Protocol (stdio)
┌──────────────────────▼──────────────────────────┐
│              AIVectorMemory Server               │
│                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ remember │ │  recall   │ │   auto_save      │ │
│  │ forget   │ │  task     │ │   status/track   │ │
│  └────┬─────┘ └────┬─────┘ └───────┬──────────┘ │
│       │            │               │             │
│  ┌────▼────────────▼───────────────▼──────────┐  │
│  │         Embedding Engine (ONNX)            │  │
│  │      intfloat/multilingual-e5-small        │  │
│  └────────────────────┬───────────────────────┘  │
│                       │                          │
│  ┌────────────────────▼───────────────────────┐  │
│  │     SQLite + sqlite-vec (Vector Index)     │  │
│  │     ~/.aivectormemory/memory.db            │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Option 1: pip install (Recommended)

```bash
# Install
pip install aivectormemory

# Upgrade to latest version
pip install --upgrade aivectormemory

# Navigate to your project directory, one-click IDE setup
cd /path/to/your/project
run install
```

`run install` interactively guides you to select your IDE, auto-generating MCP config, Steering rules, and Hooks — no manual setup needed.

> **macOS users note**:
> - If you get `externally-managed-environment` error, add `--break-system-packages`
> - If you get `enable_load_extension` error, your Python doesn't support SQLite extension loading (macOS built-in Python and python.org installers don't support it). Use Homebrew Python instead:
>   ```bash
>   brew install python
>   /opt/homebrew/bin/python3 -m pip install aivectormemory
>   ```

### Option 2: uvx (zero install)

No `pip install` needed, run directly:

```bash
cd /path/to/your/project
uvx aivectormemory install
```

> Requires [uv](https://docs.astral.sh/uv/getting-started/installation/) to be installed. `uvx` auto-downloads and runs the package — no manual installation needed.

### Option 3: Manual configuration

```json
{
  "mcpServers": {
    "aivectormemory": {
      "command": "run",
      "args": ["--project-dir", "/path/to/your/project"]
    }
  }
}
```

<details>
<summary>📍 IDE Configuration File Locations</summary>

| IDE | Config Path |
|-----|------------|
| Kiro | `.kiro/settings/mcp.json` |
| Cursor | `.cursor/mcp.json` |
| Claude Code | `.mcp.json` |
| Windsurf | `.windsurf/mcp.json` |
| VSCode | `.vscode/mcp.json` |
| Trae | `.trae/mcp.json` |
| OpenCode | `opencode.json` |
| Codex | `.codex/config.toml` |

</details>

For Codex, use project-scoped TOML instead of JSON:

```toml
[mcp_servers.aivectormemory]
command = "run"
args = ["--project-dir", "/path/to/your/project"]
```

> Codex only loads project-scoped `.codex/config.toml` after the repository is marked as a trusted project.

## 🛠️ 9 MCP Tools

### `remember` — Store a memory

```
content (string, required)   Memory content in Markdown format
tags    (string[], required)  Tags, e.g. ["pitfall", "python"]
scope   (string)              "project" (default) / "user" (cross-project)
```

Similarity > 0.95 auto-updates existing memory, no duplicates.

### `recall` — Semantic search

```
query   (string)     Semantic search keywords
tags    (string[])   Exact tag filter
scope   (string)     "project" / "user" / "all"
top_k   (integer)    Number of results, default 5
```

Vector similarity matching — finds related memories even with different wording.

### `forget` — Delete memories

```
memory_id  (string)     Single ID
memory_ids (string[])   Batch IDs
```

### `status` — Session state

```
state (object, optional)   Omit to read, pass to update
  is_blocked, block_reason, current_task,
  next_step, progress[], recent_changes[], pending[]
```

Maintains work progress across sessions, auto-restores context in new sessions.

### `track` — Issue tracking

```
action   (string)   "create" / "update" / "archive" / "list"
title    (string)   Issue title
issue_id (integer)  Issue ID
status   (string)   "pending" / "in_progress" / "completed"
content  (string)   Investigation content
```

### `task` — Task management

```
action     (string, required)  "batch_create" / "update" / "list" / "delete" / "archive"
feature_id (string)            Linked feature identifier (required for list)
tasks      (array)             Task list (batch_create, supports subtasks)
task_id    (integer)           Task ID (update)
status     (string)            "pending" / "in_progress" / "completed" / "skipped"
```

Links to spec docs via feature_id. Update auto-syncs tasks.md checkboxes and linked issue status.

### `readme` — README generation

```
action   (string)    "generate" (default) / "diff" (compare differences)
lang     (string)    Language: en / zh-TW / ja / de / fr / es
sections (string[])  Specify sections: header / tools / deps
```

Auto-generates README content from TOOL_DEFINITIONS / pyproject.toml, multi-language support.

### `auto_save` — Auto save preferences

```
preferences  (string[])  User-expressed technical preferences (fixed scope=user, cross-project)
extra_tags   (string[])  Additional tags
```

Auto-extracts and stores user preferences at end of each conversation, smart dedup.

### `graph` — Code knowledge graph

```
action       (string, required)  "query" / "trace" / "batch" / "add_node" / "add_edge" / "remove" / "refresh"
name         (string)            Entity name (add_node/query)
entity_type  (string)            Entity type: function/class/module/api/table/config (add_node/query)
file_path    (string)            File path, auto-converts to relative (add_node/query/refresh)
source       (string)            Source node name or ID (add_edge)
target       (string)            Target node name or ID (add_edge)
relation     (string)            Relation type: calls/imports/inherits/uses/depends_on/contains (add_edge/trace)
start        (string)            Start node name or ID (trace)
direction    (string)            Traversal direction: "up" / "down" / "both" (trace)
max_depth    (integer)           Max traversal depth, default 3 (trace)
```

Manages function call chains, data flows, and dependency relationships. Trace upstream/downstream impact before code changes.

## 📊 Web Dashboard

```bash
run web --port 9080
run web --port 9080 --quiet          # Suppress request logs
run web --port 9080 --quiet --daemon  # Run in background (macOS/Linux)
```

Visit `http://localhost:9080` in your browser. Default username `admin`, password `admin123` (can be changed in settings after first login).

- Multi-project switching, memory browse/search/edit/delete/export/import
- Semantic search (vector similarity matching)
- One-click project data deletion
- Session status, issue tracking
- Tag management (rename, merge, batch delete)
- Token authentication protection
- 3D vector memory network visualization
- 🌐 Multi-language support (简体中文 / 繁體中文 / English / Español / Deutsch / Français / 日本語)

<p align="center">
  <img src="docs/20260306234753_6_1635.jpg" alt="WeChat Group" width="280">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="docs/8_1635.jpg" alt="QQ Group: 1085682431" width="280">
  <br>
  <em>Scan to join WeChat group &nbsp;|&nbsp; Scan to join QQ group</em>
</p>

## ⚡ Pairing with Steering Rules

AIVectorMemory is the storage layer. Use Steering rules to tell AI **when and how** to call these tools.

Running `run install` auto-generates Steering rules and Hooks config — no manual setup needed.

| IDE | Steering Location | Hooks |
|-----|------------------|-------|
| Kiro | `.kiro/steering/aivectormemory.md` | `.kiro/hooks/*.hook` |
| Cursor | `.cursor/rules/aivectormemory.md` | `.cursor/hooks.json` |
| Claude Code | `CLAUDE.md` (appended) | `.claude/settings.json` |
| Windsurf | `.windsurf/rules/aivectormemory.md` | `.windsurf/hooks.json` |
| VSCode | `.github/copilot-instructions.md` (appended) | `.claude/settings.json` |
| Trae | `.trae/rules/aivectormemory.md` | — |
| OpenCode | `AGENTS.md` (appended) | `.opencode/plugins/*.js` |
| Codex | `AGENTS.md` (appended) | — |

<details>
<summary>📋 Steering Rules Example (auto-generated)</summary>

```markdown
# AIVectorMemory - Workflow Rules

## 1. New Session Startup (execute in order)

1. `recall` (tags: ["project-knowledge"], scope: "project", top_k: 100) load project knowledge
2. `recall` (tags: ["preference"], scope: "user", top_k: 20) load user preferences
3. `status` (no state param) read session state
4. Blocked → report and wait; Not blocked → enter processing flow

## 2. Message Processing Flow

- Step A: `status` read state, wait if blocked
- Step B: Classify message type (chat/correction/preference/code issue)
- Step C: `track create` record issue
- Step D: Investigate (`recall` pitfalls + read code + find root cause)
- Step E: Present plan to user, set blocked awaiting confirmation
- Step F: Modify code (`recall` pitfalls before changes)
- Step G: Run tests to verify
- Step H: Set blocked awaiting user verification
- Step I: User confirms → `track archive` + clear block

## 3. Blocking Rules

Must `status({ is_blocked: true })` when proposing plans or awaiting verification.
Only clear after explicit user confirmation. Never self-clear.

## 4-9. Issue Tracking / Code Checks / Spec Task Mgmt / Memory Quality / Tool Reference / Dev Standards

(Full rules auto-generated by `run install`)
```

</details>

<details>
<summary>🔗 Hooks Config Example (Kiro only, auto-generated)</summary>

Auto-save on session end removed. Dev workflow check (`.kiro/hooks/dev-workflow-check.kiro.hook`):

```json
{
  "enabled": true,
  "name": "Dev Workflow Check",
  "version": "1",
  "when": { "type": "promptSubmit" },
  "then": {
    "type": "askAgent",
    "prompt": "Core principles: verify before acting, no blind testing, only mark done after tests pass"
  }
}
```

</details>

## 🇨🇳 Users in China

The embedding model (~200MB) is auto-downloaded on first run. If slow:

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

Or add env to MCP config:

```json
{
  "env": { "HF_ENDPOINT": "https://hf-mirror.com" }
}
```

## 📦 Tech Stack

| Component | Technology |
|-----------|-----------|
| Runtime | Python >= 3.10 |
| Vector DB | SQLite + sqlite-vec |
| Embedding | ONNX Runtime + intfloat/multilingual-e5-small |
| Tokenizer | HuggingFace Tokenizers |
| Protocol | Model Context Protocol (MCP) |
| Web | Native HTTPServer + Vanilla JS |

## 📋 Changelog

### v2.4.1

**Patch: i18n Rules Sync**
- 🔄 Synced all 7 language rule files (STEERING_CONTENT + DEV_WORKFLOW_PROMPT) with CLAUDE.md v2.4.0 updates
- 🧬 Added `graph` tool references to all steering rules (trace/batch/add_node/add_edge/remove)
- ✏️ Updated authority role from "Lead Architect" to "Project Owner" across all languages
- 📝 Added 3 new violation rules and 2 new forbidden items to all languages

### v2.4.0

**New: Code Knowledge Graph**
- 🧬 `graph` tool — manage function call chains, data flows, and dependency relationships as a structured knowledge graph
- 🔍 `trace` action — traverse upstream/downstream call chains from any entity, assess impact scope before code changes
- 📊 Web dashboard graph visualization page — browse nodes, edges, and call relationships in the knowledge graph
- 🗃️ DB migration v15 — new `graph_nodes` and `graph_edges` tables for graph storage
- 🌐 All 7 language README files updated in sync

### v2.3.1

**Enhancement: Rule System Overhaul + OpenClaw Support**
- 🧠 Fixed 5 missing memory system calls in AI rules: recall pitfalls before investigation (Step D), before dangerous ops (§7), before Spec writing (§8), before subtask execution (§8), and remember pitfalls after fix (Step I)
- 🦞 Added OpenClaw IDE support — now 11 IDEs total (MCP config merges into ~/.openclaw/openclaw.json, steering appends to AGENTS.md)
- 🎭 Playwright self-test rules strengthened — added ToolSearch deferred tools loading requirement, banned `open` command workaround
- 🔧 Merged v2.2.0–v2.2.6 features: hooks system (bash_guard + stop_guard + check_track), scoring engine improvements, recall optimizations, web dashboard bulk delete, desktop memory delete modal
- ⚠️ DEV_WORKFLOW_PROMPT: added 2 new violation reminders (recall before code change, remember after fix)
- 🌐 All 7 language rule files updated in sync

### v2.1.1

**Enhancement: AI Rule System Upgrade**
- 📋 CLAUDE.md completion: added Identity & Tone (§1), 7 Core Principles (§3), message type judgment examples, expanded IDE safety and self-test sections
- ⚠️ Hook added Common Violations Reminder: ❌ negative examples reinforcing the 4 most frequently missed rules (self-test, recall, track create, IDE safety)
- 🌐 All 7 language rule files updated in sync (zh-CN/zh-TW/en/ja/es/de/fr)
- 🔢 CLAUDE.md sections renumbered to §1–§11, cross-references updated accordingly

### v2.1.0

**New: Smart Memory Engine + Uninstall**
- 🧠 FTS5 full-text search with Chinese tokenization (jieba) — keyword search now actually works for CJK content
- 🔀 Hybrid retrieval: vector + FTS5 dual-path with RRF (Reciprocal Rank Fusion) merging
- 📊 Composite scoring: results ranked by similarity × 0.5 + recency × 0.3 + frequency × 0.2, weighted by importance
- ⚡ Conflict detection: similar memories (0.85–0.95) auto-superseded, old facts fade automatically
- 📦 Memory tiers: frequently accessed memories auto-promote to long_term and get searched first
- 🗑️ Auto-archive: stale short_term memories (90 days inactive + low importance) cleaned up automatically
- 🔗 Relation expansion: tag overlap ≥ 2 builds related links, 1-hop expansion surfaces connected memories
- 📝 Auto-summary: long memories (>500 chars) get summaries, brief mode returns summaries to save tokens
- 🧹 Code cleanup: removed 15 dead code items, refactored 7 duplicate patterns into shared utilities
- ❌ `run uninstall` — cleanly removes all IDE configurations (MCP, steering, hooks, permissions) while preserving memory data

### v2.0.9

**Enhancement: Security & Rule Optimization**
- 🔒 Fixed SQL injection, command injection, and path traversal vulnerabilities
- 🛡️ Added transaction protection for data integrity (archive, insert, update operations)
- 🧠 Unified similarity formula across all search paths
- 📏 Compressed AI workflow rules by 38% (219→136 lines) with zero process removal
- 🧹 v12 migration cleans up legacy garbage memories automatically
- 🌐 All 7 languages synchronized

### v2.0.8

**New: Playwright Browser Testing Built-in**
- 🎭 `run install` now automatically configures Playwright browser testing — AI can open a real browser to verify frontend changes instead of guessing
- 🎭 Uses a dedicated test browser (Chrome for Testing) that won't interfere with your personal browser tabs
- 🔑 Simplified permission setup — no more manual permission popups for common tools
- 📏 Updated AI rules across all 7 languages to enforce proper browser testing behavior

### v2.0.7

**Enhancement: More IDE Support**
- 🖥️ Added support for Antigravity and GitHub Copilot IDEs
- 🔑 `run install` now auto-configures tool permissions, reducing manual setup
- 📏 Streamlined AI self-testing rules

### v2.0.6

**Enhancement: Faster Startup**
- ⚡ Optimized memory loading on session start — loads faster with less context usage
- 🔑 Auto-configures Claude Code permissions during installation
- 🌐 All 7 languages synchronized

### v2.0.5

**Enhancement: Simpler Rules**
- 📏 AI workflow rules restructured for clarity and reduced token usage
- 💾 AI now automatically saves your preferences at the end of each session
- 🌐 All 7 languages synchronized

### v2.0.4

**Fix: Tool Reliability**
- 🔧 Comprehensive audit and fix of all MCP tool parameters — improved reliability across all IDEs

### v2.0.3

**Enhancement: Better Search & Safety**
- 🔍 Memory search now combines semantic and keyword matching for more accurate recall
- 🛡️ Added cross-project protection — AI won't accidentally modify files in other projects

### v2.0.2

**Enhancement: Rule Generalization & Desktop Version Fix**
- 📏 Added "recall before asking user" rule — AI must query memory system before asking user for project information (server address, passwords, deploy config, etc.)
- 📏 Generalized pre-operation check rule — removed specific examples to apply to all operation scenarios
- 🖥️ Fixed desktop app settings page showing hardcoded version "1.0.0" instead of actual app version
- 🌐 All 7 language i18n steering rules and workflow prompts synchronized

### v2.0.1

**Fix: Hook Cross-Project Compatibility**
- 🔧 `check_track.sh` now derives project path from script location instead of `$(pwd)`, fixing track detection failure when Claude Code runs hooks from non-root working directory
- 🔧 `compact-recovery.sh` now uses relative path derivation instead of hardcoded absolute paths, ensuring correct behavior when installed to any project
- 🔧 Removed redundant CLAUDE.md re-injection from compact-recovery (already auto-loaded by Claude Code)
- 🔧 `install.py` template synchronized with all hook fixes
- 🌐 All 7 language i18n compact-recovery hints updated

### v2.0

**Performance: ONNX INT8 Quantization**
- ⚡ Embedding model auto-quantized from FP32 to INT8 on first load, model file from 448MB down to 113MB
- ⚡ MCP Server memory usage reduced from ~1.6GB to ~768MB (50%+ reduction)
- ⚡ Quantization is transparent to users — automatic on first use, cached for subsequent loads, falls back to FP32 on failure

**New: Remember Password**
- 🔐 Login page on both desktop and web dashboard now has a "Remember password" checkbox
- 🔐 When checked, credentials are saved to localStorage and auto-filled on next login; when unchecked, saved credentials are cleared
- 🔐 Checkbox is hidden in registration mode

**Enhancement: Steering Rules**
- 📝 IDENTITY & TONE section strengthened with more specific constraints (no pleasantries, no translating user messages, etc.)
- 📝 Self-testing requirements now distinguish between backend-only, MCP Server, and frontend-visible changes (Playwright required for frontend)
- 📝 Development rules now mandate self-testing after completing development
- 📝 All 7 language versions synchronized

### v1.0.11

- 🐛 Desktop app version comparison switched to semantic versioning, fixing false upgrade prompts when local version is higher
- 🐛 Health check page field names aligned with backend, fixing consistency status always showing Mismatch
- 🔧 check_track.sh hook adds Python fallback, resolving silent hook failure when system sqlite3 is unavailable (#4)

### v1.0.10

- 🖥️ Desktop app one-click install + upgrade detection
- 🖥️ Auto-detect Python and aivectormemory installation status on startup
- 🖥️ Show one-click install button when not installed, check PyPI and desktop new versions when installed
- 🐛 Installation detection switched to importlib.metadata.version() for accurate package version

### v1.0.8

- 🔧 Fix PyPI package size anomaly (sdist from 32MB down to 230KB), excluded accidentally packaged dev files

### v1.0.6

**New: Native Desktop App**
- 🖥️ Native desktop client supporting macOS (ARM64), Windows (x64), Linux (x64)
- 🖥️ Desktop app shares the same database as Web dashboard, fully feature-equivalent
- 🖥️ Dark/light theme switching, Glass frosted visual style
- 🖥️ Login auth, project selection, stats overview, memory management, issue tracking, task management, tag management, settings, data maintenance — full feature coverage
- 📦 Auto-published installers via GitHub Releases, download and use

**New: CI/CD Auto Build**
- 🔄 GitHub Actions auto-builds desktop installers for all 3 platforms
- 🔄 Push a tag to trigger the full compile, package, and release pipeline

**Fixes**
- 🐛 Windows platform compatibility fixes
- 🐛 sqlite-vec extension download URL fix

### v1.0.5

**Optimization: Token Usage Reduction**
- ⚡ Steering rules changed from per-message dynamic injection to static loading, reducing repeated token consumption
- ⚡ Greatest impact for Claude Code users — ~2K fewer tokens per message

### v1.0.4

**New: Full-Stack i18n (7 Languages)**
- 🌐 Web dashboard + desktop UI fully supports 7 languages: 简体中文 / 繁體中文 / English / Español / Deutsch / Français / 日本語
- 🌐 One-click language switch in settings page, takes effect immediately
- 🌐 MCP tool responses follow language setting, AI replies automatically use the corresponding language
- 🌐 Switching language auto-regenerates steering rules for all installed projects

**New: Web Dashboard Settings Page**
- ⚙️ Language switch, theme settings, system info display
- ⚙️ Database health check, repair, backup and other maintenance tools

### v1.0.3

**Optimization: Memory Search**
- 🔍 `recall` search supports OR/AND tag matching modes, fixing missed results with multi-tag searches
- 🔍 Semantic search + tag filter defaults to OR matching (broader), tags-only browsing keeps AND matching (more precise)

<details>
<summary>📋 v0.2.x and earlier changelog</summary>

See [CHANGELOG-archive.md](docs/CHANGELOG-archive.md)

</details>

## License

Apache-2.0

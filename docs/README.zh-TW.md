🌐 [简体中文](README.zh-CN.md) | 繁體中文 | [English](../README.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [日本語](README.ja.md)

<p align="center">
  <img src="logo.png" alt="AIVectorMemory Logo" width="200">
</p>
<h1 align="center">AIVectorMemory</h1>
<p align="center">
  <strong>為 AI 程式助手裝上記憶 — 跨會話持久化記憶 MCP Server</strong>
</p>
<p align="center">
  <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/v/aivectormemory?color=blue&label=PyPI" alt="PyPI"></a>
  <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/pyversions/aivectormemory" alt="Python"></a>
  <a href="https://github.com/Edlineas/aivectormemory/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache_2.0-green" alt="License"></a>
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple" alt="MCP"></a>
</p>
---

> **你還在用 CLAUDE.md / MEMORY.md 當記憶？** 這類 Markdown 檔案記憶模式有致命缺陷：檔案越寫越大，每次會話全量注入吃掉大量 Token；內容只能關鍵詞匹配，搜「資料庫逾時」找不到「MySQL 連線池踩坑」；多專案共用一個檔案互相污染；沒有任務追蹤，開發進度全靠人腦記；更別提 200 行截斷、手動維護、無法去重合併這些日常痛點了。
>
> **AIVectorMemory 是完全不同的方案。** 本地向量資料庫儲存，語義搜尋精準召回（用詞不同也能匹配），按需檢索只載入相關記憶（Token 消耗直降 50%+），多專案自動隔離互不干擾，內建問題追蹤 + 任務管理讓 AI 全自動管理開發流程。所有資料永久保存在你的電腦上，零雲端依賴，換會話、換 IDE 都不丟。

## ✨ 核心特性

| 特性 | 說明 |
|------|------|
| 🧠 **跨會話記憶** | AI 終於能記住你的專案了 — 踩過的坑、做過的決策、定下的規範，換個會話照樣記得 |
| 🔍 **語義搜尋** | 不用記原文怎麼寫的，搜「資料庫逾時」就能找到「MySQL 連線池踩坑」 |
| 💰 **省 50%+ Token** | 不再每次對話都複製貼上專案背景，語義檢索按需召回，告別全量上下文注入 |
| 🔗 **任務驅動開發** | 問題追蹤 → 任務拆分 → 狀態同步 → 聯動歸檔，AI 自動管理完整開發流程 |
| 📊 **Web 看板** | 視覺化管理所有記憶和任務，3D 向量網路一眼看清知識關聯 |
| 🏠 **完全本地** | 零依賴雲端服務，ONNX 本地推理，無需 API Key，資料不出你的電腦 |
| 🔌 **全 IDE 通吃** | Cursor / Kiro / Claude Code / Windsurf / VSCode / OpenCode / Trae / Codex — 一鍵安裝，開箱即用 |
| 📁 **多專案隔離** | 一個 DB 管所有專案，自動隔離互不干擾，切換專案無感知 |
| 🔄 **智慧去重** | 相似度 > 0.95 自動合併更新，記憶庫永遠乾淨，不會越用越亂 |

<p align="center">
  QQ群：1085682431 &nbsp;|&nbsp; 微信：changhuibiz<br>
  共同参与项目开发加QQ群或微信交流
</p>

## 🏗️ 架構

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
│  │     SQLite + sqlite-vec（向量索引）         │  │
│  │     ~/.aivectormemory/memory.db            │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## 🚀 快速開始

### 方式一：pip 安裝（推薦）

```bash
# 安裝
pip install aivectormemory

# 升級到最新版
pip install --upgrade aivectormemory

# 進入你的專案目錄，一鍵配置 IDE
cd /path/to/your/project
run install
```

`run install` 會互動式引導你選擇 IDE，自動生成 MCP 配置、Steering 規則和 Hooks，無需手動編寫。

> **macOS 使用者注意**：
> - 遇到 `externally-managed-environment` 錯誤，加 `--break-system-packages`
> - 遇到 `enable_load_extension` 錯誤，說明當前 Python 不支援 SQLite 擴展載入（macOS 自帶 Python 和 python.org 官方安裝包均不支援），請改用 Homebrew Python：
>   ```bash
>   brew install python
>   /opt/homebrew/bin/python3 -m pip install aivectormemory
>   ```

### 方式二：uvx 執行（零安裝）

無需 `pip install`，直接執行：

```bash
cd /path/to/your/project
uvx aivectormemory install
```

> 需要先安裝 [uv](https://docs.astral.sh/uv/getting-started/installation/)，`uvx` 會自動下載並執行，無需手動安裝套件。

### 方式三：手動配置

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
<summary>📍 各 IDE 設定檔位置</summary>

| IDE | 設定檔路徑 |
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

Codex 使用專案級 TOML 設定，而不是 JSON：

```toml
[mcp_servers.aivectormemory]
command = "run"
args = ["--project-dir", "/path/to/your/project"]
```

> 只有把倉庫標記為 trusted project 後，Codex 才會載入專案級 `.codex/config.toml`。

## 🛠️ 8 個 MCP 工具

### `remember` — 存入記憶

```
content (string, 必填)   記憶內容，Markdown 格式
tags    (string[], 必填)  標籤，如 ["踩坑", "python"]
scope   (string)          "project"（預設）/ "user"（跨專案）
```

相似度 > 0.95 自動更新已有記憶，不重複儲存。

### `recall` — 語義搜尋

```
query   (string)     語義搜尋關鍵詞
tags    (string[])   標籤精確過濾
scope   (string)     "project" / "user" / "all"
top_k   (integer)    回傳數量，預設 5
```

向量相似度匹配，用詞不同也能找到相關記憶。

### `forget` — 刪除記憶

```
memory_id  (string)     單個 ID
memory_ids (string[])   批次 ID
```

### `status` — 會話狀態

```
state (object, 可選)   不傳=讀取，傳=更新
  is_blocked, block_reason, current_task,
  next_step, progress[], recent_changes[], pending[]
```

跨會話保持工作進度，新會話自動恢復上下文。

### `track` — 問題追蹤

```
action   (string)   "create" / "update" / "archive" / "list"
title    (string)   問題標題
issue_id (integer)  問題 ID
status   (string)   "pending" / "in_progress" / "completed"
content  (string)   排查內容
```

### `task` — 任務管理

```
action     (string, 必填)  "batch_create" / "update" / "list" / "delete" / "archive"
feature_id (string)        關聯功能標識（list 時必填）
tasks      (array)         任務列表（batch_create，支援子任務）
task_id    (integer)       任務 ID（update）
status     (string)        "pending" / "in_progress" / "completed" / "skipped"
```

透過 feature_id 關聯 spec 文件，update 自動同步 tasks.md checkbox 並聯動問題狀態。

### `readme` — README 生成

```
action   (string)    "generate"（預設）/ "diff"（差異對比）
lang     (string)    語言：en / zh-TW / ja / de / fr / es
sections (string[])  指定章節：header / tools / deps
```

從 TOOL_DEFINITIONS / pyproject.toml 自動生成 README 內容，支援多語言。

### `auto_save` — 自動儲存偏好

```
preferences  (string[])  使用者表達的技術偏好（固定 scope=user，跨專案通用）
extra_tags   (string[])  額外標籤
```

每次對話結束自動提取並儲存使用者偏好，智慧去重。

## 📊 Web 看板

```bash
run web --port 9080
run web --port 9080 --quiet          # 屏蔽請求日誌
run web --port 9080 --quiet --daemon  # 背景執行（macOS/Linux）
```

瀏覽器存取 `http://localhost:9080`，預設用戶名 `admin`，密碼 `admin123`（首次登入後可在設定中修改）

- 多專案切換，記憶瀏覽/搜尋/編輯/刪除/匯出/匯入
- 語義搜尋（向量相似度匹配）
- 專案資料一鍵刪除
- 會話狀態、問題追蹤
- 標籤管理（重新命名、合併、批次刪除）
- Token 認證保護
- 3D 向量記憶網路視覺化
- 🌐 多語言支援（简体中文 / 繁體中文 / English / Español / Deutsch / Français / 日本語）

<p align="center">
  <img src="003.png" alt="登入介面" width="100%">
  <br>
  <em>登入介面</em>
</p>

<p align="center">
  <img src="dashboard-projects.png" alt="專案選擇" width="100%">
  <br>
  <em>專案選擇</em>
</p>

<p align="center">
  <img src="dashboard-overview.png" alt="統計概覽 & 向量網路視覺化" width="100%">
  <br>
  <em>統計概覽 & 向量網路視覺化</em>
</p>

<p align="center">
  <img src="20260306234753_6_1635.jpg" alt="微信群" width="280">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="8_1635.jpg" alt="QQ群：1085682431" width="280">
  <br>
  <em>微信掃碼加群 &nbsp;|&nbsp; QQ掃碼加群</em>
</p>

## ⚡ 搭配 Steering 規則

AIVectorMemory 是儲存層，透過 Steering 規則告訴 AI **何時、如何**呼叫這些工具。

執行 `run install` 會自動產生 Steering 規則和 Hooks 設定，無需手動編寫。

| IDE | Steering 位置 | Hooks |
|-----|--------------|-------|
| Kiro | `.kiro/steering/aivectormemory.md` | `.kiro/hooks/*.hook` |
| Cursor | `.cursor/rules/aivectormemory.md` | `.cursor/hooks.json` |
| Claude Code | `CLAUDE.md`（追加） | `.claude/settings.json` |
| Windsurf | `.windsurf/rules/aivectormemory.md` | `.windsurf/hooks.json` |
| VSCode | `.github/copilot-instructions.md`（追加） | `.claude/settings.json` |
| Trae | `.trae/rules/aivectormemory.md` | — |
| OpenCode | `AGENTS.md`（追加） | `.opencode/plugins/*.js` |
| Codex | `AGENTS.md`（追加） | — |

<details>
<summary>📋 Steering 規則範例（自動產生）</summary>

```markdown
# AIVectorMemory - 工作規則

## 1. 新會話啟動（必須按順序執行）

1. `recall`（tags: ["項目知識"], scope: "project", top_k: 100）載入項目知識
2. `recall`（tags: ["preference"], scope: "user", top_k: 20）載入使用者偏好
3. `status`（不傳 state）讀取會話狀態
4. 有阻塞 → 匯報並等待；無阻塞 → 進入處理流程

## 2. 收到訊息後的處理流程

- 步驟 A：`status` 讀取狀態，有阻塞則等待
- 步驟 B：判斷訊息類型（閒聊/糾正/偏好/程式碼問題）
- 步驟 C：`track create` 記錄問題
- 步驟 D：排查（`recall` 查踩坑 + 查看程式碼 + 找根因）
- 步驟 E：向使用者說明方案，設阻塞等確認
- 步驟 F：修改程式碼（修改前 `recall` 查踩坑）
- 步驟 G：執行測試驗證
- 步驟 H：設阻塞等待使用者驗證
- 步驟 I：使用者確認 → `track archive` + 清阻塞

## 3. 阻塞規則

提方案等確認、修復完等驗證時必須 `status({ is_blocked: true })`。
使用者明確確認後才能清除阻塞，禁止自行清除。

## 4-9. 問題追蹤 / 程式碼檢查 / Spec 任務管理 / 記憶品質 / 工具速查 / 開發規範

（完整規則由 `run install` 自動產生）
```

</details>

<details>
<summary>🔗 Hooks 設定範例（全 IDE 支援，自動產生）</summary>

會話結束自動儲存已移除，開發流程檢查（`.kiro/hooks/dev-workflow-check.kiro.hook`）：

```json
{
  "enabled": true,
  "name": "開發流程檢查",
  "version": "1",
  "when": { "type": "promptSubmit" },
  "then": {
    "type": "askAgent",
    "prompt": "核心原則：操作前驗證、禁止盲目測試、自測通過才能說完成"
  }
}
```

</details>

## 🇨🇳 中國大陸使用者

首次執行自動下載 Embedding 模型（~200MB），如果慢：

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

或在 MCP 設定中加 env：

```json
{
  "env": { "HF_ENDPOINT": "https://hf-mirror.com" }
}
```

## 📦 技術棧

| 元件 | 技術 |
|------|------|
| 執行環境 | Python >= 3.10 |
| 向量資料庫 | SQLite + sqlite-vec |
| Embedding | ONNX Runtime + intfloat/multilingual-e5-small |
| 分詞器 | HuggingFace Tokenizers |
| 協議 | Model Context Protocol (MCP) |
| Web | 原生 HTTPServer + Vanilla JS |

## 📋 更新日誌

### v2.2.1

**熱修復：移除 git commit/push 硬阻斷 + 擴展手動操作檢測**
- 🐛 修復 bash_guard 硬阻斷 git commit/push。改為 steering 規則 + stop_guard 兜底
- 🛡️ stop_guard 手動操作詞表擴展為短子串匹配
- 📝 G1-G4 檢查清單增加「立即執行」

### v2.2.0

**重大升級：通用 Hooks — 8 個 IDE、7 語言、跨平台、自動升級**
- 🛡️ Hooks 從 .sh 腳本遷移到 Python 模組（`python3 -m aivectormemory.hooks.xxx`）— 跨平台，pip 升級自動生效
- 🛡️ `bash_guard` 擴展到 7 條規則：+ git commit/push 攔截 + 部署命令攔截
- 🛡️ `stop_guard` 擴展到 7 項檢查：+ 後端測試 + grep 副作用 + track update + status 阻塞
- 🌐 所有 hook 錯誤訊息支持 7 種語言
- 🔌 bash_guard 部署到所有 IDE：Cursor、Windsurf、Kiro、Codex CLI、Copilot、Gemini CLI
- 🆕 新增 IDE 支持：Codex CLI、GitHub Copilot、Gemini CLI
- ✅ 測試套件：48 → 114 個測試

### v2.1.11

**修復：桌面端記憶刪除 + Web 看板批量刪除**
- 🐛 修復桌面端記憶刪除無效 — 原生 `confirm()` 在 Wails WebView 中不工作，改為自定義 Modal 確認框
- ✨ Web 看板記憶頁面（專案 + 全域）增加批量刪除功能 — 批量操作按鈕、checkbox 多選、全選、批量刪除確認
- 🌐 7種語言新增批量刪除相關翻譯

### v2.1.10

**增強：自行修正規則 — AI 必須自行修復自己的操作失誤**
- 📝 核心原則第 5 條強化（7語言同步）：「自己的操作失誤必須自行修正，禁止問使用者要不要修復」

### v2.1.9

**增強：Hook 硬性攔截 — Bash Guard + Stop Guard + 測試決策樹**
- 🛡️ 新增 `bash_guard.sh`（PreToolUse Bash）：攔截 `open http`（必須用 Playwright MCP）、多行 `python3 -c`、`$()+管道` 組合、`mysql -e` 多語句
- 🛡️ 新增 `stop_guard.sh`（Stop hook）：解析 transcript 檢測——改了程式碼沒用 Playwright 驗證 + 回覆含「手動操作」違規詞。AI 必須用 Playwright 或明確聲明「此改動不影響前端頁面」
- 🎯 G1 測試規則增加決策樹（7語言同步）：按改動影響範圍選擇測試方式（前端程式碼→Playwright，API 影響頁面→curl+Playwright，純後端→pytest/curl，不確定→Playwright）
- 🔧 移除 `_cleanup_legacy_playwright`（重新安裝不再刪除已有的 Playwright 設定）
- 🔧 Playwright MCP 安裝預設值從 N 改為 Y
- 🔧 自測規則強化：Playwright MCP 使用前需 ToolSearch 載入，禁止假設工具不可用

### v2.1.8

**增強：工作規則恢復詳細版 — 完整工作流程步驟 + 防跳過機制**
- 📝 恢復精簡前的詳細工作流程步驟（步驟 C/D/E/F/I 含明確 recall 格式、排查檢查點、中途打斷處理）
- 🛡️ 新增兜底規則：使用者提到否定詞（「不對/不行/沒有/報錯」）→ 預設 track create，AI 不能再自行判斷「設計如此」跳過記錄
- ⚠️ 所有 11 個章節標題加上 ⚠️ 前綴，提升注意力優先級
- 🌐 第 1 節統一為 `IDENTITY & TONE`，欄位名用英文 key（Role/Language/Voice/Authority），7 語言同步
- 🔧 修復 `_write_steering` anchor 以支援靈活的章節標題格式

### v2.1.7

**修復：Playwright MCP 配置不再強制寫入**
- 🔧 `install` 時 Playwright MCP 改為可選（僅在有 `npx` 時詢問，預設不安裝）
- 🩹 `install` 自動清理舊版強制寫入的 Playwright 配置 — 修復 OpenCode「mcp.playwright: Invalid input」崩潰
- 🗑️ 移除 server 啟動時的 `auto_repair_playwright_config`（配置校驗失敗時不可達）
- ➕ 新增 `avmrun` 短命令別名（`avmrun install`、`avmrun web` 等）

### v2.1.6

**修復：CLI 入口點重新命名**
- 🔧 將 CLI 入口點從 `run` 重新命名為 `aivectormemory` — `uvx aivectormemory` 現可直接使用，無需 `--from` 變通方案
- ♻️ 同步更新 argparse `prog` 名稱及安裝配置

### v2.1.5

**修復：Playwright MCP 配置相容性**
- 🔧 修復 OpenCode 升級後報 `mcp.playwright: Invalid input` 錯誤 — `_build_playwright_config` 缺少 OpenCode 格式處理（缺少 `type: local` + 陣列 `command`）
- ♻️ 重構 `_build_playwright_config` 複用 `_build_config` 格式邏輯 — 消除重複分支，自動適配所有 IDE 格式
- 🩹 新增 `auto_repair_playwright_config`：MCP server 啟動時自動檢測並修復錯誤的 Playwright 配置 — 升級無感，無需手動重裝

### v2.1.4

**修復：被取代記憶的可見性**
- 🔓 移除了將被取代記憶從召回結果中完全隱藏的硬過濾 — 此前 `exclude_superseded=true`（預設）在評分之前就阻止了這些記憶，使其永久不可見
- 📊 被取代記憶現在透過 importance 降低（`×0.3`）+ `sqrt(importance)` 評分自然排序 — 它們在結果中排名靠後而非完全消失
- 🧹 移除了 `_load_superseded_ids` 函數及相關死代碼

### v2.1.3

**修復：評分引擎全面重構**
- 🧮 修復關鍵 bug：複合評分現在使用原始向量相似度而非 RRF 排名分 — 此前 ~0.8 的相似度被替換為 ~0.015 的 RRF 分數，破壞了語義相關性信號
- √ importance 從直接乘數改為 `sqrt(importance)` — 降低極端懲罰（0.15 → 0.387 而非 0.15），同時保留 supersede 抑制能力
- 🛡️ 相似度保底：相似度 ≥ 0.85 的記憶獲得保底最低分，防止高相關性記憶被低 importance 埋沒
- ⚖️ 權重重新平衡：similarity 0.55（原 0.5）、recency 0.30、frequency 0.15（原 0.2）— 語義相關性現在主導排序
- 📉 FTS 純文字回退分從 0.5 降至 0.3 — 純關鍵字匹配不再獲得虛高的相似度分數

### v2.1.2

**修復：記憶召回準確性**
- 🔍 修復分層搜尋貪心截斷：`long_term` 結果填滿後 `short_term` 記憶完全跳過，導致高相關性記憶不可見
- 🔧 兩個層級同時搜尋，由複合評分統一排序（相似度 × 時效 × 頻率 × 重要度）
- 🛡️ 修復 `_search_tier` 中 filters 字典引用修改 bug

### v2.1.1

**優化：AI 規則體系升級**
- 📋 CLAUDE.md 補全：新增身份與語氣（§1）、核心原則 7 條（§3）、訊息類型判斷示例、IDE 安全和自測詳細展開
- ⚠️ Hook 新增高頻違規提醒：用 ❌ 負面示例強化自測、recall、track create、IDE 安全 4 項最常遺漏規則
- 🌐 7 語言規則檔案全量同步更新（zh-CN/zh-TW/en/ja/es/de/fr）
- 🔢 CLAUDE.md 章節重新編號為 §1–§11，交叉引用同步更新

### v2.1.0

**新功能：智慧記憶引擎 + 解除安裝**
- 🧠 FTS5 全文搜尋，支援中文分詞（jieba）— 關鍵字搜尋終於能正確匹配中文內容
- 🔀 混合檢索：向量 + FTS5 雙路搜尋，RRF（倒數排名融合）合併結果
- 📊 複合評分：相似度×0.5 + 時間衰減×0.3 + 存取頻率×0.2，乘以重要性權重
- ⚡ 矛盾偵測：相似記憶（0.85–0.95）自動標記為已替代，舊事實自動淡出
- 📦 記憶分層：高頻存取記憶自動晉升為 long_term，優先搜尋
- 🗑️ 自動歸檔：過期短期記憶（90 天未存取 + 低重要性）自動清理
- 🔗 關係擴展：標籤重疊 ≥ 2 自動建立關聯，1 跳擴展發現相關記憶
- 📝 自動摘要：長記憶（>500 字）產生摘要，brief 模式回傳摘要節省 token
- 🧹 程式碼清理：刪除 15 項死碼，7 項重複程式碼重構為共用函式
- ❌ `run uninstall` — 一鍵清理所有 IDE 設定（MCP、規則、hooks、權限），保留記憶資料

### v2.0.9

**增強：安全加固 + 規則優化**
- 🔒 修復 SQL 注入、命令注入、目錄遍歷等安全漏洞
- 🛡️ 為資料完整性添加事務保護（歸檔、插入、更新操作）
- 🧠 統一所有搜尋路徑的相似度計算公式
- 📏 AI 工作規則壓縮 38%（219→136 行），零流程刪除
- 🧹 v12 遷移自動清理歷史垃圾記憶
- 🌐 7 種語言同步更新

### v2.0.8

**新功能：內建 Playwright 瀏覽器測試**
- 🎭 `run install` 現在自動配置 Playwright 瀏覽器測試 — AI 可以開啟真實瀏覽器驗證前端變更
- 🎭 使用獨立的測試瀏覽器（Chrome for Testing），不會影響你的個人瀏覽器分頁
- 🔑 簡化權限配置 — 常用工具不再彈出權限確認
- 📏 7 種語言 AI 規則全部更新，強制規範瀏覽器測試行為

### v2.0.7

**增強：更多 IDE 支援**
- 🖥️ 新增 Antigravity 和 GitHub Copilot IDE 支援
- 🔑 `run install` 自動配置工具權限，減少手動設定
- 📏 精簡 AI 自測規則

### v2.0.6

**增強：更快啟動**
- ⚡ 優化會話啟動時的記憶載入 — 啟動更快，上下文佔用更少
- 🔑 安裝時自動配置 Claude Code 權限
- 🌐 7 種語言同步

### v2.0.5

**增強：規則精簡**
- 📏 AI 工作流規則重構，更清晰且減少 token 消耗
- 💾 AI 現在會在每次會話結束時自動儲存你的偏好設定
- 🌐 7 種語言同步

### v2.0.4

**修復：工具可靠性**
- 🔧 全面審計修復所有 MCP 工具參數 — 提升各 IDE 下的可靠性

### v2.0.3

**增強：更精準的搜尋 & 安全防護**
- 🔍 記憶搜尋現在結合語義和關鍵字匹配，召回更精準
- 🛡️ 新增跨專案操作防護 — AI 不會意外修改其他專案的檔案

### v2.0.2

**增強：規則通用化 & 桌面端版本顯示修復**
- 📏 新增「recall 優先於詢問使用者」規則 — AI 在詢問使用者專案資訊（伺服器地址、密碼、部署配置等）前必須先查詢記憶系統
- 📏 操作前檢查規則通用化 — 移除具體舉例，適用於所有操作場景
- 🖥️ 修復桌面端設定頁版本號硬編碼為 "1.0.0" 的問題，改為動態取得實際版本
- 🌐 7 種語言 i18n 引導規則和工作流提示同步更新

### v2.0.1

**修復：Hook 跨專案相容性**
- 🔧 `check_track.sh` 改為從腳本自身位置推導專案路徑，修復 Claude Code 從非根目錄執行 hook 時 track 偵測失敗的問題
- 🔧 `compact-recovery.sh` 改為相對路徑推導，修復安裝到其他專案後路徑指向錯誤專案的問題
- 🔧 移除 compact-recovery 中冗餘的 CLAUDE.md 重複注入（Claude Code 已自動載入）
- 🔧 `install.py` 範本同步所有 hook 修復
- 🌐 7 種語言 i18n compact-recovery 提示文字更新

### v2.0

**效能優化：ONNX INT8 量化**
- ⚡ Embedding 模型首次載入時自動從 FP32 量化為 INT8，模型檔案從 448MB 降至 113MB
- ⚡ MCP Server 記憶體佔用從 ~1.6GB 降至 ~768MB（降幅超 50%）
- ⚡ 量化對使用者完全透明 — 首次使用自動執行，後續載入使用快取，失敗自動回退 FP32

**新增：記住密碼**
- 🔐 桌面端和 Web 看板登入頁新增「記住密碼」checkbox
- 🔐 勾選後憑證儲存至 localStorage，下次登入自動填充；取消勾選則清除已儲存憑證
- 🔐 註冊模式下隱藏 checkbox

**強化：工作規則**
- 📝 IDENTITY & TONE 章節增加更具體的約束（禁止客套話、禁止翻譯使用者訊息等）
- 📝 自測要求細分為純後端、MCP Server、前端可見變更三類（前端變更必須 Playwright 驗證）
- 📝 開發規則新增「開發完成必須自測」
- 📝 7 種語言版本同步更新

### v1.0.11

- 🐛 桌面端版本比較改為語義版本比較，修復本地版本較高時誤報升級
- 🐛 健康檢查頁面欄位名稱與後端對齊，修復一致性狀態永遠顯示 Mismatch
- 🔧 check_track.sh hook 新增 Python fallback，解決無系統 sqlite3 時 hook 靜默失敗（#4）

### v1.0.10

- 🖥️ 桌面端一鍵安裝 + 升級檢測功能
- 🖥️ 啟動時自動檢測 Python 和 aivectormemory 安裝狀態
- 🖥️ 未安裝時顯示一鍵安裝按鈕，已安裝時檢測 PyPI 和桌面端新版本
- 🐛 安裝檢測改用 importlib.metadata.version() 取得準確套件版本

### v1.0.3

**recall 搜尋優化**
- 🔍 `recall` 新增 `tags_mode` 參數：`any`（OR 匹配）/ `all`（AND 匹配）
- 🔍 `query + tags` 時預設 OR 匹配（匹配任一標籤即進入候選），解決多標籤搜尋漏結果問題
- 🔍 僅 `tags` 時保持 AND 匹配（精確分類瀏覽），向後相容
- 📝 Steering 規則更新搜尋規範，按搜尋目的選標籤，禁止所有搜尋都帶「踩坑」

### v0.2.8

**Web 看板**
- 📋 歸檔問題詳情彈窗：點擊歸檔卡片彈出唯讀詳情（含所有結構化欄位：排查過程/根因/解決方案/自測結果/修改檔案），底部紅色刪除按鈕支援永久刪除歸檔記錄

**Steering 規則強化**
- 📝 `track create` 強制要求 `content` 必填（簡述問題現象和背景），禁止只傳 title 留空
- 📝 排查後 `track update` 強制要求填充 `investigation`（排查過程）和 `root_cause`（根本原因）
- 📝 修復後 `track update` 強制要求填充 `solution`（解決方案）、`files_changed`（修改檔案）、`test_result`（自測結果）
- 📝 第 4 節新增「欄位填充規範」子節，明確各階段必填欄位
- 📝 第 5 節從「程式碼修改檢查」擴展為「操作前檢查」，新增看板啟動/PyPI 發佈/服務重啟等操作前 recall 踩坑記錄規則
- 📝 `install.py` STEERING_CONTENT 同步全部變更

**工具優化**
- 🔧 `track` 工具 `content` 欄位描述從「排查內容」改為「問題描述（create 時必填，簡述問題現象和背景）」

### v0.2.7

**自動關鍵詞提取**
- 🔑 `remember`/`auto_save` 自動從內容提取關鍵詞補充到 tags，無需 AI 手動傳遞完整標籤
- 🔑 採用 jieba 中文分詞 + 英文正則提取，中英文混合內容均能準確提取高品質關鍵詞
- 🔑 新增 `jieba>=0.42` 依賴

### v0.2.6

**Steering 規則重構**
- 📝 Steering 規則文檔從舊的 3 節結構重寫為 9 節結構（新會話啟動/處理流程/阻塞規則/問題追蹤/代碼檢查/Spec任務管理/記憶品質/工具速查/開發規範）
- 📝 `install.py` STEERING_CONTENT 模板同步更新，新專案安裝即用新規則
- 📝 tags 從固定列表改為動態提取（從內容提取關鍵詞標籤），提升記憶檢索精度

**Bug 修復**
- 🐛 `readme` 工具 `handle_readme()` 缺少 `**_` 導致 MCP 調用報錯 `unexpected keyword argument 'engine'`
- 🐛 Web 看板記憶搜尋分頁修復（有搜尋詞時先全量過濾再分頁，解決搜尋結果不完整問題）

**文檔更新**
- 📖 README 工具數量 7→8、架構圖 `digest`→`task`、工具描述新增 `task`/`readme`
- 📖 `auto_save` 參數從舊的 `decisions[]/modifications[]/pitfalls[]/todos[]` 更新為 `preferences[]/extra_tags[]`
- 📖 Steering 規則範例從 3 節格式更新為 9 節結構摘要
- 📖 同步更新 6 個語言版本（簡體中文/English/Español/Deutsch/Français/日本語）

### v0.2.5

**任務驅動開發模式**
- 🔗 問題追蹤（track）與任務管理（task）透過 `feature_id` 打通成完整鏈路：發現問題 → 建立任務 → 執行任務 → 狀態自動同步 → 聯動歸檔
- 🔄 `task update` 更新任務狀態時自動同步關聯問題狀態（全部完成→completed，有進行中→in_progress）
- 📦 `track archive` 歸檔問題時自動歸檔關聯任務（最後一個活躍問題歸檔時聯動）
- 📦 `task` 工具新增 `archive` action，將功能組所有任務移入 `tasks_archive` 歸檔表
- 📊 問題卡片顯示關聯任務進度（如 `5/10`），任務頁面支援歸檔篩選

**新增工具**
- 🆕 `task` 工具 — 任務管理（batch_create/update/list/delete/archive），支援樹狀子任務，透過 feature_id 關聯 spec 文件
- 🆕 `readme` 工具 — 從 TOOL_DEFINITIONS/pyproject.toml 自動生成 README 內容，支援多語言和差異對比

**工具增強**
- 🔧 `track` 新增 delete action、9 個結構化欄位（description/investigation/root_cause/solution/test_result/notes/files_changed/feature_id/parent_id）、list 按 issue_id 查單條
- 🔧 `recall` 新增 source 參數過濾（manual/auto_save）和 brief 精簡模式（只回傳 content+tags，節省上下文）
- 🔧 `auto_save` 寫入記憶標記 source="auto_save"，區分手動記憶和自動儲存

**知識庫拆表重構**
- 🗃️ project_memories + user_memories 獨立表，消除 scope/filter_dir 混合查詢，查詢效能提升
- 📊 DB Schema v4→v6：issues 新增 9 個結構化欄位 + tasks/tasks_archive 表 + memories.source 欄位

**Web 看板**
- 📊 首頁新增阻塞狀態卡片（紅色阻塞警告/綠色正常運行），點擊跳轉會話狀態頁
- 📊 新增任務管理頁面（功能組摺疊/展開、狀態篩選、搜尋、CRUD）
- 📊 側邊欄導覽順序最佳化（會話狀態、問題追蹤、任務管理提前至核心位置）
- 📊 記憶列表新增 source 過濾和 exclude_tags 排除過濾

**穩定性與規範**
- 🛡️ Server 主迴圈全域例外捕獲，單條訊息錯誤不再導致 server 退出
- 🛡️ Protocol 層空行跳過和 JSON 解析例外容錯
- 🕐 時間戳從 UTC 改為本地時區
- 🧹 清理冗餘程式碼（刪除無呼叫方法、冗餘匯入、備份檔案）
- 📝 Steering 範本新增 Spec 流程與任務管理章節、context transfer 續接規則

### v0.2.4

- 🔇 Stop hook prompt 改為直接指令，消除 Claude Code 重複回覆
- 🛡️ Steering 規則 auto_save 規範增加短路防護，會話結束場景跳過其他規則
- 🐛 `_copy_check_track_script` 冪等性修復（返回變更狀態避免誤報「已同步」）
- 🐛 issue_repo delete 中 `row.get()` 對 `sqlite3.Row` 不相容修復（改用 `row.keys()` 判斷）
- 🐛 Web 看板專案選擇頁面捲動修復（專案多時無法捲動）
- 🐛 Web 看板 CSS 污染修復（strReplace 全域替換導致 6 處樣式異常）
- 🔄 Web 看板所有 confirm() 彈窗替換為自訂 showConfirm 模態框（記憶/問題/標籤/專案刪除）
- 🔄 Web 看板刪除操作增加 API 錯誤回應處理（toast 提示替代 alert）
- 🧹 `.gitignore` 補充 `.devmemory/` 舊版殘留目錄忽略規則
- 🧪 pytest 臨時專案資料庫殘留自動清理（conftest.py session fixture）

### v0.2.3

- 🛡️ PreToolUse Hook：Edit/Write 前強制檢查 track issue，無活躍問題則拒絕執行（Claude Code / Kiro / OpenCode 三端支援）
- 🔌 OpenCode 外掛升級為 `@opencode-ai/plugin` SDK 格式（tool.execute.before hook）
- 🔧 `run install` 自動部署 check_track.sh 檢查腳本並動態填充路徑
- 🐛 issue_repo archive/delete 中 `row.get()` 對 `sqlite3.Row` 不相容修復
- 🐛 session_id 從 DB 讀取最新值再遞增，避免多實例競態
- 🐛 track date 參數格式校驗（YYYY-MM-DD）+ issue_id 類型校驗
- 🐛 Web API 請求解析安全加固（Content-Length 校驗 + 10MB 上限 + JSON 異常捕獲）
- 🐛 Tag 過濾 scope 邏輯修復（`filter_dir is not None` 替代 falsy 判斷）
- 🐛 Export 向量資料 struct.unpack 位元組長度校驗
- 🐛 Schema 版本化遷移（schema_version 表 + v1/v2/v3 增量遷移）
- 🐛 `__init__.py` 版本號同步修復

### v0.2.2

- 🔇 Web 看板 `--quiet` 參數屏蔽請求日誌
- 🔄 Web 看板 `--daemon` 參數背景執行（macOS/Linux）
- 🔧 `run install` MCP 配置生成修復（sys.executable + 完整欄位）
- 📋 問題追蹤增刪改歸檔（Web 看板新增/編輯/歸檔/刪除 + 記憶關聯）
- 👆 所有列表頁點擊行任意位置彈出編輯彈窗（記憶/問題/標籤）
- 🔒 會話延續/上下文轉移時阻塞規則強制生效（跨會話必須重新確認）

### v0.2.1

- ➕ 看板前端新增專案（目錄瀏覽器 + 手動輸入）
- 🏷️ 標籤跨專案污染修復（標籤操作限定當前專案 + 全域記憶範圍）
- 📐 彈窗分頁省略號截斷 + 寬度 80%
- 🔌 OpenCode install 自動生成 auto_save 外掛（session.idle 事件觸發）
- 🔗 Claude Code / Cursor / Windsurf install 自動生成 Hooks 設定（會話結束自動儲存）
- 🎯 看板互動體驗補全（Toast 回饋、空狀態引導、匯出/匯入工具列）
- 🔧 統計概覽卡片點擊跳轉（點擊記憶數/問題數直接彈窗查看）
- 🏷️ 標籤管理頁區分專案/全域標籤來源（📁/🌐 標記）
- 🏷️ 專案卡片標籤數合併全域記憶標籤

### v0.2.0

- 🔐 Web 看板 Token 認證機制
- ⚡ Embedding 向量快取，相同內容不重複計算
- 🔍 recall 支援 query + tags 組合查詢
- 🗑️ forget 支援批次刪除（memory_ids 參數）
- 📤 記憶匯出/匯入（JSON 格式）
- 🔎 Web 看板語義搜尋
- 🗂️ Web 看板專案刪除按鈕
- 📊 Web 看板效能最佳化（消除全表掃描）
- 🧠 digest 智慧壓縮
- 💾 session_id 持久化
- 📏 content 長度限制保護
- 🏷️ version 動態引用（不再寫死）

### v0.1.x

- 初始版本：7 個 MCP 工具、Web 看板、3D 向量視覺化、多語言支援

## License

Apache-2.0

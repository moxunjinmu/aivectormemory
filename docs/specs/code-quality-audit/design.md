# 代码质量审计修复 - 设计文档

## 1. P0：安全漏洞修复

### 1.1 SQL 注入防护（P0-1）

**当前问题**：check_track.sh 中 `$PROJECT_DIR` 和 `$FEATURE_ID` 直接拼接到 SQL 字符串（:24, :37, :40, :43）。

**修复方案**：将 `run_sql` 函数改为接受参数化查询。

- sqlite3 CLI 不支持参数化，改用 python3 fallback 方式统一处理
- `run_sql` 函数签名改为 `run_sql <sql> <param1> <param2> ...`
- 内部用 python3 sqlite3 模块的参数化查询（`?` 占位符）
- 同步修改 `.claude/hooks/check_track.sh` 和 `aivectormemory/hooks/check_track.sh`

**修改文件**：
- `.claude/hooks/check_track.sh`
- `aivectormemory/hooks/check_track.sh`

### 1.2 命令注入防护（P0-2）

**当前问题**：install.py:185-186 OpenCode 插件生成的 JS 代码中 `execSync` 直接拼接 projectDir。

**修复方案**：改用 Node.js 内置 `child_process.execFileSync` + 参数数组，或改用 python3 脚本执行 SQL 查询。

- 将 `sqlite3 "${DB_PATH}" "SELECT ... '${projectDir}' ..."` 改为调用独立脚本
- 脚本接受 DB_PATH 和 projectDir 作为命令行参数，内部使用参数化查询

**修改文件**：
- `aivectormemory/install.py`（OpenCode 插件模板部分）

### 1.3 目录遍历防护（P0-3）

#### 1.3a browse_directory 路径验证

**当前问题**：projects.py:119-134 直接接受用户传入的 path 参数。

**修复方案**：
- `os.path.realpath()` 规范化路径
- 限制只能浏览用户 HOME 目录及其子目录
- 拒绝包含 `..` 的路径

#### 1.3b _serve_static 路径验证

**当前问题**：app.py:77-79 未验证路径是否在 STATIC_DIR 内。

**修复方案**：
- `file_path.resolve()` 后检查 `file_path.resolve().is_relative_to(STATIC_DIR.resolve())`
- 不满足则返回 404

#### 1.3c _resolve_project 参数验证

**当前问题**：api.py:9-12 ?project= 参数无验证。

**修复方案**：
- 检查 project 路径是否为绝对路径
- 检查路径是否实际存在
- 拒绝包含 `..` 的路径

**修改文件**：
- `aivectormemory/web/routes/projects.py`
- `aivectormemory/web/app.py`
- `aivectormemory/web/api.py`

### 1.4 分页参数上限（P0-4）

**当前问题**：limit/offset/top_k 参数无上限验证。

**修复方案**：在 Web API 入口处统一校验：
- `limit`：`max(1, min(limit, 500))`
- `offset`：`max(0, min(offset, 100000))`
- `top_k`：`max(1, min(top_k, 100))`
- int() 转换加 try-except，失败返回默认值

**修改文件**：
- `aivectormemory/web/routes/issues.py`（:13-14）
- `aivectormemory/web/routes/memories.py`（:14-15, :232）
- `aivectormemory/tools/recall.py`（:60）
- `aivectormemory/tools/__init__.py`（recall inputSchema 加 minimum/maximum）

### 1.5 API 类型转换保护（P0-5）

**当前问题**：api.py:49, :69 的 `int()` 无 try-except。

**修复方案**：
```python
try:
    inum = int(path.split("/")[3])
except (ValueError, IndexError):
    return _json_response(handler, {"error": "invalid ID"}, 400)
```

**修改文件**：
- `aivectormemory/web/api.py`（:49, :69）

---

## 2. P1：数据完整性修复

### 2.1 issue 与 memories 表解耦（P1-6）

**当前问题**：issues.py:78-86 在 issue 创建时调用 `mem_repo.insert()` 往 memories 表插记录。

**修复方案**：
- **删除** issues.py 中 `post_issue()` 的 `mem_repo.insert()` 调用（:78-86）
- **删除** issues.py 中 `put_issue()` 的 `UPDATE memories` 语句（:55-56）
- **删除** issues.py 中 `delete_issue()` 的 `mem_repo.delete()` 调用（:111）
- **删除** track.py archive/delete 中关于 memory_id 的清理逻辑
- issues 表的 `memory_id` 字段保留但不再写入（避免 schema 变更影响面过大），新创建的 issue memory_id 为空字符串
- v12 迁移中清理历史数据中 memories 表里 `[问题追踪]` 开头的记录

**修改文件**：
- `aivectormemory/web/routes/issues.py`
- `aivectormemory/tools/track.py`

### 2.2 track.py 传递 tags 参数（P1-7）

**当前问题**：track.py:59 create 调用 `repo.create()` 时未传 tags。

**修复方案**：
```python
result = repo.create(d, title, content, args.get("memory_id", ""),
                     args.get("parent_id", 0), tags=args.get("tags"))
```

**修改文件**：
- `aivectormemory/tools/track.py`（:59）

### 2.3 事务保护（P1-8）

**修复方案**：使用 `connection.py` 现有的 `transaction()` 上下文管理器包装多步操作。

#### 8a. issue_repo.archive()
将 INSERT archive + INSERT vec + DELETE issues 包装在 `with self.conn` 事务中（如果 connection 支持），或在方法内显式 BEGIN/COMMIT。

#### 8b. task_repo.archive_by_feature()
将循环 INSERT + DELETE 包装在事务中。

#### 8c. track.py archive 联动
issue archive 和 task archive_by_feature 在同一事务中执行。由于跨 repo，需要在 track.py 层面控制事务。

#### 8d. base.py _update_existing()
UPDATE + DELETE vec + INSERT vec + sync_tags 在同一事务中。

#### 8e. memory insert find_duplicate 竞态
在 insert 方法中加入 `BEGIN IMMEDIATE` 确保写锁，防止并发插入。

**修改文件**：
- `aivectormemory/db/issue_repo.py`
- `aivectormemory/db/task_repo.py`
- `aivectormemory/db/base.py`
- `aivectormemory/tools/track.py`

### 2.4 Web API 与工具层行为统一（P1-9）

**当前问题**：Web API put_task/delete_task 缺少 tasks.md 同步和 issue 级联更新。

**修复方案**：将 task.py 中的同步逻辑抽取为共享函数，Web API 和工具层共用。

```python
# 新增 aivectormemory/tools/_task_sync.py
def sync_after_task_update(conn, project_dir, feature_id, title, status):
    """tasks.md 同步 + Feature 聚合状态 + issue 级联更新"""
    _sync_tasks_md(project_dir, feature_id, title, status == "completed")
    new_status = TaskRepo(conn, project_dir).get_feature_status(feature_id)
    for issue in IssueRepo(conn, project_dir).list_by_feature_id(feature_id):
        if issue["status"] != new_status:
            IssueRepo(conn, project_dir).update(issue["id"], status=new_status)
```

Web API 的 `put_task` 和 `delete_task` 调用该函数。

**修改文件**：
- `aivectormemory/tools/task.py`（抽取逻辑）
- `aivectormemory/web/routes/tasks.py`（调用共享函数）

### 2.5 issue_number 并发竞态（P1-11）

**当前问题**：issue_repo.py:11-20 `_next_number()` 读-改-写非原子。

**修复方案**：在 `create()` 方法中使用 `BEGIN IMMEDIATE` 事务包装 _next_number + INSERT 操作，确保写锁。

**修改文件**：
- `aivectormemory/db/issue_repo.py`

### 2.6 tags.py json.loads 异常处理（P1-12）

**当前问题**：tags.py:41, 68, 94 三处 `json.loads()` 无 try-except。

**修复方案**：统一包装为安全解析函数：
```python
def _safe_parse_tags(raw):
    if isinstance(raw, list):
        return raw
    try:
        return json.loads(raw) if isinstance(raw, str) else []
    except (json.JSONDecodeError, TypeError):
        return []
```

**修改文件**：
- `aivectormemory/web/routes/tags.py`

---

## 3. P2：向量引擎可靠性

### 3.1 encode() 失败降级（P2-13）

**当前问题**：engine.py 的 encode() 失败直接 raise，7 处调用无保护。

**修复方案**：在 `EmbeddingEngine.encode()` 内部捕获异常，返回零向量。

```python
def encode(self, text: str) -> list[float]:
    if not text or not text.strip():
        return [0.0] * MODEL_DIMENSION
    try:
        if not self.ready:
            self.load()
        return list(self._encode_cached(text))
    except Exception as e:
        log.warning("Embedding encode failed: %s, returning zero vector", e)
        return [0.0] * MODEL_DIMENSION
```

这样所有 7 处调用方无需修改。零向量不会匹配任何查询（余弦相似度为 0），安全降级。

**修改文件**：
- `aivectormemory/embedding/engine.py`

### 3.2 空文本验证（P2-14）

已在 3.1 方案中覆盖（encode 方法开头检查空文本）。

### 3.3 向量维度一致性（P2-15）

**当前问题**：schema.py 硬编码 `FLOAT[384]`，config.py 用环境变量。

**修复方案**：
- schema.py 中的向量表 DDL 改为动态生成：`f"embedding FLOAT[{MODEL_DIMENSION}]"`
- 在 `encode()` 返回时验证维度：`assert len(result) == MODEL_DIMENSION`

**修改文件**：
- `aivectormemory/db/schema.py`（:22, :136, :142）
- `aivectormemory/embedding/engine.py`

### 3.4 网络下载超时（P2-16）

**修复方案**：在 `_download_model()` 中设置环境变量 `HF_HUB_TIMEOUT=30`。

**修改文件**：
- `aivectormemory/embedding/engine.py`

### 3.5 SQLite busy_timeout（P2-17）

**修复方案**：在 connection.py WAL 配置后添加：
```python
conn.execute("PRAGMA busy_timeout=5000")
```

**修改文件**：
- `aivectormemory/db/connection.py`（:24 之后）

---

## 4. P3：MCP 工具层修复

### 4.1 相似度计算公式统一（P3-18）

**当前问题**：4 种不同的相似度公式。

**修复方案**：统一使用 `1 - (distance² / 2)` 公式（sqlite-vec 返回的是 L2 距离，此公式将其转换为近似余弦相似度）。

- `_add_similarity()`：去掉 `has_tags` 条件分支，统一用 `1 - (d²/2)`
- `search_by_vector_with_tags()`（base.py:135）：返回的 distance 改为 L2 距离而非 `1-cos_sim`
- 纯标签搜索无 distance 时：设 similarity=1.0（保持不变，标签精确匹配）
- 混合搜索关键词加成：`0.5 + 0.3*kw_score` 改为 `0.3 + 0.2*kw_score`（降低基础分，避免关键词结果排名高于高相似度向量结果）

**修改文件**：
- `aivectormemory/tools/recall.py`
- `aivectormemory/db/base.py`

### 4.2 keywords.py 停用词扩展（P3-19）

**修复方案**：在 `_EN_STOP` 集合中新增系统管理相关词汇：

```python
_EN_STOP |= {"modification", "todo", "decision", "issue", "task", "track",
             "feature", "problem", "bug", "question", "tracking", "description",
             "update", "change", "pitfall", "information"}
```

中文 `_CN_STOP` 新增：
```python
_CN_STOP |= {"修改", "任务", "问题", "追踪", "记录", "描述", "功能", "更新"}
```

**修改文件**：
- `aivectormemory/tools/keywords.py`

### 4.3 行为纠正机制重构（P3-20）

#### 20a. 步骤 I 去掉"有踩坑价值 → remember"

从 CLAUDE.md 和 7 个 i18n 文件的步骤 I 中删除该条件行。

#### 20b. 步骤 B "用户纠正错误行为 → remember" 改为 "→ 更新 steering 文件"

将步骤 B 中的 `remember` 改为"更新项目 steering 文件的自定义规则区域"。

#### 20c. remember 工具 description 调整

从 STEERING_CONTENT 的记忆质量要求（第 7 节）中移除"行为纠正类"。tags 分类标签保留"踩坑/项目知识"，移除"行为纠正"。

#### 20d. steering 文件支持增量追加

**当前实现**：install.py 的 `_write_steering()` 支持两种模式：
- **file 模式**（Kiro/Cursor/Windsurf/Trae）：全量覆盖
- **append 模式**（Claude Code/VSCode/OpenCode）：使用 `<!-- aivectormemory-steering -->` 标记块，保留块外内容

**修复方案**：
- file 模式也改为标记块机制：在文件中使用 `<!-- aivectormemory-steering -->` 和 `<!-- /aivectormemory-steering -->` 包裹模板内容
- AI 自我升级的规则写入 `<!-- custom-rules -->` 标记块（位于模板块之外）
- install 时只覆盖 `<!-- aivectormemory-steering -->` 块内容，保留 `<!-- custom-rules -->` 块

#### 20e. 清理行为纠正类记忆

在 v12 迁移中删除 tags 含 `"行为纠正"` 的记忆。

**修改文件**：
- `CLAUDE.md`
- `aivectormemory/i18n/rules/*.py`（7 个文件）
- `aivectormemory/install.py`（_write_steering 函数）

### 4.4 readme.py 返回值类型修复（P3-21）

**当前问题**：readme.py 返回 dict，server.py `str(result)` 产生非标准 JSON。

**修复方案**：readme.py 的 `handle_readme()` 返回时用 `to_json()` 包装：
```python
return to_json({"content": content, "lang": lang, ...})
```

**修改文件**：
- `aivectormemory/tools/readme.py`

---

## 5. P4：install/i18n 修复

### 5.1 Hook 函数 lang 参数补充（P4-22/23）

**修复方案**：
- `_write_cursor_hooks(hooks_dir)` 签名加 `lang: str | None = None`
- `_write_windsurf_hooks(hooks_dir)` 签名加 `lang: str | None = None`
- `run_install()` 中调用 `_write_claude_code_hooks(hooks_dir, lang=selected_lang)`
- 同样补充 cursor/windsurf 调用的 `lang=selected_lang`

**修改文件**：
- `aivectormemory/install.py`（:350, :392, :807, :809, :811）

### 5.2 语言文件自测章节补充（P4-24）

**当前状态**：经反向验证确认，所有 7 个语言文件均已包含自测章节（之前的审查误报）。无需修改。

---

## 6. P5：桌面端 Go 修复

### 6.1 QueryRow.Scan 错误处理（P5-25）

**修复方案**：所有 16 处 `QueryRow().Scan()` 改为检查错误：

```go
// 前
d.QueryRow("SELECT COUNT(*) FROM memories").Scan(&r.MemoriesTotal)

// 后
if err := d.QueryRow("SELECT COUNT(*) FROM memories").Scan(&r.MemoriesTotal); err != nil {
    log.Printf("scan error: %v", err)
}
```

对于计数类查询（COUNT(*)），错误时保持零值即可，记录日志。

**修改文件**：
- `desktop/internal/db/health.go`（8 处）
- `desktop/internal/db/issues.go`（7 处）
- `desktop/internal/db/memories.go`（3 处）
- `desktop/internal/db/projects.go`（1 处）

### 6.2 事务锁死锁修复（P5-26）

**当前问题**：`Begin()` 先 Lock() 后 conn.Begin()，失败时 mutex 被锁未释放。

**修复方案**：调换顺序，先 Begin 后 Lock：
```go
func (d *DB) Begin() (*sql.Tx, error) {
    tx, err := d.conn.Begin()
    if err != nil {
        return nil, err  // 未持有锁，安全返回
    }
    d.mu.Lock()
    return tx, nil
}
```

**修改文件**：
- `desktop/internal/db/connection.go`（:224-227）

### 6.3 goroutine 数据竞争修复（P5-27）

#### 27a. repair.go goroutine

**修复方案**：
- 添加 `context.Done()` 检查，在应用关闭时中断
- 使用 channel 通知完成状态

#### 27b. engine.go 临时文件竞争

**修复方案**：
- 临时文件名加 UUID 后缀：`avm_embed_input_{uuid}.json`
- 或为 Engine 添加 `sync.Mutex`，Encode() 方法加锁

#### 27c. launcher.go goroutine

**修复方案**：
- 为 `l.cmd` 添加 `sync.Mutex` 保护
- `go cmd.Wait()` 改为用 channel 接收结果

**修改文件**：
- `desktop/internal/embedding/repair.go`
- `desktop/internal/embedding/engine.go`
- `desktop/internal/webserver/launcher.go`

### 6.4 tx.Exec 错误检查（P5-28）

**修复方案**：ImportMemories 中所有 `tx.Exec()` 改为检查错误：
```go
if _, err := tx.Exec(...); err != nil {
    tx.Rollback()
    return imported, skipped, err
}
```

**修改文件**：
- `desktop/internal/db/memories.go`（:358-368）

---

## 7. P6：历史数据清理

### 7.1 v12 迁移脚本（P6-29）

**文件**：`aivectormemory/db/migrations/v12.py`

```python
def upgrade(conn, **_):
    # 29a: 删除 [问题追踪] 开头的记忆
    conn.execute("""
        DELETE FROM memory_tags WHERE memory_id IN (
            SELECT id FROM memories WHERE content LIKE '[问题追踪]%'
        )""")
    conn.execute("DELETE FROM vec_memories WHERE id IN (SELECT id FROM memories WHERE content LIKE '[问题追踪]%')")
    conn.execute("DELETE FROM memories WHERE content LIKE '[问题追踪]%'")

    # 29b: 删除 modification/todo/decision 旧碎片
    conn.execute("""
        DELETE FROM memory_tags WHERE memory_id IN (
            SELECT id FROM memories
            WHERE (tags LIKE '%"modification"%' OR tags LIKE '%"todo"%' OR tags LIKE '%"decision"%')
            AND tags NOT LIKE '%"preference"%'
            AND tags NOT LIKE '%"项目知识"%'
        )""")
    conn.execute("""
        DELETE FROM vec_memories WHERE id IN (
            SELECT id FROM memories
            WHERE (tags LIKE '%"modification"%' OR tags LIKE '%"todo"%' OR tags LIKE '%"decision"%')
            AND tags NOT LIKE '%"preference"%'
            AND tags NOT LIKE '%"项目知识"%'
        )""")
    conn.execute("""
        DELETE FROM memories
        WHERE (tags LIKE '%"modification"%' OR tags LIKE '%"todo"%' OR tags LIKE '%"decision"%')
        AND tags NOT LIKE '%"preference"%'
        AND tags NOT LIKE '%"项目知识"%'
    """)

    # 29c: 清理孤立标签
    conn.execute("DELETE FROM memory_tags WHERE memory_id NOT IN (SELECT id FROM memories)")
    conn.execute("DELETE FROM user_memory_tags WHERE memory_id NOT IN (SELECT id FROM user_memories)")

    # 29e: 删除行为纠正类记忆
    conn.execute("""
        DELETE FROM memory_tags WHERE memory_id IN (
            SELECT id FROM memories WHERE tags LIKE '%"行为纠正"%'
        )""")
    conn.execute("DELETE FROM vec_memories WHERE id IN (SELECT id FROM memories WHERE tags LIKE '%"行为纠正"%')")
    conn.execute("DELETE FROM memories WHERE tags LIKE '%"行为纠正"%'")

    conn.commit()
```

**注册**：
- `migrations/__init__.py` 添加 `from .v12 import upgrade as v12` 和 `12: v12`
- `schema.py` 更新 `CURRENT_SCHEMA_VERSION = 12`

### 7.2 批量 forget（P6-30）

手动执行，使用 `forget` 工具删除已确认的 ~16 条垃圾记忆（测试数据、过期项目知识）。在 v12 迁移完成后执行。

---

## 8. 修改文件总表

| 文件 | 涉及需求 |
|------|---------|
| `.claude/hooks/check_track.sh` | P0-1 |
| `aivectormemory/hooks/check_track.sh` | P0-1 |
| `aivectormemory/install.py` | P0-2, P4-22/23 |
| `aivectormemory/web/routes/projects.py` | P0-3a |
| `aivectormemory/web/app.py` | P0-3b |
| `aivectormemory/web/api.py` | P0-3c, P0-5 |
| `aivectormemory/web/routes/issues.py` | P0-4a, P1-6 |
| `aivectormemory/web/routes/memories.py` | P0-4a/4b |
| `aivectormemory/web/routes/tags.py` | P1-12 |
| `aivectormemory/web/routes/tasks.py` | P1-9 |
| `aivectormemory/tools/track.py` | P1-6, P1-7, P1-8c |
| `aivectormemory/tools/task.py` | P1-9 |
| `aivectormemory/tools/recall.py` | P0-4b, P3-18 |
| `aivectormemory/tools/keywords.py` | P3-19 |
| `aivectormemory/tools/readme.py` | P3-21 |
| `aivectormemory/tools/__init__.py` | P0-4b, P3-20c |
| `aivectormemory/db/issue_repo.py` | P1-8a, P1-11 |
| `aivectormemory/db/task_repo.py` | P1-8b |
| `aivectormemory/db/base.py` | P1-8d/8e, P3-18 |
| `aivectormemory/db/connection.py` | P2-17 |
| `aivectormemory/db/schema.py` | P2-15, P6-29 |
| `aivectormemory/db/migrations/v12.py` | P6-29（新建） |
| `aivectormemory/db/migrations/__init__.py` | P6-29 |
| `aivectormemory/embedding/engine.py` | P2-13/14/15/16 |
| `aivectormemory/server.py` | （无需修改，encode 降级在 engine 内处理） |
| `aivectormemory/i18n/rules/*.py` | P3-20a/20b/20c（7 个文件） |
| `aivectormemory/i18n/responses.py` | （无需修改） |
| `CLAUDE.md` | P3-20a/20b |
| `desktop/internal/db/connection.go` | P5-26 |
| `desktop/internal/db/health.go` | P5-25 |
| `desktop/internal/db/issues.go` | P5-25 |
| `desktop/internal/db/memories.go` | P5-25, P5-28 |
| `desktop/internal/db/projects.go` | P5-25 |
| `desktop/internal/db/tasks.go` | （无需修改，Scan 已有错误检查） |
| `desktop/internal/embedding/repair.go` | P5-27a |
| `desktop/internal/embedding/engine.go` | P5-27b |
| `desktop/internal/webserver/launcher.go` | P5-27c |

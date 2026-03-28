# 代码质量审计修复 - 任务文档

## 第1组：P0 安全漏洞修复

- [x] 1.1 check_track.sh SQL 注入修复 — `run_sql` 改为 python3 参数化查询，修改 `.claude/hooks/check_track.sh` 4 个注入点（:24,:37,:40,:43）
- [x] 1.2 check_track.sh 副本同步 — 同步修改 `aivectormemory/hooks/check_track.sh`（与 1.1 保持一致）
- [x] 1.3 OpenCode 插件命令注入修复 — `install.py` OpenCode 模板中 `execSync` 改为参数化查询（:185-186）
- [x] 1.4 browse_directory 目录遍历修复 — `projects.py` 添加 `os.path.realpath()` + HOME 目录限制（:119-134）
- [x] 1.5 _serve_static 路径遍历修复 — `app.py` 添加 `resolve().is_relative_to(STATIC_DIR)` 检查（:77-79）
- [x] 1.6 _resolve_project 参数验证 — `api.py` 检查绝对路径 + 存在性 + 无 `..`（:9-12）
- [x] 1.7 分页参数上限：issues.py — limit `max(1,min(v,500))`、offset `max(0,min(v,100000))`（:13-14）
- [x] 1.8 分页参数上限：memories.py — 同上 limit/offset（:14-15）+ top_k `max(1,min(v,100))`（:232）
- [x] 1.9 分页参数上限：recall.py + inputSchema — top_k 加范围验证（:60）+ `__init__.py` 加 minimum/maximum
- [x] 1.10 API 类型转换保护 — `api.py` issue ID（:49）和 task ID（:69）int() 加 try-except 返回 400

## 第2组：P1 数据完整性修复

- [x] 2.1 issue-memory 解耦：post_issue — 删除 `issues.py` 中 `mem_repo.insert()` 调用（:78-86）
- [x] 2.2 issue-memory 解耦：put_issue — 删除 `issues.py` 中 `UPDATE memories` 语句（:49-57）
- [x] 2.3 issue-memory 解耦：delete_issue — 删除 `issues.py` 中 `mem_repo.delete()` 调用（:111）
- [x] 2.4 issue-memory 解耦：track.py — 删除 archive/delete 中 memory_id 清理逻辑
- [x] 2.5 track.py 传递 tags — create 调用 `repo.create()` 时补充 `tags=args.get("tags")`（:59）
- [x] 2.6 事务保护：issue_repo.archive() — INSERT archive + DELETE 包装事务（issue_repo.py:72-101）
- [x] 2.7 事务保护：task_repo.archive_by_feature() — 循环 INSERT + DELETE 包装事务（task_repo.py:148-171）
- [x] 2.8 事务保护：track.py archive 联动 — issue archive + task archive_by_feature 同一事务（track.py:74-89）
- [x] 2.9 事务保护：base.py _update_existing() — UPDATE + DELETE vec + INSERT vec + sync_tags 包装事务（base.py:59-69）
- [x] 2.10 事务保护：base.py insert() 竞态 — find_duplicate + insert 使用 BEGIN IMMEDIATE（base.py:38-52）
- [x] 2.11 Web API 与工具层统一：抽取共享函数 — 从 task.py 抽取 `sync_after_task_update()` 到 `_task_sync.py`
- [x] 2.12 Web API 与工具层统一：put_task 调用共享函数 — tasks.py put_task 调用 sync_after_task_update（:26-34）
- [x] 2.13 Web API 与工具层统一：delete_task 调用共享函数 — tasks.py delete_task 调用 sync_after_task_update（:37-40）
- [x] 2.14 issue_number 并发竞态修复 — issue_repo.py create() 中 _next_number + INSERT 包装 BEGIN IMMEDIATE（:11-20）
- [x] 2.15 tags.py json.loads 异常处理 — 添加 `_safe_parse_tags()` 替换 3 处 json.loads（tags.py:41,68,94）
- [x] 2.16 issues 表 memory_id 字段处理 — design.md 决定保留字段但不再写入，v12 迁移中清理历史 memory_id 关联数据

## 第3组：P2 向量引擎可靠性

- [x] 3.1 encode() 失败降级 + 空文本验证 — engine.py encode() 内部 try-except 返回零向量 + 空文本检查
- [x] 3.2 向量维度动态化 — schema.py 3 处 `FLOAT[384]` 改为 `f"FLOAT[{MODEL_DIMENSION}]"`（:22,:136,:142）
- [x] 3.3 网络下载超时 — engine.py `_download_model()` 设置 `HF_HUB_TIMEOUT=30`
- [x] 3.4 SQLite busy_timeout — connection.py WAL 后添加 `PRAGMA busy_timeout=5000`（:24 之后）

## 第4组：P3 MCP 工具层修复

- [x] 4.1 相似度公式统一：recall.py — `_add_similarity()` 去掉 has_tags 分支，统一 `1-(d²/2)`
- [x] 4.2 相似度公式统一：base.py — `search_by_vector_with_tags()` 返回 L2 距离而非 `1-cos_sim`
- [x] 4.3 相似度公式统一：混合搜索加成 — recall.py `_merge_hybrid()` 改为 `0.3+0.2*kw_score`（:44）
- [x] 4.4 keywords.py 停用词扩展 — _EN_STOP 新增 16 个词 + _CN_STOP 新增 8 个词
- [x] 4.5 规则修改：步骤 I — CLAUDE.md + 7 个 i18n 文件删除"有踩坑价值 → remember"（:63/:70）
- [x] 4.6 规则修改：步骤 B — CLAUDE.md + 7 个 i18n 文件将"remember"改为"更新 steering 文件"
- [x] 4.7 规则修改：记忆质量要求 — CLAUDE.md + 7 个 i18n 文件移除"行为纠正类"分类
- [x] 4.8 steering 增量追加：install.py — _write_steering() file 模式改为标记块，保留 custom-rules 块
- [x] 4.9 readme.py 返回值修复 — handle_readme() 所有返回 dict 处改为 `to_json()` 包装

## 第5组：P4 install/i18n 修复

- [x] 5.1 _write_cursor_hooks 补充 lang 参数 — install.py 函数签名加 `lang: str | None = None`（:350）
- [x] 5.2 _write_windsurf_hooks 补充 lang 参数 — install.py 函数签名加 `lang: str | None = None`（:392）
- [x] 5.3 run_install() 调用补充 lang — Claude Code(:807)、Cursor(:809)、Windsurf(:811) 传 `lang=selected_lang`

## 第6组：P5 桌面端 Go 修复

- [x] 6.1 Scan 错误处理：health.go — 8 处 QueryRow.Scan 加错误检查
- [x] 6.2 Scan 错误处理：issues.go — 7 处 QueryRow.Scan 加错误检查
- [x] 6.3 Scan 错误处理：memories.go — 3 处 QueryRow.Scan 加错误检查
- [x] 6.4 Scan 错误处理：projects.go — 1 处 QueryRow.Scan 加错误检查
- [x] 6.5 事务锁死锁修复 — connection.go Begin() 调换顺序：先 conn.Begin() 后 mu.Lock()（:224-227）
- [x] 6.6 repair.go goroutine 修复 — 添加 context.Done() 检查 + channel 完成通知
- [x] 6.7 engine.go 临时文件竞争 — Encode() 加 sync.Mutex 或临时文件名加 UUID
- [x] 6.8 launcher.go goroutine 修复 — l.cmd 加 sync.Mutex + cmd.Wait() 用 channel 接收
- [x] 6.9 ImportMemories tx.Exec 错误检查 — memories.go 4 处 tx.Exec 加错误检查和 Rollback（:358-368）

## 第7组：P6 历史数据清理

- [x] 7.1 创建 v12 迁移脚本 — `migrations/v12.py` 清理 [问题追踪] 记忆 + modification/todo/decision 碎片 + 行为纠正类记忆（P3-20e） + 孤立标签
- [x] 7.2 注册 v12 迁移 — `migrations/__init__.py` 导入 v12 + `schema.py` CURRENT_SCHEMA_VERSION=12
- [x] 7.3 批量 forget 垃圾记忆 — 删除 ~16 条已确认的测试数据和过期记忆

## 第8组：验证

- [x] 8.1 pytest 全量测试 — 运行 `pytest` 确认所有测试通过
- [x] 8.2 桌面端编译 — 运行 `~/go/bin/wails build` 确认编译通过
- [x] 8.3 SQL 注入验证 — 用含特殊字符的 PROJECT_DIR 测试 check_track.sh
- [x] 8.4 recall 查询验证 — 确认无垃圾数据（[问题追踪]、modification、行为纠正）

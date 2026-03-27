# 代码质量审计修复 - 需求文档

## 背景

全面代码审查发现 189 个问题（52 高 / 81 中 / 56 低），涉及 10 个模块。经 20 个子代理反向验证后补充遗漏。本次修复聚焦高危问题和直接影响用户体验的中危问题。

## 功能范围

### P0：安全漏洞（必须修复）

1. **SQL 注入防护** — check_track.sh（`.claude/hooks/` 和 `aivectormemory/hooks/` 两份）中 `$PROJECT_DIR` 和 `$FEATURE_ID` 未转义直接拼接 SQL，共 4 个注入点（:24, :37, :40, :43）
2. **命令注入防护** — OpenCode 插件 `execSync()` 中 projectDir 直接拼接命令字符串（install.py:185-186）
3. **目录遍历防护**：
   - 3a. `browse_directory()` 未验证 path 参数，可遍历系统任意目录（projects.py:119-134）
   - 3b. `_serve_static()` 未验证路径是否在 STATIC_DIR 内（app.py:77-79）
   - 3c. `_resolve_project()` ?project= 参数无验证，可访问任意项目数据（api.py:9-12）
4. **分页参数上限**：
   - 4a. Web API limit/offset 无上限（issues.py:13-14, memories.py:14-15）
   - 4b. top_k 参数无范围验证（recall.py:60, memories.py:232）
5. **API 类型转换保护** — issue/task ID 转换无 try-except（api.py:49, :69），非数字路径导致 500 错误

### P1：数据完整性（必须修复）

6. **issue 与 memories 表彻底解耦**：
   - 6a. POST /api/issues 不再调用 mem_repo.insert() 创建 memory（issues.py:78-86）
   - 6b. PUT /api/issues 不再直接 UPDATE memories 表（issues.py:49-57）
   - 6c. archive/delete 操作清理关联 memory 记录（issues.py:97-101, track.py:74-97）
   - 6d. 移除 issues 表 memory_id 字段（schema 变更）
7. **track.py 创建时传递 tags 参数** — 当前完全忽略 tags（track.py:59）
8. **事务保护**：
   - 8a. issue_repo.archive() — INSERT archive + DELETE issues 非原子（issue_repo.py:72-101）
   - 8b. task_repo.archive_by_feature() — 循环 INSERT + DELETE 非原子（task_repo.py:148-171）
   - 8c. track.py archive → task archive 联动无事务（track.py:74-89）
   - 8d. base.py _update_existing() — DELETE vec + INSERT vec + sync_tags 无事务（base.py:59-69）
   - 8e. memory insert 的 find_duplicate 竞态（base.py:38-52）
9. **Web API 与工具层行为统一**：
   - 9a. put_task 缺少 tasks.md 同步（tasks.py:26-34 vs task.py:78）
   - 9b. put_task 缺少 Feature 聚合状态计算和 issue 级联更新（task.py:80-85）
   - 9c. delete_task 也缺少上述两个逻辑（tasks.py:37-40）
10. **并发去重竞态条件** — 两个并发请求可创建重复记忆（base.py:41-52）
11. **issue_number 并发竞态** — _next_number() 读-改-写非原子（issue_repo.py:11-20）
12. **tags.py json.loads() 无异常处理** — 3 处解析可能抛异常导致 500（tags.py:41, 68, 94）

### P2：向量引擎可靠性（必须修复）

13. **encode() 失败降级处理** — 引擎加载失败直接 raise，整个工具链中断。所有 7 处调用均无 try-except：
    - remember.py:28, recall.py:83/102/126, auto_save.py:22, web/routes/issues.py:83, web/routes/memories.py:240
    - 改为：记录日志 + 返回空向量（384 维零向量）
14. **空文本验证** — encode 空字符串时可能产生 NaN 向量（engine.py:88-110）
15. **向量维度一致性检查** — schema 硬编码 384 维（schema.py:22,136,142）与 MODEL_DIMENSION 环境变量不同步
16. **网络下载超时** — hf_hub_download/snapshot_download 无超时（engine.py:51-58），设置 HF_HUB_TIMEOUT=30
17. **SQLite busy_timeout 未配置** — 写入冲突立即失败（connection.py:24），配置 `PRAGMA busy_timeout=5000`

### P3：MCP 工具层修复（必须修复）

18. **相似度计算公式统一** — 当前有 4 种不同公式：
    - `1-(d²/2)`：base.py:79, recall.py:22(无标签), issue_repo.py:215, memories.py:264
    - `1-d`：recall.py:22(有标签)
    - 固定 `1.0`：recall.py:81,100（纯标签搜索）
    - `0.5+0.3*kw_score`：recall.py:44（混合搜索关键词加成）
    - 统一为一种公式
19. **keywords.py 停用词扩展** — 当前 _EN_STOP 缺少系统管理词汇，需新增：modification, todo, decision, issue, task, track, feature, problem, bug, question, tracking, description；中文新增：修改, 任务, 问题, 追踪, 记录, 描述
20. **行为纠正机制重构：从"存记忆"改为"自我升级规则"**：
    - 20a. 步骤 I 去掉"有踩坑价值 → remember"条件（CLAUDE.md:63 + 7 个 i18n 文件:70）
    - 20b. 步骤 B 的"用户纠正错误行为 → remember"改为"→ 更新 steering 文件"
    - 20c. remember 工具 description 移除对"行为纠正"的引导，只保留"项目知识"和"踩坑经验"
    - 20d. steering 文件支持增量追加：install.py 生成基础规则（模板区域），AI 自我升级的规则写入独立区域（如 `<!-- custom-rules -->` 标记块），install 时不覆盖该区域
    - 20e. 清理记忆系统中现有的"行为纠正"类记忆（已被规则覆盖的）
21. **readme.py 返回值类型修复** — 唯一返回 dict 而非 str 的工具，server.py str() 转换产生非标准 JSON（server.py:96, readme.py）

### P4：install/i18n 修复（应该修复）

22. **Cursor/Windsurf hook 函数补充 lang 参数** — 函数签名缺 lang（install.py:350, :392），调用时也未传递（:809, :811）
23. **Claude Code hook 调用补充 lang 参数** — _write_claude_code_hooks 调用时未传 lang=selected_lang（install.py:807）
24. **5 个语言文件补充自测章节** — de/es/fr/ja/zh_TW 的 DEV_WORKFLOW_PROMPT 缺少自测规则

### P5：桌面端 Go 修复（应该修复）

25. **QueryRow.Scan 错误处理** — 16 处 Scan 无错误检查（health.go:8处, issues.go:7处, memories.go:3处, projects.go:1处）
26. **事务锁死锁修复** — Begin() 内先 Lock() 后 conn.Begin()，失败时 mutex 被锁未释放。3 个调用点：tasks.go:88, projects.go:168, memories.go:297
27. **goroutine 数据竞争**：
    - 27a. repair.go:73 后台 goroutine 无生命周期管理，无 context 检查（:115,125,130）
    - 27b. engine.go:31-32 临时文件并发竞争（同名文件互相覆盖）
    - 27c. launcher.go:38,41 两个 goroutine 无同步机制
28. **事务内 tx.Exec 错误检查** — ImportMemories 中多处忽略错误（memories.go:358-368）

### P6：历史数据清理（应该修复）

29. **新迁移脚本 v12 清理垃圾记忆**：
    - 29a. 删除 content 以 `[问题追踪]` 开头的记忆 + 对应 vec_memories 和 memory_tags
    - 29b. 删除 tags 含 modification/todo/decision 且非 preference 的旧碎片
    - 29c. 清理 memory_tags 表中的孤立标签
    - 29d. SCHEMA_VERSION 11→12
30. **批量 forget 删除已确认的垃圾记忆** — ~16 条测试数据和过期记忆

### 本次不修复（低优先级，后续迭代）

- Web API CORS/CSRF 保护（本地工具，非公网服务）
- 请求速率限制（同上）
- 密码复杂度（本地开发工具）
- Token URL 传递改 Header（需前端联动）
- 冒泡排序改标准库 sort（性能优化类）
- tags JSON 冗余存储（需要 schema 大改）
- 子任务深度限制（当前只支持一级，够用）
- 任务恢复功能（低频需求）
- import_memories() 数据验证（低频操作）
- 全局事务标志线程安全（MCP Server 单线程模型）
- Token 滑动过期机制（本地工具）

## 验收标准

1. 所有 P0-P3 问题修复完成，相关测试通过
2. P4-P5 修复完成，桌面端编译通过
3. P6 数据清理完成，recall 查询无垃圾数据
4. 现有测试全部通过（`pytest`）
5. 桌面端编译通过（`wails build`）
6. check_track.sh SQL 注入验证通过（含特殊字符的 PROJECT_DIR 测试）
7. 相似度搜索排序一致性验证（不同查询路径返回相同排序）

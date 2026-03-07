# 语言设置统一 - 任务清单

## 第1组：全局语言配置基础设施

- [ ] 1.1 创建 `aivectormemory/settings.py`：`get_language()`、`set_language(lang)`、`SETTINGS_PATH`、`DEFAULT_LANG`
- [ ] 1.2 编写 `settings.py` 单元测试

## 第2组：i18n 翻译模块

- [ ] 2.1 创建 `aivectormemory/i18n/__init__.py`：`get_steering(lang)`、`get_workflow_prompt(lang)`、`LANG_MODULE_MAP`
- [ ] 2.2 创建 `aivectormemory/i18n/rules/__init__.py`
- [ ] 2.3 创建 `aivectormemory/i18n/rules/zh_CN.py`：从 install.py 迁移 `STEERING_CONTENT` 和 `DEV_WORKFLOW_PROMPT`（基准语言，逐行复制禁止重写）
- [ ] 2.4 创建 `aivectormemory/i18n/rules/en.py`：英文翻译
- [ ] 2.5 创建 `aivectormemory/i18n/rules/zh_TW.py`：繁体中文翻译
- [ ] 2.6 创建 `aivectormemory/i18n/rules/ja.py`：日文翻译
- [ ] 2.7 创建 `aivectormemory/i18n/rules/es.py`：西班牙文翻译
- [ ] 2.8 创建 `aivectormemory/i18n/rules/de.py`：德文翻译
- [ ] 2.9 创建 `aivectormemory/i18n/rules/fr.py`：法文翻译
- [ ] 2.10 编写 i18n 模块单元测试（验证所有语言文件可加载、常量存在）

## 第3组：install.py 改造

- [ ] 3.1 删除 install.py 中的 `STEERING_CONTENT` 和 `DEV_WORKFLOW_PROMPT` 硬编码常量
- [ ] 3.2 install.py 所有引用改为 `from aivectormemory.i18n import get_steering, get_workflow_prompt`
- [ ] 3.3 `_write_steering()` 增加 `lang` 参数，从 i18n 模块加载内容
- [ ] 3.4 `_write_inject_workflow_script()` 改造：生成含所有语言 case 分支的 bash 脚本
- [ ] 3.5 `_build_opencode_plugin_content()` 改造：接收 `lang` 参数，加载对应语言文本
- [ ] 3.6 Kiro hook `DEV_WORKFLOW_PROMPT` 引用改为 i18n 加载
- [ ] 3.7 install 交互流程增加语言选择步骤（IDE 选择之后，MCP 配置之前）
- [ ] 3.8 验证 `aivectormemory install` 全流程（选择语言 → 生成对应语言文件）

## 第4组：regenerate 命令

- [ ] 4.1 新增 CLI 子命令 `aivectormemory regenerate --lang <lang>`
- [ ] 4.2 实现项目遍历逻辑：从数据库读取已注册项目，检测每个项目安装的 IDE 配置
- [ ] 4.3 对每个项目重新执行 `_write_steering()` + `_write_hooks()` 等
- [ ] 4.4 验证 regenerate 命令（切换语言后检查生成的文件内容）

## 第5组：桌面端联动

- [ ] 5.1 Go 后端新增 `SetLanguage(lang string) error` 方法（写 settings.json + 调用 regenerate）
- [ ] 5.2 桌面端 Vue 前端语言切换时调用 `SetLanguage`（在现有 UI 语言切换基础上增加）
- [ ] 5.3 桌面端启动时读取 settings.json 的 language 作为默认 UI 语言
- [x] 5.4 验证桌面端切换语言 → 已安装项目文件更新

## 第6组：看板联动

- [ ] 6.1 Web 看板新增 API `POST /api/settings/language`（调用 set_language + regenerate）
- [ ] 6.2 Web 看板新增 API `GET /api/settings/language`（读取当前语言）
- [ ] 6.3 看板设置页面增加语言选择器（读取 + 修改）
- [x] 6.4 验证看板切换语言 → 已安装项目文件更新

## 第7组：集成测试与验收

- [ ] 7.1 端到端测试：install → 选择 English → 验证所有生成文件为英文
- [ ] 7.2 端到端测试：regenerate → 切换为日文 → 验证文件更新
- [x] 7.3 向后兼容测试：settings.json 不存在时默认 zh-CN
- [ ] 7.4 向后兼容测试：旧版本安装的项目执行 regenerate 后正常更新

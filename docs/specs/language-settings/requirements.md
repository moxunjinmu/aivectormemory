# 语言设置统一 - 需求文档

## 背景

当前系统的规则内容（STEERING_CONTENT、DEV_WORKFLOW_PROMPT、inject-workflow-rules.sh）硬编码为中文。用户在桌面端选择其他语言后，以下内容不会跟随切换：

1. **动态注入的 hook 内容**（inject-workflow-rules.sh → Claude Code、Cursor、Windsurf 的 hook 输出）
2. **静态规则文件**（CLAUDE.md、AGENTS.md、.kiro/steering/aivectormemory.md、.cursor/rules/ 等）
3. **install.py 模板**（STEERING_CONTENT、DEV_WORKFLOW_PROMPT 硬编码中文）

## 目标

用户在桌面端选择语言后，所有已安装项目的 AI 规则和 hook 输出统一切换到对应语言。

## 支持语言

zh-CN（简体中文）、zh-TW（繁體中文）、en（English）、es（Español）、de（Deutsch）、fr（Français）、ja（日本語）

## 功能需求

### F1：全局语言配置存储

- 桌面端语言切换时，将语言偏好写入全局配置文件 `~/.aivectormemory/settings.json`
- 格式：`{ "language": "zh-CN" }`
- 默认值：`zh-CN`
- `aivectormemory install` 时也增加语言选择步骤，写入同一配置

### F2：动态 hook 多语言支持

涉及 IDE：Claude Code、Cursor、Windsurf

- hook 脚本（bash）启动时读取 `~/.aivectormemory/settings.json` 中的 `language` 字段
- 根据语言值输出对应语言版本的规则内容
- 多语言规则文本存储在 Python 包的 `aivectormemory/i18n/rules/` 目录下
- hook 脚本通过调用 Python 命令加载翻译并输出（或直接内嵌多语言文本）

### F3：静态规则文件多语言支持

涉及 IDE：所有（Kiro steering、CLAUDE.md、AGENTS.md、Cursor rules、Windsurf rules、VSCode copilot-instructions、Trae rules）

- install.py 的 `STEERING_CONTENT` 和 `DEV_WORKFLOW_PROMPT` 改为从 i18n 模块按语言加载
- install 时根据全局语言配置生成对应语言的静态文件
- 桌面端切换语言时，遍历已安装项目重新生成静态规则文件

### F4：桌面端语言切换联动

- 桌面端切换语言后：
  1. 更新桌面端 UI 语言（已有）
  2. 写入 `~/.aivectormemory/settings.json`
  3. 遍历数据库中已注册的项目目录
  4. 对每个项目重新执行静态文件生成（steering + hooks 中的静态部分）
- 动态 hook（bash 脚本本身不变）下次触发时自动读取新语言

### F5：i18n 翻译内容

- 翻译内容存储在 `aivectormemory/i18n/rules/` 目录下，按语言分文件（如 `zh_CN.py`、`en.py`）
- 翻译范围：
  - STEERING_CONTENT（工作规则，约 250 行）
  - DEV_WORKFLOW_PROMPT（开发流程检查，约 40 行）
- 中文为基准语言，其他语言翻译保持语义一致
- 翻译使用 AI 辅助生成

### F6：看板/桌面端 UI 语言联动

- 看板和桌面端设置页面可修改语言
- 看板修改语言时也写入 `~/.aivectormemory/settings.json`（与桌面端共享）
- 读取 settings.json 的 language 作为默认 UI 语言

## 非功能需求

- 向后兼容：未设置语言或 settings.json 不存在时默认 zh-CN，行为与当前一致
- 性能：hook 读取 settings.json 增加的延迟 < 50ms
- install.py 瘦身：模板文本从硬编码迁移到 i18n 文件
- 修改语言后下次对话即生效（动态 hook 无需重启 IDE）

## 验收标准

1. 桌面端选择 English → 所有已安装项目的规则文件和 hook 输出变为英文
2. 桌面端切换回简体中文 → 恢复中文
3. `aivectormemory install` 时可选语言
4. 新项目 install 时使用当前全局语言
5. 未安装桌面端时（纯 CLI），默认 zh-CN，功能不受影响
6. 老用户升级后默认中文，无感知、无阻断

# CI/CD Release 工作流 - 任务清单

## 第1组：仓库迁移

- [ ] 1.1 使用 `gh` CLI 创建私有仓库 `Edlineas/aivectormemory-dev`
- [x] 1.2 切换 origin 到私有仓库，添加 public remote 指向公开仓库
- [x] 1.3 推送 dev 和 main 分支到私有仓库
- [x] 1.4 验证私有仓库代码完整，公开仓库不受影响

## 第2组：GitHub PAT 配置

- [ ] 2.1 输出 PAT 创建指引（Fine-grained token，scope: Contents Read/Write，仓库: aivectormemory）
- [ ] 2.2 用户创建 PAT 后，配置到私有仓库 Secrets（`PUBLIC_REPO_TOKEN`）

## 第3组：安装脚本

- [ ] 3.1 编写 `scripts/install.sh`（macOS/Linux 安装脚本：复制 vec0 到 `~/.aivectormemory/`，macOS 复制 .app 到 `/Applications/`）
- [ ] 3.2 编写 `scripts/install.bat`（Windows 安装脚本：复制 vec0.dll 到 `%USERPROFILE%\.aivectormemory\`）

## 第4组：Workflow 编写

- [ ] 4.1 创建 `.github/workflows/release.yml` 基础结构（触发条件、构建矩阵定义）
- [ ] 4.2 编写 macOS 构建步骤（setup-go、setup-node、install wails、wails build）
- [ ] 4.3 编写 Windows 构建步骤（安装 mingw-w64、设置 CGO_ENABLED=1）
- [ ] 4.4 编写 Linux 构建步骤（安装 libgtk-3-dev、libwebkit2gtk-4.0-dev）
- [ ] 4.5 编写 sqlite-vec 下载步骤（根据平台矩阵下载对应预编译二进制）
- [ ] 4.6 编写打包步骤（可执行文件 + vec0 + install 脚本 + README，按命名规范打包）
- [x] 4.7 编写 upload-artifact 步骤
- [ ] 4.8 编写 release job（download artifacts → softprops/action-gh-release 发布到公开仓库）

## 第5组：README 同步脚本

- [ ] 5.1 编写 `scripts/sync-readme.sh`（从 dev 分支 checkout README 文件，commit 并 push 到 public remote 的 main 分支）

## 第6组：验证与测试

- [ ] 6.1 本地验证 workflow YAML 语法（`actionlint` 或在线校验）
- [ ] 6.2 推送测试 tag 到私有仓库，触发 Actions 构建
- [x] 6.3 验证所有平台构建成功
- [x] 6.4 验证 Release 正确发布到公开仓库
- [x] 6.5 验证 README 同步脚本可用

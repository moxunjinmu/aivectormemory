// AIVectorMemory plugin for OpenCode (@opencode-ai/plugin)
// - tool.execute.before: 检查 Edit/Write 前是否有活跃 track issue
// - event: stop 时提醒调用 auto_save
import { execSync } from "child_process";
import { homedir } from "os";
import { existsSync } from "fs";
import { join } from "path";

const DB_PATH = join(homedir(), ".aivectormemory", "memory.db");

function hasActiveIssues(projectDir) {
  if (!existsSync(DB_PATH)) return true; // 首次使用放行
  try {
    const result = execSync(
      `sqlite3 "${DB_PATH}" "SELECT COUNT(*) FROM issues WHERE project_dir='${projectDir}' AND status IN ('pending','in_progress');"`,
      { encoding: "utf-8", timeout: 5000 }
    ).trim();
    return parseInt(result, 10) > 0;
  } catch {
    return true; // 查询失败放行
  }
}

export default async ({ project }) => ({
  "tool.execute.before": async ({ tool, sessionID }, output) => {
    if (tool !== "Edit" && tool !== "Write" && tool !== "edit" && tool !== "write") return;
    const projectDir = project?.path || process.cwd();
    if (!hasActiveIssues(projectDir)) {
      output.args = {
        ...output.args,
        __blocked: "⚠️ 当前项目没有活跃的 track issue。请先调用 track(action: create) 记录问题后再修改代码。",
      };
    }
  },
  event: async ({ event }) => {
    if (event.type === "session.stop" || event.type === "stop") {
      console.error(
        "Reminder: call auto_save (mcp_aivectormemory_auto_save) to save session data."
      );
    }
  },
});

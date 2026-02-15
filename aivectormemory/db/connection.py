import sqlite3
import sqlite_vec
from pathlib import Path
from aivectormemory.config import get_db_path


class ConnectionManager:
    def __init__(self, project_dir: str | None = None):
        self._db_path = get_db_path()
        self.project_dir = str(Path(project_dir or Path.cwd()).resolve())
        self._conn: sqlite3.Connection | None = None

    def _ensure_dir(self):
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        self._ensure_dir()
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            conn.enable_load_extension(False)
        except AttributeError:
            conn.close()
            raise RuntimeError(
                "SQLite 扩展加载不可用。\n"
                "macOS 自带的 Python 和 python.org 官方安装包不支持 SQLite 扩展加载。\n"
                "请使用 Homebrew Python：\n"
                "  brew install python\n"
                "  /opt/homebrew/bin/python3 -m pip install aivectormemory\n"
                "详见：https://alexgarcia.xyz/sqlite-vec/python.html"
            )
        return conn

    @property
    def conn(self) -> sqlite3.Connection:
        if not self._conn:
            self._conn = self._connect()
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

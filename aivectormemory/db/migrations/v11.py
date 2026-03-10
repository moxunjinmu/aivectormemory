"""v11: issues/issues_archive 表增加 tags 列"""


def upgrade(conn, **_):
    for tbl in ("issues", "issues_archive"):
        try:
            conn.execute(f"ALTER TABLE {tbl} ADD COLUMN tags TEXT NOT NULL DEFAULT '[]'")
        except Exception:
            pass  # 列已存在则跳过

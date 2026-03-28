"""v12: 清理垃圾记忆 + 行为纠正类 + 孤立标签"""


def upgrade(conn, **_):
    # 29a: 删除 [问题追踪] 开头的记忆
    conn.execute("DELETE FROM memory_tags WHERE memory_id IN (SELECT id FROM memories WHERE content LIKE '[问题追踪]%')")
    conn.execute("DELETE FROM vec_memories WHERE id IN (SELECT id FROM memories WHERE content LIKE '[问题追踪]%')")
    conn.execute("DELETE FROM memories WHERE content LIKE '[问题追踪]%'")

    # 29b: 删除 modification/todo/decision 旧碎片（保留 preference 和 项目知识）
    frag = "(tags LIKE '%\"modification\"%' OR tags LIKE '%\"todo\"%' OR tags LIKE '%\"decision\"%') AND tags NOT LIKE '%\"preference\"%' AND tags NOT LIKE '%\"项目知识\"%'"
    conn.execute(f"DELETE FROM memory_tags WHERE memory_id IN (SELECT id FROM memories WHERE {frag})")
    conn.execute(f"DELETE FROM vec_memories WHERE id IN (SELECT id FROM memories WHERE {frag})")
    conn.execute(f"DELETE FROM memories WHERE {frag}")

    # 20e/29e: 删除行为纠正类记忆
    conn.execute("DELETE FROM memory_tags WHERE memory_id IN (SELECT id FROM memories WHERE tags LIKE '%\"行为纠正\"%')")
    conn.execute("DELETE FROM vec_memories WHERE id IN (SELECT id FROM memories WHERE tags LIKE '%\"行为纠正\"%')")
    conn.execute("DELETE FROM memories WHERE tags LIKE '%\"行为纠正\"%'")

    # 29c: 清理孤立标签
    conn.execute("DELETE FROM memory_tags WHERE memory_id NOT IN (SELECT id FROM memories)")
    conn.execute("DELETE FROM user_memory_tags WHERE memory_id NOT IN (SELECT id FROM user_memories)")

    conn.commit()

import sqlite3

conn = sqlite3.connect("kanban.db")
cursor = conn.cursor()

# 1. boards（看板）
cursor.execute("""
CREATE TABLE IF NOT EXISTS boards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# 2. columns（欄位 / 狀態）
cursor.execute("""
CREATE TABLE IF NOT EXISTS columns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    board_id INTEGER,
    name TEXT NOT NULL,
    position INTEGER,
    FOREIGN KEY(board_id) REFERENCES boards(id)
)
""")

# 3. cards（卡片 / 製令）
cursor.execute("""
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    column_id INTEGER,
    work_order TEXT,
    machine_model TEXT,
    customer TEXT,
    title TEXT,
    description TEXT,
    priority TEXT,
    status TEXT,
    owner TEXT,
    due_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(column_id) REFERENCES columns(id)
)
""")

conn.commit()
conn.close()

print("kanban.db 建立完成")
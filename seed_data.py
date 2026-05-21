import sqlite3

conn = sqlite3.connect("kanban.db")
cursor = conn.cursor()

# 1. 建立看板
cursor.execute("""
INSERT INTO boards (name)
VALUES ('工具機組裝管理')
""")

board_id = cursor.lastrowid

# 2. 建立 Kanban 欄位（流程）
columns = [
    "待BOM確認",
    "待備料",
    "備料中",
    "待組裝",
    "組裝中",
    "配線中",
    "測試中",
    "待出貨",
    "已完成"
]

for i, name in enumerate(columns):
    cursor.execute("""
    INSERT INTO columns (board_id, name, position)
    VALUES (?, ?, ?)
    """, (board_id, name, i))

# 3. 建立一張工單卡片（模擬現場）
cursor.execute("""
INSERT INTO cards (
    column_id,
    work_order,
    machine_model,
    customer,
    title,
    description,
    priority,
    status,
    owner,
    due_date
)
VALUES (
    1,
    'WO-20260521-001',
    '線切割機',
    '測試客戶A',
    '主機組裝',
    '第一台工具機組裝測試',
    '高',
    '進行中',
    '你',
    '2026-06-01'
)
""")

conn.commit()
conn.close()

print("已建立測試 Kanban 資料")
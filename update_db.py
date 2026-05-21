import sqlite3

conn = sqlite3.connect("kanban.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE cards ADD COLUMN issue_status TEXT DEFAULT '正常'")
except sqlite3.OperationalError:
    print("issue_status 欄位已存在")

try:
    cursor.execute("ALTER TABLE cards ADD COLUMN issue_note TEXT DEFAULT ''")
except sqlite3.OperationalError:
    print("issue_note 欄位已存在")

# 先把第一張卡片設成缺料測試
cursor.execute("""
UPDATE cards
SET issue_status = '缺料',
    issue_note = '缺 Sensor / 氣壓件待確認'
WHERE id = 1
""")

# ====================================
# 建立 logs table
# ====================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS logs (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    card_id INTEGER,

    action TEXT,

    created_at TEXT

)

""")

conn.commit()
conn.close()

print("缺料/異常欄位更新完成")
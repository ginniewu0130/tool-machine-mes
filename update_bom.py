import sqlite3

conn = sqlite3.connect("kanban.db")
cursor = conn.cursor()

# BOM / 料件表
cursor.execute("""

CREATE TABLE IF NOT EXISTS bom_items (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    card_id INTEGER,

    part_number TEXT,
    part_name TEXT,

    quantity INTEGER,

    status TEXT,

    note TEXT,

    FOREIGN KEY(card_id) REFERENCES cards(id)

)

""")

# 建立測試資料
cursor.execute("""

INSERT INTO bom_items (

    card_id,
    part_number,
    part_name,
    quantity,
    status,
    note

)

VALUES (?, ?, ?, ?, ?, ?)

""", (

    1,
    "A001",
    "Sensor",
    2,
    "缺料",
    "供應商延遲"

))

cursor.execute("""

INSERT INTO bom_items (

    card_id,
    part_number,
    part_name,
    quantity,
    status,
    note

)

VALUES (?, ?, ?, ?, ?, ?)

""", (

    1,
    "A002",
    "滑軌",
    4,
    "已到料",
    ""

))

conn.commit()
conn.close()

print("BOM 資料表建立完成")
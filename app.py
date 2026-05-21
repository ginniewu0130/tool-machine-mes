from flask import Flask, render_template, request, jsonify, redirect
import sqlite3

app = Flask(__name__)

# ====================================
# 新增系統 Log
# ====================================

def add_log(cursor, card_id, action):

    cursor.execute("""

        INSERT INTO logs (

            card_id,
            action,
            created_at

        )

        VALUES (?, ?, datetime('now'))

    """, (

        card_id,
        action

    ))

# ====================================
# 取得資料
# ====================================
def get_data():

    conn = sqlite3.connect("kanban.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM columns ORDER BY position")
    columns = cursor.fetchall()

    cursor.execute("SELECT * FROM cards")
    cards = cursor.fetchall()

    conn.close()

    return columns, cards


# ====================================
# 首頁
# ====================================
@app.route("/")
def index():

    columns, cards = get_data()

    conn = sqlite3.connect("kanban.db")
    cursor = conn.cursor()

    # 製令總數
    cursor.execute("""
        SELECT COUNT(*) FROM cards
    """)
    total_cards = cursor.fetchone()[0]

    # 缺料製令
    cursor.execute("""
        SELECT COUNT(*)
        FROM cards
        WHERE issue_status = '缺料'
    """)
    shortage_cards = cursor.fetchone()[0]

    # BOM總數
    cursor.execute("""
        SELECT COUNT(*)
        FROM bom_items
    """)
    total_bom = cursor.fetchone()[0]

    # 缺料件數
    cursor.execute("""
        SELECT COUNT(*)
        FROM bom_items
        WHERE status = '缺料'
    """)
    shortage_bom = cursor.fetchone()[0]

    # 已到料件數
    cursor.execute("""
        SELECT COUNT(*)
        FROM bom_items
        WHERE status = '已到料'
    """)
    arrived_bom = cursor.fetchone()[0]

    conn.close()

    # 平均齊套率
    if total_bom > 0:

        avg_kit_rate = round(
            (arrived_bom / total_bom) * 100,
            1
        )

    else:

        avg_kit_rate = 0

    

    return render_template(
    "index.html",
    columns=columns,
    cards=cards,
    total_cards=total_cards,
    shortage_cards=shortage_cards,
    total_bom=total_bom,
    shortage_bom=shortage_bom,
    avg_kit_rate=avg_kit_rate
    )


# ====================================
# 卡片詳細頁
# ====================================
@app.route("/card/<int:card_id>")
def card_detail(card_id):

    conn = sqlite3.connect("kanban.db")
    cursor = conn.cursor()

    # 取得製令
    cursor.execute("""
        SELECT * FROM cards
        WHERE id = ?
    """, (card_id,))

    card = cursor.fetchone()

    # 取得 BOM
    cursor.execute("""
        SELECT * FROM bom_items
        WHERE card_id = ?
    """, (card_id,))

    bom_items = cursor.fetchall()

    # 取得 logs
    cursor.execute("""

        SELECT *
        FROM logs
        WHERE card_id = ?
        ORDER BY id DESC

    """, (card_id,))

    logs = cursor.fetchall()

# =========================
# 計算齊套率
# =========================

    total_items = len(bom_items)

    arrived_items = 0

    for item in bom_items:

        if item[5] == "已到料":
            arrived_items += 1

    if total_items > 0:

        kit_rate = round(
            (arrived_items / total_items) * 100,
            1
        )

    else:

        kit_rate = 0

    conn.close()



    return render_template(
        "card_detail.html",
        card=card,
        bom_items=bom_items,
        kit_rate=kit_rate,
        total_items=total_items,
        arrived_items=arrived_items,
        logs=logs
    )

# ====================================
# 新增 BOM 料件
# ====================================
@app.route("/add_bom/<int:card_id>", methods=["POST"])
def add_bom(card_id):

    part_number = request.form["part_number"]
    part_name = request.form["part_name"]
    quantity = request.form["quantity"]
    status = request.form["status"]
    note = request.form["note"]

    conn = sqlite3.connect("kanban.db")
    cursor = conn.cursor()

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

        card_id,
        part_number,
        part_name,
        quantity,
        status,
        note

    ))
    
    add_log(

        cursor,
        card_id,

        f"新增BOM 料號：{part_number}名稱：{part_name}數量：{quantity} 狀態：{status}"

    )

    conn.commit()
    conn.close()

    return redirect(f"/card/{card_id}")

# ====================================
# BOM 編輯頁
# ====================================
@app.route("/edit_bom/<int:bom_id>")
def edit_bom(bom_id):

    conn = sqlite3.connect("kanban.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM bom_items
        WHERE id = ?
    """, (bom_id,))

    bom = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_bom.html",
        bom=bom
    )

# ====================================
# 更新卡片
# ====================================
@app.route("/update_card/<int:card_id>", methods=["POST"])
def update_card(card_id):

    work_order = request.form["work_order"]
    machine_model = request.form["machine_model"]
    customer = request.form["customer"]
    owner = request.form["owner"]
    issue_status = request.form["issue_status"]
    issue_note = request.form["issue_note"]

    conn = sqlite3.connect("kanban.db")
    cursor = conn.cursor()

    cursor.execute("""

        UPDATE cards

        SET
            work_order = ?,
            machine_model = ?,
            customer = ?,
            owner = ?,
            issue_status = ?,
            issue_note = ?

        WHERE id = ?

    """, (

        work_order,
        machine_model,
        customer,
        owner,
        issue_status,
        issue_note,
        card_id

    ))

    conn.commit()
    conn.close()

    return redirect("/")

# ====================================
# 更新 BOM
# ====================================
@app.route("/update_bom/<int:bom_id>", methods=["POST"])
def update_bom(bom_id):

    part_number = request.form["part_number"]
    part_name = request.form["part_name"]
    quantity = request.form["quantity"]
    status = request.form["status"]
    note = request.form["note"]

    conn = sqlite3.connect("kanban.db")
    cursor = conn.cursor()

    # 找 card_id
    cursor.execute("""
        SELECT card_id
        FROM bom_items
        WHERE id = ?
    """, (bom_id,))

    card_id = cursor.fetchone()[0]

    # 更新
    cursor.execute("""

        UPDATE bom_items

        SET
            part_number = ?,
            part_name = ?,
            quantity = ?,
            status = ?,
            note = ?

        WHERE id = ?

    """, (

        part_number,
        part_name,
        quantity,
        status,
        note,
        bom_id

    ))

    add_log(

        cursor,
        card_id,

    f"[BOM更新] {part_number} / {part_name} / 狀態：{status}"   

    )

    conn.commit()
    conn.close()

    return redirect(f"/card/{card_id}")

# ====================================
# 拖拉移動
# ====================================
@app.route("/move_card", methods=["POST"])
def move_card():

    data = request.json

    card_id = data["card_id"]
    column_id = data["column_id"]

    conn = sqlite3.connect("kanban.db")
    cursor = conn.cursor()

    cursor.execute("""

        UPDATE cards
        SET column_id = ?
        WHERE id = ?

    """, (column_id, card_id))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "ok"
    })


# ====================================
# 新增製令
# ====================================
@app.route("/add_card", methods=["POST"])
def add_card():

    work_order = request.form["work_order"]
    machine_model = request.form["machine_model"]
    customer = request.form["customer"]
    owner = request.form["owner"]

    conn = sqlite3.connect("kanban.db")
    cursor = conn.cursor()

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
            due_date,
            issue_status,
            issue_note

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        1,
        work_order,
        machine_model,
        customer,
        "新製令",
        "",
        "普通",
        "進行中",
        owner,
        "",
        "正常",
        ""

    ))

    conn.commit()
    conn.close()

    return redirect("/")


# ====================================
# 啟動
# ====================================
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
from flask import Flask, render_template_string, request, jsonify, redirect
import sqlite3

app = Flask(__name__)

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

    # 工單總數
    cursor.execute("""
        SELECT COUNT(*) FROM cards
    """)
    total_cards = cursor.fetchone()[0]

    # 缺料工單
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

    html = """

    <html>

    <head>

        <title>工具機 Kanban</title>

    </head>

    <body style="font-family:Arial; background:#f5f5f5; padding:20px;">

        <h1>工具機 Kanban（MES 雛形）</h1>
        
        <!-- Dashboard -->

        <div
            style="
                display:flex;
                gap:20px;
                margin-bottom:20px;
                flex-wrap:wrap;
            "
        >

            <div style="
                background:white;
                padding:15px;
                border-radius:10px;
                width:180px;
            ">
                <h3>工單總數</h3>
                <h2>{{ total_cards }}</h2>
            </div>

            <div style="
                background:#ffd6d6;
                padding:15px;
                border-radius:10px;
                width:180px;
            ">
                <h3>缺料工單</h3>
                <h2>{{ shortage_cards }}</h2>
            </div>

            <div style="
                background:white;
                padding:15px;
                border-radius:10px;
                width:180px;
            ">
                <h3>BOM總數</h3>
                <h2>{{ total_bom }}</h2>
            </div>

            <div style="
                background:#fff3cd;
                padding:15px;
                border-radius:10px;
                width:180px;
            ">
                <h3>缺料件數</h3>
                <h2>{{ shortage_bom }}</h2>
            </div>

            <div style="
                background:#d4edda;
                padding:15px;
                border-radius:10px;
                width:180px;
            ">
                <h3>平均齊套率</h3>
                <h2>{{ avg_kit_rate }}%</h2>
            </div>

        </div>

        <!-- 新增工單 -->
        <form method="POST" action="/add_card"
              style="
              background:white;
              padding:15px;
              margin-bottom:20px;
              border-radius:8px;
              ">

            <h3>新增工單</h3>

            工單號：
            <input type="text" name="work_order" required>

            機型：
            <input type="text" name="machine_model" required>

            客戶：
            <input type="text" name="customer">

            負責人：
            <input type="text" name="owner">

            <button type="submit">
                新增工單
            </button>

        </form>


        <!-- Kanban -->
        <div style="display:flex; gap:20px; align-items:flex-start;">

        {% for col in columns %}

            <div
                class="column"
                data-column-id="{{ col[0] }}"
                style="
                    background:#e9ecef;
                    padding:10px;
                    width:250px;
                    min-height:500px;
                    border-radius:10px;
                "
            >

                <h3>{{ col[2] }}</h3>

                {% for card in cards %}

                    {% if card[1] == col[0] %}

                        <div
                            class="card"
                            draggable="true"
                            data-card-id="{{ card[0] }}"
                            onclick="window.location='/card/{{ card[0] }}'"
                            style="
                                padding:10px;
                                margin-bottom:10px;
                                border-radius:8px;
                                cursor:pointer;
                                box-shadow:0 2px 4px rgba(0,0,0,0.2);

                                background:
                                {% if card[13] == '缺料' %}
                                    #ffd6d6
                                {% elif card[13] == '待採購' %}
                                    #fff3cd
                                {% elif card[13] == '外包延遲' %}
                                    #ffe0b2
                                {% elif card[13] == '品質異常' %}
                                    #f8d7da
                                {% else %}
                                    white
                                {% endif %}
                            "
                        >

                            <b>{{ card[2] }}</b><br><br>

                            機型：{{ card[3] }}<br>
                            客戶：{{ card[4] }}<br>
                            負責人：{{ card[9] }}<br><br>

                            <b>異常：</b>{{ card[13] }}<br>

                            <small>
                                {{ card[14] }}
                            </small>

                        </div>

                    {% endif %}

                {% endfor %}

            </div>

        {% endfor %}

        </div>


        <!-- 拖拉 -->
        <script>

            let draggedCard = null;

            document.querySelectorAll(".card").forEach(card => {

                card.addEventListener("dragstart", function(e) {

                    draggedCard = this;
                    e.stopPropagation();

                });

            });


            document.querySelectorAll(".column").forEach(column => {

                column.addEventListener("dragover", function(e) {

                    e.preventDefault();

                });


                column.addEventListener("drop", function() {

                    let cardId = draggedCard.dataset.cardId;
                    let newColumnId = this.dataset.columnId;

                    fetch("/move_card", {

                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({

                            card_id: cardId,
                            column_id: newColumnId

                        })

                    })
                    .then(response => response.json())
                    .then(data => {

                        location.reload();

                    });

                });

            });

        </script>

    </body>

    </html>

    """

    return render_template_string(
    html,
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

    # 取得工單
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

    html = """

    <html>

    <body style="font-family:Arial; padding:30px;">

        <h1>工單詳細頁</h1>

        <form method="POST" action="/update_card/{{ card[0] }}">

            <p>
                工單號：<br>
                <input type="text" name="work_order" value="{{ card[2] }}">
            </p>

            <p>
                機型：<br>
                <input type="text" name="machine_model" value="{{ card[3] }}">
            </p>

            <p>
                客戶：<br>
                <input type="text" name="customer" value="{{ card[4] }}">
            </p>

            <p>
                負責人：<br>
                <input type="text" name="owner" value="{{ card[9] }}">
            </p>

            <p>
                異常狀態：<br>

                <select name="issue_status">

                    <option value="正常"
                    {% if card[13] == '正常' %}selected{% endif %}
                    >正常</option>

                    <option value="缺料"
                    {% if card[13] == '缺料' %}selected{% endif %}
                    >缺料</option>

                    <option value="待採購"
                    {% if card[13] == '待採購' %}selected{% endif %}
                    >待採購</option>

                    <option value="外包延遲"
                    {% if card[13] == '外包延遲' %}selected{% endif %}
                    >外包延遲</option>

                    <option value="品質異常"
                    {% if card[13] == '品質異常' %}selected{% endif %}
                    >品質異常</option>

                </select>

            </p>

            <p>
                異常說明：<br>

                <textarea
                    name="issue_note"
                    rows="5"
                    cols="50"
                >{{ card[14] }}</textarea>

            </p>

            <button type="submit">
                儲存
            </button>

        </form>
        <hr>

        <h2>齊套率分析</h2>

        <div
            style="
                background:#f5f5f5;
                padding:15px;
                margin-bottom:20px;
                border-radius:10px;
            "
        >

            <h3>

                齊套率：

                {% if kit_rate >= 90 %}

                    <span style="color:green;">
                        {{ kit_rate }}%
                    </span>

                {% elif kit_rate >= 60 %}

                    <span style="color:orange;">
                        {{ kit_rate }}%
                    </span>

                {% else %}

                    <span style="color:red;">
                        {{ kit_rate }}%
                    </span>

                {% endif %}

            </h3>

            <p>
                已到料：
                {{ arrived_items }}
                /
                {{ total_items }}
            </p>

        </div>
        <hr>

        <h2>BOM / 缺料明細</h2>

                <form
            method="POST"
            action="/add_bom/{{ card[0] }}"
            style="
                background:#f5f5f5;
                padding:15px;
                margin-bottom:20px;
            "
        >

            <h3>新增料件</h3>

            料號：
            <input type="text" name="part_number" required>

            名稱：
            <input type="text" name="part_name" required>

            數量：
            <input type="number" name="quantity" value="1">

            狀態：

            <select name="status">

                <option value="已到料">
                    已到料
                </option>

                <option value="缺料">
                    缺料
                </option>

                <option value="待採購">
                    待採購
                </option>

            </select>

            備註：
            <input type="text" name="note">

            <button type="submit">
                新增料件
            </button>

        </form>

        <table border="1" cellpadding="10">

            <tr>
                <th>料號</th>
                <th>名稱</th>
                <th>數量</th>
                <th>狀態</th>
                <th>備註</th>
                <th>操作</th>
            </tr>

            {% for item in bom_items %}

            <tr

                {% if item[5] == '缺料' %}
                    style="background:#ffd6d6;"
                {% elif item[5] == '已到料' %}
                    style="background:#d4edda;"
                {% endif %}

            >

                <td>{{ item[2] }}</td>
                <td>{{ item[3] }}</td>
                <td>{{ item[4] }}</td>
                <td>{{ item[5] }}</td>
                <td>{{ item[6] }}</td>
                <td>
                    <a href="/edit_bom/{{ item[0] }}">
                        編輯
                    </a>
                </td>

            </tr>

            {% endfor %}

        </table>

        <br>

        <a href="/">← 回 Kanban</a>

    </body>

    </html>

    """

    return render_template_string(
    html,
    card=card,
    bom_items=bom_items,
    kit_rate=kit_rate,
    total_items=total_items,
    arrived_items=arrived_items
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

    html = """

    <html>

    <body style="font-family:Arial; padding:30px;">

        <h1>BOM 編輯</h1>

        <form method="POST" action="/update_bom/{{ bom[0] }}">

            <p>
                料號：<br>
                <input type="text"
                       name="part_number"
                       value="{{ bom[2] }}">
            </p>

            <p>
                名稱：<br>
                <input type="text"
                       name="part_name"
                       value="{{ bom[3] }}">
            </p>

            <p>
                數量：<br>
                <input type="number"
                       name="quantity"
                       value="{{ bom[4] }}">
            </p>

            <p>
                狀態：<br>

                <select name="status">

                    <option value="已到料"
                    {% if bom[5] == '已到料' %}selected{% endif %}
                    >
                    已到料
                    </option>

                    <option value="缺料"
                    {% if bom[5] == '缺料' %}selected{% endif %}
                    >
                    缺料
                    </option>

                    <option value="待採購"
                    {% if bom[5] == '待採購' %}selected{% endif %}
                    >
                    待採購
                    </option>

                </select>

            </p>

            <p>
                備註：<br>

                <textarea
                    name="note"
                    rows="5"
                    cols="50"
                >{{ bom[6] }}</textarea>

            </p>

            <button type="submit">
                儲存
            </button>

        </form>

        <br>

        <a href="/">← 回首頁</a>

    </body>

    </html>

    """

    return render_template_string(
        html,
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
# 新增工單
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
        "新工單",
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
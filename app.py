from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB_NAME = "inventory.db"


# =========================
# Database
# =========================

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            description TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total REAL NOT NULL,
            sold_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================
# HTML
# =========================

BASE_HTML = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>{{ title }}</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Tahoma, Arial, sans-serif;
            background: #f4f6f9;
            color: #222;
        }

        nav {
            background: #1f2937;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }

        nav .logo {
            color: white;
            font-size: 22px;
            font-weight: bold;
        }

        nav a {
            color: white;
            text-decoration: none;
            margin-left: 15px;
            padding: 8px 12px;
            border-radius: 6px;
        }

        nav a:hover {
            background: #374151;
        }

        .container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }

        h1, h2 {
            margin-top: 0;
        }

        .cards {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 25px;
        }

        .card {
            background: white;
            border-radius: 12px;
            padding: 22px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.08);
        }

        .card .number {
            font-size: 30px;
            font-weight: bold;
            margin-top: 10px;
        }

        .blue {
            border-right: 5px solid #2563eb;
        }

        .green {
            border-right: 5px solid #16a34a;
        }

        .orange {
            border-right: 5px solid #f59e0b;
        }

        .red {
            border-right: 5px solid #dc2626;
        }

        .box {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.08);
            margin-bottom: 25px;
        }

        input, textarea, select {
            width: 100%;
            padding: 11px;
            border: 1px solid #d1d5db;
            border-radius: 7px;
            font-family: inherit;
            margin-top: 6px;
        }

        textarea {
            min-height: 100px;
            resize: vertical;
        }

        label {
            display: block;
            margin-bottom: 15px;
            font-weight: bold;
        }

        button, .btn {
            border: none;
            background: #2563eb;
            color: white;
            padding: 11px 18px;
            border-radius: 7px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            font-family: inherit;
        }

        button:hover, .btn:hover {
            background: #1d4ed8;
        }

        .btn-danger {
            background: #dc2626;
        }

        .btn-danger:hover {
            background: #b91c1c;
        }

        .btn-green {
            background: #16a34a;
        }

        .btn-green:hover {
            background: #15803d;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        th, td {
            padding: 13px;
            border-bottom: 1px solid #e5e7eb;
            text-align: right;
        }

        th {
            background: #f3f4f6;
        }

        .status {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: bold;
        }

        .available {
            background: #dcfce7;
            color: #166534;
        }

        .low {
            background: #fef3c7;
            color: #92400e;
        }

        .out {
            background: #fee2e2;
            color: #991b1b;
        }

        .alert {
            padding: 14px;
            border-radius: 8px;
            margin-bottom: 20px;
            background: #dcfce7;
            color: #166534;
        }

        .error {
            background: #fee2e2;
            color: #991b1b;
        }

        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }

        .actions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .empty {
            text-align: center;
            padding: 30px;
            color: #777;
        }

        @media (max-width: 800px) {
            .cards {
                grid-template-columns: 1fr 1fr;
            }

            .form-grid {
                grid-template-columns: 1fr;
            }

            table {
                font-size: 13px;
            }
        }

        @media (max-width: 500px) {
            .cards {
                grid-template-columns: 1fr;
            }

            nav {
                padding: 15px;
            }

            .container {
                padding: 0 10px;
            }
        }
    </style>
</head>

<body>

<nav>
    <div class="logo">📦 مدیریت انبار</div>

    <div>
        <a href="{{ url_for('dashboard') }}">داشبورد</a>
        <a href="{{ url_for('products') }}">محصولات</a>
        <a href="{{ url_for('add_product') }}">افزودن محصول</a>
        <a href="{{ url_for('sales') }}">فروش‌ها</a>
    </div>
</nav>

<div class="container">

    {% with messages = get_flashed_messages() %}
        {% if messages %}
            {% for message in messages %}
                <div class="alert">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    {{ content|safe }}

</div>

</body>
</html>
"""


# =========================
# Dashboard
# =========================

@app.route("/")
def dashboard():
    conn = get_db()

    total_products = conn.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    available = conn.execute(
        "SELECT COUNT(*) FROM products WHERE stock > 5"
    ).fetchone()[0]

    low_stock = conn.execute(
        "SELECT COUNT(*) FROM products WHERE stock BETWEEN 1 AND 5"
    ).fetchone()[0]

    out_of_stock = conn.execute(
        "SELECT COUNT(*) FROM products WHERE stock = 0"
    ).fetchone()[0]

    recent_sales = conn.execute("""
        SELECT
            sales.id,
            products.name,
            sales.quantity,
            sales.total,
            sales.sold_at
        FROM sales
        JOIN products ON products.id = sales.product_id
        ORDER BY sales.id DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    content = render_template_string("""
        <h1>داشبورد</h1>

        <div class="cards">

            <div class="card blue">
                <div>تعداد محصولات</div>
                <div class="number">{{ total_products }}</div>
            </div>

            <div class="card green">
                <div>موجود</div>
                <div class="number">{{ available }}</div>
            </div>

            <div class="card orange">
                <div>کم موجود</div>
                <div class="number">{{ low_stock }}</div>
            </div>

            <div class="card red">
                <div>ناموجود</div>
                <div class="number">{{ out_of_stock }}</div>
            </div>

        </div>

        <div class="box">
            <h2>آخرین فروش‌ها</h2>

            {% if recent_sales %}
            <table>
                <tr>
                    <th>محصول</th>
                    <th>تعداد</th>
                    <th>مبلغ کل</th>
                    <th>تاریخ</th>
                </tr>

                {% for sale in recent_sales %}
                <tr>
                    <td>{{ sale["name"] }}</td>
                    <td>{{ sale["quantity"] }}</td>
                    <td>{{ "{:,.0f}".format(sale["total"]) }} تومان</td>
                    <td>{{ sale["sold_at"] }}</td>
                </tr>
                {% endfor %}
            </table>

            {% else %}
                <div class="empty">
                    هنوز فروشی ثبت نشده است.
                </div>
            {% endif %}
        </div>
    """,
    total_products=total_products,
    available=available,
    low_stock=low_stock,
    out_of_stock=out_of_stock,
    recent_sales=recent_sales)

    return render_template_string(
        BASE_HTML,
        title="داشبورد",
        content=content
    )


# =========================
# Products
# =========================

@app.route("/products")
def products():
    conn = get_db()

    products = conn.execute("""
        SELECT * FROM products
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    content = render_template_string("""
        <div class="box">

            <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap;">
                <h1>محصولات</h1>

                <a class="btn" href="{{ url_for('add_product') }}">
                    + افزودن محصول
                </a>
            </div>

            {% if products %}

            <table>
                <tr>
                    <th>نام</th>
                    <th>کد</th>
                    <th>قیمت</th>
                    <th>موجودی</th>
                    <th>وضعیت</th>
                    <th>عملیات</th>
                </tr>

                {% for product in products %}

                <tr>
                    <td>{{ product["name"] }}</td>

                    <td>{{ product["code"] }}</td>

                    <td>
                        {{ "{:,.0f}".format(product["price"]) }}
                        تومان
                    </td>

                    <td>{{ product["stock"] }}</td>

                    <td>
                        {% if product["stock"] > 5 %}

                            <span class="status available">
                                موجود
                            </span>

                        {% elif product["stock"] > 0 %}

                            <span class="status low">
                                کم موجود
                            </span>

                        {% else %}

                            <span class="status out">
                                ناموجود
                            </span>

                        {% endif %}
                    </td>

                    <td>
                        <div class="actions">

                            {% if product["stock"] > 0 %}

                            <a
                                class="btn btn-green"
                                href="{{ url_for('sell_product', product_id=product['id']) }}"
                            >
                                فروش
                            </a>

                            {% endif %}

                            <a
                                class="btn btn-danger"
                                href="{{ url_for('delete_product', product_id=product['id']) }}"
                                onclick="return confirm('آیا از حذف این محصول مطمئن هستید؟')"
                            >
                                حذف
                            </a>

                        </div>
                    </td>

                </tr>

                {% endfor %}

            </table>

            {% else %}

                <div class="empty">
                    هنوز محصولی ثبت نشده است.
                </div>

            {% endif %}

        </div>
    """, products=products)

    return render_template_string(
        BASE_HTML,
        title="محصولات",
        content=content
    )


# =========================
# Add Product
# =========================

@app.route("/add", methods=["GET", "POST"])
def add_product():

    if request.method == "POST":

        name = request.form["name"].strip()
        code = request.form["code"].strip()
        price = request.form["price"]
        stock = request.form["stock"]
        description = request.form["description"].strip()

        try:
            price = float(price)
            stock = int(stock)
        except ValueError:

            content = """
            <div class="box">
                <div class="alert error">
                    قیمت یا موجودی اشتباه وارد شده است.
                </div>

                <a class="btn" href="/add">
                    بازگشت
                </a>
            </div>
            """

            return render_template_string(
                BASE_HTML,
                title="خطا",
                content=content
            )

        conn = get_db()

        conn.execute("""
            INSERT INTO products
            (name, code, price, stock, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            code,
            price,
            stock,
            description,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("products"))

    content = """
    <div class="box">

        <h1>افزودن محصول</h1>

        <form method="POST">

            <div class="form-grid">

                <label>
                    نام محصول

                    <input
                        type="text"
                        name="name"
                        placeholder="مثلاً لپ‌تاپ"
                        required
                    >
                </label>

                <label>
                    کد محصول

                    <input
                        type="text"
                        name="code"
                        placeholder="مثلاً LAP-001"
                        required
                    >
                </label>

                <label>
                    قیمت

                    <input
                        type="number"
                        name="price"
                        min="0"
                        placeholder="مثلاً 25000000"
                        required
                    >
                </label>

                <label>
                    موجودی

                    <input
                        type="number"
                        name="stock"
                        min="0"
                        placeholder="مثلاً 10"
                        required
                    >
                </label>

            </div>

            <label>
                توضیحات

                <textarea
                    name="description"
                    placeholder="توضیحات محصول..."
                ></textarea>

            </label>

            <button type="submit">
                ثبت محصول
            </button>

        </form>

    </div>
    """

    return render_template_string(
        BASE_HTML,
        title="افزودن محصول",
        content=content
    )


# =========================
# Delete Product
# =========================

@app.route("/delete/<int:product_id>")
def delete_product(product_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM products WHERE id = ?",
        (product_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("products"))


# =========================
# Sell Product
# =========================

@app.route("/sell/<int:product_id>", methods=["GET", "POST"])
def sell_product(product_id):

    conn = get_db()

    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if not product:
        conn.close()

        return """
        <h2>محصول پیدا نشد.</h2>
        <a href="/products">بازگشت</a>
        """

    if request.method == "POST":

        try:
            quantity = int(request.form["quantity"])
        except ValueError:

            conn.close()

            content = """
            <div class="box">
                <div class="alert error">
                    تعداد وارد شده صحیح نیست.
                </div>

                <a class="btn" href="/products">
                    بازگشت
                </a>
            </div>
            """

            return render_template_string(
                BASE_HTML,
                title="خطا",
                content=content
            )

        if quantity <= 0:

            conn.close()

            content = """
            <div class="box">
                <div class="alert error">
                    تعداد باید بیشتر از صفر باشد.
                </div>

                <a class="btn" href="/products">
                    بازگشت
                </a>
            </div>
            """

            return render_template_string(
                BASE_HTML,
                title="خطا",
                content=content
            )

        if quantity > product["stock"]:

            conn.close()

            content = render_template_string("""
                <div class="box">

                    <div class="alert error">
                        موجودی کافی نیست.
                        موجودی فعلی: {{ stock }}
                    </div>

                    <a class="btn" href="/products">
                        بازگشت
                    </a>

                </div>
            """, stock=product["stock"])

            return render_template_string(
                BASE_HTML,
                title="خطا",
                content=content
            )

        total = quantity * product["price"]

        new_stock = product["stock"] - quantity

        conn.execute("""
            UPDATE products
            SET stock = ?
            WHERE id = ?
        """, (new_stock, product_id))

        conn.execute("""
            INSERT INTO sales
            (product_id, quantity, total, sold_at)
            VALUES (?, ?, ?, ?)
        """, (
            product_id,
            quantity,
            total,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("sales"))

    conn.close()

    content = render_template_string("""
        <div class="box">

            <h1>ثبت فروش</h1>

            <p>
                <strong>محصول:</strong>
                {{ product["name"] }}
            </p>

            <p>
                <strong>قیمت هر عدد:</strong>
                {{ "{:,.0f}".format(product["price"]) }}
                تومان
            </p>

            <p>
                <strong>موجودی فعلی:</strong>
                {{ product["stock"] }}
            </p>

            <form method="POST">

                <label>
                    تعداد فروش

                    <input
                        type="number"
                        name="quantity"
                        min="1"
                        max="{{ product['stock'] }}"
                        required
                    >
                </label>

                <button type="submit">
                    ثبت فروش
                </button>

                <a class="btn" href="/products">
                    انصراف
                </a>

            </form>

        </div>
    """, product=product)

    return render_template_string(
        BASE_HTML,
        title="ثبت فروش",
        content=content
    )


# =========================
# Sales
# =========================

@app.route("/sales")
def sales():

    conn = get_db()

    sales = conn.execute("""
        SELECT
            sales.id,
            products.name,
            products.code,
            sales.quantity,
            sales.total,
            sales.sold_at
        FROM sales
        JOIN products
        ON products.id = sales.product_id
        ORDER BY sales.id DESC
    """).fetchall()

    total_sales = conn.execute("""
        SELECT COALESCE(SUM(total), 0)
        FROM sales
    """).fetchone()[0]

    conn.close()

    content = render_template_string("""
        <div class="box">

            <h1>فروش‌ها</h1>

            <div class="card green" style="margin-bottom:20px;">
                <div>مجموع فروش</div>

                <div class="number">
                    {{ "{:,.0f}".format(total_sales) }}
                    تومان
                </div>
            </div>

            {% if sales %}

            <table>

                <tr>
                    <th>محصول</th>
                    <th>کد</th>
                    <th>تعداد</th>
                    <th>مبلغ</th>
                    <th>تاریخ</th>
                </tr>

                {% for sale in sales %}

                <tr>

                    <td>
                        {{ sale["name"] }}
                    </td>

                    <td>
                        {{ sale["code"] }}
                    </td>

                    <td>
                        {{ sale["quantity"] }}
                    </td>

                    <td>
                        {{ "{:,.0f}".format(sale["total"]) }}
                        تومان
                    </td>

                    <td>
                        {{ sale["sold_at"] }}
                    </td>

                </tr>

                {% endfor %}

            </table>

            {% else %}

            <div class="empty">
                هنوز فروشی ثبت نشده است.
            </div>

            {% endif %}

        </div>
    """, sales=sales, total_sales=total_sales)

    return render_template_string(
        BASE_HTML,
        title="فروش‌ها",
        content=content
    )


# =========================
# Start
# =========================

if __name__ == "__main__":
    init_db()

    print("")
    print("==============================")
    print("Inventory website started")
    print("http://127.0.0.1:5000")
    print("==============================")
    print("")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
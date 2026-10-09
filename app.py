from datetime import date
from pathlib import Path
import os
import sqlite3

from flask import Flask, abort, flash, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB = BASE_DIR / "instance" / "rental.db"

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
    DATABASE=os.environ.get("DATABASE", str(DEFAULT_DB)),
)

# Each entity has a list page and create/read/update/delete operations.
# Five entities x four CRUD operation types = at least 20 implemented operations.
ENTITIES = {
    "tools": {
        "title": "Инструменты", "singular": "инструмент", "table": "tools",
        "fields": [
            {"name": "name", "label": "Название", "type": "text", "required": True},
            {"name": "brand", "label": "Производитель", "type": "text"},
            {"name": "serial_number", "label": "Серийный номер", "type": "text"},
            {"name": "category_id", "label": "Категория", "type": "select", "ref": "categories", "required": True},
            {"name": "daily_rate", "label": "Цена за сутки (₽)", "type": "number", "step": "0.01", "required": True},
            {"name": "condition", "label": "Состояние", "type": "select_values", "options": ["Отличное", "Хорошее", "Удовлетворительное", "На ремонте"], "required": True},
            {"name": "available", "label": "Доступен для аренды", "type": "checkbox"},
            {"name": "description", "label": "Описание", "type": "textarea"},
        ],
        "columns": [("name", "Название"), ("brand", "Производитель"), ("category_name", "Категория"), ("daily_rate", "Цена/сутки"), ("condition", "Состояние"), ("available_label", "Доступность")],
        "search": ["name", "brand", "serial_number"],
    },
    "categories": {
        "title": "Категории", "singular": "категорию", "table": "categories",
        "fields": [
            {"name": "name", "label": "Название", "type": "text", "required": True},
            {"name": "description", "label": "Описание", "type": "textarea"},
        ],
        "columns": [("name", "Название"), ("description", "Описание")],
        "search": ["name", "description"],
    },
    "customers": {
        "title": "Клиенты", "singular": "клиента", "table": "customers",
        "fields": [
            {"name": "full_name", "label": "ФИО", "type": "text", "required": True},
            {"name": "phone", "label": "Телефон", "type": "text", "required": True},
            {"name": "email", "label": "Электронная почта", "type": "email"},
            {"name": "document_number", "label": "Номер документа", "type": "text"},
        ],
        "columns": [("full_name", "ФИО"), ("phone", "Телефон"), ("email", "Email"), ("document_number", "Документ")],
        "search": ["full_name", "phone", "email", "document_number"],
    },
    "rentals": {
        "title": "Аренды", "singular": "аренду", "table": "rentals",
        "fields": [
            {"name": "tool_id", "label": "Инструмент", "type": "select", "ref": "tools", "required": True},
            {"name": "customer_id", "label": "Клиент", "type": "select", "ref": "customers", "required": True},
            {"name": "start_date", "label": "Дата начала", "type": "date", "required": True},
            {"name": "end_date", "label": "Дата окончания", "type": "date", "required": True},
            {"name": "status", "label": "Статус", "type": "select_values", "options": ["Забронирована", "Активна", "Завершена", "Отменена"], "required": True},
            {"name": "total_price", "label": "Итоговая стоимость (₽)", "type": "number", "step": "0.01", "required": True},
            {"name": "notes", "label": "Примечание", "type": "textarea"},
        ],
        "columns": [("tool_name", "Инструмент"), ("customer_name", "Клиент"), ("start_date", "Начало"), ("end_date", "Окончание"), ("status", "Статус"), ("total_price", "Стоимость")],
        "search": ["status", "start_date", "end_date"],
    },
    "maintenance": {
        "title": "Обслуживание", "singular": "запись обслуживания", "table": "maintenance",
        "fields": [
            {"name": "tool_id", "label": "Инструмент", "type": "select", "ref": "tools", "required": True},
            {"name": "service_date", "label": "Дата обслуживания", "type": "date", "required": True},
            {"name": "service_type", "label": "Тип работ", "type": "text", "required": True},
            {"name": "cost", "label": "Стоимость (₽)", "type": "number", "step": "0.01", "required": True},
            {"name": "notes", "label": "Примечание", "type": "textarea"},
        ],
        "columns": [("tool_name", "Инструмент"), ("service_date", "Дата"), ("service_type", "Тип работ"), ("cost", "Стоимость"), ("notes", "Примечание")],
        "search": ["service_date", "service_type", "notes"],
    },
}

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    brand TEXT NOT NULL DEFAULT '',
    serial_number TEXT NOT NULL DEFAULT '',
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    daily_rate REAL NOT NULL CHECK(daily_rate >= 0),
    condition TEXT NOT NULL DEFAULT 'Хорошее',
    available INTEGER NOT NULL DEFAULT 1,
    description TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL DEFAULT '',
    document_number TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS rentals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_id INTEGER NOT NULL REFERENCES tools(id) ON DELETE RESTRICT,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Забронирована',
    total_price REAL NOT NULL CHECK(total_price >= 0),
    notes TEXT NOT NULL DEFAULT '',
    CHECK(end_date >= start_date)
);
CREATE TABLE IF NOT EXISTS maintenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_id INTEGER NOT NULL REFERENCES tools(id) ON DELETE RESTRICT,
    service_date TEXT NOT NULL,
    service_type TEXT NOT NULL,
    cost REAL NOT NULL CHECK(cost >= 0),
    notes TEXT NOT NULL DEFAULT ''
);
"""

def get_db():
    db_path = Path(app.config["DATABASE"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript(SCHEMA)

def entity_or_404(entity):
    if entity not in ENTITIES:
        abort(404)
    return ENTITIES[entity]

def reference_options(field):
    ref = field.get("ref")
    if not ref:
        return []
    with get_db() as conn:
        if ref == "categories":
            rows = conn.execute("SELECT id, name AS label FROM categories ORDER BY name").fetchall()
        elif ref == "tools":
            rows = conn.execute("SELECT id, name AS label FROM tools ORDER BY name").fetchall()
        elif ref == "customers":
            rows = conn.execute("SELECT id, full_name AS label FROM customers ORDER BY full_name").fetchall()
        else:
            rows = []
    return rows

def decorate_fields(entity):
    config = ENTITIES[entity]
    result = []
    for original in config["fields"]:
        field = dict(original)
        if field["type"] == "select":
            field["options_data"] = reference_options(field)
        result.append(field)
    return result

def list_sql(entity, search=""):
    if entity == "tools":
        sql = """SELECT t.*, c.name AS category_name,
                 CASE WHEN t.available=1 THEN 'Доступен' ELSE 'Недоступен' END AS available_label
                 FROM tools t JOIN categories c ON c.id=t.category_id"""
    elif entity == "rentals":
        sql = """SELECT r.*, t.name AS tool_name, c.full_name AS customer_name
                 FROM rentals r JOIN tools t ON t.id=r.tool_id
                 JOIN customers c ON c.id=r.customer_id"""
    elif entity == "maintenance":
        sql = """SELECT m.*, t.name AS tool_name FROM maintenance m JOIN tools t ON t.id=m.tool_id"""
    else:
        sql = f"SELECT * FROM {ENTITIES[entity]['table']}"
    params = []
    if search.strip():
        fields = ENTITIES[entity]["search"]
        clauses = [f"CAST({field} AS TEXT) LIKE ?" for field in fields]
        sql += " WHERE " + " OR ".join(clauses)
        params = [f"%{search.strip()}%"] * len(clauses)
    sql += " ORDER BY id DESC"
    with get_db() as conn:
        return conn.execute(sql, params).fetchall()

def get_record(entity, record_id):
    table = ENTITIES[entity]["table"]
    with get_db() as conn:
        row = conn.execute(f"SELECT * FROM {table} WHERE id=?", (record_id,)).fetchone()
    if row is None:
        abort(404)
    return row

def prepare_values(entity, form):
    values = {}
    for field in ENTITIES[entity]["fields"]:
        name = field["name"]
        kind = field["type"]
        raw = form.get(name, "").strip()
        if kind == "checkbox":
            values[name] = 1 if form.get(name) == "on" else 0
            continue
        if field.get("required") and not raw:
            raise ValueError(f"Поле «{field['label']}» обязательно для заполнения.")
        if not raw:
            values[name] = 0 if kind == "number" else ""
            continue
        if kind == "number":
            try:
                value = float(raw)
            except ValueError:
                raise ValueError(f"Поле «{field['label']}» должно быть числом.")
            if value < 0:
                raise ValueError(f"Поле «{field['label']}» не может быть отрицательным.")
            values[name] = value
        elif kind == "select":
            try:
                values[name] = int(raw)
            except ValueError:
                raise ValueError(f"Выберите корректное значение поля «{field['label']}».")
        elif kind == "select_values":
            if raw not in field["options"]:
                raise ValueError(f"Недопустимое значение поля «{field['label']}».")
            values[name] = raw
        else:
            values[name] = raw
    if entity == "rentals" and values["end_date"] < values["start_date"]:
        raise ValueError("Дата окончания не может быть раньше даты начала.")
    return values

def save_record(entity, values, record_id=None):
    table = ENTITIES[entity]["table"]
    names = list(values.keys())
    try:
        with get_db() as conn:
            if record_id is None:
                placeholders = ", ".join("?" for _ in names)
                conn.execute(
                    f"INSERT INTO {table} ({', '.join(names)}) VALUES ({placeholders})",
                    [values[name] for name in names],
                )
            else:
                assignments = ", ".join(f"{name}=?" for name in names)
                conn.execute(
                    f"UPDATE {table} SET {assignments} WHERE id=?",
                    [values[name] for name in names] + [record_id],
                )
    except sqlite3.IntegrityError as exc:
        message = str(exc)
        if "UNIQUE" in message:
            raise ValueError("Запись с таким уникальным значением уже существует.") from exc
        if "FOREIGN KEY" in message:
            raise ValueError("Выбранная связанная запись не существует.") from exc
        if "CHECK constraint" in message:
            raise ValueError("Проверьте корректность дат и числовых значений.") from exc
        raise ValueError("Не удалось сохранить запись. Проверьте введённые данные.") from exc

@app.route("/")
def dashboard():
    with get_db() as conn:
        stats = {
            "tools": conn.execute("SELECT COUNT(*) FROM tools").fetchone()[0],
            "available": conn.execute("SELECT COUNT(*) FROM tools WHERE available=1").fetchone()[0],
            "customers": conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0],
            "active_rentals": conn.execute("SELECT COUNT(*) FROM rentals WHERE status='Активна'").fetchone()[0],
        }
        recent = conn.execute("""SELECT r.id, t.name AS tool_name, c.full_name AS customer_name,
                                  r.start_date, r.end_date, r.status
                                  FROM rentals r JOIN tools t ON t.id=r.tool_id
                                  JOIN customers c ON c.id=r.customer_id
                                  ORDER BY r.id DESC LIMIT 5""").fetchall()
    return render_template("dashboard.html", stats=stats, recent=recent)

@app.route("/<entity>")
def list_records(entity):
    config = entity_or_404(entity)
    search = request.args.get("q", "")
    rows = list_sql(entity, search)
    return render_template("list.html", entity=entity, config=config, rows=rows,
                           search=search, columns=config["columns"])

@app.route("/<entity>/new", methods=["GET", "POST"])
def create_record(entity):
    config = entity_or_404(entity)
    fields = decorate_fields(entity)
    if request.method == "POST":
        try:
            values = prepare_values(entity, request.form)
            save_record(entity, values)
            flash("Запись успешно создана.", "success")
            return redirect(url_for("list_records", entity=entity))
        except ValueError as exc:
            flash(str(exc), "error")
    return render_template("form.html", entity=entity, config=config, fields=fields,
                           record=None, heading=f"Добавить: {config['singular']}")

@app.route("/<entity>/<int:record_id>/edit", methods=["GET", "POST"])
def edit_record(entity, record_id):
    config = entity_or_404(entity)
    record = get_record(entity, record_id)
    fields = decorate_fields(entity)
    if request.method == "POST":
        try:
            values = prepare_values(entity, request.form)
            save_record(entity, values, record_id)
            flash("Изменения сохранены.", "success")
            return redirect(url_for("list_records", entity=entity))
        except ValueError as exc:
            flash(str(exc), "error")
    return render_template("form.html", entity=entity, config=config, fields=fields,
                           record=record, heading=f"Редактировать: {config['singular']}")

@app.route("/<entity>/<int:record_id>/delete", methods=["POST"])
def delete_record(entity, record_id):
    config = entity_or_404(entity)
    get_record(entity, record_id)
    try:
        with get_db() as conn:
            conn.execute(f"DELETE FROM {config['table']} WHERE id=?", (record_id,))
        flash("Запись удалена.", "success")
    except sqlite3.IntegrityError:
        flash("Нельзя удалить запись: она используется в связанных данных.", "error")
    return redirect(url_for("list_records", entity=entity))

@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")

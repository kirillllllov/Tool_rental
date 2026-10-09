import pytest
from app import app as flask_app, init_db

@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "test.sqlite"
    flask_app.config.update(TESTING=True, DATABASE=str(db_path), SECRET_KEY="test-secret")
    init_db()
    with flask_app.test_client() as client:
        yield client

def seed_category(client):
    return client.post("/categories/new", data={"name": "Электроинструмент", "description": "Инструменты с электроприводом"}, follow_redirects=True)

def seed_tool(client):
    seed_category(client)
    return client.post("/tools/new", data={
        "name": "Перфоратор", "brand": "TestBrand", "serial_number": "PB-001",
        "category_id": "1", "daily_rate": "800", "condition": "Хорошее",
        "available": "on", "description": "Тестовый инструмент"
    }, follow_redirects=True)

def seed_customer(client):
    return client.post("/customers/new", data={
        "full_name": "Иван Иванов", "phone": "+7 900 000-00-00",
        "email": "ivan@example.com", "document_number": "TEST-001"
    }, follow_redirects=True)

def test_dashboard_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Система аренды строительных инструментов".encode() in response.data

def test_category_create_read_update_delete(client):
    response = seed_category(client)
    assert response.status_code == 200
    assert "Электроинструмент".encode() in response.data
    response = client.post("/categories/1/edit", data={"name": "Ручной инструмент", "description": "Обновлено"}, follow_redirects=True)
    assert "Ручной инструмент".encode() in response.data
    response = client.post("/categories/1/delete", follow_redirects=True)
    assert "Записи не найдены".encode() in response.data

def test_tool_create_read_update_delete(client):
    seed_tool(client)
    response = client.get("/tools")
    assert "Перфоратор".encode() in response.data
    response = client.post("/tools/1/edit", data={
        "name": "Перфоратор PRO", "brand": "TestBrand", "serial_number": "PB-001",
        "category_id": "1", "daily_rate": "950", "condition": "Отличное",
        "available": "on", "description": "Обновлённое описание"
    }, follow_redirects=True)
    assert "Перфоратор PRO".encode() in response.data
    response = client.post("/tools/1/delete", follow_redirects=True)
    assert "Записи не найдены".encode() in response.data

def test_customer_create_read_update_delete(client):
    seed_customer(client)
    assert "Иван Иванов".encode() in client.get("/customers").data
    response = client.post("/customers/1/edit", data={
        "full_name": "Пётр Петров", "phone": "+7 911 111-11-11",
        "email": "petr@example.com", "document_number": "TEST-002"
    }, follow_redirects=True)
    assert "Пётр Петров".encode() in response.data
    response = client.post("/customers/1/delete", follow_redirects=True)
    assert "Записи не найдены".encode() in response.data

def test_rental_create_read_update_delete(client):
    seed_tool(client)
    seed_customer(client)
    data = {"tool_id": "1", "customer_id": "1", "start_date": "2026-10-10",
            "end_date": "2026-10-12", "status": "Забронирована", "total_price": "1600", "notes": ""}
    client.post("/rentals/new", data=data, follow_redirects=True)
    assert "Перфоратор".encode() in client.get("/rentals").data
    data["status"] = "Активна"
    response = client.post("/rentals/1/edit", data=data, follow_redirects=True)
    assert "Активна".encode() in response.data
    response = client.post("/rentals/1/delete", follow_redirects=True)
    assert "Записи не найдены".encode() in response.data

def test_maintenance_create_read_update_delete(client):
    seed_tool(client)
    data = {"tool_id": "1", "service_date": "2026-10-01", "service_type": "Проверка",
            "cost": "500", "notes": "Плановое обслуживание"}
    client.post("/maintenance/new", data=data, follow_redirects=True)
    assert "Проверка".encode() in client.get("/maintenance").data
    data["service_type"] = "Замена щёток"
    response = client.post("/maintenance/1/edit", data=data, follow_redirects=True)
    assert "Замена щёток".encode() in response.data
    response = client.post("/maintenance/1/delete", follow_redirects=True)
    assert "Записи не найдены".encode() in response.data

def test_invalid_rental_dates_are_rejected(client):
    seed_tool(client)
    seed_customer(client)
    response = client.post("/rentals/new", data={
        "tool_id": "1", "customer_id": "1", "start_date": "2026-10-15",
        "end_date": "2026-10-10", "status": "Забронирована", "total_price": "100"
    }, follow_redirects=True)
    assert "Дата окончания не может быть раньше даты начала".encode() in response.data

def test_negative_price_is_rejected(client):
    seed_category(client)
    response = client.post("/tools/new", data={
        "name": "Дрель", "category_id": "1", "daily_rate": "-5",
        "condition": "Хорошее", "available": "on"
    }, follow_redirects=True)
    assert "не может быть отрицательным".encode() in response.data

def test_rental_end_date_before_start_date_is_rejected(client):
    seed_tool(client)
    seed_customer(client)

    response = client.post(
        "/rentals/new",
        data={
            "tool_id": "1",
            "customer_id": "1",
            "start_date": "2026-10-20",
            "end_date": "2026-10-10",
            "status": "Забронирована",
            "total_price": "800",
            "notes": "Проверка некорректного периода",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Дата окончания не может быть раньше даты начала".encode() in response.data


def test_rental_required_fields_are_validated(client):
    response = client.post(
        "/rentals/new",
        data={
            "tool_id": "",
            "customer_id": "",
            "start_date": "",
            "end_date": "",
            "status": "",
            "total_price": "",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "обязательно для заполнения".encode() in response.data

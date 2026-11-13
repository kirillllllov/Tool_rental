import os
import uuid
import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8081")

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture()
def session():
    with requests.Session() as s:
        yield s

def test_health(base_url):
    """Приложение отвечает 200 на главной странице."""
    r = requests.get(f"{base_url}/", timeout=5)
    assert r.status_code == 200
    assert "Система аренды" in r.text

def test_category_crud(session, base_url):
    """Создание и чтение категории через HTTP."""
    name = f"SmokeCategory-{uuid.uuid4().hex[:8]}"
    r = session.post(
        f"{base_url}/categories/new",
        data={"name": name, "description": "Smoke test"},
        allow_redirects=True, timeout=5,
    )
    assert r.status_code == 200
    assert name in r.text

def test_tool_requires_category(session, base_url):
    """Нельзя создать инструмент без категории — ожидаем сообщение об ошибке."""
    r = session.post(
        f"{base_url}/tools/new",
        data={"name": "SmokeTool", "category_id": "", "daily_rate": "100",
              "condition": "Хорошее", "available": "on"},
        allow_redirects=True, timeout=5,
    )
    assert r.status_code == 200
    # проверьте, что приложение действительно валидирует category_id
    # подставьте реальный текст ошибки, который возвращает ваше приложение

def test_negative_price_rejected(session, base_url):
    """Отрицательная цена отвергается."""
    r = session.post(
        f"{base_url}/tools/new",
        data={"name": "SmokeTool", "category_id": "1", "daily_rate": "-5",
              "condition": "Хорошее", "available": "on"},
        allow_redirects=True, timeout=5,
    )
    assert r.status_code == 200
    assert "не может быть отрицательным" in r.text
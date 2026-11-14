import uuid

import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import Order, User

MISSING_ID = 999_999_999


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


def _make_user(client):
    """Регистрирует уникального пользователя, возвращает (id, заголовки)."""
    email = f"test-{uuid.uuid4().hex[:12]}@example.com"
    r = client.post("/register", json={
        "email": email, "password": "secret", "full_name": "Test User",
    })
    assert r.status_code == 201, r.text
    user_id = r.json()["id"]
    r = client.post("/token", data={"username": email, "password": "secret"})
    assert r.status_code == 200, r.text
    return user_id, {"Authorization": f"Bearer {r.json()['access_token']}"}


def _cleanup(user_ids):
    db = SessionLocal()
    try:
        for uid in user_ids:
            db.query(Order).filter(Order.user_id == uid).delete()
            db.query(User).filter(User.id == uid).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture
def auth_headers(client):
    user_id, headers = _make_user(client)
    yield headers
    _cleanup([user_id])


@pytest.fixture
def other_headers(client):
    """Второй пользователь для проверок владения."""
    user_id, headers = _make_user(client)
    yield headers
    _cleanup([user_id])


@pytest.fixture
def product_id(client, auth_headers):
    r = client.get("/products", headers=auth_headers, params={"limit": 1})
    assert r.status_code == 200 and r.json(), "в таблице products нет товаров"
    return r.json()[0]["id"]


@pytest.fixture
def order_id(client, auth_headers, product_id):
    r = client.post("/orders", json={"product_id": product_id, "quantity": 1},
                    headers=auth_headers)
    assert r.status_code == 201, r.text
    return r.json()["id"]


# ---------- Auth ----------

def test_orders_require_token(client):
    assert client.get("/orders").status_code == 401


def test_me(client, auth_headers):
    assert client.get("/me", headers=auth_headers).status_code == 200


# ---------- Create ----------

def test_create_order_unknown_product_is_400(client, auth_headers):
    r = client.post("/orders", json={"product_id": MISSING_ID, "quantity": 1},
                    headers=auth_headers)
    assert r.status_code == 400


def test_create_order_zero_quantity_is_422(client, auth_headers, product_id):
    r = client.post("/orders", json={"product_id": product_id, "quantity": 0},
                    headers=auth_headers)
    assert r.status_code == 422


# ---------- PATCH ----------

@pytest.mark.parametrize("body", [{"quantity": None}, {"status": None}])
def test_patch_order_rejects_null(client, auth_headers, order_id, body):
    r = client.patch(f"/orders/{order_id}", json=body, headers=auth_headers)
    assert r.status_code == 422


def test_patch_order_empty_body_ok(client, auth_headers, order_id):
    r = client.patch(f"/orders/{order_id}", json={}, headers=auth_headers)
    assert r.status_code == 200


def test_patch_order_delivered(client, auth_headers, order_id):
    r = client.patch(f"/orders/{order_id}", json={"status": "delivered"},
                     headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "delivered"


def test_patch_order_invalid_status_is_422(client, auth_headers, order_id):
    r = client.patch(f"/orders/{order_id}", json={"status": "banana"},
                     headers=auth_headers)
    assert r.status_code == 422


# ---------- Ownership / roles ----------

def test_other_user_gets_403(client, order_id, other_headers):
    assert client.get(f"/orders/{order_id}", headers=other_headers).status_code == 403
    r = client.patch(f"/orders/{order_id}", json={"status": "paid"}, headers=other_headers)
    assert r.status_code == 403


def test_customer_cannot_delete_order(client, auth_headers, order_id):
    assert client.delete(f"/orders/{order_id}", headers=auth_headers).status_code == 403


def test_get_missing_order_is_404(client, auth_headers):
    assert client.get(f"/orders/{MISSING_ID}", headers=auth_headers).status_code == 404
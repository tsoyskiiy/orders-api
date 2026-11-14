import httpx

BASE_URL = "http://127.0.0.1:8000"

with httpx.Client(base_url=BASE_URL) as c:
    #1 Регистрация (409 при повторном запуске: это нормально)
    r = c.post("/register", json={
        "email": "ada@example.com",
        "password": "secret",
        "full_name": "Ada Lovelace",
    })
    print("register:", r.status_code)

    #2 Вход
    r = c.post("/token", data={"username": "ada@example.com", "password": "secret"})
    r.raise_for_status()
    auth = {"Authorization": f"Bearer {r.json()['access_token']}"}
    print("token: получен")

    #3 Кто я
    print("me:", c.get("/me", headers=auth).json())

    #4 Товары
    products = c.get("/products", headers=auth, params={"limit": 3}).json()
    print("products:", [p["name"] for p in products])

    #5 Заказы
    order = c.post("/orders", json={"product_id": products[0]["id"], "quantity": 2},
                   headers=auth).json()
    print("created order:", order)
    print("my orders:", c.get("/orders", headers=auth).json())
    print("one order:", c.get(f"/orders/{order['id']}", headers=auth).json())

    #6 Обновление
    r = c.patch(f"/orders/{order['id']}", json={"status": "paid"}, headers=auth)
    print("patch:", r.status_code, r.json())

    #7 Проверки защиты
    print("delete as customer (ждём 403):",
          c.delete(f"/orders/{order['id']}", headers=auth).status_code)
    print("orders without token (ждём 401):", c.get("/orders").status_code)
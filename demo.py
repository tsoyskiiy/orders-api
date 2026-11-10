import httpx

with httpx.Client(base_url="http://127.0.0.1:8000") as c:
    r = c.post("/register", json={
        "email": "ada@example.com",
        "password": "secret",
        "full_name": "Ada Lovelace",
    })
    print("register:", r.status_code)

    r = c.post("/token", data={"username": "ada@example.com", "password": "secret"})
    token = r.json()["access_token"]
    auth = {"Authorization": f"Bearer {token}"}
    print("token: получен")

    print("me:", c.get("/me", headers=auth).json())

    products = c.get("/products", headers=auth, params={"limit": 3}).json()
    print("products:", [p["name"] for p in products])

    order = c.post("/orders", json={"product_id": products[0]["id"], "quantity": 2},
                   headers=auth).json()
    print("created order:", order)
    print("my orders:", c.get("/orders", headers=auth).json())
    print("one order:", c.get(f"/orders/{order['id']}", headers=auth).json())

    r = c.patch(f"/orders/{order['id']}", json={"status": "paid"}, headers=auth)
    print("patch:", r.status_code, r.json())

    print("delete as customer (ждём 403):",
          c.delete(f"/orders/{order['id']}", headers=auth).status_code)
    print("orders without token (ждём 401):", c.get("/orders").status_code)
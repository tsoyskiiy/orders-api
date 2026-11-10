
# Orders API

Защищённый REST API на FastAPI поверх учебной базы PostgreSQL
(users, orders, products): CRUD заказов, JWT-аутентификация,
авторизация по владельцу и роли admin.

## Установка

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Настройка

Создай файл `.env` в корне проекта:

```
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@localhost:5432/DBNAME
SECRET_KEY=<результат: python -c "import secrets; print(secrets.token_hex(32))">
```

База данных должна быть создана и заполнена скриптами `schema.sql` и `seed.sql`.

## Запуск

```bash
fastapi dev app/main.py
```

Документация: http://127.0.0.1:8000/docs
Демо: `python demo.py`

## Эндпоинты

| Метод | Путь | Доступ |
|---|---|---|
| POST | /register | открыт |
| POST | /token | открыт |
| GET | /me | авторизованный |
| GET | /products, /products/{id} | авторизованный |
| POST | /orders | авторизованный |
| GET | /orders | свои заказы (admin: все), фильтры status, product_id, пагинация skip/limit |
| GET, PATCH | /orders/{id} | владелец или admin |
| DELETE | /orders/{id} | только admin |

## Тестовые пользователи

`user1@example.com` / `password123` (из seed-данных).
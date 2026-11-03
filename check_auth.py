from app.database import SessionLocal
from app.auth import (
    hash_password, verify_password, authenticate_user, create_access_token,
)
import jwt
from app.auth import SECRET_KEY, ALGORITHM

h = hash_password("secret")
print("Хеш:", h)
print("Верный пароль:  ", verify_password("secret", h))
print("Неверный пароль:", verify_password("wrong", h))

db = SessionLocal()
user = authenticate_user(db, "user1@example.com", "password123")
print("Вход user1 с верным паролем:", user.email if user else None)
print("Вход user1 с неверным паролем:", authenticate_user(db, "user1@example.com", "nope"))

token = create_access_token(user.id)
print("Токен:", token)
print("Содержимое:", jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]))
db.close()
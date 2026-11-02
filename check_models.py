from app.database import SessionLocal
from app.models import User, Product, Order

db = SessionLocal()

print("Users:   ", db.query(User).count())
print("Products:", db.query(Product).count())
print("Orders:  ", db.query(Order).count())

user = db.query(User).first()
print("Первый пользователь:", user.email, user.role)

product = db.query(Product).first()
print("Первый товар:", product.name, product.price)

order = db.query(Order).first()
if order:
    print("Первый заказ:", order.user_id, order.product_id, order.quantity, order.status)

db.close()
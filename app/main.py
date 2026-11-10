from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password,
    require_admin
)
from app.database import get_db
from app.models import User, Order, Product
from app.schemas import (
    OrderCreate,
    OrderOut,
    OrderUpdate,
    Token,
    UserCreate,
    UserOut,
)

app = FastAPI(title="Orders API")


@app.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role="customer",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.id))


@app.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

def get_order_or_404(db: Session, order_id: int, current_user: User) -> Order:
    """Находит заказ и проверяет, что он принадлежит пользователю (или это admin)."""
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not your order")
    return order


@app.post("/orders", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.get(Product, payload.product_id)
    if product is None:
        raise HTTPException(status_code=400, detail="product_id does not exist")

    order = Order(
        user_id=current_user.id,
        product_id=payload.product_id,
        quantity=payload.quantity,
        status="pending",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@app.get("/orders", response_model=list[OrderOut])
def list_orders(
    status: str | None = None,
    product_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Order)
    if current_user.role != "admin":
        query = query.filter(Order.user_id == current_user.id)
    if status is not None:
        query = query.filter(Order.status == status)
    if product_id is not None:
        query = query.filter(Order.product_id == product_id)

    return query.order_by(Order.id).offset(skip).limit(limit).all()


@app.get("/orders/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_order_or_404(db, order_id, current_user)


@app.patch("/orders/{order_id}", response_model=OrderOut)
def update_order(
    order_id: int,
    payload: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = get_order_or_404(db, order_id, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(order, field, value)
    db.commit()
    db.refresh(order)
    return order


@app.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
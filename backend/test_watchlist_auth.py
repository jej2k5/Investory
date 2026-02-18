from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app, get_current_active_user, get_db
from models import Base, User, Watchlist


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def _reset_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    user_a = User(username="usera", hashed_password="hashed", role="user", is_active=True, requires_password_change=False)
    user_b = User(username="userb", hashed_password="hashed", role="user", is_active=True, requires_password_change=False)
    db.add_all([user_a, user_b])
    db.commit()
    db.refresh(user_a)
    db.refresh(user_b)

    item_a = Watchlist(user_id=user_a.id, symbol="AAPL", company_name="Apple")
    item_b = Watchlist(user_id=user_b.id, symbol="MSFT", company_name="Microsoft")
    db.add_all([item_a, item_b])
    db.commit()
    db.refresh(item_a)
    db.refresh(item_b)
    user_a_id = user_a.id
    user_b_id = user_b.id
    item_a_id = item_a.id
    item_b_id = item_b.id
    db.close()

    return user_a_id, user_b_id, item_a_id, item_b_id


def _as_user(user_id: int):
    def _override():
        db = TestingSessionLocal()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()

    app.dependency_overrides[get_current_active_user] = _override


def test_list_watchlist_is_scoped_to_authenticated_user():
    user_a_id, _, item_a_id, _ = _reset_data()
    _as_user(user_a_id)

    response = client.get("/api/watchlist")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == item_a_id
    assert payload[0]["symbol"] == "AAPL"


def test_create_watchlist_uses_authenticated_user_id():
    user_a_id, _, _, _ = _reset_data()
    _as_user(user_a_id)

    response = client.post(
        "/api/watchlist",
        json={"symbol": "NVDA", "company_name": "NVIDIA", "alert_enabled": False},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["user_id"] == user_a_id
    assert payload["symbol"] == "NVDA"


def test_user_cannot_read_other_users_watchlist_item():
    user_a_id, _, _, item_b_id = _reset_data()
    _as_user(user_a_id)

    response = client.get(f"/api/watchlist/{item_b_id}")

    assert response.status_code == 404


def test_user_cannot_update_other_users_watchlist_item():
    user_a_id, _, _, item_b_id = _reset_data()
    _as_user(user_a_id)

    response = client.put(
        f"/api/watchlist/{item_b_id}",
        json={"target_buy_price": 120.5},
    )

    assert response.status_code == 404


def test_user_cannot_delete_other_users_watchlist_item():
    user_a_id, _, _, item_b_id = _reset_data()
    _as_user(user_a_id)

    response = client.delete(f"/api/watchlist/{item_b_id}")

    assert response.status_code == 404

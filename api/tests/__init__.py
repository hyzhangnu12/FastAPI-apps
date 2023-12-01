from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..config import settings
from api.database import get_db
from api.main import app
from .. import models
from fastapi.testclient import TestClient
import pytest

SQLALCHEMY_DATABASE_URL = f'{settings.DB_ENGINE}+{settings.DB_DRIVER}://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}_test'

# print(SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def session():
    print("\n=====New Session fixture=====")
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    # Dependency
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

@pytest.fixture
def user_1_create():
    user = {
        "username": "fake_user_123",
        "email": "fake_user_123@gmail.com",
        "password": "password_123"
    }
    return user

@pytest.fixture
def user_2_create():
    user = {
        "username": "fake_user_456",
        "email": "fake_user_456@gmail.com",
        "password": "password_456"
    }
    return user

@pytest.fixture
def user_signup(user_1_create, client):
    res = client.post("/users/signup", json=user_1_create)
    assert res.status_code == 200
    new_user = res.json()
    new_user['password'] = user_1_create['password']
    return new_user

@pytest.fixture
def access_token(client, user_signup):
    res = client.post("/users/login", data={"username": user_signup["email"], "password": user_signup["password"]})
    bearer_token = res.json()
    return bearer_token['access_token']

@pytest.fixture
def authorized_client(client, access_token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {access_token}"
    }
    return client
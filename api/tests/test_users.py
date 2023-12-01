from sqlalchemy import insert_sentinel
from api.tests import client, session, user_1_create, user_2_create, user_signup, access_token, authorized_client
from api.config import settings
from jose import jwt
import pytest


def test_root(client):
    res = client.get("/")
    print(res.json())
    assert res.json()["message"] == "Welcome to our place!"
    assert res.status_code == 200


def test_users_signup(client, user_1_create):
    res = client.post("/users/signup", json=user_1_create)
    print(res, res.json())
    assert res.status_code == 200
    user_signuped = res.json()
    assert user_signuped['email'] == user_1_create['email']
    assert user_signuped['username'] == user_1_create['username']


@pytest.mark.parametrize("email, username, password, status_code", [
    ('test_123@gmail.com', 'test_123', 'password_123', 200),
    ('test_123gmail.com', 'test_123', 'password_123', 422),
    ('a@b', 'test_123', 'password_123', 422),
    ('test_123@gmail.com', 'test_12', 'password_123', 200),
    ('test_123@gmail.com', '', 'password_123', 200),
    ('test_123@gmail.com', None, 'password_123', 422),
    ('test_123@gmail.com', 'test_123', '', 200),
    ('test_123@gmail.com', 'test_123', None, 422),
    ('test_123@gmail.com', '', '', 200),
])
def test_user_signup_incorrect(client, email, username, password, status_code):
    res = client.post("/users/signup", 
                      json={"email": email, "username": username, "password": password})
    assert res.status_code == status_code


@pytest.mark.parametrize("email, username, password, status_code", [
    ('fake_user_123@gmail.com', 'fake_user_12', 'password_13', 400),
    ('fake_user_12@gmail.com', 'fake_user_123', 'password_123', 200)
])
def test_user_signup_unique_emqil(client, user_1_create, email, username, password, status_code):
    res = client.post("/users/signup", json=user_1_create)
    res = client.post("/users/signup", 
                      json={"email": email, "username": username, "password": password})
    assert res.status_code == status_code


def test_user_login(client, user_signup):
    res = client.post("/users/login", 
        data={"username": user_signup['email'], "password": user_signup["password"]})
    assert res.status_code == 200
    print(res, res.json())
    bearer_token = res.json()
    assert bearer_token['token_type'] == 'bearer'
    payload = jwt.decode(bearer_token['access_token'], settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print(payload)
    id = payload.get('sub')
    assert int(id) == user_signup['id'] # type: ignore


@pytest.mark.parametrize("email, password, status_code", [
    ("wrong_email@gamil.com", "password_123", 401),
    ("fake_user_123@gamil.com", "wrong_password", 401),
    ("wrong_email@gamil.com", "wrong_password", 401),
    (None, "password_123", 422),
    ("fake_user_123@gamil.com", None, 422)
])
def test_user_login_wrong_credential(client, user_signup, email, password, status_code):
    res = client.post("/users/login", data={"username": email, "password": password})
    print(res, res.json())
    assert res.status_code == status_code


def test_user_me(authorized_client, user_signup):
    res = authorized_client.get("/users/me")
    print(res, res.json())
    print(user_signup)
    del user_signup["password"]
    assert user_signup.items() == res.json().items()


def test_user_all(authorized_client, user_signup):
    res = authorized_client.get("/users/")
    print(res, res.json())
    print(user_signup)
    del user_signup["password"]
    assert user_signup in res.json()
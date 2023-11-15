from datetime import datetime, timedelta
from typing import Annotated
from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import EmailStr
from .. import models, database, schemas

# random string by "openssl rand -hex 32"
SECRET_KEY = "c73aa39640c22bb5ce28ebf8bc509a2aba0771edf1c5ec4333e3c5f21dd6a843"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10

# Hash password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# JWT Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserCreate):
    db_query = db.query(models.User).filter(models.User.id == user_id)
    hashed_password = hash_password(user.password)
    db_user = db_query.first()
    db_query.update({'username': user.username, 'hashed_password': hashed_password}, synchronize_session=False)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_query = db.query(models.User).filter(models.User.id == user_id)
    db_query.delete(synchronize_session=False)
    db.commit()

def login_authenticate_user(
    db: Session, 
    username: Annotated[EmailStr, "It's user email"], 
    password: str
):
    db_user = get_user_by_email(db, username)
    if db_user is None:
        return False
    elif not verify_password(password, db_user.hashed_password):
        return False
    return db_user


def create_access_token(
    data: dict, 
    expires_delta: timedelta | None = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_active_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(database.get_db)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        #token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    db_user = get_user(db, int(user_id))
    if db_user is None:
        raise credentials_exception
    elif not db_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return db_user
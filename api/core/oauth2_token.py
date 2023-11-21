from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from pydantic import EmailStr
from . import crud, utils
from .. import models, database, schemas
from ..routers import exception_code
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from ..config import settings


# JWT Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def authenticate_user(
    db: Session, 
    username: Annotated[EmailStr, "It's user email"], 
    password: str
) -> models.User | None:
    db_user = crud.get_user_by_email(db, username)
    if db_user is not None and utils.verify_password(password, db_user.hashed_password):
        return db_user

def create_access_token(
    payload: dict,     # { 'sub': TokenData }
    expires_delta: timedelta
) -> schemas.Token:
    to_encode = payload.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return schemas.Token(access_token=encoded_jwt, token_type = "bearer")

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(database.get_db)]
) -> models.User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        '''tokenData: schemas.TokenData = payload.get("sub")
        tokenData = payload.get("sub")
        if tokenData is not None:
            user_id = int(tokenData)
        if tokenData is None or user_id is None:    
            raise exception_code.E_code["403"]'''
        user_id = payload.get("sub")
        if user_id is None:
            raise exception_code.E_code["403"]
    except JWTError as e:
        print(f'Failed to verify token: {str(e)}')
        raise exception_code.E_code["403"]
    db_user = crud.get_user(db, int(user_id))
    if db_user is None:
        raise exception_code.E_code["403"]
    return db_user

def get_current_active_user(
    current_user: Annotated[schemas.User, Depends(get_current_user)]
) -> schemas.User:
    if not current_user.is_active:
        raise exception_code.E_code["423"]
    return current_user
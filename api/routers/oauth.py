from fastapi import APIRouter
from typing import Annotated
from sqlalchemy.orm import Session

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .. import database, schemas, models
from ..controls import oauth2

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(database.get_db)]
):
    db_user = oauth2.login_authenticate_user(db, form_data.username, form_data.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    #access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = oauth2.create_access_token(
        data={"sub": str(db_user.id)}#, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=schemas.User)
async def read_users_me(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_active_user)]
):
    return current_user


@router.get("/users/me/items/", response_model=list[schemas.Item])
async def read_own_items(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_active_user)]
):
    return current_user.items



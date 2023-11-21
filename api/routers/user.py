from fastapi import APIRouter
from typing import Annotated
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .. import database, schemas, models
from ..controls import crud, oauth2_token
from . import exception_code
from ..config import settings

router = APIRouter(tags=['users'], prefix='/users')

@router.post("/signup", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Annotated[Session, Depends(database.get_db)]):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise exception_code.E_code["400"]
    return crud.create_user(db=db, user=user)
        
   
@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(database.get_db)]
):
    db_user = oauth2_token.authenticate_user(db, form_data.username, form_data.password)
    if db_user is None:
        raise exception_code.E_code["401"]
    tokenData = schemas.TokenData(user_id=db_user.id)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    bearer_token: schemas.Token = oauth2_token.create_access_token(
        payload={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )
    return bearer_token

@router.get("/me", response_model=schemas.User)
async def read_users_me(
    current_user: Annotated[schemas.User, Depends(oauth2_token.get_current_active_user)]
):
    return current_user

@router.put("/me/update-username", response_model=schemas.User)
async def update_username(
    current_user: Annotated[schemas.User, Depends(oauth2_token.get_current_active_user)],
    user: schemas.UserUpdateUsername,
    db: Annotated[Session, Depends(database.get_db)]
):
    return crud.update_username(db=db, user_id=current_user.id, user=user)

@router.put("/me/update-password", response_model=schemas.User)
async def update_password(
    current_user: Annotated[schemas.User, Depends(oauth2_token.get_current_active_user)],
    user: schemas.UserUpdatePassword,
    db: Annotated[Session, Depends(database.get_db)]
):
    db_user = oauth2_token.authenticate_user(db, current_user.email, user.password_0)
    if db_user is None:
        raise exception_code.E_code["401"]
    if user.password_1 != user.password_2:
        raise HTTPException(status_code=400, detail="New password and valid password are different!")
    return crud.update_password(db=db, user_id=current_user.id, user=user)

@router.get("/me/items", response_model=list[schemas.Item])
async def read_own_items(
    current_user: Annotated[schemas.User, Depends(oauth2_token.get_current_active_user)]
):
    return current_user.items

@router.get("/", response_model=list[schemas.User])
async def read_users(
    current_user: Annotated[schemas.User, Depends(oauth2_token.get_current_active_user)],
    db: Annotated[Session, Depends(database.get_db)]
):
    return crud.get_users(db)

@router.delete("/me/quit", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    current_user: Annotated[schemas.User, Depends(oauth2_token.get_current_active_user)],
    db: Annotated[Session, Depends(database.get_db)]
):
    crud.delete_user(db=db, user_id=current_user.id)






'''
@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db=db, user_id=user_id, user=user)

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_query = db.query(models.User).filter(models.User.id ==  user_id)
    if db_query.first() is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=204)
'''
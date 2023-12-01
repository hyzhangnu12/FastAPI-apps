from fastapi import APIRouter
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from .. import database, schemas
from ..core import crud, oauth2_token
from . import exception_code

router = APIRouter(tags=['items'], prefix='/items')


@router.get("/", response_model=list[schemas.Item])
async def read_items(
    current_user: Annotated[schemas.User, Depends(oauth2_token.get_current_active_user)],
    db: Annotated[Session, Depends(database.get_db)]
):
    return crud.get_items(db)

@router.post("/", response_model=schemas.Item)
async def create_item(
    current_user: Annotated[schemas.User, Depends(oauth2_token.get_current_active_user)],
    db: Annotated[Session, Depends(database.get_db)],
    item: schemas.ItemBase
):
    return crud.create_item(db=db, user_id=current_user.id, item=item)

@router.get("/{item_id}", response_model=schemas.Item)
async def read_item(
    current_user: Annotated[schemas.User, Depends(oauth2_token.get_current_active_user)],
    db: Annotated[Session, Depends(database.get_db)],
    item_id: int,
):
    db_item = crud.get_item(db=db, item_id=item_id) 
    if db_item is None:
        raise exception_code.E_code["404"]
    return db_item

@router.put("/{item_id}/update", response_model=schemas.Item)
async def update_item(
    current_user: Annotated[schemas.User, Depends(oauth2_token.get_current_active_user)],
    db: Annotated[Session, Depends(database.get_db)],
    new_item: schemas.ItemBase, item_id: int
):
    return crud.update_item(db=db, user_id=current_user.id, item_id=item_id, new_item=new_item) 

@router.delete("/{item_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    current_user: Annotated[schemas.User, Depends(oauth2_token.get_current_active_user)],
    db: Annotated[Session, Depends(database.get_db)],
    item_id: int
):
    crud.delete_item(db=db, user_id=current_user.id, item_id=item_id) 
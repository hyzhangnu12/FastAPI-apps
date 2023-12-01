from fastapi import APIRouter
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from .. import database, schemas
from ..core import crud, oauth2_token
from . import exception_code

router = APIRouter(tags=['votes'], prefix='/votes')


@router.get("/", response_model=list[schemas.Vote])
async def read_votes(
    current_user: Annotated[schemas.User, Depends(oauth2_token.get_current_active_user)],
    db: Annotated[Session, Depends(database.get_db)]
):
    return crud.get_votes(db)

@router.post("/{item_id}", response_model=schemas.Vote | None)
async def create_vote(
    current_user: Annotated[schemas.User, Depends(oauth2_token.get_current_active_user)],
    db: Annotated[Session, Depends(database.get_db)],
    item_id: int
):
    return crud.create_vote(db=db, user_id=current_user.id, item_id=item_id)
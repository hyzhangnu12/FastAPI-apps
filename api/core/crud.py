from sqlalchemy.orm import Session
from .. import models, database, schemas
from . import utils, oauth2_token
from ..routers import exception_code


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = utils.hash_password(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_username(db: Session, user_id: int, user: schemas.UserUpdateUsername):
    db_query = db.query(models.User).filter(models.User.id == user_id)
    db_user = db_query.first()
    db_query.update({'username': user.username}, synchronize_session=False)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_password(db: Session, user_id: int, user: schemas.UserUpdatePassword):
    db_query = db.query(models.User).filter(models.User.id == user_id)
    hashed_password = utils.hash_password(user.password_1)
    db_user = db_query.first()
    db_query.update({'hashed_password': hashed_password}, synchronize_session=False)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_query = db.query(models.User).filter(models.User.id == user_id)
    db_query.delete(synchronize_session=False)
    db.commit()



def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def create_item(db: Session, user_id: int, item: schemas.ItemBase):
    db_item = models.Item(**item.model_dump(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, user_id: int, item_id: int, new_item: schemas.ItemBase):
    db_query = db.query(models.Item).filter(models.Item.id == item_id)
    db_item = db_query.first()
    if db_item is None:
        raise exception_code.E_code["404"]
    elif db_item.owner_id != user_id: # type: ignore
        raise exception_code.E_code["4031"]
    db_query.update(new_item.model_dump(), synchronize_session=False) # type: ignore
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, user_id: int, item_id: int):
    db_query = db.query(models.Item).filter(models.Item.id == item_id)
    db_item = db_query.first()
    if db_item is None:
        raise exception_code.E_code["404"]
    elif db_item.owner_id != user_id: # type: ignore
        raise exception_code.E_code["4031"]
    db_query.delete(synchronize_session=False)
    db.commit()



def get_votes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Vote).offset(skip).limit(limit).all()

def create_vote(db: Session, user_id: int, item_id: int):
    db_query = db.query(models.Vote).filter(models.Vote.user_id==user_id, models.Vote.item_id==item_id)
    db_vote = db_query.first()
    if db_vote is not None:
        db_query.delete(synchronize_session=False)
        db.commit()
    else:
        db_vote = models.Vote(user_id=user_id, item_id=item_id)
        db.add(db_vote)
        db.commit()
        db.refresh(db_vote)
        return db_vote
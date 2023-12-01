from pydantic import BaseModel, EmailStr
from datetime import datetime


class ItemBase(BaseModel):
    title: str
    description: str | None = None
    published: bool | None = True

class ItemCreate(ItemBase):
    owner_id: int


class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdateUsername(BaseModel):
    username: str

class UserUpdatePassword(BaseModel):
    password_0: str
    password_1: str
    password_2: str




class Item(ItemBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    owner: UserBase

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    items: list[Item] = []

    class Config:
        from_attributes = True


class Vote(BaseModel):
    user_id: int
    item_id: int
    created_at: datetime
    updated_at: datetime
    voter: UserBase
    item: ItemCreate

    class Config:
        from_attributes = True



    
class Token(BaseModel):
    access_token: str
    token_type: str | None = "bearer"

class TokenDataUser(BaseModel):
    id: int

    class Config:
        from_attributes = True
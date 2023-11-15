from pydantic import BaseModel, EmailStr
from datetime import datetime


class ItemBase(BaseModel):
    title: str
    description: str | None = None
    published: bool | None = True

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    items: list[Item] = []

    class Config:
        from_attributes = True

    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int | None = None
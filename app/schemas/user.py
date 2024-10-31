from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    display_name: str | None = None

class UserCreate(UserBase):
    password: str

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str


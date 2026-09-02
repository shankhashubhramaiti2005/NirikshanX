from pydantic import BaseModel, EmailStr, Field
from ..models.user import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str = ""
    role: UserRole = UserRole.CONSUMER

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class LoginForm(BaseModel):
    username: str
    password: str
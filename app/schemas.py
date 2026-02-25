from pydantic import BaseModel
from typing import Optional

# ---------- Profile Schemas ----------
class ProfileBase(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class ProfileCreate(ProfileBase):
    user_id: int

class ProfileUpdate(ProfileBase):
    pass

class Profile(ProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# ---------- User Schemas ----------
class UserBase(BaseModel):
    name: str
    email: str
    age: Optional[int] = None

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    is_active: Optional[bool] = None   # Ajouté

class User(UserBase):
    id: int
    is_active: bool = True              # Ajouté
    profile: Optional[Profile] = None

    class Config:
        from_attributes = True
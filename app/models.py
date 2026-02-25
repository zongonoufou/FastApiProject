from sqlalchemy import Column, Integer, String, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)           # Longueur ajoutée
    email = Column(String(100), unique=True, index=True) # Longueur ajoutée
    age = Column(Integer)
    is_active = Column(Boolean, default=True)
    profile = relationship("Profile", back_populates="user", uselist=False)

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    bio = Column(String(500), nullable=True)        # Longueur ajoutée
    avatar_url = Column(String(255), nullable=True) # Longueur ajoutée
    
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    user = relationship("User", back_populates="profile")
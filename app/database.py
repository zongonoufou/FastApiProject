from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from dotenv import load_dotenv
import os

# Charger le fichier .env

from pathlib import Path

env_path = Path(__file__).parent / '.env' 
load_dotenv(dotenv_path=env_path)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("Base de donnees non definies")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True  # évite les erreurs de connexion expirée
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base = declarative_base()

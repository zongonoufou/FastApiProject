# app/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal, engine   # import absolu
from app import models, schemas, crud
from app.fake_data import seed_users_with_profiles

# ---------- Gestionnaire de cycle de vie (lifespan) ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code exécuté au démarrage de l'application
    print("Création des tables...")
    models.Base.metadata.create_all(bind=engine)

    # Initialisation de la base avec des données fictives si elle est vide
    db = SessionLocal()
    try:
        if db.query(models.User).count() == 0:
            print("Génération de données fictives...")
            seed_users_with_profiles(db, count=20)
    finally:
        db.close()

    print("Application prête.")
    yield   # L'application tourne ici

    # Code exécuté à l'arrêt de l'application
    print("Arrêt de l'application...")
    # Vous pouvez ajouter des opérations de nettoyage si nécessaire

# ---------- Création de l'application FastAPI ----------
app = FastAPI(
    title="API User & Profile",
    description="Une API simple avec FastAPI, SQLAlchemy et Faker",
    version="1.0.0",
    lifespan=lifespan
)

# ---------- Dépendance pour obtenir une session base de données ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Configuration CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Endpoints pour User ----------
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenue sur l'API User & Profile"}

@app.get("/users/", response_model=List[schemas.User], tags=["Users"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupère la liste des utilisateurs (avec leur profil si existant)."""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Récupère un utilisateur par son ID."""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return db_user

@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Crée un nouvel utilisateur (sans profil)."""
    # Ici on pourrait aussi accepter un profil optionnel via un deuxième paramètre,
    # mais pour simplifier on crée seulement l'utilisateur.
    # Si vous voulez créer un utilisateur avec profil en une seule requête,
    # il faudrait un schéma dédié (UserWithProfileCreate) et une méthode combinée.
    return crud.create_user(db, user)

@app.get("/users/{user_id}/profile", response_model=schemas.Profile, tags=["Users", "Profiles"])
def read_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Récupère le profil d'un utilisateur."""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    if db_user.profile is None:
        raise HTTPException(status_code=404, detail="Profil non trouvé pour cet utilisateur")
    return db_user.profile

# ---------- Endpoints pour Profile ----------
@app.get("/profiles/", response_model=List[schemas.Profile], tags=["Profiles"])
def read_profiles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupère la liste de tous les profils."""
    profiles = crud.get_profiles(db, skip=skip, limit=limit)
    return profiles

@app.get("/profiles/{profile_id}", response_model=schemas.Profile, tags=["Profiles"])
def read_profile(profile_id: int, db: Session = Depends(get_db)):
    """Récupère un profil par son ID."""
    db_profile = crud.get_profile(db, profile_id=profile_id)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    return db_profile

@app.post("/profiles/", response_model=schemas.Profile, tags=["Profiles"])
def create_profile(profile: schemas.ProfileCreate, user_id: int, db: Session = Depends(get_db)):
    """Crée un profil pour un utilisateur spécifique.
    - **user_id** : ID de l'utilisateur auquel ce profil appartient.
    """
    # Vérifier que l'utilisateur existe
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    try:
        return crud.create_profile(db, profile, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Variante : création d'un profil via /users/{user_id}/profile (plus RESTful)
@app.post("/users/{user_id}/profile", response_model=schemas.Profile, tags=["Users", "Profiles"])
def create_profile_for_user(user_id: int, profile: schemas.ProfileCreate, db: Session = Depends(get_db)):
    """Crée un profil pour l'utilisateur spécifié."""
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    try:
        return crud.create_profile(db, profile, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.patch("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def patch_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Mise à jour partielle d'un utilisateur (ex: is_active)"""
    return crud.update_user(db, user_id, user_update)

@app.delete("/users/{user_id}", tags=["Users"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Supprime définitivement un utilisateur"""
    result = crud.delete_user(db, user_id)
    return {"message": "Utilisateur supprimé avec succès"}

# route pour les stats   
@app.get("/stats/")
def get_stats(db: Session = Depends(get_db)):
    total_users = db.query(models.User).count()
    users_with_profile = db.query(models.User).filter(models.User.profile != None).count()
    avg_age = db.query(func.avg(models.User.age)).scalar()
    return {
        "total_users": total_users,
        "users_with_profile": users_with_profile,
        "avg_age": avg_age
    }

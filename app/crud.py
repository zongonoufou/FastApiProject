from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException

# ---------- User CRUD ----------
def get_user(db: Session, user_id: int):
    """Récupère un utilisateur par son ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Récupère un utilisateur par son email (utile pour éviter les doublons)"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Liste les utilisateurs avec pagination"""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    """Crée un nouvel utilisateur sans profil associé"""
    # Vérifier si l'email existe déjà
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    """Met à jour un utilisateur existant (champs partiels)"""
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Mise à jour des champs fournis
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    """Supprime un utilisateur et son profil associé (cascade manuelle si nécessaire)"""
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Supprimer d'abord le profil s'il existe (optionnel, car la BD peut avoir ON DELETE CASCADE)
    if db_user.profile:
        db.delete(db_user.profile)
    
    db.delete(db_user)
    db.commit()
    return {"message": "Utilisateur supprimé avec succès"}

# ---------- Profile CRUD ----------
def get_profile(db: Session, profile_id: int):
    """Récupère un profil par son ID"""
    return db.query(models.Profile).filter(models.Profile.id == profile_id).first()

def get_profile_by_user_id(db: Session, user_id: int):
    """Récupère le profil d'un utilisateur donné"""
    return db.query(models.Profile).filter(models.Profile.user_id == user_id).first()

def get_profiles(db: Session, skip: int = 0, limit: int = 100):
    """Liste tous les profils"""
    return db.query(models.Profile).offset(skip).limit(limit).all()

def create_profile(db: Session, profile: schemas.ProfileCreate, user_id: int):
    """Crée un profil pour un utilisateur spécifique"""
    # Vérifier que l'utilisateur existe
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Vérifier si l'utilisateur a déjà un profil
    if get_profile_by_user_id(db, user_id):
        raise HTTPException(status_code=400, detail="Cet utilisateur a déjà un profil")
    
    db_profile = models.Profile(**profile.dict(), user_id=user_id)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def update_profile(db: Session, profile_id: int, profile_update: schemas.ProfileUpdate):
    """Met à jour un profil existant"""
    db_profile = get_profile(db, profile_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_profile, field, value)
    
    db.commit()
    db.refresh(db_profile)
    return db_profile

def delete_profile(db: Session, profile_id: int):
    """Supprime un profil (sans supprimer l'utilisateur)"""
    db_profile = get_profile(db, profile_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    db.delete(db_profile)
    db.commit()
    return {"message": "Profil supprimé avec succès"}

# ---------- Méthodes métier combinées ----------
def create_user_with_profile(db: Session, user_data: schemas.UserCreate, profile_data: schemas.ProfileCreate):
    """Crée un utilisateur et son profil en une seule opération"""
    # Créer l'utilisateur d'abord
    user = create_user(db, user_data)  # cette fonction vérifie déjà l'unicité de l'email
    
    # Créer le profil associé
    try:
        profile = create_profile(db, profile_data, user.id)
    except Exception as e:
        # En cas d'échec de création du profil, supprimer l'utilisateur pour rester cohérent
        db.delete(user)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Échec de création du profil : {str(e)}")
    
    # Recharger l'utilisateur avec son profil
    db.refresh(user)
    return user

def get_user_with_profile(db: Session, user_id: int):
    """Récupère un utilisateur avec son profil (équivalent à get_user mais explicite)"""
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user  # le profil est accessible via user.profile grâce à la relation

def update_user_and_profile(db: Session, user_id: int, user_update: schemas.UserUpdate, profile_update: schemas.ProfileUpdate):
    """Met à jour à la fois l'utilisateur et son profil (si le profil existe)"""
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Mettre à jour l'utilisateur
    if user_update:
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
    
    # Mettre à jour le profil s'il existe et si des données sont fournies
    if profile_update and user.profile:
        update_data = profile_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user.profile, field, value)
    elif profile_update and not user.profile:
        # Si pas de profil et qu'on veut le mettre à jour, on pourrait le créer
        # Mais ici on lève une erreur pour rester simple
        raise HTTPException(status_code=404, detail="L'utilisateur n'a pas de profil à mettre à jour")
    
    db.commit()
    db.refresh(user)
    return user
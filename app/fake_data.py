from faker import Faker
from sqlalchemy.orm import Session
from app import schemas, models   # import absolu (pas de point)

fake = Faker()

def seed_users_with_profiles(db: Session, count: int = 20):
    """
    Génère des utilisateurs et, pour 80% d'entre eux, un profil associé.
    """
    users_created = []
    for _ in range(count):
        # 1. Créer l'utilisateur
        user_data = schemas.UserCreate(
            name=fake.name(),
            email=fake.email(),
            age=fake.random_int(min=18, max=80)
        )
        db_user = models.User(**user_data.model_dump())
        db.add(db_user)
        db.flush()  # crucial : obtient l'ID sans commit

        # 2. Créer un profil pour 80% des utilisateurs
        if fake.boolean(chance_of_getting_true=80):
            profile_data = schemas.ProfileCreate(
                user_id=db_user.id,          # 🟢 le champ manquant est maintenant fourni
                bio=fake.text(max_nb_chars=200),
                avatar_url=fake.image_url()
            )
            db_profile = models.Profile(**profile_data.model_dump())
            db.add(db_profile)

        users_created.append(db_user)

    db.commit()
    return users_created
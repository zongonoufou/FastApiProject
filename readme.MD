# SIGIS - Système Intelligent de Gestion des Incidents de Sécurité (Backend & Administration)


Ce projet fournit une API RESTful pour la gestion d'utilisateurs et de profils, accompagnée d'une interface d'administration web. Il est conçu dans le cadre du projet **SIGIS** (Système Intelligent de Gestion des Incidents de Sécurité) mais peut être réutilisé pour toute application nécessitant une gestion d'utilisateurs.

---

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Stack technique](#-stack-technique)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
  - [Backend (FastAPI)](#backend-fastapi)
  - [Frontend (administration)](#frontend-administration)
- [Variables d'environnement](#-variables-denvironnement)
- [Exécution avec Docker](#-exécution-avec-docker)
- [Documentation de l'API](#-documentation-de-lapi)
- [Utilisation](#-utilisation)
- [Contribuer](#-contribuer)
- [Licence](#-licence)

---

## ✨ Fonctionnalités

- **Gestion complète des utilisateurs** : création, lecture, mise à jour, suppression.
- **Profils utilisateur** : chaque utilisateur peut avoir un profil (bio, avatar).
- **Statistiques** : tableau de bord avec le nombre total d'utilisateurs, ceux avec profil, âge moyen.
- **Interface d'administration** : page web simple et moderne pour gérer les utilisateurs (ajout, modification, suppression).
- **Dockerisé** : lancement facile avec Docker Compose.
- **API documentée** : documentation interactive Swagger/ReDoc.

---

## 🛠 Stack technique

| Composant       | Technologie                          |
|-----------------|--------------------------------------|
| Backend         | FastAPI (Python 3.10+)               |
| Base de données | MySQL (via SQLAlchemy + PyMySQL)     |
| ORM             | SQLAlchemy 2.0                       |
| Validation      | Pydantic v2                          |
| Frontend        | HTML5, CSS3, JavaScript vanilla      |
| Conteneurisation| Docker, Docker Compose                |
| Migration       | Alembic (optionnel)                   |

---

## 📦 Prérequis

- Python 3.10 ou supérieur
- MySQL Server (ou conteneur MySQL)
- Node.js (uniquement si vous souhaitez modifier le frontend, non requis pour l'exécution)
- Docker (optionnel, pour la conteneurisation)
- Git

---

## 🚀 Installation

### Backend (FastAPI)

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/votre-utilisateur/fastaproject.git
   cd fastaproject
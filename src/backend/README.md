# 🖥️ Backend — API FastAPI (Recipe)

Le backend constitue le **cœur métier** de l’application de gestion et de recherche de recettes.

Il est développé avec **FastAPI (Python)** et expose une API REST permettant :

- l’authentification sécurisée des utilisateurs (JWT),
- la gestion des stocks personnels,
- la gestion des ingrédients,
- la recherche de recettes,
- la communication sécurisée avec le frontend React,
- l’interaction avec une base de données PostgreSQL.

Le projet utilise exclusivement **uv** pour la gestion des dépendances et l’exécution.

______________________________________________________________________

## 🏗️ Architecture du backend

Le backend respecte une séparation claire des responsabilités :

```
Routers  →  Services  →  DAO  →  Base PostgreSQL
```

- **Routers** : définition des endpoints API
- **Services** : logique applicative et règles métier
- **DAO** : accès aux données
- **Business Objects** : objets métier
- **Utils** : gestion JWT, logs, outils divers

Structure du projet :

```
backend/
│
├── api/
│   ├── main.py
│   ├── config.py
│   ├── routers/
│   └── schemas/
│
├── business_objects/
├── dao/
├── services/
├── utils/
├── data/
├── tests/
│
├── pyproject.toml
├── uv.lock
└── .env.template
```

______________________________________________________________________

## ⚙️ Stack technique

- Python 3.11+
- FastAPI
- PostgreSQL
- JWT (authentification access / refresh)
- uv (gestion d’environnement et exécution)
- Docker (optionnel)

______________________________________________________________________

## 🚀 Installation

Se placer dans le dossier `backend/` :

```bash
cd backend
```

Installer les dépendances (reproductible via `uv.lock`) :

```bash
uv sync --frozen
```

Installer aussi les dépendances de développement :

```bash
uv sync --frozen --group dev
```

______________________________________________________________________

## 🔐 Configuration (.env)

Créer un fichier `.env` à partir du template :

```bash
cp .env.template .env
```

Variables principales :

### Base de données

```env
POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_SCHEMA=
```

### Authentification JWT

```env
JWT_SECRET=
JWT_ISSUER=
ACCESS_TTL_MINUTES=
REFRESH_TTL_DAYS=
```

______________________________________________________________________

## 🗄️ Base de données

### Option 1 — PostgreSQL via Docker

```bash
docker compose up -d postgres
```

Puis lancer l’API localement.

### Option 2 — Backend + PostgreSQL via Docker

```bash
docker compose up --build
```

______________________________________________________________________

## ▶️ Lancer le backend

```bash
uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Backend accessible sur :  
👉 http://127.0.0.1:8000

Documentation interactive (Swagger) :  
👉 http://127.0.0.1:8000/docs

Healthcheck :  
👉 http://127.0.0.1:8000/health

______________________________________________________________________

## 🔁 Initialisation de la base

Scripts disponibles :

- `data/init_db.sql`
- `data/pop_db.sql`
- `data/pop_db_test.sql`
- `utils/reset_database.py`

Réinitialisation complète :

```bash
uv run python utils/reset_database.py
```

______________________________________________________________________

## 🧪 Tests et qualité

Installer les dépendances dev :

```bash
uv sync --frozen --group dev
```

### Lancer les tests

```bash
uv run pytest
```

### Lint (Ruff)

```bash
uv run ruff check .
```

### Formatage

```bash
uv run ruff format .
```

### Type checking (Pyright)

```bash
uvx pyright
```

______________________________________________________________________

## 🔌 Endpoints principaux

### Auth — `/api/auth`

- `POST /register`
- `POST /login`
- `POST /refresh`

### Utilisateurs

- `/api/users`

### Stocks

- `/api/stocks`

### Ingrédients

- `/api/ingredients`

📌 Liste complète disponible via Swagger (`/docs`).

______________________________________________________________________

## 🚀 Production / Déploiement

Le backend est conçu pour pouvoir être déployé en environnement de production de manière propre et sécurisée.

### ⚙️ Configuration recommandée en production

En production :

- ne pas utiliser `--reload`
- utiliser un `JWT_SECRET` fort et unique
- restreindre `CORS_ALLOW_ORIGINS`
- utiliser une base PostgreSQL dédiée
- désactiver les schémas de test

Exemple de lancement sans mode développement :

```bash
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000
```

______________________________________________________________________

### 🐳 Déploiement via Docker

Le backend peut être conteneurisé et exécuté via Docker Compose.

Build et lancement :

```bash
docker compose up --build -d
```

Cela permet :

- isolation de l’environnement
- cohérence entre dev et production
- simplification du déploiement sur serveur

______________________________________________________________________

### 🌐 Déploiement sur serveur

Pour un déploiement sur VPS ou serveur dédié :

1. Installer :
   - Python 3.11+
   - uv
   - PostgreSQL (ou base distante)
2. Cloner le repository
3. Configurer le `.env`
4. Installer les dépendances :

```bash
uv sync --frozen
```

5. Lancer l’application :

```bash
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Il est recommandé d’utiliser :

- un reverse proxy (Nginx)
- HTTPS (certificat SSL)
- un gestionnaire de processus (systemd)

______________________________________________________________________

### 🔐 Sécurité

Bonnes pratiques recommandées :

- Ne jamais committer le fichier `.env`
- Utiliser des secrets forts et uniques
- Restreindre l’accès aux ports
- Mettre en place HTTPS en production
- Activer les logs applicatifs

______________________________________________________________________

### 📈 Évolutions possibles

- Déploiement via CI/CD
- Intégration avec GitHub Actions
- Conteneurisation complète multi-services
- Monitoring (Prometheus / Grafana)
- Logging centralisé

______________________________________________________________________

## 📌 Notes

- Le backend est entièrement indépendant du frontend.
- Toutes les commandes Python doivent être exécutées via `uv`.
- Le projet est conçu pour être modulaire, maintenable et évolutif.

______________________________________________________________________

📦 _Ce README décrit le backend de l’application Recipe et pourra évoluer avec l’ajout de nouvelles fonctionnalités._

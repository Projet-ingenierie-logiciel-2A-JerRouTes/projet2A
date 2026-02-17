## 🐳 Architecture Docker (Conteneurisation)

L'application est entièrement orchestrée avec Docker Compose. Cette approche permet d'isoler les environnements et de garantir que le projet fonctionne de la même manière sur toutes les machines.

| Conteneur | Technologie | Image de base | Rôle technique | Persistance |
| :--- | :--- | :--- | :--- | :--- |
| **`projet2a_frontend`** | React + Vite | `node:20-alpine` | Interface utilisateur (UI) réactive | ❌ Non |
| **`projet2a_backend`** | Python + FastAPI | `python:3.13-slim` | API REST & Logique métier (Math/Stat) | ❌ Non |
| **`projet2a_postgres`** | PostgreSQL | `postgres:16-alpine` | Stockage relationnel des stocks | ✅ **Volume** |

### Conteneur "frontend"

Dans le projet dans le dossier frontend

```bash
# Image de base légère recommandée par le cours pour Node.js
FROM node:20-alpine

# Définition du répertoire de travail à l'intérieur du conteneur
WORKDIR /app

# Copie des fichiers de dépendances (optimisation du cache des layers Docker)
# On copie package.json ET package-lock.json s'il existe
COPY package*.json ./

# Installation des dépendances (incluant lucide-react et axios déjà présents)
RUN npm install

# Copie du reste du code source du frontend
COPY . .

# Exposition du port par défaut utilisé par Vite
EXPOSE 5173

# Commande pour lancer Vite en mode développement
# Le flag --host est INDISPENSABLE pour que le conteneur accepte les connexions externes
CMD ["npm", "run", "dev", "--", "--host"]
```

### Conteneur "backend"

Dans le projet dans le dossier backend

```bash
# Utilisation de votre image de base (Trixie est une version de Debian)
FROM python:3.13-slim

# Définition du dossier de travail (évite de copier à la racine du conteneur)
#WORKDIR /app
WORKDIR /projet

# Copie uniquement du fichier de dépendances pour optimiser le cache Docker
COPY requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie de tout le reste du code source vers /app
#COPY . .
COPY . ./src/backend/

# EXPOSE est crucial pour que Docker sache que le port 8000 doit être ouvert
EXPOSE 8000

# Pour FastAPI, on utilise uvicorn au lieu de "python main.py" 
# car cela permet de gérer les requêtes asynchrones et le rechargement à chaud
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["uvicorn", "src.backend.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Docker-compose

```bash
# Note : La ligne 'version' est supprimée pour éviter le Warning Docker Compose V2.

services:
  # ============================================================================
  # SERVICE : BASE DE DONNÉES (Le socle de stockage)
  # ============================================================================
  db:
    # Utilisation d'une version stable de PostgreSQL
    image: postgres:16
    container_name: projet2a_postgres
    # Redémarre automatiquement le conteneur si le PC redémarre ou si le service crash
    restart: always
    
    # Configuration des variables d'environnement (Identifiants de connexion)
    environment:
      - POSTGRES_DB=${POSTGRES_DATABASE} # image officielle Postgres EXIGE ce nom exact pour créer la BDD
      - POSTGRES_USER
      - POSTGRES_PASSWORD

    # Expose le port de la base pour pouvoir y accéder depuis un outil comme DBeaver
    ports:
      - "5432:5432"
    
    volumes:
      # PERSISTANCE : Lie un volume Docker au dossier de données de Postgres.
      # Même après un 'docker compose down', les stocks d'Alice et Bob restent sauvés.
      - projet2a_pgdata:/var/lib/postgresql/data
      
      # INITIALISATION : Chaque fichier .sql dans ./data est exécuté au PREMIER lancement.
      # Indispensable pour créer vos tables et insérer vos données de test automatiquement.
      #- ./data:/docker-entrypoint-initdb.d/
    
    # ISOLATION & SÉCURITÉ : On s'assure que Postgres répond avant de lancer le reste.
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U projet_user -d projet2a"]
      interval: 5s   # Teste toutes les 5 secondes
      timeout: 5s    # Attend 5 secondes max pour une réponse
      retries: 10    # Réessaie 10 fois avant de déclarer le service "unhealthy"

  # ============================================================================
  # SERVICE : BACKEND (L'intelligence en Python FastAPI)
  # ============================================================================
  backend:
    # Docker va chercher le 'Dockerfile' dans le dossier spécifié
    build: ./src/backend
    container_name: projet2a_backend
    restart: always
    
    volumes:
      # MODE DÉVELOPPEMENT : Lie votre code source au dossier /app du conteneur.
      # Permet de voir vos modifs de code en temps réel sans tout reconstruire.
      #- ./src/backend:/app
      - ./src:/app/src

    
    ports:
      - "8000:8000"
    
    environment:
      # Docker pioche ces valeurs directement dans ton .env
      - POSTGRES_HOST
      - POSTGRES_PORT
      - POSTGRES_DATABASE
      - POSTGRES_USER
      - POSTGRES_PASSWORD
      - POSTGRES_SCHEMA
      - PYTHONPATH=/app
    
    # ORCHESTRATION : Le backend ne démarre QUE quand la DB est déclarée "healthy".
    depends_on:
      db:
        condition: service_healthy

  # ============================================================================
  # SERVICE : FRONTEND (L'interface en React + Vite)
  # ============================================================================
  frontend:
    build: ./src/frontend
    container_name: projet2a_frontend
    restart: always
    
    volumes:
      # Synchronisation du code pour le Hot Reload de Vite
      - ./src/frontend:/app
      # Évite que le volume n'écrase les node_modules installés lors du build
      - /app/node_modules
    
    ports:
      - "5173:5173"
    
    # Le front dépend du backend pour fonctionner correctement
    depends_on:
      - backend

# ==============================================================================
# SECTION VOLUMES : Déclaration du stockage nommé
# ==============================================================================
volumes:
  # Ce volume est géré par Docker et persiste en dehors du cycle de vie des conteneurs.
  projet2a_pgdata:
```

## Lancer le projet

1. Etape 1 : Rendre le script exécutable

```bash
chmod +x start.sh
```

2. Etape 2 : Lancer le script

```bash
./start.sh
```

## Infos diverses

### Pour vider le cache

1. Supprimer les conteneurs et les volumes

Cette commande arrête les services et supprime les volumes anonymes (ce qui videra ta base de données pour forcer une réinitialisation propre) :

```bash
sudo docker compose down -v
```

2. Nettoyage global

Pour libérer un maximum d'espace et supprimer tout ce qui n'est pas utilisé (images orphelines, réseaux) :

```bash
sudo docker system prune -a --volumes -f
```

### Pense bête docker :

**Vérification de l'état des conteneur** :

```bash
sudo docker compose ps
```

**Pour arrêter/Stopper tous les conteneur** :
Ce n'est qu'un arrêt, les conteneurs sont conservé sur la machine

```bash
sudo docker compose stop
```

Pour arrête les conteneurs, les supprime, et nettoie le réseau virtuel créé par Docker.

```bash
sudo docker compose down
```

**Pour lancer un conteneur** :

```bash
sudo docker compose up -d
```

**Pour obtenir les log d'un conteneur**

```bash
# Pour le backend
sudo docker compose logs backend

# Pour le frontend
sudo docker compose logs frontend

# Pour le postgrey
sudo docker compose logs projet2a_postgres
```

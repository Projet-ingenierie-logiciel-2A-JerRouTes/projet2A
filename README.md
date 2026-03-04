
<h2 id="sommaire">📍 Sommaire</h2>

* [🎯 Objectifs du projet](#-objectifs-du-projet)
* [🧩 Fonctionnalités](#-fonctionnalités)
    * [👤 Administrateur](#en-tant-que-administateur-après-connection)
    * [👥 Utilisateur](#en-tant-quutilisateur)
    * [🌐 Invité](#en-tant-quinvité)
* [🏗️ Architecture générale](#️-architecture-générale)
    * [🗄️ Base de données](#️-base-de-données)
    * [🖥️ BackEnd](#️-backend)
    * [🖥️ FrontEnd](#️-frontend)
* [⚙️ Lancement du projet](#️-lancement-du-projet)
* [🔐 Configuration (.env)](#-configuration-env)
* [🧪 Tests Backend](#-tests-backend)
* [🌐 Déploiement en Production (Mode Web)](#-deploiement-web)
* [🧪 Qualité et outils](#-qualité-et-outils)
* [📅 Compte-rendus de réunions](#-compte-rendus-de-réunions)
* [👥 Organisation et méthode de travail](#-organisation-et-méthode-de-travail)

______________________________________________________________________

# 📦 Projet : Logiciel de gestion et de recherche de recettes

Ce projet a pour objectif de développer un **logiciel de gestion de stock alimentaire et de recherche de recettes** permettant à des utilisateurs de retrouver des recettes à partir des ingrédients dont ils disposent, tout en gérant un stock personnel et des contraintes alimentaires.

Le projet est réalisé dans le cadre du **module de création logicielle** et suit une approche structurée :

- architecture MVD (Modèle – Vue – Données),
- séparation claire frontend / backend,
- bonnes pratiques de développement,
- qualité et maintenabilité du code,
- tests automatisés.

[⬆️ Retour au sommaire](#sommaire)

______________________________________________________________________

# 🎯 Objectifs du projet

- Permettre la recherche de recettes à partir d’ingrédients disponibles
- Gérer un stock d’ingrédients par utilisateur
- Proposer une application multi-utilisateur sécurisée
- Mettre en place une architecture claire et évolutive
- Respecter les conventions de développement (PEP 8, bonnes pratiques JavaScript)

[⬆️ Retour au sommaire](#sommaire)

______________________________________________________________________

# 🧩 Fonctionnalités

### En tant que administateur (après connection)

- Informations sur les utilisateurs
  - Voir tous les utilisateurs
  - Ajouter un admin ou un utilisateur 
  - Voir les informations d'un utilisateur en particulier
  - *A faire* : compléter les informations utilisateur (stock)
  - *A faire* : Modifier/supprimer un utilisateur (Fait côté backend)

- Informations sur les ingredients
  - Voir tous les ingredients
  - Ajouter un ingredient
  - Voir les informations d'un ingredient en particulier
  - *A faire* : compléter les informations utilisateur (tag)
  - *A faire* : Modifier/supprimer un ingredient

- Informations sur les stocks
  - Voir tous les stocks
  - Ajouter un stock
  - Voir les informations d'un stock en particulier
  - *A faire* : compléter les informations du stock (utilisateur, contenu)
  - Modifier/supprimer un stock

- Informations sur les recettes
  - Voir toutes les recettes
  - Voir les informations d'une recette en particulier
  - *A faire* : ajouter une recette
  - *A faire* : compléter les informations d'une recette étape
  - *A faire* : Modifier/supprimer une recette (Fait côté Backend)

### En tant qu'utilisateur 

- Connexion utilisateur
- Visualisation des stocks disponibles
- Ajout / suppression d’ingrédients
- Recherche de recettes
- Consultation des recettes détaillées
- Mise à jour du stock après réalisation d’une recette (*fonctionnalité en cours*)

### En tant qu'invité

- Affichage de recettes aléatoires
- Recherche de recettes à partir d’ingrédients

[⬆️ Retour au sommaire](#sommaire)

______________________________________________________________________

# 🏗️ Architecture générale

L’application repose sur une architecture **MVD (Modèle – Vue – Données)** :

```
Interface utilisateur  <->  Métier  <->  Base de données
```

- **Vue** : React
- **Modèle / logique métier** : FastAPI
- **Données** : PostgreSQL

______________________________________________________________________

## 🗄️ Base de données

La base PostgreSQL gère :

- utilisateurs
- sessions
- ingrédients
- stocks
- recettes

Diagramme :

![Diagramme](Documentation/Images/diagramme_bdd.drawio.png)

[⬆️ Retour au sommaire](#sommaire)

______________________________________________________________________

## 🖥️ BackEnd

Backend développé avec **FastAPI (Python)**.

Responsabilités :

- authentification JWT
- logique métier
- accès base PostgreSQL
- API REST

Documentation backend :

```
src/backend/README.md
```

______________________________________________________________________

## 🖥️ FrontEnd

Frontend développé avec :

- **React**
- **Vite**

Fonctionnalités :

- authentification utilisateur
- communication API
- gestion du stock
- affichage des recettes

Documentation :

```
src/frontend/README.md
```

[⬆️ Retour au sommaire](#sommaire)

______________________________________________________________________

# ⚙️ Lancement du projet

Le projet est conçu pour être **portable et facilement déployable**.  
L’utilisation de **Docker** est la méthode recommandée pour lancer l'application.

Tous les services nécessaires au projet sont conteneurisés.

---

## 🐳 Lancement avec Docker (méthode recommandée)

### Prérequis

Installer :

- Docker
- Docker Compose

Vérifier :

```bash
docker --version
docker compose version
```

---

### Lancer l’application

Depuis la racine du projet :

```bash
docker compose up --build
```

Cette commande :

- construit les images Docker
- démarre la base de données
- lance le backend FastAPI
- lance le frontend React

---

### Accès aux services

Frontend :

```
http://localhost:5173
```

Backend :

```
http://localhost:8000
```

Documentation API :

```
http://localhost:8000/docs
```

---

### Arrêter l'application

```bash
docker compose down
```

---

### Voir les logs

```bash
docker compose logs -f
```

Ou pour un service spécifique :

```bash
docker compose logs -f backend
```

---

### Reconstruction complète

```bash
docker compose down -v
docker compose up --build
```

---

## 🧪 Lancer les tests

Les tests backend utilisent **pytest** avec **uv**.

Dans le conteneur backend :

```bash
docker compose exec backend uv run pytest
```

Ou en local :

```bash
uv run pytest
```

---

## 🐧 Script start.sh (Linux uniquement)

Un script `start.sh` est fourni pour simplifier le lancement.

Sous Linux :

```bash
chmod +x start.sh
./start.sh
```

⚠️ Ce script est optionnel : toutes les commandes nécessaires sont décrites dans ce README afin de garantir que le projet puisse être lancé **sans dépendre d’un script externe**.

---

## 🛠️ Lancement manuel (développement)

Possible si l’on souhaite lancer les services séparément.

### Base de données

```bash
docker compose up -d
```

### Backend

```bash
uv run uvicorn api.main:app --reload
```

### Frontend

```bash
cd src/frontend
npm install
npm run dev
```

[⬆️ Retour au sommaire](#sommaire)

______________________________________________________________________

# 🔐 Configuration (.env)

Le backend utilise des variables d’environnement définies dans un fichier `.env`.

Un template est fourni dans :

```
src/backend/.env.template
```

Créer votre fichier `.env` :

```bash
cp src/backend/.env.template src/backend/.env
```

### Exemple de configuration

```env
API_KEY_SPOONACULAR="your_api_key"

POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DATABASE=projet2a
POSTGRES_USER=projet_user
POSTGRES_PASSWORD=projet_pwd
POSTGRES_SCHEMA=projet_dao
POSTGRES_DB=projet2a

JWT_SECRET=your_secret_key
JWT_ISSUER=projet2a

ACCESS_TTL_MINUTES=15
REFRESH_TTL_DAYS=7
```

### Frontend

```
src/frontend/.env.local.template
```

______________________________________________________________________

# 🧪 Tests Backend

Les tests backend utilisent **pytest** et **uv**.

### Lancer les tests en local

```bash
uv run pytest
```

Ou uniquement les tests backend :

```bash
uv run pytest src/backend
```

### Lancer les tests dans Docker

```bash
docker compose exec backend uv run pytest
```

### Exemple avec sortie détaillée

```bash
uv run pytest -v
```

______________________________________________________________________

# 🌐 Déploiement en Production (Mode Web)

Application déployée sur VPS Linux OVH.

URL :

https://www.mongardemanger.fr

Documentation API :

https://www.mongardemanger.fr/api/docs

Architecture :

```
Client
↓
DNS
↓
VPS Linux
↓
Nginx
↓
Docker
↓
Base PostgreSQL
```

Sécurité :

- HTTPS
- firewall
- SSH par clé
- variables sensibles dans `.env`

______________________________________________________________________

# 🧪 Qualité et outils

- tests automatisés **pytest**
- linting **pre-commit**
- workflows CI

______________________________________________________________________

# 📅 Compte-rendus de réunions

- Réunion 1
- Réunion 2
- Réunion 3

______________________________________________________________________

# 👥 Organisation et méthode de travail

Le projet a été réalisé en équipe en suivant une organisation collaborative afin de faciliter la coordination et le suivi de l’avancement.

### 🏗 Réunions de construction

Des réunions régulières ont été organisées au début du projet afin de :

- définir l’architecture de l’application
- répartir les tâches entre les membres de l’équipe
- discuter des choix techniques (frameworks, structure du projet, base de données)
- planifier les différentes étapes du développement

Les comptes-rendus de ces réunions sont disponibles dans la section dédiée du dépôt.

---

### 💬 Communication

Un **canal de discussion WhatsApp** a été utilisé tout au long du projet afin de :

- poser rapidement des questions techniques
- partager des ressources et des idées
- coordonner le travail entre les membres de l’équipe

Cela a permis une communication fluide et réactive pendant toute la durée du projet.

---

### 🐙 Suivi des tâches (GitHub)

En fin de projet, les **Issues GitHub** ont été utilisées pour :

- identifier les bugs
- suivre certaines tâches restantes
- organiser les améliorations à apporter

Cela a permis de structurer davantage le suivi du développement.

---

### 🤝 Travail en présentiel

Des séances de **travail en groupe en présentiel** ont également été organisées afin de :

- faire des points d’avancement
- résoudre certains problèmes techniques plus rapidement
- synchroniser les développements backend et frontend

Ces moments ont permis d’améliorer la coordination et la cohérence globale du projet.

[⬆️ Retour au sommaire](#sommaire)

______________________________________________________________________

📌 _Ce README décrit l’état actuel du projet et pourra évoluer avec l’ajout de nouvelles fonctionnalités._
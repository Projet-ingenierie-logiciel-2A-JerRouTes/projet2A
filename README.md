# 📦 Projet : Logiciel de gestion et de recherche de recettes

Ce projet a pour objectif de développer un **logiciel de gestion de stock alimentaire et de recherche de recettes** permettant à des utilisateurs de retrouver des recettes à partir des ingrédients dont ils disposent, tout en gérant un stock personnel et des contraintes alimentaires.

Le projet est réalisé dans le cadre du **module de création logicielle** et suit une approche structurée :

- architecture MVD (Modèle – Vue – Données),
- séparation claire frontend / backend,
- bonnes pratiques de développement,
- qualité et maintenabilité du code,
- tests automatisés.

______________________________________________________________________

## 🎯 Objectifs du projet

- Permettre la recherche de recettes à partir d’ingrédients disponibles
- Gérer un stock d’ingrédients par utilisateur
- Proposer une application multi-utilisateur sécurisée
- Mettre en place une architecture claire et évolutive
- Respecter les conventions de développement (PEP 8, bonnes pratiques JavaScript)

______________________________________________________________________

## 🧩 Fonctionnalités

### En tant que administateur (après connection)
- Informations sur les utilisateurs
  - Voir tous les utilisateurs
  - Ajouter un admin ou un utilisateur 
  - Voir les informations d'un utilisateur en particulier
  - *A faire* : compléter les informations utilisateur (stock)
  - *A faire* : Modifier/supprimer un utilisateur
  
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
  - *A faire* : Modifier/supprimer un stock

- Informations sur les recettes
  - Voir toutes les recettes
  - Voir les informations d'une recette en particulier*
  - *A faire* : ajouter une recette
  - *A faire* : compléter les informations d'une recette étape
  - *A faire* : Modifier/supprimer une recette (ajouter boutons)

### En tant qu'utilisateur 

- Etape 1 : connection
- Etape 2 : visualisation des "stocks" disponibles avec leur contenu (menu déroulant)
  - Création d'un nouveau stock
  - Ajouter ingredient à stock (avec auto implémentation)
  - Vider stock
  - Supprimer stock
  - *A faire* : Modifier/Supprimer un lot
- Etape 3 : Recherche de recettes
  - Recherche de recette dans BDD plus API externe (spoonacular) si plus de endpoint possible recherche uniquement dans BDD
  - Affichage des recettes trouvée (entre 1 et 6 avec affichage dinamyque) si pas de recette trouvée (choisit aléatoirement 6 recettes dans BDD),
  Recette avec nom, photo (API externe Pixabay), temps de préparation et nombre de personne. Chaque vignette de recette est cliquable pour avoir plus de détail.
  - Affichage d'une recette : affichage avec scrolbar si besoin
  - Réalisation de recette (pour mise à jour du stock **Création en cours**), affichage de la quantité d'ingrédient nécessaire avec quantité qui s'adapte au nombre de personnes, vérification si présence dans le stock, bouton pour mettre à jour le stock (**non opérationnel**) 

### En tant qu'invité

- Affichage de 6 recettes aléatoires pris dans la base de données (clique sur recette possible pour afficher détail recette)
- Saisi d'ingrédient (sans quantité)
- Recherche à partir de la liste d'ingredient
- Affichage de recette adaptée a liste

______________________________________________________________________

## 🏗️ Architecture générale

L’application repose sur une architecture **MVD (Modèle – Vue – Données)** :

```
Interface utilisateur  <->  Métier  <->  Base de données
```

- **Interface utilisateur (Vue)** : interaction avec l’utilisateur via une application web (React)
- **Métier (Modèle)** : logique applicative, règles de gestion, authentification
- **Données** : persistance des utilisateurs, recettes, ingrédients et stocks

### 🗄️ Base de données

La base de données PostgreSQL gère les entités principales du projet :

- Utilisateurs
- Sessions (authentification JWT)
- Ingrédients
- Stocks
- Recettes
- Relations utilisateur / stock

📌 Diagramme de la base de données :\
![Diagramme](Documentation/Images/diagramme_bdd.drawio.png)

______________________________________________________________________

### 🖥️ BackEnd

Le backend est développé avec **FastAPI (Python)** et constitue le cœur métier de l’application.

Il gère :

- l’authentification sécurisée des utilisateurs (JWT),
- la logique métier,
- l’accès à la base PostgreSQL,
- la gestion des stocks et des ingrédients,
- l’exposition de l’API REST consommée par le frontend.

📘 Documentation détaillée :  
[README du backend](src/backend/README.md)

Le backend est totalement indépendant du frontend et peut être exécuté séparément.


______________________________________________________________________

### 🖥️ FrontEnd

Le frontend est développé avec **React** et **Vite**.

📘 Documentation détaillée :\
[README du frontend](src/frontend/README.md)

Fonctionnalités principales :

- Inscription et connexion des utilisateurs (JWT)
- Communication sécurisée avec l’API backend
- Gestion du stock et affichage des recettes

______________________________________________________________________

### 🖥️ Interface utilisateur

L’interface utilisateur permet :

- la création de comptes et la connexion des utilisateurs,
- la consultation et la gestion du stock personnel,
- la recherche de recettes en fonction des ingrédients disponibles.

Elle est conçue pour être :

- simple d’utilisation,
- réactive,
- évolutive.

______________________________________________________________________

### ⚙️ Modèle métier

Le modèle métier regroupe :

- les règles de gestion des utilisateurs,
- la logique d’authentification (JWT),
- la gestion des stocks et des ingrédients,
- les règles de recherche de recettes.

Il est implémenté côté backend avec **FastAPI** et suit une séparation claire entre :

- objets métiers,
- accès aux données (DAO),
- logique applicative (services).

______________________________________________________________________

## ⚙️ Lancement du projet

### Prérequis

- Node.js 20+
- npm
- Python 3.11+
- Docker & Docker Compose

### Avec les conteneurs

1. Etape 1 : Rendre le script exécutable

```bash
chmod +x start.sh
```

2. Etape 2 : Lancer le script

```bash
./start.sh
```

Le dashbaord est directement disponible dans votre navigateur

Explication des éléments de contenerisation

- [Contenerisation](Documentation/Infos_divers/contenerisation.md)

### Manuellement

#### 1️⃣ Lancer la base de données

```bash
sudo docker compose up -d
```

#### 2️⃣ Lancer le backend

```bash
uv run uvicorn api.main:app --reload
```

Backend accessible sur :\
👉 http://127.0.0.1:8000

#### 3️⃣ Lancer le frontend

```bash
cd src/frontend
npm install
npm run dev
```

Frontend accessible sur :\
👉 http://localhost:5173

______________________________________________________________________

## 🔐 Configuration (.env)

### Backend

Exemple de variables d’environnement :

```env
PYTHONPATH=src

POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DATABASE=projet2a
POSTGRES_DB=projet2a
POSTGRES_USER=projet_user
POSTGRES_PASSWORD=projet_pwd
POSTGRES_SCHEMA=projet_test_dao
```

### Frontend

Voir le fichier :

```bash
src/frontend/.env.local.template
```

______________________________________________________________________

## 🧪 Qualité et outils

- Tests automatisés backend avec **pytest**
- Linting et formatage via **pre-commit**
- Workflows CI pour les tests

📎 Ressources :

- [Guide pre-commit](Documentation/Infos_divers/pour_pre_commit.md)
- [Workflows de tests](Documentation/Infos_divers/worklows.md)

______________________________________________________________________

## 📅 Compte-rendus de réunions

- Vendredi 23 janvier : [Réunion 1](Documentation/reunion_construction/reunion1_23_01.md)
- Vendredi 30 janvier : [Réunion 2](Documentation/reunion_construction/reunion2_30_01.md)
- Vendredi 1 février : lien perdu

______________________________________________________________________

## Backlog

- [Divers](Backlog/BacklogDivers.md)
- [Résolution de problème](Backlog/BacklogProbleme.md)
- [API](Backlog/BacklogApi.md)
- [Architecture & Cohérence des Données](Backlog/BacklogArchi.md)
- [FrontEnd](Backlog/BacklogFront.md)
- [BackEnd](Backlog/BacklogBack.md)
- [DAO](Backlog/BacklogDAO.md)

______________________________________________________________________

📌 _Ce README décrit l’état actuel du projet et pourra évoluer avec l’ajout de nouvelles fonctionnalités._

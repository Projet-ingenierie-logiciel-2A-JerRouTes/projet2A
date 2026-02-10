# 📦 Projet : Logiciel de gestion et de recherche de recettes

Ce projet a pour objectif de développer un logiciel de gestion et de recherche de recettes permettant à des utilisateurs de retrouver des recettes à partir des ingrédients dont ils disposent, tout en gérant un stock personnel et des contraintes alimentaires.

Le projet est réalisé dans le cadre du module de création logicielle et suit une approche structurée (architecture MVD, bonnes pratiques de développement, qualité du code).

______________________________________________________________________

## 🎯 Objectifs du projet

- Permettre la recherche de recettes à partir d’ingrédients disponibles
- Gérer un stock d’ingrédients par utilisateur
- Proposer une application multi-utilisateur
- Mettre en place une architecture claire et évolutive
- Respecter les conventions de développement Python (PEP 8)

______________________________________________________________________

## 🧩 Fonctionnalités

- Fonctionnalités de base (Niveau 1)
  - Ajout de recettes par utilisateur
  - Ajout et gestion des ingrédients
  - Recherche de recettes dont tous les ingrédients sont disponibles
  - Gestion multi-utilisateur
- Fonctionnalités avancées (Niveau 2)
  - Recherche de recettes avec :
    - Ajout dynamique d’ingrédients disponibles
    - Restrictions (ingrédients exclus, calories, origine des recettes…)
  - Gestion automatique du stock
  - Ajout d’ingrédients via ticket de caisse

______________________________________________________________________

## 🏗️ Architecture générale

L’application repose sur une architecture MVD (Modèle – Vue – Données) :

Interface utilisateur \<-> Métier \<-> Base de données

- **Interface utilisateur** : interaction avec l’utilisateur
- **Métier** : logique applicative et règles de gestion
- **Base de données** : stockage des utilisateurs, recettes, ingrédients et stocks

### 🗄️ Base de données

La base de données gère les entités principales du projet :

- Utilisateurs
- Ingrédients
- Stocks
- Recettes
- Relations utilisateur / stock

📌 Diagramme de la base de données :
![Diagramme](Documentation/Images/diagramme_bdd.drawio.png)

______________________________________________________________________

### 🖥️ FrontEnd

[README du frontend](https://github.com/Projet-ingenierie-logiciel-2A-JerRouTes/projet2A/blob/christelle_frontend/src/frontend/README.md)

______________________________________________________________________

### 🖥️ Interface utilisateur

______________________________________________________________________

### ⚙️ Modèle métier

______________________________________________________________________

## Informations techniques utiles

- Pour le linting et le formatage automatique avant chaque commit:
  [Guide pre-commit](Documentation/Infos_divers/pour_pre_commit.md)
- Creation d'un workflows de test en cas de modification :
  [Workflows test](Documentation/Infos_divers/worklows.md)

## Compte-rendu réunion

- Vendredi 23 janvier [Réunion 1](Documentation/reunion_construction/reunion1_23_01.md)
- Vendredi 30 janvier [Réunion 2](Documentation/reunion_construction/reunion2_30_01.md)


## Elements du .env

PYTHONPATH=src

POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_DATABASE=
POSTGRES_USER=
POSTGRES_PASSWORD=

POSTGRES_SCHEMA=projet_test_dao

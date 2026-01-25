# Réunion 1 - Vendredi 23 janvier

______________________________________________________________________

## Description et questions

### 🎯 Actions utilisateur

#### 🔹 Niveau 1 (fonctionnalités de base)

- Ajouter des recettes par utilisateur
- Ajouter des ingrédients
- Rechercher des recettes avec **ingrédients totalement présents**
- Gestion **multi-utilisateur**

#### 🔹 Niveau 2 (fonctionnalités avancées)

- Recherche de recettes avec :
  - Ajout d’ingrédients disponibles
  - Restrictions (ingrédients, calories, origine des recettes…)
- Gestion de stock (mise à jour automatique)
- Ajout d’ingrédients via **ticket de caisse**

______________________________________________________________________

### ❓ Questions techniques

- Comment alimenter la BDD recettes ?
  - Web scraping
  - API externe
- Repérage de recettes similaires
- Méthode de recherche de recettes

### 📐 Conventions de développement

- Respect de **PEP 8**
- Nommage :
  - Variables / fonctions / classes **en anglais**

______________________________________________________________________

## 🏗️ Architecture générale (MVD)

Interface utilisateur \<-> Métier \<-> BDD

______________________________________________________________________

### 🖥️ Interface Utilisateur

#### 🔐 Écran 1 : Connexion

- Accès sans connexion
- Se connecter
- Créer un compte
- Connexion administrateur

#### 🧾 Écran 2a : Sans connexion

- Saisie des ingrédients + quantités
- Recherche de recettes

#### 👤 Écran 2b : Avec connexion (profil utilisateur)

- Ajout d’ingrédients
- Ajout de recettes
- Recherche de recettes à partir des ingrédients en stock

______________________________________________________________________

### ⚙️ Métier (Modèle objet)

#### 👤 Utilisateur

- `pseudo` (unique)
- `password`
- Classe abstraite :
  - `Admin`
  - `GenericUser`

#### 🧂 Ingredient

- `name`
- `unit`
- `tags`
- Classe simple

#### 🍲 Recette

- `name`
- Liste d’ingrédients + quantités
- Catégories
- Classe simple

#### 🔍 Outils de recherche

- Recherche par stock
- Nombre de personnes
- Classe abstraite :
  - Type de méthode (`BDD`, `API`, etc.)

##### 📦 Stock

- Nom
- Liste d’ingrédients + quantités
- Classe simple

______________________________________________________________________

### Base de données

#### Utilisateur

- `id_user` (PK)
- `pseudo` (unique)
- `password`
- `id_stock`

#### Liste des ingrédients

- `id` (PK)
- `name`
- `unit`
- `tags`

#### Stock

- `id_stock` (PK)
- Objet stock

#### Relation stock / utilisateur

- `id_stock` (FK)
- `id_user` (FK)

#### Recette

- `id` (PK)
- `creator`
- `status`
- Objet recette

## 👥 Répartition des tâches (pour vendredi)

- **Khalid**

  - Schémas BDD
  - Métier → `Recette`

- **Maxime**

  - Métier → `OutilsRecherche`
  - Métier → `Ingredient`

- **Christelle**

  - Métier → `Utilisateur`
  - Métier → `Stock`

______________________________________________________________________

## 📅 Prochain point

📍 **30/01**

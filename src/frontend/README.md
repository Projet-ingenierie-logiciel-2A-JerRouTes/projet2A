## 🎨 Frontend – Application Frigo

Cette partie du projet contient l’interface utilisateur développée avec **React** et **Vite**.\
Elle permet l’interaction avec l’API backend (FastAPI) pour l’authentification des utilisateurs et la gestion des données.

______________________________________________________________________

## 🚀 Installation

Pour lancer le projet localement, suivez ces étapes :

### 1. Prérequis

Assurez-vous d’avoir installé :

- **Node.js** (version 20+ recommandée)
- **npm** (installé automatiquement avec Node)

Le backend doit également être lancé (par défaut sur `http://127.0.0.1:8000`).

______________________________________________________________________

### 2. Configuration de l’environnement

Ouvrez un terminal à la racine du projet, puis placez-vous dans le dossier frontend :

```bash
cd src/frontend
```

Copiez le template de configuration et adaptez-le si nécessaire :

```bash
cp .env.local.template .env.local
```

Dans le fichier `.env.local`, définissez l’URL de l’API backend :

```env
VITE_API_URL=http://127.0.0.1:8000
```

______________________________________________________________________

### 3. Installation des dépendances

Installez les bibliothèques nécessaires listées dans le `package.json` :

```bash
npm install
```

______________________________________________________________________

### 4. Lancement de l’application

Démarrez le serveur de développement :

```bash
npm run dev
```

L’application sera accessible (par défaut) à l’adresse :\
👉 **http://localhost:5173**

______________________________________________________________________

## 🔌 Documentation de l'API (Endpoints)

L'interface de programmation (API) est développée avec **FastAPI**. Elle suit les standards REST pour assurer une communication fluide entre le client React et la base de données métier. La documentation interactive complète est accessible via le Swagger UI à l'adresse : `http://localhost:8000/docs`.

### 🛠️ Endpoints Administrateur (Visualisation Globale)

Ces points d'accès permettent de monitorer l'état des données en temps réel durant le développement.

| Méthode | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/admin/users` | Récupère la liste complète des utilisateurs inscrits (ID, pseudo, rôle). |
| `GET` | `/admin/stocks` | Retourne le dictionnaire de tous les stocks existants pour vérifier l'intégrité des données. |

### 🔐 Authentification & Utilisateurs

Ce module gère la sécurité et les profils utilisateurs.

| Méthode | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/login` | Authentifie un utilisateur. **Requête** : `pseudo`, `password`. **Réponse** : Infos profil + `id_stock`. |
| `POST` | `/register` | Enregistre un nouvel utilisateur. Vérifie la disponibilité du pseudo et la concordance des mots de passe. |

### 📦 Gestion du Stock & Référentiel

Ce module permet la manipulation des ingrédients et la consultation des inventaires.

| Méthode | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/ingredients` | Récupère le catalogue global (IDs, noms, unités par défaut) utilisé pour l'autocomplétion. |
| `GET` | `/stock/{id}` | Récupère le contenu d'un frigo spécifique, trié par ingrédient. |

______________________________________________________________________

## 🛠 Détails Techniques

### Validation des données (Modèles Pydantic)

L'API utilise des modèles de données rigoureux pour valider les entrées (DTO - Data Transfer Objects). Cela garantit l'intégrité du système avant tout traitement métier :

- **`LoginRequest`** : Assure la présence des identifiants nécessaires.
- **`RegisterRequest`** : Gère la logique de création de compte avec double validation de mot de passe.

### Gestion des Erreurs et Codes HTTP

Chaque réponse utilise les codes d'état HTTP standards pour informer le frontend du résultat de l'opération :

- **`200 OK`** : Succès de la requête.
- **`201 Created`** : Création de compte réussie.
- **`400 Bad Request`** : Erreur client (ex: mots de passe non identiques).
- **`401 Unauthorized`** : Échec d'authentification (mot de passe erroné).
- **`404 Not Found`** : Ressource inexistante (Utilisateur ou Stock non trouvé).

______________________________________________________________________

## 🌐 Configuration CORS

Pour permettre au frontend (déployé sur le port `5173`) de communiquer avec le backend (port `8000`), un middleware **CORSMiddleware** est configuré pour autoriser les requêtes provenant de `http://localhost:5173`.

______________________________________________________________________

### 🛠 Composants techniques

#### 🔐 Authentification et Accès

L’authentification repose sur une API sécurisée (JWT) exposée par le backend.

##### `Login.jsx`

- Gère la connexion des utilisateurs existants.
- Endpoints utilisés :
  - `POST /api/auth/login`
  - `GET /api/users/me`
- Fonctionnement :
  - Envoi des identifiants (pseudo **ou** email + mot de passe).
  - Stockage automatique du token JWT côté navigateur.
  - Récupération du profil utilisateur via `/me`.
- Codes erreurs gérés :
  - **404** : Utilisateur inconnu.
  - **401** : Mot de passe incorrect.
  - **422** : Données invalides.
  - Erreur réseau : serveur injoignable.

##### `CreationCompte.jsx`

- Permet l’inscription de nouveaux utilisateurs.
- Endpoint utilisé :
  - `POST /api/auth/register`
- Fonctionnement :
  - Validation côté front (confirmation du mot de passe).
  - Envoi des données : `username`, `email`, `password`.
- Codes erreurs gérés :
  - **409** : Email déjà utilisé.
  - **422** : Champs invalides.
  - Message `detail` renvoyé par l’API backend.

Les tokens JWT sont stockés via `localStorage` et ajoutés automatiquement aux requêtes protégées.

______________________________________________________________________

#### 📦 Gestion de l’Inventaire Intelligent

La gestion du stock repose sur une synchronisation entre le catalogue global des ingrédients et le stock spécifique de l’utilisateur.

##### `Stock.jsx` (le composant « Cerveau »)

Conteneur principal de l’inventaire.

- États complexes :
  - `items` : objet indexé par `id_ingredient`, contenant des listes de lots (quantité + date).
  - `catalogue` : référentiel complet des ingrédients autorisés.
- Endpoints utilisés :
  - `GET /ingredients` : chargement du catalogue au montage.
  - `GET /stock/{id_stock}` : récupération des lots de l’utilisateur.
- Logique d’affichage :
  - Réalise une “jointure” côté client entre les IDs du stock et les noms/unités du catalogue via la fonction `getIngredientInfo`.

##### `AddIngredientForm.jsx` (Saisie Assistée)

- Formulaire avancé facilitant l’ajout de produits.
- Recherche prédictive :
  - Filtrage dynamique du catalogue à chaque saisie.
- Gestion des unités (synchronisation Python) :
  - Utilise un dictionnaire `unitLabels` pour convertir les enums Python (`GRAM`, `LITER`, `PIECE`) en symboles UI (`g`, `L`, `pcs`).
- Mode saisie libre :
  - Si un ingrédient n’est pas présent dans le catalogue :
    - affichage d’un menu déroulant pour choisir l’unité,
    - envoi de `id_ingredient: null` au parent, déclenchant la création côté serveur.

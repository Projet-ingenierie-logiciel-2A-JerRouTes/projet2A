## 🎨 Frontend – Application Frigo

Cette partie du projet contient l’interface utilisateur développée avec **React** et **Vite**.  
Elle permet l’interaction avec l’API backend (FastAPI) pour l’authentification des utilisateurs et la gestion des données.

---

### 🚀 Installation

Pour lancer le projet localement, suivez ces étapes :

#### 1. Prérequis
Assurez-vous d’avoir installé :

- **Node.js** (version 20+ recommandée)
- **npm** (installé automatiquement avec Node)

Le backend doit également être lancé (par défaut sur `http://127.0.0.1:8000`).

---

#### 2. Configuration de l’environnement

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

---

#### 3. Installation des dépendances

Installez les bibliothèques nécessaires listées dans le `package.json` :

```bash
npm install
```

---

#### 4. Lancement de l’application

Démarrez le serveur de développement :

```bash
npm run dev
```

L’application sera accessible (par défaut) à l’adresse :  
👉 **http://localhost:5173**

---

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

---

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
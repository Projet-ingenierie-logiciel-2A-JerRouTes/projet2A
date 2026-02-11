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

### Structure

L'API est structurée autour de quatre grands modules. Elle utilise des **Data Transfer Objects (DTO)** via Pydantic pour garantir la validité des échanges entre le frontend React et le backend Python.

#### 🛠️ 1. Initialisation

Vérification de l'état de santé de l'application et des données.

| Méthode | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Vérifie si l'API est en ligne et si les données initiales (`seed_data`) sont chargées. |

______________________________________________________________________

#### 👥 2. Utilisateurs & Authentification

Gestion des accès et des profils.

| Méthode | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/users` | Liste tous les utilisateurs (IDs, pseudos, rôles). |
| `POST` | `/login` | Authentifie un utilisateur. Renvoie le profil et l'`id_stock` associé. |
| `POST` | `/register` | Crée un compte. Vérifie la disponibilité du pseudo et la validité du mot de passe. |

______________________________________________________________________

#### 🍎 3. Référentiel Ingrédients

Gestion du catalogue global (utilisé pour l'autocomplétion dans le formulaire d'ajout).

| Méthode | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/ingredients` | Récupère la liste de tous les ingrédients connus (ID, nom, unité). |
| `POST` | `/ingredients` | **Ajout au catalogue** : Crée un nouvel ingrédient. Utilise la classe métier `Ingredient` pour valider les données. |

______________________________________________________________________

#### 📦 4. Référentiel Stock

Consultation des inventaires (frigos) des utilisateurs.

| Méthode | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/stocks` | (Admin) Affiche le dictionnaire complet de tous les stocks du serveur. |
| `GET` | `/stock/{id_stock}` | Récupère le contenu détaillé (quantités, dates d'expiration) d'un stock spécifique. |

______________________________________________________________________

### 🛠️ Spécifications Techniques

#### Validation des données (DTO)

L'API rejette automatiquement les requêtes malformées grâce aux modèles suivants :

- **`LoginRequest`** : Requiert `pseudo` et `password`.
- **`RegisterRequest`** : Requiert `pseudo`, `password` et `confirm_password`.
- **`IngredientRequest`** : Requiert `name` (non vide) et `unit` (doit être une valeur valide de l'énumération `Unit`).

#### Codes d'état HTTP utilisés

- **200 OK** : Succès de la requête.
- **201 Created** : Ressource créée avec succès.
- **400 Bad Request** : Erreur de logique (ex: l'ingrédient existe déjà, mots de passe différents).
- **401 Unauthorized** : Identifiants de connexion incorrects.
- **404 Not Found** : La ressource (utilisateur ou stock) n'existe pas.
- **422 Unprocessable Entity** : Format de donnée invalide (ex: unité de mesure inconnue).

______________________________________________________________________

## 🔌 Structure REACT

### 🔐 Orchestrateur : Composant `App.jsx`

#### 📋 Variables d'État (Global States)

Le pilotage de l'interface repose sur trois états piliers définis dans `App.jsx` :

- **`user`** (Object|null) : Stocke les informations de l'utilisateur connecté (ID, pseudo, id_stock). Sert de témoin d'authentification pour les composants enfants.
- **`is_registering`** (Boolean) : Détermine quel formulaire afficher dans la phase d'accès (Connexion vs Création de compte).
- **`show_stock`** (Boolean) : Déclencheur principal de l'affichage de l'inventaire. S'il est à `true`, les formulaires d'accès sont démontés au profit du composant `Stock`.

______________________________________________________________________

#### 🔄 Cheminement et Flux de l'Application

Le cycle de vie d'une session suit ce cheminement logique :

1. **Phase d'Entrée** : Par défaut, l'application présente le composant `Login`.
   - *Action* : Si l'utilisateur clique sur "Créer un compte", `is_registering` passe à `true` et affiche `CreationCompte`.
1. **Phase d'Authentification** :
   - Le composant enfant (`Login` ou `CreationCompte`) communique avec l'API FastAPI.
   - En cas de succès, les données utilisateur sont "remontées" à `App.jsx` via le callback `handleLogin`.
1. **Phase d'Affichage** :
   - `setUser(data)` enregistre l'identité en mémoire.
   - `setShowStock(true)` bascule l'affichage.
1. **Phase d'Inventaire** :
   - Le composant `Stock` est monté et reçoit la prop `user`.
   - Il utilise l'ID contenu dans `user.id_stock` pour effectuer ses propres appels API et afficher les ingrédients correspondants.

### 🔐 Authentification : Composant `Login.jsx`

Ce composant gère l'accès sécurisé à l'application. Il utilise une authentification basée sur **JWT (JSON Web Token)** pour identifier l'utilisateur et récupérer ses informations personnelles.

#### 📋 Variables d'État (React States)

Le formulaire utilise le `useState` pour piloter l'interface en temps réel :

- **`pseudo`** : Stocke l'identifiant saisi (peut être le pseudo ou l'email).
- **`password`** : Stocke le mot de passe de manière sécurisée (champ masqué).
- **`error_message`** : Gère l'affichage dynamique des alertes en cas d'échec de connexion.

#### 🌐 Points d'entrée API (Endpoints)

La procédure de connexion se déroule en deux étapes asynchrones :

1. **`POST /login`** : Envoie les identifiants au backend. Si le couple login/password est valide, un token de session est généré.
1. **`GET /me`** : Une fois authentifié, cet appel récupère les détails de l'utilisateur courant (nom, rôle, id_stock) pour initialiser l'application.

### 🔄 Cheminement

1. **Soumission** : Blocage du rechargement (`e.preventDefault()`).
1. **Authentification** : Appel à `login()`. Si succès, le token est stocké par le service.
1. **Identification** : Appel immédiat à `me()` pour récupérer l'identité complète.
1. **Remontée** : Transmission des données à `App.jsx` via le callback `onLogin(data)`.

#### 🛠️ Logique de Gestion des Erreurs

Le composant interprète les codes de réponse HTTP du serveur pour fournir un feedback précis à l'utilisateur :

| Code HTTP | Message affiché | Cause possible |
| :--- | :--- | :--- |
| `401` | "Mot de passe incorrect" | Le pseudo existe mais le secret ne correspond pas. |
| `404` | "Utilisateur inconnu" | Le pseudo ou l'email n'existe pas en base de données. |
| `422` | "Champs invalides" | Format de données incorrect (ex: champ vide). |
| `Autre` | "Erreur de connexion" | Serveur injoignable ou erreur interne. |

______________________________________________________________________

#### 💡 Informations Utiles

- **Accessibilité Invité** : Le bouton "Chercher des recettes sans compte" permet d'accéder aux fonctionnalités de consultation (`onGuestAccess`) sans passer par la phase d'authentification.
- **Flux de données** : En cas de succès, l'objet utilisateur complet est "remonté" au composant parent `App.jsx` via la prop `onLogin(data)`, ce qui déclenche l'affichage du stock personnel.
- **Sécurité** : La méthode `e.preventDefault()` est utilisée pour éviter le rechargement de la page, permettant une expérience "Single Page Application" (SPA) fluide.

### 📝 Inscription : Composant `CreationCompte.jsx`

Ce composant permet aux nouveaux utilisateurs de rejoindre la plateforme en créant un profil unique. Il intègre des validations de sécurité côté client et côté serveur.

#### 📋 Variables d'État (React States)

Le composant utilise les hooks `useState` pour capturer les informations et gérer l'interface après succès :

- **Données de saisie** : `pseudo`, `email`, `password`, `confirm_password`.
- **États de flux** :
  - **`isRegistered`** : Un booléen qui bascule sur `true` après le succès de l'API, remplaçant le formulaire par un bouton d'accès direct au stock.
  - **`message` / `error_message`** : Feedback visuel pour confirmer la réussite ou expliquer l'échec.

#### 🌐 Points d'entrée API (Endpoints)

L'inscription repose sur un appel asynchrone principal :

- **`POST /register`** : Envoie un objet JSON contenant le `username`, l' `email` et le `password`.
  - *Note technique* : Le backend se charge de hacher le mot de passe avant le stockage en base de données.

### 🔄 Cheminement

1. **Validation Locale** : Vérification stricte de la concordance des deux mots de passe.
1. **Requête** : Envoi des données au backend.
1. **Success State** : Si `201 Created`, `isRegistered` passe à `true`.
1. **Finalisation** : Le formulaire disparaît pour laisser place au bouton "Construire mon stock".

#### 🛠️ Logique de gestion des Erreurs

Le composant traite les codes HTTP spécifiques renvoyés par FastAPI :

| Code HTTP | Message affiché | Cause |
| :--- | :--- | :--- |
| `409` | "Email déjà utilisé" | L'adresse mail existe déjà dans le système. |
| `400` | "Erreur lors de l'inscription" | Problème de logique métier ou pseudo déjà pris. |
| `422` | "Champs invalides" | Format invalide (ex: email mal formé). |

______________________________________________________________________

#### 💡 Informations Utiles

- **UX (Expérience Utilisateur)** : Une fois le compte créé, le formulaire disparaît pour laisser place à un bouton "Construire mon stock", guidant l'utilisateur vers la prochaine étape logique de l'application.
- **Navigation** : La prop `onBack` permet une navigation fluide vers la page de connexion sans rechargement de page.
- **Sécurité** : L'utilisation de types `password` pour les inputs garantit que les caractères saisis ne sont pas visibles à l'écran.

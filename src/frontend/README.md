## 🎨 Frontend - Application Frigo

Cette partie du projet contient l'interface utilisateur développée avec React et Vite. Elle permet de visualiser les données.

### 🚀 Installation
Pour lancer le projet localement, suivez ces étapes :

1. Prérequis
Assurez-vous d'avoir installé :

Node.js (Version 20+ recommandée)

npm (installé automatiquement avec Node)

2. Configuration de l'environnement
Ouvrez votre terminal dans le dossier du projet et déplacez-vous dans le répertoire frontend :

```
cd src/frontend
```

3. Installation des dépendances
Installez les bibliothèques nécessaires listées dans le package.json :

```
npm install
```

4. Lancement de l'application
Démarrez le serveur de développement :

```
npm run dev
```

### 🛠 Composant technique

#### 🔐 Authentification et Accès
```Login.jsx```
- Gère l'entrée des utilisateurs existants.
- Endpoints utilisés : POST /login
- **Dans le main** : Verification si user existe et si mdp bon
- Codes erreurs gérés :
   - 404 : Utilisateur inconnu.
   - 401 : Mot de passe incorrect.
   - TypeError : Serveur injoignable.

```CreationCompte.jsx```
- Permet l'enregistrement de nouveaux profils.
- Endpoints utilisés : POST /register
- **Dans le main** : Validation de la correspondance des mots de passe, et de l'existant des user déjà existant
- Codes erreurs gérés : Récupération du message detail envoyé par FastAPI (ex: pseudo déjà utilisé).

#### 📦 Gestion de l'Inventaire Intelligent
La gestion du stock repose sur une synchronisation constante entre le catalogue global des ingrédients et le stock spécifique de l'utilisateur.

```Stock.jsx``` (Le composant "Cerveau")
C'est le conteneur principal de l'inventaire.

- États complexes :
   - items : Objet indexé par id_ingredient contenant des listes de lots (quantité + date).
   - catalogue : Référentiel complet des ingrédients autorisés.
- Endpoints utilisés :
   - GET /ingredients : Chargement du catalogue au montage.
   - GET /stock/{id_stock} : Récupération des lots de l'utilisateur.
- Logique d'affichage : Réalise une "jointure" côté client entre les IDs du stock et les noms/unités du catalogue via la fonction getIngredientInfo.

```AddIngredientForm.jsx``` (Saisie Assistée)
- Formulaire avancé facilitant l'ajout de produits.
- Recherche prédictive : Filtrage dynamique du catalogue à chaque saisie.
- Gestion des Unités (Sync Python) : Utilise un dictionnaire unitLabels pour convertir les Enums Python (GRAM, LITER, PIECE) en symboles UI (g, L, pcs).
- Mode Saisie Libre : Si un ingrédient n'est pas dans le catalogue, le composant :
- Affiche un menu déroulant pour choisir l'unité manuellement.
- Envoie id_ingredient: null au parent, déclenchant la création d'un nouvel ingrédient côté serveur.

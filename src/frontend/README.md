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

L'accès à l'application est protégé par un écran de connexion (`Login.jsx`) qui gère la transition vers l'interface principale :

- **Rendu Conditionnel** : L'application utilise un état `user` (initialisé à `null`). Tant que cet état n'est pas rempli, seul le formulaire de connexion est injecté dans le DOM.
- **Communication Inter-Composants** : Le composant `Login` communique avec le parent `App` via une fonction de rappel (*callback*) `onLogin`.
- **Persistance de session (UX)** : Une fois le pseudo validé, l'interface bascule dynamiquement pour afficher l'inventaire et un bouton de déconnexion permettant de réinitialiser l'état à `null`.

#### Gestion de l'Inventaire

Le composant `InventaireFrigo` utilise les concepts fondamentaux de React pour gérer les données en temps réel :

1. **États Locaux (`useState`)** :
   - `stock` : Un tableau d'objets stockant l'intégralité des produits.
   - `ingredient` / `quantite` : États synchronisés avec les champs de saisie (Two-way data binding).

2. **Logique d'Immuabilité** :
   - Pour l'ajout, nous utilisons le *Spread Operator* : `setStock([...stock, nouvelArticle])`.
   - Pour la suppression, nous utilisons la méthode `.filter()`.

3. **Rendu Dynamique** :
   - Utilisation de `.map()` pour transformer le tableau JavaScript en lignes de tableau HTML (`<tr>`).
   - Chaque ligne possède une `key` unique (générée par `Date.now()`) pour optimiser les performances de rendu de React.

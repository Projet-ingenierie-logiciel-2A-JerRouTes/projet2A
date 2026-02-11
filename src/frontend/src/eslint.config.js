// 1. IMPORTATION DES PLUGINS ET OUTILS
import js from "@eslint/js"; // Importe les règles recommandées par défaut pour JavaScript
import reactPlugin from "eslint-plugin-react"; // Importe les fonctionnalités spécifiques à l'analyse de React
import globals from "globals"; // Bibliothèque pour reconnaître les variables globales (window, document, etc.)

export default [
  // 2. CONFIGURATION DE BASE
  js.configs.recommended, // Active les règles de base (ex: éviter les boucles infinies, variables non définies)

  {
    // 3. CIBLAGE DES FICHIERS
    // Indique que ces règles s'appliquent à tous les fichiers JS, JSX et TypeScript
    files: ["**/*.{js,jsx,ts,tsx}"],

    // 4. ACTIVATION DU PLUGIN REACT
    plugins: {
      react: reactPlugin,
    },

    // 5. OPTIONS DE LANGAGE ET ENVIRONNEMENT
    languageOptions: {
      parserOptions: {
        ecmaFeatures: {
          jsx: true, // Autorise le linter à lire la syntaxe JSX (HTML dans le JS)
        },
      },
      globals: {
        // Ajoute les variables globales du navigateur (ex: localStorage, fetch)
        // pour que ESLint ne dise pas qu'elles sont "non définies"
        ...globals.browser,
      },
    },

    // 6. DÉFINITION DES RÈGLES
    rules: {
      // Désactive l'obligation d'importer 'React' en haut de chaque fichier.
      // Indispensable pour React 17, 18 et 19 qui gèrent cela automatiquement.
      "react/react-in-jsx-scope": "off",

      // Signale les variables créées mais jamais utilisées (ex: un import oublié).
      // Mis en "warn" pour ne pas bloquer le build mais alerter le développeur.
      "no-unused-vars": "warn",

      // Force le linter à considérer que 'React' est utilisé s'il y a du JSX.
      // (Sécurité supplémentaire pour la compatibilité).
      "react/jsx-uses-react": "error",

      // Empêche ESLint de marquer tes composants (comme <Login /> ou <Stock />)
      // comme "inutilisés" s'ils ne sont présents que dans ton code JSX.
      "react/jsx-uses-vars": "error",
    },
  },
];

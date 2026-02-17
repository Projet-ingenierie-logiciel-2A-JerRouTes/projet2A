# Image de base légère recommandée par le cours pour Node.js
FROM node:20-alpine

# Définition du répertoire de travail à l'intérieur du conteneur
WORKDIR /app

# Copie des fichiers de dépendances (optimisation du cache des layers Docker)
# On copie package.json ET package-lock.json s'il existe
COPY package*.json ./

# Installation des dépendances (incluant lucide-react et axios déjà présents)
RUN npm install

# Copie du reste du code source du frontend
COPY . .

# Exposition du port par défaut utilisé par Vite
EXPOSE 5173

# Commande pour lancer Vite en mode développement
# Le flag --host est INDISPENSABLE pour que le conteneur accepte les connexions externes
CMD ["npm", "run", "dev", "--", "--host"]
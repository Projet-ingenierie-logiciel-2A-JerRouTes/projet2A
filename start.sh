#!/bin/bash

echo "🚀 Démarrage du projet2A..."

# 1. Lancement des conteneurs
sudo docker compose up -d

echo "⏳ Attente de la base de données..."
until [ "$(sudo docker inspect -f '{{.State.Health.Status}}' projet2a_postgres)" == "healthy" ]; do
    sleep 2
done

# 2. Vérification et Initialisation de la BDD
# On vérifie si la table 'users' existe dans le schéma 'projet_test_dao'
TABLE_EXISTS=$(sudo docker exec projet2a_postgres psql -U projet_user -d projet2a -tAc "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'projet_test_dao' AND table_name = 'users');")

if [ "$TABLE_EXISTS" = "f" ]; then
    echo "📦 Initialisation de la base de données (Schéma + Data)..."
    
    # Exécution de l'ordre logique des fichiers
    sudo docker exec -i projet2a_postgres psql -U projet_user -d projet2a < ./data/init_db.sql
    sudo docker exec -i projet2a_postgres psql -U projet_user -d projet2a < ./data/pop_db.sql
    
    echo "✅ Base de données initialisée avec succès."
else
    echo "ℹ️ La base de données est déjà présente. Saut de l'initialisation."
fi

# 3. Ouverture des interfaces
xdg-open http://localhost:5173 2>/dev/null || echo "👉 Frontend : http://localhost:5173"
xdg-open http://localhost:8000 2>/dev/null || echo "👉 API Docs : http://localhost:8000"


#!/bin/bash

echo "🚀 Démarrage du projet2A..."

# 1. Lancement des conteneurs en arrière-plan
sudo docker compose up -d

echo "⏳ Attente de l'initialisation de la base de données..."
# On attend que le service db soit 'healthy' (défini dans ton docker-compose)
while [ "$(sudo docker inspect -f '{{.State.Health.Status}}' projet2a_postgres)" != "healthy" ]; do
    sleep 2
done

echo "✅ Base de données prête !"
echo "🌐 Ouverture des interfaces..."

# 2. Ouverture automatique du dashboar
xdg-open http://localhost:8000 2>/dev/null || open http://localhost:8000
#!/bin/bash
set -e

echo "🚀 Démarrage du projet2A (DB Docker + Backend/Frontend locaux)..."

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/src/backend"
FRONTEND_DIR="$ROOT_DIR/src/frontend"

# ---------------------------------------------------------------------
# 0) Charger le .env du backend uniquement (backend indépendant)
# ---------------------------------------------------------------------
load_env_file() {
  local env_file="$1"
  if [ -f "$env_file" ]; then
    echo "🔧 Chargement de $env_file"
    set -a
    # shellcheck disable=SC1090
    source "$env_file"
    set +a
  fi
}

load_env_file "$BACKEND_DIR/.env"

# ---------------------------------------------------------------------
# 1) Variables DB
# ---------------------------------------------------------------------
POSTGRES_USER="${POSTGRES_USER:-projet_user}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-projet_pwd}"

# Compat POSTGRES_DB / POSTGRES_DATABASE
if [ -n "${POSTGRES_DB:-}" ]; then
  POSTGRES_DB="$POSTGRES_DB"
else
  POSTGRES_DB="${POSTGRES_DATABASE:-projet2a}"
fi

POSTGRES_SCHEMA="${POSTGRES_SCHEMA:-projet_dao}"

DB_CONTAINER="projet2a_postgres"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

python "$BACKEND_DIR/utils/reset_database.py"
#INIT_SQL="$BACKEND_DIR/data/init_db.sql"
#POP_SQL="$BACKEND_DIR/data/pop_db_test.sql"

# ---------------------------------------------------------------------
# 2) Lancement DB Docker
# ---------------------------------------------------------------------
echo "🐳 Lancement de la base de données (Docker)..."

if sudo docker compose config --services | grep -qx "db"; then
  sudo docker compose up -d db
elif sudo docker compose config --services | grep -qx "postgres"; then
  sudo docker compose up -d postgres
else
  echo "❌ Aucun service 'db' ou 'postgres' trouvé dans docker-compose."
  exit 1
fi

echo "⏳ Attente de la base de données..."
until [ "$(sudo docker inspect -f '{{.State.Health.Status}}' "$DB_CONTAINER" 2>/dev/null)" == "healthy" ]; do
  sleep 2
done
echo "✅ Base de données OK (healthy)."


# ---------------------------------------------------------------------
# 3) Réinitialisation via Python
# ---------------------------------------------------------------------
echo "📦 Réinitialisation de la base via reset_database.py..."

cd "$BACKEND_DIR"
uv run python utils/reset_database.py
cd "$ROOT_DIR" >/dev/null

echo "✅ Base prête."


# ---------------------------------------------------------------------
# 3) Initialisation DB si nécessaire
# ---------------------------------------------------------------------
echo "🔎 Vérification de l'initialisation du schéma '$POSTGRES_SCHEMA'..."

TABLE_EXISTS=$(sudo docker exec "$DB_CONTAINER" \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc \
  "SELECT EXISTS (
      SELECT FROM information_schema.tables
      WHERE table_schema = '$POSTGRES_SCHEMA'
      AND table_name = 'users'
  );")

if [ "$TABLE_EXISTS" = "f" ]; then
  echo "📦 Initialisation de la base de données (Schéma + Data)..."

  # 0) Créer le schéma cible si nécessaire
  sudo docker exec -i "$DB_CONTAINER" \
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 \
    -c "CREATE SCHEMA IF NOT EXISTS $POSTGRES_SCHEMA;"

  # 1) Exécuter init_db.sql dans le schéma cible
  sudo docker exec -i -e PGOPTIONS="-c search_path=$POSTGRES_SCHEMA,public" "$DB_CONTAINER" \
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 \
    < "$INIT_SQL"

  # 2) Exécuter pop_db.sql dans le schéma cible
  sudo docker exec -i -e PGOPTIONS="-c search_path=$POSTGRES_SCHEMA,public" "$DB_CONTAINER" \
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 \
    < "$POP_SQL"

  echo "✅ Base de données initialisée avec succès."
else
  echo "ℹ️ La base de données est déjà présente. Saut de l'initialisation."
fi

# ---------------------------------------------------------------------
# 4) Lancement Backend (local)
# ---------------------------------------------------------------------
echo "🐍 Lancement du backend (local, uv + uvicorn)..."
cd "$BACKEND_DIR"
uv run uvicorn api.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload &
BACKEND_PID=$!
cd "$ROOT_DIR" >/dev/null

# ---------------------------------------------------------------------
# 5) Lancement Frontend (local)
# ---------------------------------------------------------------------
echo "⚛️  Lancement du frontend (local, npm)..."
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
  echo "📦 Installation des dépendances frontend (npm install)..."
  npm install
fi

npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT" &
FRONTEND_PID=$!
cd "$ROOT_DIR" >/dev/null

# ---------------------------------------------------------------------
# 6) Ouverture navigateur
# ---------------------------------------------------------------------
echo "🌐 Ouverture des interfaces..."
xdg-open "http://localhost:$FRONTEND_PORT" 2>/dev/null || \
  echo "👉 Frontend : http://localhost:$FRONTEND_PORT"

xdg-open "http://localhost:$BACKEND_PORT/docs" 2>/dev/null || \
  echo "👉 API Docs : http://localhost:$BACKEND_PORT/docs"

# ---------------------------------------------------------------------
# 7) Cleanup (CTRL+C)
# ---------------------------------------------------------------------
cleanup() {
  echo ""
  echo "🛑 Arrêt des services locaux..."
  kill "$BACKEND_PID" 2>/dev/null || true
  kill "$FRONTEND_PID" 2>/dev/null || true
  echo "✅ Backend/Frontend arrêtés."
  echo "ℹ️ La DB Docker reste active (docker compose stop db pour l'arrêter)."
}
trap cleanup EXIT

echo "✅ Tout est lancé ! (CTRL+C pour arrêter backend+frontend)"
wait

#!/bin/bash
set -e

echo "🚀 Démarrage du projet2A (DB Docker + Backend/Frontend locaux)..."

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/src/backend"
FRONTEND_DIR="$ROOT_DIR/src/frontend"

# ---------------------------------------------------------------------
# 0) Charger le .env du backend (variables exportées)
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
# 1) Variables (valeurs par défaut si absentes du .env)
# ---------------------------------------------------------------------
POSTGRES_USER="${POSTGRES_USER:-projet_user}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-projet_pwd}"

# Compat POSTGRES_DB / POSTGRES_DATABASE
if [ -n "${POSTGRES_DB:-}" ]; then
  POSTGRES_DB="$POSTGRES_DB"
else
  POSTGRES_DB="${POSTGRES_DATABASE:-projet2a}"
fi

# Schéma réel (pas test)
POSTGRES_SCHEMA="${POSTGRES_SCHEMA:-projet_dao}"

DB_CONTAINER="projet2a_postgres"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

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

echo "⏳ Attente de la base de données (healthy)..."
until [ "$(sudo docker inspect -f '{{.State.Health.Status}}' "$DB_CONTAINER" 2>/dev/null)" == "healthy" ]; do
  sleep 2
done
echo "✅ Base de données OK (healthy)."

# ---------------------------------------------------------------------
# 3) Reset DB (local) -> on se connecte à Postgres via le port exposé
# ---------------------------------------------------------------------
echo "📦 Réinitialisation de la base via reset_database.py (schéma: $POSTGRES_SCHEMA)..."

cd "$BACKEND_DIR"

# IMPORTANT : reset lancé en LOCAL (hors Docker), donc host = localhost
export POSTGRES_HOST=127.0.0.1
export POSTGRES_PORT="${POSTGRES_PORT:-5432}"
export POSTGRES_USER
export POSTGRES_PASSWORD
export POSTGRES_DB
export POSTGRES_DATABASE="$POSTGRES_DB"
export POSTGRES_SCHEMA

# VRAIE base : test_dao=False
uv run python -c "from utils.reset_database import ResetDatabase; ResetDatabase().lancer(test_dao=False, populate=True)"

cd "$ROOT_DIR" >/dev/null
echo "✅ Base prête."

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
  echo "ℹ️ La DB Docker reste active (sudo docker compose stop db pour l'arrêter)."
}
trap cleanup EXIT

echo "✅ Tout est lancé ! (CTRL+C pour arrêter backend+frontend)"
wait
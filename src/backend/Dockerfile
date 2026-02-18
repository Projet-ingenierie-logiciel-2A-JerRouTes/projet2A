FROM python:3.13-slim

# Dossier de travail
WORKDIR /app

# Installer curl pour installer uv
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Installer uv
RUN curl -Ls https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copier uniquement les fichiers de dépendances
COPY pyproject.toml uv.lock ./

# Installer les dépendances (prod uniquement)
RUN uv sync --frozen --no-dev

# Copier le reste du backend
COPY . .

# Exposer le port FastAPI
EXPOSE 8000

# Lancer l'API
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

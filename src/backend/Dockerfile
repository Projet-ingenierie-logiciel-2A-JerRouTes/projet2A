# OLD
###########################################################
#FROM python:3.13.12-trixie
#
#COPY . .
#
#RUN pip install -r requirements.txt
#
#ENTRYPOINT ["python", "main.py"]
#
# on choisit la commande lancée au démarragegit
##############################################################


# Utilisation de votre image de base (Trixie est une version de Debian)
FROM python:3.13-slim

# Définition du dossier de travail (évite de copier à la racine du conteneur)
#WORKDIR /app
WORKDIR /projet

# Copie uniquement du fichier de dépendances pour optimiser le cache Docker
COPY requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie de tout le reste du code source vers /app
#COPY . .
COPY . ./src/backend/

# EXPOSE est crucial pour que Docker sache que le port 8000 doit être ouvert
EXPOSE 8000

# Pour FastAPI, on utilise uvicorn au lieu de "python main.py" 
# car cela permet de gérer les requêtes asynchrones et le rechargement à chaud
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["uvicorn", "src.backend.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
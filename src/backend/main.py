from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Import de ta fonction de génération
from src.backend.seed_data import get_app_data
from src.backend.business_objects.user import GenericUser

app = FastAPI(title="Frigo App - Backend ENSAI")

# --- CONFIGURATION CORS ---
# On garde ta configuration initiale car elle fonctionne
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CHARGEMENT DES DONNÉES ---
# data contient "users" (une liste d'objets User) et "stocks" (un dictionnaire)
data = get_app_data()
db_users = data["users"]
db_stocks = data["stocks"]

# --- MODÈLES DE DONNÉES (DTO) ---
# Ces classes servent uniquement à valider ce que React nous envoie
class LoginRequest(BaseModel):
    pseudo: str
    password: str

class RegisterRequest(BaseModel):
    pseudo: str
    password: str
    confirm_password: str

# --- ROUTES ---

@app.get("/")
def read_root():
    return {"message": "Serveur opérationnel avec seed_data !"}

@app.post("/login")
async def login(request: LoginRequest):

    # A recoder proprement gestion des erreurs ne doit pas se faire ici
    ##################################################################
    # On cherche l'utilisateur par son pseudo
    user = next((u for u in db_users if u.pseudo == request.pseudo), None)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    if user.check_password(request.password):
        user_stock = db_stocks.get(user.id_stock)
        return {
            "id": user.id_user,
            "pseudo": user.pseudo,
            "role": user.display_role(),
            "id_stock": user.id_stock,
            "nom_stock": user_stock.nom if user_stock else "Aucun stock"
        }

    raise HTTPException(status_code=401, detail="Mot de passe incorrect")


@app.post("/register")
async def register(request: RegisterRequest):

    # A recoder proprement gestion des erreurs ne doit pas se faire ici
    ##################################################################
    # 1. Vérification du mot de passe (si tu les reçois tous les deux du front)
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Les mots de passe ne sont pas identiques")

    # 2. Vérification du pseudo
    if any(u.pseudo == request.pseudo for u in db_users):
        raise HTTPException(status_code=400, detail="Ce pseudo est déjà utilisé")

    # 3. Création du nouvel utilisateur
    new_id = max(u.id_user for u in db_users) + 1 if db_users else 1
    new_user = GenericUser(new_id, request.pseudo, request.password)
    db_users.append(new_user)

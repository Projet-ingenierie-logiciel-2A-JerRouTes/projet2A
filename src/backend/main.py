from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import de ta fonction de génération
from src.backend.seed_data import get_app_data

app = FastAPI(title="Frigo App - Backend ENSAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CHARGEMENT DES DONNÉES ---
data = get_app_data()
db_users = data["users"]
db_stocks = data["stocks"]

class LoginRequest(BaseModel):
    pseudo: str
    password: str

@app.post("/login")
async def login(request: LoginRequest):
    user = next((u for u in db_users if u.pseudo == request.pseudo), None)

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    if user.check_password(request.password):
        # On récupère le stock associé à l'utilisateur depuis notre dictionnaire de stocks
        user_stock = db_stocks.get(user.id_stock)

        return {
            "id": user.id_user,
            "pseudo": user.pseudo,
            "role": user.display_role(),
            "id_stock": user.id_stock,
            "nom_stock": user_stock.nom if user_stock else "Aucun stock"
        }

    raise HTTPException(status_code=401, detail="Mot de passe incorrect")

@app.get("/")
def read_root():
    return {"message": "Serveur opérationnel avec seed_data !"}

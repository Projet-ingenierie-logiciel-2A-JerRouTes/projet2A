from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# On importe tes classes depuis le dossier business_objects
from business_objects.user import GenericUser, Admin

app = FastAPI(title="Frigo App - Backend ENSAI")

# Configuration du CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulation de base de données
db_users = [
    Admin(1, "Christelle", "123"),
    GenericUser(2, "Generic", "abc")
]

# Modèle Pydantic pour la validation des données reçues de React
class LoginRequest(BaseModel):
    pseudo: str
    password: str

@app.post("/login")
async def login(request: LoginRequest):
    # Recherche de l'utilisateur
    user = next((u for u in db_users if u.pseudo == request.pseudo), None)

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # On utilise la méthode check_password définie dans ton fichier user.py
    if user.check_password(request.password):
        return {
            "id": user.id_user,
            "pseudo": user.pseudo,
            "role": user.display_role()
        }

    raise HTTPException(status_code=401, detail="Mot de passe incorrect")

@app.get("/")
def read_root():
    return {"message": "Serveur Frigo App opérationnel !"}

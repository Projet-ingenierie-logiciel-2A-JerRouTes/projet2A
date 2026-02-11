from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.backend.business_objects.user import GenericUser

# Import de ta fonction de génération
from src.frontend.src.seed_data import get_app_data

# Création de l'application avec une description détaillée pour le Swagger
app = FastAPI(
    title="Frigo App - Backend ENSAI",
    description="""
    API de gestion de frigo intelligent.
    Permet la gestion des utilisateurs, la consultation du catalogue d'ingrédients
    et la manipulation des stocks personnels.
    """,
    version="1.0.0",
)

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
ingredients = data["ingredients"]


# --- MODÈLES DE DONNÉES (DTO) ---
# Ces classes servent uniquement à valider ce que React nous envoie
class LoginRequest(BaseModel):
    pseudo: str
    password: str


class RegisterRequest(BaseModel):
    pseudo: str
    password: str
    confirm_password: str


# --- ROUTES ADMIN ---
@app.get(
    "/admin/users",
    tags=["Administration"],
    summary="Liste complète des utilisateurs",
    response_description="La liste de tous les objets utilisateurs enregistrés",
)
async def get_all_users():
    """
    Récupère l'intégralité des utilisateurs présents dans la base de données volatile
    (db_users).
    Utile pour vérifier les inscriptions et les rôles.
    """
    # On renvoie une version simplifiée pour ne pas exposer les mots de passe si
    # nécessaire
    return [
        {
            "id_user": u.id_user,
            "pseudo": u.pseudo,
            "id_stock": u.id_stock,
            "role": u.display_role(),
        }
        for u in db_users
    ]


@app.get(
    "/admin/stocks",
    tags=["Administration"],
    summary="Visualisation de tous les stocks",
    response_description="Dictionnaire complet des stocks indexés par ID",
)
async def get_all_stocks():
    """
    Renvoie le dictionnaire complet de tous les stocks présents sur le serveur.
    Permet de voir quel utilisateur possède quel ingrédient en temps réel.
    """
    return db_stocks


# --- ROUTES GENERIC ---
@app.get("/")
def read_root():
    """
    Vérifie si l'API est en ligne et si le chargement des données initiales (seed_data)
    a réussi.
    """
    return {"message": "Serveur opérationnel avec seed_data !"}


@app.post("/login")
async def login(request: LoginRequest):
    """
    Authentifie un utilisateur et renvoie ses informations de profil ainsi que son ID
    de stock.
    - **404**: Pseudo inexistant
    - **401**: Mot de passe erroné
    """

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
            "nom_stock": user_stock.nom if user_stock else "Aucun stock",
        }

    raise HTTPException(status_code=401, detail="Mot de passe incorrect")


@app.post("/register")
async def register(request: RegisterRequest):
    """
    Enregistre un nouvel utilisateur dans la base de données.
    - Vérifie la correspondance des mots de passe.
    - Vérifie l'unicité du pseudo.
    """

    # A recoder proprement gestion des erreurs ne doit pas se faire ici
    ##################################################################
    # 1. Vérification du mot de passe (si tu les reçois tous les deux du front)
    if request.password != request.confirm_password:
        raise HTTPException(
            status_code=400, detail="Les mots de passe ne sont pas identiques"
        )

    # 2. Vérification du pseudo
    if any(u.pseudo == request.pseudo for u in db_users):
        raise HTTPException(status_code=400, detail="Ce pseudo est déjà utilisé")

    # 3. Création du nouvel utilisateur
    new_id = max(u.id_user for u in db_users) + 1 if db_users else 1
    new_user = GenericUser(new_id, request.pseudo, request.password)
    db_users.append(new_user)


@app.get("/ingredients")
async def get_all_ingredients():
    """
    Récupère le contenu d'un frigo spécifique via son ID de stock.
    Renvoie les items regroupés par ingrédient.
    """
    # 'data' est le dictionnaire renvoyé par get_app_data()
    # On renvoie la liste des ingrédients pour que le front connaisse les noms
    return data["ingredients"]


@app.get("/stock/{id_stock}")
async def get_stock(id_stock: int):
    # 'data' provient de ton seed_data
    user_stock = data["stocks"].get(id_stock)

    if not user_stock:
        raise HTTPException(status_code=404, detail="Stock non trouvé")

    return {
        "id_stock": user_stock.id_stock,
        "nom": user_stock.nom,
        "items_by_ingredient": user_stock.items_by_ingredient,
    }

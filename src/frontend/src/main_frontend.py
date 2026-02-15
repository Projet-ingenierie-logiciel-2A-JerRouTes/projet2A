from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.backend.business_objects.unit import Unit
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
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Autorise ton React
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
    """
    DTO pour la connexion d'un utilisateur.
    """

    pseudo: str
    password: str


class RegisterRequest(BaseModel):
    """
    DTO pour la création d'un nouvel utilisateur.
    """

    pseudo: str
    password: str
    confirm_password: str


class IngredientRequest(BaseModel):
    """
    DTO pour la création d'un nouvel ingrédient.
    """

    name: str = Field(..., min_length=1, example="Poivre noir")
    unit: Unit = Field(..., example=Unit.GRAM)


# --- INITIALISATION ---
@app.get(
    "/api/auth/",
    tags=["Initialisation"],
    summary="Vérification de l'API et des données initiales",
    response_description="Message de confirmation que le serveur est opérationnel et "
    "que les données seed_data sont chargées",
)
def read_root():
    """
    Vérifie si l'API est en ligne et si le chargement des données initiales (seed_data)
    a réussi.
    """
    return {"message": "Serveur opérationnel avec seed_data !"}


# --- AUTHENTIFICATION / UTILISATEUR ---
@app.get(
    "/api/auth/users",
    tags=["Utilisateurs"],
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


@app.post(
    "/api/auth/login",
    tags=["Utilisateurs"],
    summary="Connexion utilisateur",
    response_description="Profil utilisateur",
)
async def login(payload: dict = Body(...)):  # On accepte n'importe quel dictionnaire
    print(f"DEBUG PAYLOAD REÇU: {payload}")

    # On essaie de récupérer le pseudo, peu importe le nom de la clé
    pseudo = payload.get("pseudo") or payload.get("login")
    password = payload.get("password")

    if not pseudo:
        raise HTTPException(status_code=422, detail="Pseudo manquant dans le JSON")

    user = next((u for u in db_users if u.pseudo == pseudo), None)

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    if user.check_password(password):
        user_stock = db_stocks.get(user.id_stock)
        return {
            "id": user.id_user,
            "pseudo": user.pseudo,
            "role": user.display_role(),
            "id_stock": user.id_stock,
            "nom_stock": user_stock.nom if user_stock else "Aucun stock",
        }

    raise HTTPException(status_code=401, detail="Mot de passe incorrect")


@app.post(
    "/api/auth/register",
    tags=["Utilisateurs"],
    summary="Création de compte",
    response_description="Message de confirmation de création",
)
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


# --- REFERENTIEL INGREDIENTS ---


@app.get(
    "/api/auth/ingredients",
    tags=["Référentiel ingredient"],
    summary="Liste complète des ingrédients",
    response_description="Catalogue des ingrédients pour l'autocomplétion",
)
async def get_all_ingredients():
    """
    Récupère le contenu d'un frigo spécifique via son ID de stock.
    Renvoie les items regroupés par ingrédient.
    """
    # 'data' est le dictionnaire renvoyé par get_app_data()
    # On renvoie la liste des ingrédients pour que le front connaisse les noms
    return data["ingredients"]


# --- REFERENTIEL STOCK ---
@app.get(
    "/api/auth/stocks",
    tags=["Référentiel stock"],
    summary="Visualisation de tous les stocks",
    response_description="Dictionnaire complet des stocks indexés par ID",
)
async def get_all_stocks():
    """
    Renvoie le dictionnaire complet de tous les stocks présents sur le serveur.
    Permet de voir quel utilisateur possède quel ingrédient en temps réel.
    """
    return db_stocks


@app.get(
    "/api/auth/stock/{id_stock}",
    tags=["Référentiel stock"],
    summary="Consulter un inventaire",
    response_description="Contenu détaillé d'un stock défini par son ID",
)
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

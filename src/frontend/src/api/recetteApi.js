import API from "./apiClient";

/**
 * Recherche une recette aléatoire
 * Correspond à @app.get("/api/recipes/${recipe_id}")
 */
export async function findRecipeAlea(idRecipe) {
  const res = await API.get(`/api/recipes/${idRecipe}`);
  return res.data;
}

/**
 * Recherche des recettes basées sur une liste d'ingrédients
 * Correspond à l'endpoint FastAPI : POST /api/recipes/search
 */
/*
export async function findRecipe(liste_ingredients) {
   try {
    // On garde les ingrédients tels que saisis (sans forcer le lowercase si possible)
    const payload = { 
      ingredients: liste_ingredients 
    };

    console.log("🚀 Tentative d'appel avec payload local :");
    console.log(JSON.stringify(payload));

    const res = await API.post("/api/recipes/search", payload);
    
    // On log la réponse brute pour voir si c'est un tableau vide [] ou autre chose
    console.log("📡 Réponse brute du serveur :", res.data);
    
    return res.data;
  } catch (erreur) {
    console.error("❌ Erreur lors de la recherche :", erreur.response?.data || erreur);
    return [];
  }
}*/

export async function findRecipe(liste_ingredients) {
  try {
    const payload = { ingredients: liste_ingredients };

    console.log("📤 TEST FRONTEND - Payload envoyé :", JSON.stringify(payload));

    const res = await API.post("/api/recipes/search", payload);
    
    // LOG CRUCIAL : Affiche la longueur des données reçues
    console.log("📥 RÉPONSE SERVEUR - Nombre de recettes reçues :", res.data.length);
    console.log("📥 DONNÉES BRUTES :", res.data);
    
    return res.data;
  } catch (erreur) {
    console.error("❌ ERREUR RÉSEAU OU SERVEUR :", erreur.response?.data || erreur.message);
    return [];
  }
}


/**
 * Liste les recettes présentes en base de données
 * Correspond à l'endpoint FastAPI : GET /api/recipes
 */
export async function listRecipes(filtres = {}) {
  try {
    // On définit les paramètres par défaut basés sur ton code Python
    const params = {
      limit: filtres.limit || 1000,
      offset: filtres.offset || 0,
      name: filtres.name || null,
      include_relations: filtres.include_relations ?? true // Utile pour avoir les tags/ingrédients
    };

    console.log("📤 Requête GET /api/recipes", params);

    // Axios transforme automatiquement l'objet params en ?limit=50&offset=0...
    const res = await API.get("/api/recipes", { params });
    
    return res.data;
  } catch (erreur) {
    console.error("❌ Erreur lors de la récupération de la liste des recettes :", erreur);
    return [];
  }
}



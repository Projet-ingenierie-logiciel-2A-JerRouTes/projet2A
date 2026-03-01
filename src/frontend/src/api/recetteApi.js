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
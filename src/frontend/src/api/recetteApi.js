import API from "./apiClient";

/**
 * Recherche une recette aléatoire
 * Correspond à @app.get("/api/recipes/${recipe_id}")
 */
export async function findRecipeAlea(idRecipe) {
  const res = await API.get(`/api/recipes/${idRecipe}`);
  return res.data;
}

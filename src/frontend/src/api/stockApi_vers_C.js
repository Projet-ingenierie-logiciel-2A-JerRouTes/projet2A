import API from "./apiClient";

/**
 * Récupère tous les ingrédients disponibles (Référentiel)
 * Correspond à @app.get("/api/auth/ingredients")
 */
export async function getAllIngredients() {
  const res = await API.get("/api/auth/ingredients");
  return res.data;
}

/**
 * Récupère le contenu d'un stock spécifique
 * Correspond à @app.get("/api/auth/stock/{id_stock}")
 */
export async function getStockDetails(idStock) {
  const res = await API.get(`/api/auth/stock/${idStock}`);
  return res.data;
}

/**
 * Récupère la liste de tous les stocks (vue globale)
 * Correspond à @app.get("/api/auth/stocks")
 */
export async function getAllStocks() {
  const res = await API.get("/api/auth/stocks");
  return res.data;
}

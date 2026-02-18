import API from "./apiClient";

/**
 * Récupère tous les ingrédients disponibles (Référentiel)
 * Correspond à @app.get("/ingredients")
 */
export async function getAllIngredients() {
  const res = await API.get("/api/ingredients");
  return res.data;
}

/**
 * Récupère le contenu d'un stock spécifique
 * Correspond à @app.get("/stocks/{id_stock}")
 */
export async function getStockDetails(idStock) {
  const res = await API.get(`/api/stocks/${idStock}/lots`);
  return res.data;
}

/**
 * Récupère la liste de tous les stocks (vue globale)
 * Correspond à @app.get("/stocks")
 */
export async function getAllStocks() {
  const res = await API.get("/api/stocks");
  return res.data;
}

/**
 * Récupère les d'info d'un stock
 * Correspond à @app.get("/stocks/{id_stock}")
 */
export async function getInfoStock(idStock) {
  const res = await API.get(`/api/stocks/${idStock}`);
  return res.data;
}

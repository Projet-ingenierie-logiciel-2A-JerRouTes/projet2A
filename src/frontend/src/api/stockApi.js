import API from "./apiClient";

/**
 * Récupère tous les ingrédients disponibles (Référentiel)
 * Correspond à @app.get("/ingredients")
 */
export async function getAllIngredients() {
  const res = await API.get("/ingredients");
  return res.data;
}

/**
 * Récupère le contenu d'un stock spécifique
 * Correspond à @app.get("/stocks/{id_stock}")
 */
export async function getStockDetails(idStock) {
  const res = await API.get(`/stocks/${idStock}/lots`);
  return res.data;
}

/**
 * Récupère la liste de tous les stocks (vue globale)
 * Correspond à @app.get("/stocks")
 */
export async function getAllStocks_v2() {
  const res = await API.get("/stocks");
  return res.data;
}

/**
 * Récupère la liste de tous les stocks (vue globale)
 * Correspond à @app.get("/stocks")
 */
export async function getAllStocks(user_id) {
  const res = await API.get(`/stocks/user/${user_id}`);
  return res.data;
}

/**
 * Récupère les d'info d'un stock
 * Correspond à @app.get("/stocks/{id_stock}")
 */
export async function getInfoStock(idStock) {
  const res = await API.get(`/stocks/${idStock}`);
  return res.data;
}

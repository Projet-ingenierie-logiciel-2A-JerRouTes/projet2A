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

/**
 * Ajouter un stock de nom donné
 * Correspond à @app.post("api/stocks/${name}")
 */
export async function createStock(name) {
  // On envoie un objet { name: name } en deuxième argument d'axios.post
  const res = await API.post("/api/stocks", { name: name });
  return res.data;
}

/**
 * Ajoute un lot d'ingrédient (stock_item) à un stock spécifique.
 * L'ingredientId provient généralement de votre autocomplétion (catalogue).
 * * @param {number} stock_id - L'identifiant du stock cible
 * @param {number} ingredient_id - L'identifiant de l'ingrédient sélectionné
 * @param {number} quantity - La quantité à ajouter
 * @param {string|null} expiration_date - Date au format "YYYY-MM-DD" ou null
 */
export async function addStockItem(stock_id, ingredient_id, quantity, expiration_date = null) {
  const payload = {
    ingredient_id: ingredient_id,
    quantity: parseFloat(quantity),
    expiration_date: expiration_date,
  };

  // Correspond à @router.post("/api/stocks/{stock_id}/lots")
  const res = await API.post(`/api/stocks/${stock_id}/lots`, payload);
  return res.data;
}
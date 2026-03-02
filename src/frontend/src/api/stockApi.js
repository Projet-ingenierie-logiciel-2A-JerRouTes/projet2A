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
export async function getInfoStock(id_stock) {
  const res = await API.get(`/api/stocks/${id_stock}`);
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
 * Supprime un stock d'id donné
 * Correspond à @app.delete("api/stocks/${id_stock}")
 */
export async function deleteStock(id_stock) {
  // On envoie un objet { name: name } en deuxième argument d'axios.post
  const res = await API.delete(`/api/stocks/${id_stock}`);
  return res.data;
}

/**
 * Vider un stock d'id donne
 * Correspond à @app.delete("api/stocks/${id_stock}/lots")
 */
export async function deleteLotsStock(id_stock) {
  // On envoie un objet { name: name } en deuxième argument d'axios.post
  const res = await API.delete(`/api/stocks/${id_stock}/lots`);
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


/**
 * Liste tous les stocks de l'application (Réservé aux admins)
 * Correspond à l'endpoint FastAPI : GET /api/stocks/all
 */
export async function getAllStocksAdmin(filtres = {}) {
  try {
    // Préparation des paramètres de requête (Query Params)
    const params = {
      limit: filtres.limit || 1000,
      offset: filtres.offset || 0,
      name: filtres.name || null
    };

    console.log("📤 Requête ADMIN : GET /api/stocks/all", params);

    // Appel à l'API avec les paramètres dans l'URL
    const res = await API.get("/api/stocks/all", { params });
    
    // Retourne la liste des objets StockOut { stock_id, name }
    return res.data;
  } catch (erreur) {
    // Gestion des erreurs de permissions (403 Forbidden) ou réseau
    if (erreur.response?.status === 403) {
      console.error("❌ Accès refusé : Vous n'avez pas les droits administrateur.");
    } else {
      console.error("❌ Erreur lors de la récupération de tous les stocks :", erreur.message);
    }
    return [];
  }
}

/**
 * Récupère la liste simplifiée (ID + Nom) des ingrédients du stock de l'utilisateur
 * Correspond à l'endpoint FastAPI : GET /api/stocks/ingredients/names
 */
export async function getMyIngredientNames() {
  try {
    console.log("📤 Requête : GET /api/stocks/ingredients/names");
    
    const res = await API.get("/api/stocks/ingredients/names");
    
    // La réponse est une liste d'objets : [{ ingredient_id, name }, ...]
    return res.data;
  } catch (erreur) {
    console.error("❌ Erreur lors de la récupération des noms d'ingrédients :", erreur.message);
    return [];
  }
}
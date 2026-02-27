import API from "./apiClient";

/**
 * Ajoute un ingredient au référentiel
 * Correspond à @app.post("/ingredients")
 */
export async function createIngredient(name, unit) {
  const res = await API.post("/api/ingredients", {
    name: name,
    unit: unit
  });
  return res.data;
}
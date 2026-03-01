import { useState, useEffect, useCallback } from "react";
import { getStockDetails, getAllIngredients } from "../api/stockApi";

export function userStockTable(id_stock) {
  const [formatted_stock, set_formatted_stock] = useState([]);

  // On utilise useCallback pour que la fonction puisse être exportée sans créer de boucles infinies
  const refresh_stock = useCallback(async () => {
    try {
      if (!id_stock) {
        set_formatted_stock([]);
        return;
      }

      // Récupération parallèle pour plus de rapidité
      const [donnees_catalogue, donnees_stock] = await Promise.all([
        getAllIngredients(),
        getStockDetails(id_stock)
      ]);

      const tableau_formate = donnees_stock.map((lot) => {
        const ing = donnees_catalogue.find((i) => i.ingredient_id === lot.ingredient_id);
        return {
          stock_item_id: lot.stock_item_id,
          nom_ingredient: ing ? ing.name : "Inconnu",
          quantite_affichage: `${lot.quantity} ${ing ? ing.unit : ""}`,
          validite: lot.expiration_date,
        };
      });

      set_formatted_stock(tableau_formate);
    } catch (erreur) {
      console.error("Erreur hook userStockTable :", erreur);
    }
  }, [id_stock]);

  // Chargement automatique au changement d'ID
  useEffect(() => {
    refresh_stock();
  }, [id_stock, refresh_stock]);

  // On retourne maintenant la fonction de rafraîchissement en plus des données
  return { formatted_stock, refresh_stock };
}
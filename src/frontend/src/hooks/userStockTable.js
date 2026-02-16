import { useState, useEffect } from "react";
import { getStockDetails, getAllIngredients } from "../api/stockApi";

export function userStockTable(id_stock) {
  const [stock_brut, set_stock_brut] = useState([]);
  const [catalogue, set_catalogue] = useState([]);
  const [formatted_stock, set_formatted_stock] = useState([]);

  useEffect(() => {
    const charger_donnees = async () => {
      try {
        // 1. Récupérer le catalogue (si pas déjà fait)
        const donnees_catalogue = await getAllIngredients();
        set_catalogue(donnees_catalogue);

        if (id_stock) {
          // 2. Récupérer les lots du stock
          const donnees_stock = await getStockDetails(id_stock);
          set_stock_brut(donnees_stock);

          // 3. Construction du tableau à 3 colonnes
          const tableau_formate = donnees_stock.map((lot) => {
            // Trouver l'ingrédient correspondant
            const ing = donnees_catalogue.find(
              (i) => i.ingredient_id === lot.ingredient_id,
            );

            return {
              stock_item_id: lot.stock_item_id, // Utile pour la "key" React
              nom_ingredient: ing ? ing.name : "Inconnu", // Colonne 1
              quantite_affichage: `${lot.quantity} ${ing ? ing.unit : ""}`, // Colonne 2
              validite: lot.expiration_date, // Colonne 3
            };
          });

          set_formatted_stock(tableau_formate);
        }
      } catch (erreur) {
        console.error("Erreur hook userStockTable :", erreur);
      }
    };

    charger_donnees();
  }, [id_stock]); // Se déclenche à chaque changement de stock

  // On retourne maintenant le tableau déjà prêt !
  return { formatted_stock };
}

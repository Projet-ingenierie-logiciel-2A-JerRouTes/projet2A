import { useState, useEffect } from "react";
import { getAllIngredients } from "../api/stockApi";

export function useIngredientsRecette(recette) {
  const [ingredients_complets, set_ingredients_complets] = useState([]);
  const [chargement_ing, set_chargement_ing] = useState(false);

  useEffect(() => {
    // Si pas de recette ou pas d'ingrédients à chercher, on s'arrête
    if (!recette || !recette.ingredients) {
      set_ingredients_complets([]);
      return;
    }

    const enrichir_ingredients = async () => {
      set_chargement_ing(true);
      try {
        // 1. Récupérer le catalogue global pour avoir les noms
        const catalogue = await getAllIngredients();

        // 2. Mapper les ingrédients de la recette pour ajouter les noms et unités
        const liste_enrichie = recette.ingredients.map((item) => {
          const info_catalogue = catalogue.find(
            (c) => c.ingredient_id === item.ingredient_id
          );

          return {
            ...item,
            nom: info_catalogue ? info_catalogue.name : "Ingrédient inconnu",
            unite: info_catalogue ? info_catalogue.unit : "",
            affichage_complet: `${item.quantity} ${info_catalogue ? info_catalogue.unit : ""} de ${info_catalogue ? info_catalogue.name : "Inconnu"}`
          };
        });

        set_ingredients_complets(liste_enrichie);
      } catch (erreur) {
        console.error("Erreur enrichment ingredients recette:", erreur);
      } finally {
        set_chargement_ing(false);
      }
    };

    enrichir_ingredients();
  }, [recette]); // Se relance dès qu'on clique sur une nouvelle recette

  return { ingredients_complets, chargement_ing };
}
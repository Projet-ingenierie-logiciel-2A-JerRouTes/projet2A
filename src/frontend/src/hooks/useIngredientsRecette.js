import { useState, useEffect } from "react";
import { getAllIngredients } from "../api/stockApi";

const PIXABAY_KEY = "54824000-d8df568886d364ec62c29ba9c";

export function useIngredientsRecette(recette) {
  const [ingredients_complets, set_ingredients_complets] = useState([]);
  const [chargement_ing, set_chargement_ing] = useState(false);
  const [image_temp, set_image_temp] = useState(null);

  useEffect(() => {
    if (!recette) return;

    const charger_details = async () => {
      set_chargement_ing(true);
      try {
        // --- 1. RECHERCHE IMAGE (Même si image_url est vide) ---
        if (!recette.image_url) {
          console.log("🔍 Recherche image Pixabay pour:", recette.name);
          const query = encodeURIComponent(recette.name.split(' ').slice(0, 3).join(' '));
          const url = `https://pixabay.com/api/?key=${PIXABAY_KEY}&q=${query}&image_type=photo&category=food&per_page=3`;
          
          const res = await fetch(url);
          const data = await res.json();
          if (data.hits && data.hits.length > 0) {
            set_image_temp(data.hits[0].webformatURL);
          }
        }

        // --- 2. ENRICHISSEMENT INGRÉDIENTS ---
        // On vérifie si 'ingredients' existe dans l'objet reçu du backend
        if (recette.ingredients && Array.isArray(recette.ingredients)) {
          const catalogue = await getAllIngredients();
          
          const liste_enrichie = recette.ingredients.map((item) => {
            const info = catalogue.find((c) => c.ingredient_id === item.ingredient_id);
            return {
              ...item,
              affichage_complet: `${item.quantity} ${info?.unit || ""} de ${info?.name || "Inconnu"}`
            };
          });
          set_ingredients_complets(liste_enrichie);
        } else {
          console.warn("⚠️ Aucun ingrédient trouvé dans l'objet recette:", recette);
          set_ingredients_complets([]);
        }
      } catch (erreur) {
        console.error("❌ Erreur hook detail:", erreur);
      } finally {
        set_chargement_ing(false);
      }
    };

    charger_details();
  }, [recette]);

  return { ingredients_complets, chargement_ing, image_temp };
}
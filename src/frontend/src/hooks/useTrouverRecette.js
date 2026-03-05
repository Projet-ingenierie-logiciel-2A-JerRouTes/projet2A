import { useState, useEffect, useCallback } from "react";
import { findRecipeAlea, findRecipe } from "../api/recetteApi";

const PIXABAY_KEY = "54824000-d8df568886d364ec62c29ba9c";

export const useTrouverRecette = (liste_ingredients = []) => {
  const [recettes, set_recettes] = useState([]);
  const [chargement, set_chargement] = useState(false);
  const [mode_aleatoire, set_mode_aleatoire] = useState(false);

  const chercher_image = async (nom, tags) => {
    try {
      const query = encodeURIComponent(nom.split(' ').slice(0, 2).join(' '));
      const url = `https://pixabay.com/api/?key=${PIXABAY_KEY}&q=${query}&image_type=photo&category=food&per_page=3`;
      const res = await fetch(url);
      const data = await res.json();
      return data.hits?.[0]?.webformatURL || "https://images.unsplash.com/photo-1495195129352-aec325a55b65?w=400";
    } catch { 
      return "https://images.unsplash.com/photo-1495195129352-aec325a55b65?w=400"; 
    }
  };

  const fetch_data = useCallback(async () => {
    set_chargement(true);
    let resultats = [];
    let est_en_alea = false;

    try {
      // ÉTAPE 1 : Recherche par ingrédients
      if (liste_ingredients.length > 0) {
        resultats = await findRecipe(liste_ingredients);
      }

      // ÉTAPE 2 : Mode Aléatoire si aucun résultat
      if (resultats.length === 0) {
        est_en_alea = true;
        const ids = Array.from({ length: 10 }, (_, i) => i + 1)
          .sort(() => 0.5 - Math.random())
          .slice(0, 6);
        const promesses = ids.map(id => findRecipeAlea(id));
        
        // On stocke d'abord le résultat brut du Promise.all
        const reponses_brutes = await Promise.all(promesses);
        
        // AJOUTE CETTE LIGNE ICI :
        console.log("📥 Résultat du premier appel simultané (brut) :", reponses_brutes);

        // Puis on continue le filtrage habituel
        resultats = reponses_brutes.filter(r => r !== null);
      }

      // --- FILTRE ANTI-DOUBLONS (Correction PB2) ---
      // On crée une Map où la clé est le recipe_id. 
      // Si un ID existe déjà, il est écrasé, garantissant l'unicité.
      const resultats_uniques = [
        ...new Map(resultats.map((item) => [item.recipe_id, item])).values(),
      ];

      // ÉTAPE 3 : Enrichissement images sur la liste UNIQUE (Max 6)
      const final_docs = await Promise.all(
        resultats_uniques.slice(0, 6).map(async (r) => ({
          ...r,
          image_url: await chercher_image(r.name, r.tags?.map(t => t.name) || [])
        }))
      );

      set_recettes(final_docs);
      set_mode_aleatoire(est_en_alea);
    } catch (err) {
      console.error("Erreur hook useTrouverRecette:", err);
    } finally {
      set_chargement(false);
    }
  }, [liste_ingredients]);

  useEffect(() => {
    fetch_data();
  }, [fetch_data]);

  return { recettes, chargement, mode_aleatoire };
};
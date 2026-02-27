import { useState, useEffect } from "react";
import { findRecipeAlea } from "../api/recetteApi";

export const useTrouverRecetteInvite = (doit_chercher) => {
  const [recette, set_recette] = useState(null);
  const [chargement, set_chargement] = useState(false);
  const [a_deja_cherche, set_a_deja_cherche] = useState(false);

  useEffect(() => {
    if (!doit_chercher || a_deja_cherche) return;

    const recuperer_aleatoire = async () => {
      set_chargement(true);
      try {
        const id_aleatoire = Math.floor(Math.random() * 2) + 1;
        const data = await findRecipeAlea(id_aleatoire);

        if (data) {
          // On nettoie le nom (ex: "Simple fluffy pancakes" -> "pancakes")
          // car les moteurs de recherche d'images préfèrent les mots simples
          const mot_cle_principal = data.name.split(' ').pop(); 
          const tags_str = data.tags?.map(t => t.name).join(",") || "";
          
          // On construit une requête robuste
          const query = encodeURIComponent(`${mot_cle_principal},${tags_str},food`);
          
          const random_sig = Math.random();
          // On ajoute le paramètre lock pour stabiliser l'image pendant la session
          data.image_url = `https://loremflickr.com/800/500/${query}/all?sig=${random_sig}`;
          
          set_recette(data);
        }


        set_a_deja_cherche(true);
      } catch (err) {
        console.error("❌ Erreur useTrouverRecetteInvite:", err);
      } finally {
        set_chargement(false);
      }
    };

    recuperer_aleatoire();
  }, [doit_chercher, a_deja_cherche]);

  const reset_recherche_invite = () => {
    set_recette(null);
    set_a_deja_cherche(false);
  };

  return { recette, chargement, reset_recherche_invite };
};
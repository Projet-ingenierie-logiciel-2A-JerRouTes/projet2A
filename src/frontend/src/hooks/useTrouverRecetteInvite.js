import { useState, useEffect } from "react";
import { findRecipeAlea } from "../api/recetteApi";

export const useTrouverRecetteInvite = (doit_chercher) => {
  const [recettes, set_recettes] = useState([]);
  const [chargement, set_chargement] = useState(false);
  const [a_deja_cherche, set_a_deja_cherche] = useState(false);

  useEffect(() => {
    if (!doit_chercher || a_deja_cherche) return;

    const generer_grille_suggestions = async () => {
      set_chargement(true);
      try {
        const temp_recettes = [];

        // On crée 6 entrées pour remplir la grille
        for (let i = 0; i < 6; i++) {
          // On alterne entre l'ID 1 et l'ID 2
          const id_a_chercher = (i % 2) + 1; 
          const data = await findRecipeAlea(id_a_chercher);

          /*if (data) {
            const tags_str = data.tags?.map(t => t.name).join(",") || "";
            const query = encodeURIComponent(`${data.name},${tags_str},food`);
            
            // On génère une URL d'image unique pour chaque case
            data.image_url = `https://loremflickr.com/400/300/${query}/all?sig=${Math.random() + i}`;
            
            // On crée une copie de l'objet pour éviter les conflits de référence
            temp_recettes.push({ ...data });
          }*/

          if (data) {
            // On simplifie la requête pour éviter les erreurs 404
            const tags_str = data.tags?.map(t => t.name).join(",") || "food";
            const query = encodeURIComponent(`${data.name.split(' ')[0]},${tags_str}`);
            
            // Utilisation de LoremFlickr avec un 'sig' unique par itération de boucle
            // Le paramètre 'sig' force le chargement d'une image différente par case
            data.image_url = `https://loremflickr.com/400/300/${query}/all?sig=${Math.random() + i}`;
            
            temp_recettes.push({ ...data });
            }
        }
        set_recettes(temp_recettes);
        set_a_deja_cherche(true);
      } catch (err) {
        console.error("❌ Erreur génération grille:", err);
      } finally {
        set_chargement(false);
      }
    };

    generer_grille_suggestions();
  }, [doit_chercher, a_deja_cherche]);

  const reset_recherche_invite = () => {
    set_recettes([]);
    set_a_deja_cherche(false);
  };

  return { recettes, chargement, reset_recherche_invite };
};
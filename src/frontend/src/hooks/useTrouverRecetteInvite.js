import { useState, useEffect } from "react";
import { findRecipeAlea } from "../api/recetteApi";

// REMPLACE PAR TA CLÉ RÉELLES
const PIXABAY_KEY = "54824000-d8df568886d364ec62c29ba9c";

export const useTrouverRecetteInvite = (doit_chercher) => {
  const [recettes, set_recettes] = useState([]);
  const [chargement, set_chargement] = useState(false);
  const [a_deja_cherche, set_a_deja_cherche] = useState(false);

  // Fonction interne pour chercher l'image sur Pixabay
  const chercher_image_pixabay = async (nom_recette, tags) => {
    try {
      // On nettoie le nom (on prend les 2 premiers mots pour éviter d'être trop précis)
      const terme_recherche = nom_recette.split(' ').slice(0, 2).join(' ');
      const query = encodeURIComponent(terme_recherche);
      
      const url = `https://pixabay.com/api/?key=${PIXABAY_KEY}&q=${query}&image_type=photo&category=food&orientation=horizontal&safesearch=true&per_page=3`;

      const response = await fetch(url);
      const data = await response.json();

      if (data.hits && data.hits.length > 0) {
        // On retourne l'image la plus pertinente
        return data.hits[0].webformatURL;
      } else {
        // Fallback 1 : Si rien n'est trouvé, on cherche avec le premier tag
        if (tags.length > 0) {
          const fallback_query = encodeURIComponent(tags[0]);
          const res_fallback = await fetch(`https://pixabay.com/api/?key=${PIXABAY_KEY}&q=${fallback_query}&image_type=photo&category=food&per_page=3`);
          const data_fallback = await res_fallback.json();
          if (data_fallback.hits?.length > 0) return data_fallback.hits[0].webformatURL;
        }
        // Fallback 2 : Image générique de nourriture
        return "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&cs=tinysrgb&w=400";
      }
    } catch (error) {
      console.error("Erreur Pixabay:", error);
      return "https://via.placeholder.com/400x300?text=Cuisine";
    }
  };

  useEffect(() => {
    if (!doit_chercher || a_deja_cherche) return;

    const generer_grille_suggestions = async () => {
      set_chargement(true);
      try {
        // Sélection de 6 IDs parmi tes 10 recettes
        const ids_choisis = Array.from({ length: 10 }, (_, i) => i + 1)
          .sort(() => Math.random() - 0.5)
          .slice(0, 6);

        const promesses = ids_choisis.map(async (id) => {
          const data_recette = await findRecipeAlea(id);
          
          if (data_recette) {
            const tags_noms = data_recette.tags?.map(t => t.name) || [];
            // On attend la réponse de Pixabay pour chaque recette
            data_recette.image_url = await chercher_image_pixabay(data_recette.name, tags_noms);
          }
          return data_recette;
        });

        const resultats = await Promise.all(promesses);
        set_recettes(resultats.filter(r => r !== null));
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
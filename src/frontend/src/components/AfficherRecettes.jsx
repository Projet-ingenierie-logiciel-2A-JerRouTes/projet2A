import React from "react";
import { ArrowLeft, PlusCircle, Loader2 } from "lucide-react";
import AfficherRecette from "./AfficherRecette";
import { useTrouverRecette } from "../hooks/useTrouverRecette";
import "../styles/AfficherRecettes.css";

const AffichageRecettes = ({ 
  gerer_retour, 
  on_select_recette, 
  on_clic_saisir,
  liste_ingredients = [] 
}) => {
  
  const { recettes, chargement, mode_aleatoire } = useTrouverRecette(liste_ingredients);

  // Détermination de la classe de grille selon le nombre de recettes
  const obtenir_classe_grille = () => {
    const nb = recettes.length;
    if (nb >= 5) return "grille-6"; // 2x3 (5 ou 6 recettes)
    if (nb === 4) return "grille-4"; // 2x2
    if (nb === 3) return "grille-3"; // 3 horizontal
    if (nb === 2) return "grille-2"; // 2 horizontal
    return "grille-1"; // 1 seule vignette
  };

  return (
    <div className="recettes-globale-container">
      <h1 className="titre-principal-pluriel">
        {mode_aleatoire ? "Recettes aléatoires" : "Recettes avec vos ingrédients"}
      </h1>

      {chargement ? (
        <div className="chargement-grille">
          <Loader2 className="animate-spin" size={32} />
          <p>Calcul des combinaisons culinaires...</p>
        </div>
      ) : (
        <>
          <div className={`grille-dynamique ${obtenir_classe_grille()}`}>
            {recettes.map((r, index) => (
              <div 
                key={r.recipe_id || index} 
                onClick={() => on_select_recette(r)} 
                className="wrapper-recette-cliquable"
              >
                <AfficherRecette recette={r} />
              </div>
            ))}
          </div>
          
          <div className="conteneur-actions-bas">
            <button className="bouton-retour" onClick={gerer_retour}>
              <ArrowLeft size={18} /> Retour
            </button>
            <button className="bouton-saisir-ingredient" onClick={on_clic_saisir}>
              <PlusCircle size={18} /> Saisir ingrédients
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default AffichageRecettes;
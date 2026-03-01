import React from "react";
import { ArrowLeft, PlusCircle } from "lucide-react";
import AfficherRecette from "./AfficherRecette";
import "../styles/AfficherRecettes.css";

const AffichageRecettes = ({ 
  gerer_retour, 
  recettes, 
  chargement, 
  on_select_recette, 
  on_clic_saisir 
}) => {
  
  return (
    <div className="recettes-globale-container">
      <h1 className="titre-principal-pluriel">Suggestions de recettes</h1>

      {chargement ? (
        <div className="chargement-grille">Calcul des combinaisons culinaires...</div>
      ) : recettes && recettes.length > 0 ? (
        <>
          <div className="grille-recettes-3x2">
            {recettes.map((r, index) => (
              <div 
                key={index} 
                onClick={() => on_select_recette(r)} 
                className="wrapper-recette-cliquable"
              >
                <AfficherRecette recette={r} />
              </div>
            ))}
          </div>
          
          {/* Section des boutons avec les nouvelles classes CSS */}
          <div className="conteneur-actions-bas">
            
            <button className="bouton-retour" onClick={gerer_retour}>
              <ArrowLeft size={18} /> Retour
            </button>

            <button className="bouton-saisir-ingredient" onClick={on_clic_saisir}>
              <PlusCircle size={18} /> Saisir ingrédients
            </button>

          </div>
        </>
      ) : (
        <div className="chargement-grille">Aucune recette trouvée.</div>
      )}
    </div>
  );
};

export default AffichageRecettes;
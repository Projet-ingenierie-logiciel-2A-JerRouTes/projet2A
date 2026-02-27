import React from "react";
import { ArrowLeft } from "lucide-react";
import AfficherRecette from "./AfficherRecette";
import "../styles/AfficherRecettes.css";

// Changement : on utilise 'recettes' au pluriel comme prop
const AffichageRecettes = ({ gerer_retour, recettes, chargement }) => {
  
  return (
    <div className="recettes-globale-container">
      <h1 className="titre-principal-pluriel">Suggestions de recettes</h1>

      {chargement ? (
        <div className="chargement-grille">Calcul des combinaisons culinaires...</div>
      ) : recettes && recettes.length > 0 ? (
        <>
          <div className="grille-recettes-3x2">
            {recettes.map((r, index) => (
              <AfficherRecette key={index} recette={r} />
            ))}
          </div>

          <div className="actions-bas-page">
            <button onClick={gerer_retour} className="btn-retour-final">
              <ArrowLeft size={18}/> Retour
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
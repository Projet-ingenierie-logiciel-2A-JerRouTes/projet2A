import React from "react";
import { ArrowLeft, PlusCircle, Loader2 } from "lucide-react";
import AfficherRecette from "./AfficherRecette";
import { useTrouverRecette } from "../hooks/useTrouverRecette";
import "../styles/AfficherRecettes.css";

const AffichageRecettes = ({ 
  gerer_retour, 
  on_select_recette, 
  on_clic_saisir,
  liste_ingredients = [],
  peut_saisir = true,
  utilisateur = null // Ajout de la prop utilisateur (null si invité)
}) => {
  
  const { recettes, chargement, mode_aleatoire } = useTrouverRecette(liste_ingredients);

  if (!chargement) {
    console.log(`[LOG] Méthode utilisée : ${mode_aleatoire ? "🎲 ALÉATOIRE" : "🔍 RECHERCHE INGRÉDIENTS"}`);
    console.log(`[LOG] Liste des recettes reçues (${recettes.length}) :`, recettes);
  }


  const obtenir_classe_grille = () => {
    const nb = recettes.length;
    if (nb >= 5) return "grille-6";
    if (nb === 4) return "grille-4";
    if (nb === 3) return "grille-3";
    if (nb === 2) return "grille-2";
    return "grille-1";
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
                // MODIFICATION ICI : On envoie la recette ET l'utilisateur
                onClick={() => on_select_recette(r, utilisateur)} 
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

            {peut_saisir && (
              <button className="bouton-saisir-ingredient" onClick={on_clic_saisir}>
                <PlusCircle size={18} /> Saisir ingrédients
              </button>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default AffichageRecettes;
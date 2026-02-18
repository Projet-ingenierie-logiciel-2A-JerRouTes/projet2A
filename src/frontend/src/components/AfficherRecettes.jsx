import React from "react";
import { Utensils, ArrowLeft, Loader2 } from "lucide-react";

const AffichageRecettes = ({ set_chercher_recette, chargement_recettes = false }) => {
  
  // Simulation d'une liste vide pour l'instant
  const liste_recettes = [];

  return (
    <div className="carte-centrale recettes-panel">
      {/* ENTÊTE AVEC BOUTON RETOUR */}
      <div className="entete-recettes">
        <button 
          className="bouton-retour-icone" 
          onClick={() => set_chercher_recette(false)}
          title="Retour à l'inventaire"
        >
          <ArrowLeft size={24} />
        </button>
        <div className="titre-groupe">
          <Utensils size={32} color="#10b981" />
          <h1 className="titre-principal">Suggestions de Recettes</h1>
        </div>
      </div>

      <div className="contenu-recettes">
        {chargement_recettes ? (
          /* ÉTAT DE CHARGEMENT */
          <div className="etat-vide">
            <Loader2 className="animation-spin" size={48} color="#10b981" />
            <p>Calcul des meilleures recettes selon votre stock...</p>
          </div>
        ) : liste_recettes.length > 0 ? (
          /* AFFICHAGE DES CARTES (À REMPLIR PLUS TARD) */
          <div className="grille-recettes">
            {/* Tes futures cartes ici */}
          </div>
        ) : (
          /* ÉTAT VIDE / PLACEHOLDER */
          <div className="etat-vide">
            <p style={{ color: "#64748b", fontSize: "1.1rem" }}>
              Aucune recette trouvée pour le moment. 
            </p>
            <p style={{ color: "#94a3b8", fontSize: "0.9rem" }}>
              Le moteur de recherche sera bientôt disponible.
            </p>
          </div>
        )}
      </div>

      {/* BOUTON POUR REVENIR À LA GESTION */}
      <div style={{ marginTop: "30px", display: "flex", justifyContent: "center" }}>
        <button 
          className="bouton-action btn-stock-style" 
          onClick={() => set_chercher_recette(false)}
        >
          Retour à l'inventaire
        </button>
      </div>
    </div>
  );
};

export default AffichageRecettes;
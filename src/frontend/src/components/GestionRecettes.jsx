import React, { useState, useEffect } from "react";
import { BookOpen, Undo2, Loader2, RefreshCw, Eye } from "lucide-react";
import { listRecipes } from "../api/recetteApi";
import AfficherRecetteDetail from "./AfficherRecetteDetail"; // Import de la fiche détail
import "../styles/Gestion.css";

const GestionRecettes = ({ on_back, est_admin }) => {
  const [recettes, set_recettes] = useState([]);
  const [est_en_chargement, set_est_en_chargement] = useState(true);
  
  // NOUVEAU : État pour la recette sélectionnée
  const [recette_selectionnee, set_recette_selectionnee] = useState(null);

  const charger_recettes = async () => {
    set_est_en_chargement(true);
    try {
      const data = await listRecipes({ limit: 100 }); 
      set_recettes(data);
    } catch (err) {
      console.error("Erreur récupération recettes", err);
    } finally {
      set_est_en_chargement(false);
    }
  };

  useEffect(() => {
    charger_recettes();
  }, []);

  // CONDITION DE RENDU : Si une recette est sélectionnée, on affiche son détail
  if (recette_selectionnee) {
    return (
      <AfficherRecetteDetail 
        recette={recette_selectionnee} 
        onBack={() => set_recette_selectionnee(null)} 
        est_admin={est_admin}
      />
    );
  }

  return (
    <div className="carte-centrale gestion-panel">
      <div className="entete-gestion">
        <div className="titre-groupe">
          <BookOpen size={32} color="#8b5cf6" />
          <h1 className="titre-principal">Gestion des Recettes</h1>
        </div>
        <div className="barre-outils">
          <button 
            className="bouton-action btn-recette-style" 
            onClick={charger_recettes}
            style={{ backgroundColor: '#8b5cf6', color: 'white' }}
          >
            <RefreshCw size={18} className={est_en_chargement ? "animate-spin" : ""} /> Actualiser
          </button>
        </div>
      </div>

      {est_en_chargement ? (
        <div className="chargement-flex" style={{ padding: "40px", textAlign: "center" }}>
          <Loader2 className="animate-spin" size={32} color="#8b5cf6" style={{ margin: "0 auto 10px" }} />
          <p className="message-chargement">Chargement du catalogue des recettes...</p>
        </div>
      ) : (
        <div className="conteneur-tableau">
          <table className="tableau-gestion">
            <thead>
              <tr>
                <th>Nom de la recette</th>
                <th>Temps de préparation</th>
                <th>Proportion</th>
                <th style={{ textAlign: 'center' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {recettes.map((recette) => (
                <tr key={recette.recipe_id}>
                  {/* Rendre le nom cliquable également */}
                  <td 
                    className="texte-gras cellule-cliquable" 
                    onClick={() => set_recette_selectionnee(recette)}
                    style={{ cursor: 'pointer', color: '#5b21b6' }}
                  >
                    {recette.name}
                  </td>
                  <td>
                    <span className="badge-role" style={{ backgroundColor: "#f3f4f6", color: "#374151" }}>
                      {recette.prep_time} min
                    </span>
                  </td>
                  <td>
                    {recette.portions} {recette.portions > 1 ? "personnes" : "personne"}
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <button 
                      className="btn-icone" 
                      title="Voir le détail"
                      onClick={() => set_recette_selectionnee(recette)}
                    >
                      <Eye size={18} color="#8b5cf6" />
                    </button>
                  </td>
                </tr>
              ))}
              {recettes.length === 0 && (
                <tr>
                  <td colSpan="4" style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
                    Aucune recette trouvée en base de données.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <button className="bouton-retour-gestion" onClick={on_back}>
        <Undo2 size={18} /> Retour au menu
      </button>
    </div>
  );
};

export default GestionRecettes;
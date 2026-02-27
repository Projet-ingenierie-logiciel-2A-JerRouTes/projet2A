import React from "react";
import { Clock, Users, ArrowLeft, Eye } from "lucide-react";
import "../styles/AfficherRecettes.css";

const AffichageRecettes = ({ gerer_retour, donnees_recette, chargement }) => {
  return (
    <div className="recette-container">
      <h1 className="recette-titre-page">Suggestion de recette</h1>

      <div className="contenu">
        {chargement ? (
          <div style={{ padding: '40px' }}>Chargement du festin...</div>
        ) : donnees_recette ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            
            <h2 className="recette-nom">
              {donnees_recette.name}
            </h2>

            <div className="recette-image-box">
              <img 
                src={donnees_recette.image_url} 
                alt={donnees_recette.name} 
                className="recette-image"
                onError={(e) => { 
                  // Fallback stable si le scraping échoue (Erreur 404/Blocking)
                  e.target.src = "https://images.unsplash.com/photo-1495195129352-aec325a55b65?w=800"; 
                }}
              />
            </div>

            <div className="recette-infos-barre">
              <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <Clock size={16}/> {donnees_recette.prep_time} min
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <Users size={16}/> {donnees_recette.portions} pers.
              </span>
            </div>

            <div className="recette-description-box">
              <p className="recette-description-texte">
                "{donnees_recette.description}"
              </p>
            </div>

            <div className="recette-actions">
              <button onClick={gerer_retour} className="btn-recette btn-retour">
                <ArrowLeft size={18}/> Retour
              </button>

              <button 
                className="btn-recette btn-afficher"
                onClick={() => console.log("Lien recette:", donnees_recette.image_url)}
              >
                <Eye size={18}/> Afficher la recette
              </button>
            </div>
          </div>
        ) : (
          <div style={{ padding: '40px' }}>Aucune donnée disponible.</div>
        )}
      </div>
    </div>
  );
};

export default AffichageRecettes;
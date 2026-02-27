import React from "react";
import { Clock, Users } from "lucide-react";
import "../styles/AfficherRecettes.css";

const AfficherRecette = ({ recette }) => {
  if (!recette) return null;

  // Fonction pour afficher l'objet complet dans la console
  const gerer_clic = () => {
    console.log("Details de la recette cliquée :", recette);
  };

  return (
    <div className="bullet-recette-card" onClick={gerer_clic} style={{ cursor: 'pointer' }}>
      <div className="bullet-image-box">
        <img 
          src={recette.image_url} 
          alt={recette.name} 
          className="bullet-img"
          onError={(e) => {
            e.target.onerror = null; 
            e.target.src = "https://images.unsplash.com/photo-1495195129352-aec325a55b65?auto=format&fit=crop&q=80&w=400";
          }}
        />
      </div>

      <div className="bullet-content">
        <h3 className="bullet-nom">{recette.name}</h3>

        <div className="bullet-infos">
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Clock size={14}/> {recette.prep_time} min
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Users size={14}/> {recette.portions} pers.
          </span>
        </div>

        <div className="bullet-tags">
          {recette.tags?.slice(0, 2).map((tag, i) => (
            <span key={i} className="bullet-tag-badge">
              {tag.name}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AfficherRecette;
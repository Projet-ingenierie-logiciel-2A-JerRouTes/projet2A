import React from "react";
import { AlertTriangle } from "lucide-react"; // Optionnel : pour une icône d'avertissement
import "../styles/Confirmation.css"; // Nous allons créer ce fichier juste après

const Confirmation = ({ 
  ouvert, 
  on_confirmer, 
  on_annuler, 
  titre, 
  message, 
  texte_confirmer,
  couleur_confirmer // "rouge" ou "bleu"
}) => {
  // Si la modale n'est pas censée être ouverte, on ne l'affiche pas
  if (!ouvert) return null;

  return (
    // L'arrière-plan semi-transparent qui couvre toute la page
    <div className="modale-overlay" onClick={on_annuler}>
      {/* La fenêtre modale en elle-même */}
      {/* onClick={e => e.stopPropagation()} empêche de fermer la modale si on clique dedans */}
      <div className="modale-contenu" onClick={(e) => e.stopPropagation()}>
        <div className="modale-entete">
          <AlertTriangle size={24} color="#f59e0b" />
          <h2>{titre}</h2>
        </div>
        
        <div className="modale-corps">
          <p>{message}</p>
        </div>

        <div className="modale-actions">
          {/* Bouton Annuler (Bleu par défaut) */}
          <button className="btn-modale btn-annuler" onClick={on_annuler}>
            Retour
          </button>
          
          {/* Bouton Confirmer (Dynamique : Rouge ou Bleu) */}
          <button 
            className={`btn-modale btn-confirmer ${couleur_confirmer}`}
            onClick={on_confirmer}
          >
            {texte_confirmer}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Confirmation;
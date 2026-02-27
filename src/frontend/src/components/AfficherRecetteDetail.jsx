import React from "react";
import { Clock, Users, Tag, ArrowLeft } from "lucide-react";
import { useIngredientsRecette } from "../hooks/useIngredientsRecette"; // Import du nouveau hook
import "../styles/AfficherRecettes.css"; // Réutilise ton fichier CSS existant

const AfficherRecetteDetail = ({ recette, onBack }) => {
  // Utilisation du Hook pour croiser les données (catalogue + recette)
  const { ingredients_complets, chargement_ing } = useIngredientsRecette(recette); //

  if (!recette) return null; // Sécurité

  return (
    <div className="carte-centrale-detail shadow-2xl animate-fade">
      {/* 1. SECTION TITRE */}
      <h1 className="detail-titre-page">Fiche Recette</h1>
      
      <div className="contenu-detail">
        <h2 className="recette-nom-detail">{recette.name}</h2>

        {/* 2. SECTION IMAGE (AVEC SÉCURITÉ) */}
        <div className="recette-image-box-detail">
          <img 
            src={recette.image_url} // URL scrapée dans le Hook parent
            alt={recette.name} 
            className="recette-image-detail"
            onError={(e) => { 
              e.target.onerror = null; 
              e.target.src = "https://images.unsplash.com/photo-1495195129352-aec325a55b65?auto=format&fit=crop&q=80&w=800"; // Image de secours fiable
            }}
          />
        </div>

        {/* 3. SECTION INFOS : TEMPS ET PERSONNES */}
        <div className="recette-infos-detail">
          <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Clock size={18}/> {recette.prep_time} minutes
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Users size={18}/> {recette.portions} personnes
          </span>
        </div>

        {/* --- SÉPARATEUR HUMAINEMENT VISIBLE --- */}
        <hr className="detail-separator" />

        {/* 4. SECTION INGRÉDIENTS (ENRICHIE PAR LE HOOK) */}
        <div className="recette-ingredients-section">
          <h3 className="detail-section-titre">Liste des ingrédients :</h3>
          
          {chargement_ing ? (
            <div className="detail-chargement">Traduction des codes ingrédients...</div>
          ) : ingredients_complets && ingredients_complets.length > 0 ? (
            <ul className="detail-liste-ingredients">
              {ingredients_complets.map((ing, index) => (
                <li key={index} className="detail-ingredient-item">
                  <span className="puce-ingredient">•</span>
                  {ing.affichage_complet} {/* Ex: "3 de Œufs" (selon tes données BDD) */}
                </li>
              ))}
            </ul>
          ) : (
            <div className="detail-chargement">Aucun ingrédient renseigné pour cette recette.</div>
          )}
        </div>

        {/* --- SÉPARATEUR HUMAINEMENT VISIBLE --- */}
        <hr className="detail-separator" />

        {/* BOUTON RETOUR UNIQUE EN BAS */}
        <div className="recette-actions-detail">
          <button onClick={onBack} className="btn-recette-detail btn-retour-final">
            <ArrowLeft size={18}/> Retour à la grille
          </button>
        </div>
      </div>
    </div>
  );
};

export default AfficherRecetteDetail;
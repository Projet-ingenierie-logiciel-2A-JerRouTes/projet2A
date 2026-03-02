import React from "react";
import { Clock, Users, ArrowLeft, Loader2, AlertCircle, Pencil, Trash2 } from "lucide-react";
import { useIngredientsRecette } from "../hooks/useIngredientsRecette";
import "../styles/AfficherRecettes.css";

const AfficherRecetteDetail = ({ recette, onBack, est_admin}) => {
  // 1. Extraction des données du hook (incluant image_temp de Pixabay)
  const { ingredients_complets, chargement_ing, image_temp } = useIngredientsRecette(recette);

  if (!recette) return null;

  // 2. Logique de sélection de l'image (Priorité : BDD > Pixabay > Secours Unsplash)
  const source_visuelle = recette.image_url || image_temp || "https://images.unsplash.com/photo-1495195129352-aec325a55b65?w=800";

  console.log("Détail Recette - Suis-je admin ?", est_admin);

  return (
    <div className="carte-centrale-detail shadow-2xl animate-fade">
      {/* SECTION TITRE */}
      <h1 className="detail-titre-page">Fiche Recette</h1>

      {/* Les boutons n'apparaissent que si est_admin est true */}
      {est_admin && (
        <div className="admin-actions-bar">
          <button className="btn-admin-edit">
            <Pencil size={18} /> Modifier la recette
          </button>
          <button className="btn-admin-delete">
            <Trash2 size={18} /> Supprimer la recette
          </button>
        </div>
      )}
      
      <div className="contenu-detail">
        <h2 className="recette-nom-detail">{recette.name}</h2>

        {/* SECTION IMAGE : Utilise l'image temporaire si image_url est vide */}
        <div className="recette-image-box-detail">
          <img 
            src={source_visuelle} 
            alt={recette.name} 
            className="recette-image-detail"
            onError={(e) => { 
              e.target.onerror = null; 
              e.target.src = "https://images.unsplash.com/photo-1495195129352-aec325a55b65?w=800"; 
            }}
          />
          {!recette.image_url && image_temp && (
            <span className="badge-source-image">Image suggérée par Pixabay</span>
          )}
        </div>

        {/* SECTION INFOS : TEMPS ET PERSONNES */}
        <div className="recette-infos-detail">
          <span className="info-item-detail">
            <Clock size={18} color="#64748b"/> {recette.prep_time} minutes
          </span>
          <span className="info-item-detail">
            <Users size={18} color="#64748b"/> {recette.portions} {recette.portions > 1 ? "personnes" : "personne"}
          </span>
        </div>

        <hr className="detail-separator" />

        {/* SECTION INGRÉDIENTS */}
        <div className="recette-ingredients-section">
          <h3 className="detail-section-titre">Liste des ingrédients :</h3>
          
          {chargement_ing ? (
            <div className="detail-chargement-flex">
              <Loader2 className="animate-spin" size={20} />
              <span>Récupération des détails...</span>
            </div>
          ) : ingredients_complets && ingredients_complets.length > 0 ? (
            <ul className="detail-liste-ingredients">
              {ingredients_complets.map((ing, index) => (
                <li key={index} className="detail-ingredient-item">
                  <span className="puce-ingredient">•</span>
                  {ing.affichage_complet}
                </li>
              ))}
            </ul>
          ) : (
            <div className="message-liste-vide">
              <AlertCircle size={18} />
              <span>Aucun ingrédient renseigné pour cette recette dans la base de données.</span>
            </div>
          )}
        </div>

        <hr className="detail-separator" />

        {/* ACTIONS */}
        <div className="recette-actions-detail">
          <button onClick={onBack} className="btn-recette-detail btn-retour-final">
            <ArrowLeft size={18}/> Retour à la liste
          </button>
        </div>
      </div>
    </div>
  );
};

export default AfficherRecetteDetail;
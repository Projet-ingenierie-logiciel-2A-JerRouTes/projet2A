import React from "react";
import { Clock, Users, ArrowLeft, Loader2, Utensils } from "lucide-react";
import { useIngredientsRecette } from "../hooks/useIngredientsRecette";
import "../styles/AfficherRecettes.css";

const AfficherRecetteDetail = ({ recette, onBack, est_admin, utilisateur, onRealiser }) => {
  const { ingredients_complets, chargement_ing, image_temp } = useIngredientsRecette(recette);

  if (!recette) return null;

  const source_visuelle = recette.image_url || image_temp || "https://images.unsplash.com/photo-1495195129352-aec325a55b65?w=800";

  return (
    <div className="carte-centrale-detail animate-fade">
      <h1 className="detail-titre-page" style={{ color: "#000", textAlign: "center", fontWeight: "800", marginBottom: "10px" }}>
        Fiche Recette
      </h1>

      {/* ZONE DE SCROLL INTERNE : Empêche la carte de déborder de l'écran */}
      <div className="scroll-contenu">
        <h2 className="recette-nom-detail" style={{ color: "#22c55e", textAlign: "center", marginBottom: "20px" }}>
          {recette.name}
        </h2>

        <div className="recette-image-box-detail">
          <img 
            src={source_visuelle} 
            alt={recette.name} 
            className="recette-image-detail"
            style={{ width: "100%", borderRadius: "15px", objectFit: "cover" }}
          />
        </div>

        <div className="recette-infos-detail" style={{ display: "flex", justifyContent: "center", gap: "20px", marginTop: "15px", color: "#64748b" }}>
          <span style={{ display: "flex", alignItems: "center", gap: "5px" }}>
            <Clock size={18} /> {recette.prep_time} min
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: "5px" }}>
            <Users size={18} /> {recette.portions} pers.
          </span>
        </div>

        <hr className="detail-separator" style={{ margin: "20px 0", border: "none", borderBottom: "1px solid #e2e8f0" }} />

        <div className="recette-ingredients-section">
          <h3 className="detail-section-titre" style={{ marginBottom: "15px", textAlign: "left" }}>Liste des ingrédients :</h3>
          {chargement_ing ? (
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <Loader2 className="animate-spin" size={20} />
              <span>Chargement des détails...</span>
            </div>
          ) : (
            <ul style={{ listStyle: "none", padding: 0 }}>
              {ingredients_complets?.map((ing, index) => (
                <li key={index} style={{ marginBottom: "8px", display: "flex", alignItems: "center", gap: "10px", textAlign: "left" }}>
                  <span style={{ color: "#22c55e" }}>•</span>
                  {ing.affichage_complet}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* PIED DE PAGE FIXE : Toujours visible en bas de la carte */}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "10px", marginTop: "10px", paddingTop: "10px", borderTop: "1px solid #eee" }}>
        {utilisateur && !est_admin && (
          <button 
            className="bouton-action" 
            style={{ backgroundColor: "#22c55e", color: "white", padding: "12px 60px", borderRadius: "30px", border: "none", fontWeight: "700", display: "flex", alignItems: "center", gap: "10px", cursor: "pointer" }}
            onClick={onRealiser}
          >
            <Utensils size={20} /> Réaliser cette recette
          </button>
        )}

        <button className="bouton-retour-gestion" onClick={onBack}>
          <ArrowLeft size={18}/> Retour à la liste
        </button>
      </div>
    </div>
  );
};

export default AfficherRecetteDetail;
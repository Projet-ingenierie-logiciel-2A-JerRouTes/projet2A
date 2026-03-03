import React from "react";
import { Wheat, Edit, Trash2, Undo2, Tag, Info, Scale } from "lucide-react";

const AfficherIngredient = ({ ingredient, on_back, on_edit, on_delete }) => {
  if (!ingredient) return null;

  return (
    <div className="carte-centrale gestion-panel">
      {/* 1. TITRE EN PREMIER (Noir) */}
      <div style={{ textAlign: "center", marginBottom: "20px" }}>
        <h1 className="titre-principal" style={{ color: "#000000", fontSize: "2.5rem", fontWeight: "800" }}>
          Ingrédient : {ingredient.name}
        </h1>
      </div>

      {/* 2. BOUTONS D'ACTION (Zone pointillée) */}
      <div style={{ 
        border: "1px dashed #cbd5e1", 
        borderRadius: "12px", 
        padding: "15px", 
        display: "flex", 
        justifyContent: "center", 
        gap: "15px",
        marginBottom: "30px",
        backgroundColor: "rgba(248, 250, 252, 0.5)"
      }}>
        <button 
          className="bouton-action btn-recette-style" 
          onClick={() => on_edit(ingredient.ingredient_id)}
        >
          <Edit size={18} /> Modifier l'ingrédient
        </button>
        <button 
          className="bouton-action btn-stock-style" 
          onClick={() => on_delete(ingredient.ingredient_id)}
        >
          <Trash2 size={18} /> Supprimer l'ingrédient
        </button>
      </div>

      {/* 3. DÉTAILS DE L'INGRÉDIENT */}
      <div className="details-container" style={{ padding: "0 20px", display: "grid", gap: "25px" }}>
        
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <Tag size={20} color="#22c55e" />
          <span style={{ fontSize: "1.1rem" }}>
            <strong>Catégorie :</strong> {ingredient.category || "Non classé"}
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <Scale size={20} color="#22c55e" />
          <span style={{ fontSize: "1.1rem" }}>
            <strong>Unité par défaut :</strong> {ingredient.unit}
          </span>
        </div>

        <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: "20px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "15px" }}>
            <Info size={20} color="#22c55e" />
            <span style={{ fontSize: "1.1rem" }}><strong>Informations nutritionnelles :</strong></span>
          </div>
          {/* Bloc d'infos supplémentaires si elles existent dans tes données */}
          <div style={{ 
            marginLeft: "32px", 
            padding: "15px", 
            backgroundColor: "#f0fdf4", 
            borderRadius: "12px", 
            color: "#166534",
            fontSize: "0.95rem"
          }}>
            L'identifiant unique de cet ingrédient est <strong>#{ingredient.ingredient_id}</strong>. 
            Il est utilisé pour le calcul automatique des stocks et les suggestions de recettes.
          </div>
        </div>
      </div>

      {/* 4. BOUTON RETOUR */}
      <div style={{ display: "flex", justifyContent: "center", marginTop: "40px" }}>
        <button className="bouton-retour-gestion" onClick={on_back}>
            <Undo2 size={18} /> Retour à la liste
        </button>
      </div>
    </div>
  );
};

export default AfficherIngredient;

import React from "react";
import { Package, Edit, Trash2, Undo2, User, List } from "lucide-react";

const AfficherStock = ({ stock, on_back, on_edit, on_delete }) => {
  if (!stock) return null;

  return (
    <div className="carte-centrale gestion-panel">
      {/* 1. TITRE EN PREMIER (Noir) */}
      <div style={{ textAlign: "center", marginBottom: "20px" }}>
        <h1 className="titre-principal" style={{ color: "#000000", fontSize: "2.5rem", fontWeight: "800" }}>
          Fiche Stock : {stock.name}
        </h1>
      </div>

      {/* 2. BOUTONS EN DESSOUS (Zone pointillée) */}
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
        <button className="bouton-action btn-recette-style" onClick={() => on_edit(stock.stock_id)}>
          <Edit size={18} /> Modifier le stock
        </button>
        <button className="bouton-action btn-stock-style" onClick={() => on_delete(stock.stock_id)}>
          <Trash2 size={18} /> Supprimer le stock
        </button>
      </div>

      {/* 3. DÉTAILS */}
      <div className="details-container" style={{ padding: "0 20px", display: "grid", gap: "25px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <User size={20} color="#64748b" />
          <span style={{ fontSize: "1.1rem" }}><strong>Associé à :</strong> <span style={{ color: "#94a3b8" }}>Vide</span></span>
        </div>
        <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: "20px" }}>
           <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "15px" }}>
            <List size={20} color="#64748b" />
            <span style={{ fontSize: "1.1rem" }}><strong>Liste des ingrédients :</strong></span>
          </div>
          <p style={{ color: "#94a3b8", textAlign: "center", fontStyle: "italic" }}>
             Aucun ingrédient renseigné pour ce stock.
          </p>
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

export default AfficherStock;
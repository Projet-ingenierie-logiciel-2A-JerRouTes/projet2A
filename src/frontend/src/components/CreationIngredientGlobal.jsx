import React, { useState } from "react";
import { Tag, Save, ChevronLeft, Layers } from "lucide-react";
import { createIngredient } from "../api/ingredientsApi";
import "../styles/Auth.css"; 

function CreationIngredientGlobal({ onAdd, onCancel }) {
  const [nom, set_nom] = useState("");
  const [unit, set_unit] = useState("PIECE");

  const libelles_unites = {
    GRAM: "g",
    KILOGRAM: "kg",
    MILIGRAM: "mg",
    MILLILITER: "ml",
    LITER: "L",
    PIECE: "pcs",
  };

  const handle_submit = async (e) => {
    e.preventDefault();
    if (!nom) return alert("Le nom est obligatoire");

    try {
      await createIngredient(nom, unit);
      onAdd(); // Rafraîchit la liste dans le parent
    } catch (error) {
      console.error("❌ Erreur création ingrédient :", error);
      alert("Erreur lors de la création.");
    }
  };

  return (
    <div className="conteneur-auth">
      <div className="carte-auth" style={{ maxWidth: "450px" }}>
        <div className="entete-auth">
          <h1 className="titre-auth">Nouveau référentiel</h1>
        </div>

        <form onSubmit={handle_submit}>
          <div className="groupe-champ">
            <label><Tag size={16} /> Nom de l'ingrédient</label>
            <input
              type="text"
              className="entree-texte"
              placeholder="Ex: Tomate, Farine..."
              value={nom}
              onChange={(e) => set_nom(e.target.value)}
              required
            />
          </div>

          <div className="groupe-champ">
            <label><Layers size={16} /> Unité de mesure par défaut</label>
            <select 
              className="entree-texte" 
              value={unit}
              onChange={(e) => set_unit(e.target.value)}
            >
              {Object.entries(libelles_unites).map(([key, label]) => (
                <option key={key} value={key}>{label}</option>
              ))}
            </select>
          </div>

          <div className="barre-actions">
            <button type="submit" className="bouton-valider" style={{ backgroundColor: "#10b981" }}>
              <Save size={18} /> Enregistrer
            </button>
            <button type="button" onClick={onCancel} className="bouton-retour" style={{ backgroundColor: "#ef4444", color: "white" }}>
              <ChevronLeft size={18} /> Annuler
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreationIngredientGlobal;
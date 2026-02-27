import React, { useState } from "react";
import { ChevronLeft, Save, Package, Tag, Calendar, Hash } from "lucide-react";
import { addStockItem } from "../api/stockApi";
import { createIngredient } from "../api/ingredientsApi"; // Import de ta nouvelle fonction
import "../styles/Auth.css"; 

function AddIngredientForm({ catalogue, liste_stocks, initial_stock_id, onAdd, onCancel }) {
  const [selected_stock_id, set_selected_stock_id] = useState(initial_stock_id || "");
  const [search_term, set_search_term] = useState("");
  const [selected_ingredient, set_selected_ingredient] = useState(null);
  const [quantity, set_quantity] = useState("");
  const [expiry_date, set_expiry_date] = useState("");
  const [show_suggestions, set_show_suggestions] = useState(false);
  
  // État pour l'unité manuelle si l'ingrédient est nouveau
  const [manual_unit, set_manual_unit] = useState("GRAM");

  const libelles_unites = {
    GRAM: "g",
    KILOGRAM: "kg",
    MILIGRAM: "mg",
    MILLILITER: "ml",
    LITER: "L",
    CENTIMETER: "cm",
    PIECE: "pcs",
  };

  const suggestions = (catalogue || []).filter((ing) =>
    ing.name.toLowerCase().includes(search_term.toLowerCase())
  );

  const handle_select = (ing) => {
    set_search_term(ing.name);
    set_selected_ingredient(ing);
    set_show_suggestions(false);
  };

  const handle_submit = async (e) => {
    e.preventDefault();

    if (!selected_stock_id || !quantity || !expiry_date || !search_term) {
      alert("Veuillez remplir tous les champs.");
      return;
    }

    try {
      let final_ingredient_id;

      if (selected_ingredient) {
        // Cas 1 : L'ingrédient existe dans le catalogue
        final_ingredient_id = selected_ingredient.ingredient_id;
      } else {
        // Cas 2 : Nouvel ingrédient (longueur vide ou pas de clic)
        // On le crée d'abord dans le référentiel via ingredientsApi.js
        const new_ing = await createIngredient(search_term, manual_unit);
        final_ingredient_id = new_ing.ingredient_id;
      }

      // Cas commun : Ajout au stock avec l'ID obtenu
      await addStockItem(
        selected_stock_id, 
        final_ingredient_id,
        quantity, 
        expiry_date
      ); 

      onAdd(); 
    } catch (error) {
      console.error("❌ Erreur lors de l'opération :", error.response?.data || error);
      alert("Erreur lors de l'ajout. Vérifiez la console.");
    }
  };

  return (
    <div className="conteneur-auth">
      <div className="carte-auth" style={{ maxWidth: "500px" }}>
        <div className="entete-auth">
          <h1 className="titre-auth">Ajouter un ingrédient</h1>
        </div>

        <form onSubmit={handle_submit}>
          {/* SÉLECTION DU STOCK */}
          <div className="groupe-champ">
            <label><Package size={16} /> Inventaire de destination</label>
            <select 
              className="entree-texte" 
              value={selected_stock_id} 
              onChange={(e) => set_selected_stock_id(e.target.value)} 
              required
            >
              <option value="" disabled>Choisir un stock...</option>
              {(liste_stocks || []).map((s) => (
                <option key={s.stock_id} value={s.stock_id}>{s.name}</option>
              ))}
            </select>
          </div>

          {/* NOM ET AUTOCOMPLÉTION */}
          <div className="groupe-champ" style={{ position: "relative" }}>
            <label><Tag size={16} /> Nom de l'ingrédient</label>
            <input
              type="text"
              className="entree-texte"
              placeholder="Chercher ou saisir un nom..."
              value={search_term}
              onChange={(e) => {
                set_search_term(e.target.value);
                set_show_suggestions(true);
                set_selected_ingredient(null); // On reset la sélection si on modifie le texte
              }}
              onFocus={() => set_show_suggestions(true)}
              required
            />
            {show_suggestions && search_term && suggestions.length > 0 && (
              <div className="suggestions-list" style={{ 
                position: "absolute", zIndex: 10, width: "100%", background: "white", 
                border: "1px solid #e2e8f0", borderRadius: "12px", 
                boxShadow: "0 10px 15px -3px rgba(0,0,0,0.1)", 
                maxHeight: "180px", overflowY: "auto" 
              }}>
                {suggestions.map((ing) => (
                  <div key={ing.ingredient_id} className="suggestion-item" 
                    onClick={() => handle_select(ing)}
                    style={{ padding: "12px", cursor: "pointer", borderBottom: "1px solid #f1f5f9", display: "flex", justifyContent: "space-between" }}>
                    <span style={{ fontWeight: "600" }}>{ing.name}</span>
                    <small style={{ color: '#64748b' }}>({libelles_unites[ing.unit] || ing.unit})</small>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* QUANTITÉ ET UNITÉ DYNAMIQUE */}
          <div className="groupe-champ">
            <label>
              <Hash size={16} /> Quantité 
              {selected_ingredient ? ` (${libelles_unites[selected_ingredient.unit] || selected_ingredient.unit})` : " et Unité"}
            </label>
            <div style={{ display: "flex", gap: "10px" }}>
              <input 
                type="number" 
                className="entree-texte" 
                style={{ flex: 1 }}
                value={quantity} 
                onChange={(e) => set_quantity(e.target.value)} 
                required 
                min="0.01" 
                step="0.01" 
              />
              
              {!selected_ingredient && (
                <select 
                  className="entree-texte" 
                  style={{ width: "110px" }}
                  value={manual_unit}
                  onChange={(e) => set_manual_unit(e.target.value)}
                >
                  {Object.entries(libelles_unites).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              )}
            </div>
          </div>

          {/* DATE DE PÉREMPTION */}
          <div className="groupe-champ">
            <label><Calendar size={16} /> Date de péremption</label>
            <input 
              type="date" 
              className="entree-texte" 
              value={expiry_date} 
              onChange={(e) => set_expiry_date(e.target.value)} 
              required 
            />
          </div>

          <div className="barre-actions">
            <button type="submit" className="bouton-valider" style={{ backgroundColor: "#3b82f6" }}>
              <Save size={18} /> Valider
            </button>
            <button type="button" onClick={onCancel} className="bouton-retour" style={{ backgroundColor: "#ef4444", color: "white", border: "none" }}>
              <ChevronLeft size={18} /> Annuler
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AddIngredientForm;
import React, { useState } from "react";
import { ChevronLeft, Save, Package, Tag, Calendar, Hash, AlertCircle } from "lucide-react";
import { addStockItem } from "../api/stockApi";
import "../styles/Auth.css"; 

function AddIngredientForm({ catalogue, liste_stocks, initial_stock_id, onAdd, onCancel }) {
  const [selected_stock_id, set_selected_stock_id] = useState(initial_stock_id || "");
  const [search_term, set_search_term] = useState("");
  const [selected_ingredient, set_selected_ingredient] = useState(null);
  const [quantity, set_quantity] = useState("");
  const [expiry_date, set_expiry_date] = useState("");
  const [show_suggestions, set_show_suggestions] = useState(false);

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

    // --- NOUVELLE LOGIQUE DE BLOCAGE ---
    // Si aucun ingrédient du catalogue n'est sélectionné, on bloque l'envoi
    if (!selected_ingredient) {
      alert("Ajout d'ingredient personnelle n'est pas encore autorisée. Veuillez sélectionner un élément dans la liste.");
      return;
    }

    if (!selected_stock_id || !quantity || !expiry_date) {
      alert("Veuillez remplir tous les champs.");
      return;
    }

    try {
      // Signature : addStockItem(stock_id, ingredient_id, quantity, expiration_date)
      await addStockItem(
        selected_stock_id, 
        selected_ingredient.ingredient_id, // On utilise l'ID réel du catalogue
        quantity, 
        expiry_date
      ); 

      onAdd(); 
    } catch (error) {
      console.error("❌ Erreur lors de l'envoi :", error.response?.data || error);
      alert("Erreur serveur. Vérifiez la console.");
    }
  };

  return (
    <div className="conteneur-auth">
      <div className="carte-auth" style={{ maxWidth: "500px" }}>
        <div className="entete-auth">
          <h1 className="titre-auth">Ajouter un ingrédient</h1>
        </div>

        <form onSubmit={handle_submit}>
          {/* STOCK */}
          <div className="groupe-champ">
            <label><Package size={16} /> Inventaire de destination</label>
            <select className="entree-texte" value={selected_stock_id} onChange={(e) => set_selected_stock_id(e.target.value)} required>
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
              placeholder="Chercher dans le catalogue..."
              value={search_term}
              onChange={(e) => {
                set_search_term(e.target.value);
                set_show_suggestions(true);
                set_selected_ingredient(null);
              }}
              onFocus={() => set_show_suggestions(true)}
              required
            />
            {show_suggestions && search_term && (
              <div className="suggestions-list" style={{ position: "absolute", zIndex: 10, width: "100%", background: "white", border: "1px solid #e2e8f0", borderRadius: "12px", boxShadow: "0 10px 15px -3px rgba(0,0,0,0.1)", maxHeight: "180px", overflowY: "auto" }}>
                {suggestions.length > 0 ? (
                  suggestions.map((ing) => (
                    <div key={ing.ingredient_id} className="suggestion-item" 
                      onClick={() => handle_select(ing)}
                      style={{ padding: "12px", cursor: "pointer", borderBottom: "1px solid #f1f5f9", display: "flex", justifyContent: "space-between" }}>
                      <span style={{ fontWeight: "600" }}>{ing.name}</span>
                      <small style={{ color: '#64748b' }}>({ing.unit})</small>
                    </div>
                  ))
                ) : (
                  // MESSAGE D'AVERTISSEMENT SI AUCUN RÉSULTAT
                  <div style={{ padding: "12px", color: "#ef4444", fontSize: "0.85rem", display: "flex", alignItems: "center", gap: "8px" }}>
                    <AlertCircle size={16} />
                    <span>ajout d'ingredient personnelle n'est pas encore autorisée</span>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* QUANTITÉ */}
          <div className="groupe-champ">
            <label><Hash size={16} /> Quantité {selected_ingredient && `(${selected_ingredient.unit})`}</label>
            <input type="number" className="entree-texte" value={quantity} onChange={(e) => set_quantity(e.target.value)} required min="0.01" step="0.01" />
          </div>

          {/* DATE */}
          <div className="groupe-champ">
            <label><Calendar size={16} /> Date de péremption</label>
            <input type="date" className="entree-texte" value={expiry_date} onChange={(e) => set_expiry_date(e.target.value)} required />
          </div>

          <div className="barre-actions">
            <button type="submit" className="bouton-valider" style={{ backgroundColor: selected_ingredient ? "#3b82f6" : "#94a3b8" }}>
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
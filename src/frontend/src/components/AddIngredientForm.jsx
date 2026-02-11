import { useState } from "react";

function AddIngredientForm({ catalogue, onAdd, onCancel }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedIngredient, setSelectedIngredient] = useState(null);
  const [quantity, setQuantity] = useState("");
  const [expiryDate, setExpiryDate] = useState("");
  const [customUnit, setCustomUnit] = useState("PIECE"); // Clé par défaut
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Mapping basé sur ta classe Unit.py pour l'affichage
  const unitLabels = {
    GRAM: "g",
    KILOGRAM: "kg",
    MILIGRAM: "mg",
    MILLILITER: "ml",
    LITER: "L",
    CENTIMETER: "cm",
    PIECE: "pcs",
  };

  const suggestions = catalogue.filter((ing) =>
    ing.name.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  const handleSelect = (ing) => {
    setSearchTerm(ing.name);
    setSelectedIngredient(ing);
    setShowSuggestions(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (searchTerm.trim() === "" || !quantity || !expiryDate) return;

    onAdd({
      id_ingredient: selectedIngredient
        ? selectedIngredient.id_ingredient
        : null,
      name: searchTerm,
      quantity: parseFloat(quantity),
      expiry_date: expiryDate,
      // On envoie la clé (ex: "GRAM") au backend Python
      unit: selectedIngredient ? selectedIngredient.unit : customUnit,
    });
  };

  return (
    <div className="login-form">
      <form
        onSubmit={handleSubmit}
        style={{
          width: "100%",
          display: "flex",
          flexDirection: "column",
          gap: "15px",
        }}
      >
        {/* 1. NOM / RECHERCHE */}
        <div className="input-group" style={{ overflow: "visible" }}>
          <input
            type="text"
            placeholder="Nom de l'ingrédient..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setShowSuggestions(true);
              setSelectedIngredient(null);
            }}
            onFocus={() => setShowSuggestions(true)}
            required
          />

          {showSuggestions && searchTerm && (
            <div className="suggestions-list">
              {suggestions.map((ing) => (
                <div
                  key={ing.id_ingredient}
                  className="suggestion-item"
                  onClick={() => handleSelect(ing)}
                >
                  {ing.name} <small>({unitLabels[ing.unit] || ing.unit})</small>
                </div>
              ))}
              {suggestions.length === 0 && (
                <div
                  className="suggestion-item"
                  style={{ color: "#7f21ab", fontWeight: "bold" }}
                  onClick={() => setShowSuggestions(false)}
                >
                  ✨ Créer "{searchTerm}"
                </div>
              )}
            </div>
          )}
        </div>

        {/* 2. QUANTITÉ + SÉLECTEUR D'UNITÉ (Basé sur Unit.py) */}
        <div className="input-group">
          <input
            type="number"
            placeholder="Quantité"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            required
            min="0.01"
            step="0.01"
            style={{ flex: 1 }}
          />

          {selectedIngredient ? (
            <span className="unit-badge">
              {unitLabels[selectedIngredient.unit] || selectedIngredient.unit}
            </span>
          ) : (
            <select
              className="unit-badge"
              value={customUnit}
              onChange={(e) => setCustomUnit(e.target.value)}
              style={{
                border: "none",
                background: "transparent",
                cursor: "pointer",
                outline: "none",
                width: "auto",
              }}
            >
              {Object.entries(unitLabels).map(([key, label]) => (
                <option key={key} value={key}>
                  {label}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* 3. DATE D'EXPIRATION */}
        <div className="input-group">
          <input
            type="date"
            value={expiryDate}
            onChange={(e) => setExpiryDate(e.target.value)}
            required
          />
        </div>

        {/* 4. BOUTONS */}
        <div style={{ display: "flex", gap: "10px", width: "100%" }}>
          <button type="submit" className="bouton">
            Enregistrer
          </button>
          <button
            type="button"
            className="bouton"
            onClick={onCancel}
            style={{ backgroundColor: "#444" }}
          >
            Annuler
          </button>
        </div>
      </form>
    </div>
  );
}

export default AddIngredientForm;

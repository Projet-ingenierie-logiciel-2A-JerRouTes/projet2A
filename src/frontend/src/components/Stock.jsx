import { useState } from "react";
import AddIngredientForm from "./AddIngredientForm";
import { useStockData } from "../hooks/useStockData";

const unitLabels = {
  GRAM: "g",
  KILOGRAM: "kg",
  MILIGRAM: "mg",
  MILLILITER: "ml",
  LITER: "L",
  CENTIMETER: "cm",
  PIECE: "pcs",
};

function Stock({ user, onLogout, onNavigateAdmin }) {
  const [showForm, setShowForm] = useState(false);

  // On utilise notre "cerveau" externe
  const { formattedStock, catalogue, loading, error, setItems, setCatalogue } =
    useStockData(user, unitLabels);

  const handleAddIngredient = (newIngredientData) => {
    // Logique d'ajout local pour mettre à jour l'affichage immédiatement
    let finalId = newIngredientData.id_ingredient || Date.now();
    const nouveauLot = {
      quantity: newIngredientData.quantity,
      expiry_date: newIngredientData.expiry_date,
      name: newIngredientData.name,
      ingredient_id: finalId,
    };

    setItems((prev) => ({
      ...prev,
      [finalId]: [...(prev[finalId] || []), nouveauLot],
    }));
    setShowForm(false);
  };

  //if (loading) return <div className="container-principal"><p className="message">Chargement des données en cours...</p></div>;

  return (
    <div className="container-principal">
      <div className="sous-container">
        <div className="login-form" style={{ maxWidth: "800px" }}>
          <h3 className="stock-titre">
            {user
              ? `Inventaire de ${user.user?.username || user.username}`
              : "Stock (Mode Invité)"}
          </h3>

          {!showForm ? (
            <div className="stock-table-container">
              {formattedStock.length > 0 ? (
                <table className="stock-table">
                  <thead>
                    <tr>
                      <th>Ingrédient</th>
                      <th>Quantité</th>
                      <th>Expiration</th>
                    </tr>
                  </thead>
                  <tbody>
                    {formattedStock.map((item) => (
                      <tr key={item.id}>
                        <td
                          className="ingredient-name"
                          style={{ textTransform: "capitalize" }}
                        >
                          {item.nom}
                        </td>
                        <td>{item.qte}</td>
                        <td className="expiry-date">{item.expiration}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p
                  style={{
                    color: "gray",
                    padding: "20px",
                    textAlign: "center",
                  }}
                >
                  Votre frigo est vide (instabilité thermique ?).
                </p>
              )}
            </div>
          ) : (
            <AddIngredientForm
              catalogue={catalogue}
              onAdd={handleAddIngredient}
              onCancel={() => setShowForm(false)}
            />
          )}

          {!showForm && (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "10px",
                marginTop: "20px",
              }}
            >
              <button className="bouton" onClick={() => setShowForm(true)}>
                Ajouter un ingrédient
              </button>
              <button
                className="bouton"
                style={{ backgroundColor: "#6c757d" }}
                onClick={onLogout}
              >
                Déconnexion
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Bloc Administration */}
      {user && (user.user?.status === "admin" || user.status === "admin") && (
        <div className="sous-container" style={{ marginTop: "20px" }}>
          <div
            className="login-form"
            style={{ maxWidth: "800px", border: "2px solid gold" }}
          >
            <h3 className="stock-titre" style={{ color: "gold" }}>
              🛡️ Administration Système
            </h3>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "10px",
                marginTop: "15px",
              }}
            >
              <button
                className="bouton"
                onClick={() => onNavigateAdmin("users")}
              >
                Gérer utilisateurs
              </button>
              <button
                className="bouton"
                onClick={() => onNavigateAdmin("ingredients")}
              >
                Gérer ingrédients
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="sous-container">
          <div className="message message-negatif">🛑 {error}</div>
        </div>
      )}
    </div>
  );
}

export default Stock;

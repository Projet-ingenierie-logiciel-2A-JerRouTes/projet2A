import { useState, useEffect } from "react";
import AddIngredientForm from "./AddIngredientForm";
import { getAllIngredients, getStockDetails } from "../api/stockApi";

const unitLabels = {
  GRAM: "g",
  KILOGRAM: "kg",
  MILIGRAM: "mg",
  MILLILITER: "ml",
  LITER: "L",
  CENTIMETER: "cm",
  PIECE: "pcs",
};

function Stock({ user, onLogout }) {
  const [items, setItems] = useState({});
  const [catalogue, setCatalogue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error_message, setErrorMessage] = useState("");
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    const loadAllData = async () => {
      console.log("--- 🏁 Initialisation du chargement ---");
      setLoading(true);
      setErrorMessage("");
      try {
        const dataIngr = await getAllIngredients();
        setCatalogue(dataIngr);

        if (user && user.id_stock) {
          const dataStock = await getStockDetails(user.id_stock);
          setItems(dataStock.items_by_ingredient || {});
        }
      } catch (err) {
        console.error("❌ Erreur :", err.response?.data || err.message);
        setErrorMessage(
          err.response?.data?.detail ||
            "Erreur lors de la récupération des données",
        );
      } finally {
        setLoading(false);
      }
    };
    loadAllData();
  }, [user]);

  const getIngredientInfo = (id) => {
    return catalogue.find((i) => String(i.id_ingredient) === String(id));
  };

  const handleAddIngredient = (newIngredientData) => {
    // ... (Logique d'ajout inchangée) ...
    setShowForm(false);
  };

  return (
    <div className="container-principal">
      <div className="sous-container">
        <div className="login-form" style={{ maxWidth: "800px" }}>
          <h3 className="stock-titre">
            {user ? `Inventaire de ${user.pseudo}` : "Stock (Mode Invité)"}
          </h3>

          {loading ? (
            <p className="message">Broyage des données en cours...</p>
          ) : (
            <>
              {!showForm && (
                <div className="stock-table-container">
                  {Object.keys(items).length > 0 ? (
                    <table className="stock-table">
                      <thead>
                        <tr>
                          <th>Ingrédient</th>
                          <th>Quantité</th>
                          <th>Expiration</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(items).map(([id, lots]) => {
                          const info = getIngredientInfo(id);
                          return lots.map((lot, i) => (
                            <tr key={`${id}-${i}`}>
                              <td
                                className="ingredient-name"
                                style={{ textTransform: "capitalize" }}
                              >
                                {info ? info.name : lot.name || id}
                              </td>
                              <td>
                                {lot.quantity}{" "}
                                {unitLabels[info ? info.unit : lot.unit] ||
                                  (info ? info.unit : lot.unit)}
                              </td>
                              <td className="expiry-date">{lot.expiry_date}</td>
                            </tr>
                          ));
                        })}
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
                      Stock vide. Instabilité thermique détectée ?
                    </p>
                  )}
                </div>
              )}

              {showForm && (
                <AddIngredientForm
                  catalogue={catalogue}
                  onAdd={handleAddIngredient}
                  onCancel={() => setShowForm(false)}
                />
              )}

              {/* SECTION DES BOUTONS EN BAS */}
              {!showForm && (
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "10px",
                    marginTop: "20px",
                  }}
                >
                  <button
                    type="button"
                    className="bouton"
                    onClick={() => setShowForm(true)}
                  >
                    Ajouter un ingrédient
                  </button>

                  <button
                    type="button"
                    className="bouton"
                    style={{ backgroundColor: "#6c757d" }} // Une couleur un peu plus sobre (gris) ou identique
                    onClick={onLogout}
                  >
                    Déconnexion
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {error_message && (
        <div className="sous-container">
          <div className="message message-negatif">🛑 {error_message}</div>
        </div>
      )}
    </div>
  );
}

export default Stock;

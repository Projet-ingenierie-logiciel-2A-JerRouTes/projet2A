import { useState, useEffect } from "react";
import AddIngredientForm from "./AddIngredientForm";
import { getAllIngredients, getStockDetails } from "../api/stockApi";

// Dictionnaire de conversion pour les unités
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
  const [items, setItems] = useState({});
  const [catalogue, setCatalogue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error_message, setErrorMessage] = useState("");
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    const loadAllData = async () => {
      console.log("--- 🏁 Initialisation du chargement des données ---");
      setLoading(true);
      setErrorMessage("");

      try {
        // 1. Récupération du catalogue
        const dataIngr = await getAllIngredients();
        console.log("✅ Catalogue reçu :", dataIngr);
        setCatalogue(dataIngr);

        // 2. Récupération du stock utilisateur
        if (user && user.id_stock) {
          console.log(
            `📡 Récupération du stock ID ${user.id_stock} pour ${user.pseudo}`,
          );
          const dataStock = await getStockDetails(user.id_stock);
          console.log("📦 Données du stock :", dataStock.items_by_ingredient);
          setItems(dataStock.items_by_ingredient || {});
        }
      } catch (err) {
        console.error(
          "❌ Erreur de chargement :",
          err.response?.data || err.message,
        );
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
    console.log("➕ Ajout d'un lot :", newIngredientData);
    let finalId = newIngredientData.id_ingredient;

    if (finalId === null) {
      finalId =
        catalogue.length > 0
          ? Math.max(...catalogue.map((i) => i.id_ingredient)) + 1
          : 1;
      const nouvelIng = {
        id_ingredient: finalId,
        name: newIngredientData.name,
        unit: newIngredientData.unit,
      };
      setCatalogue((prev) => [...prev, nouvelIng]);
    }

    const nouveauLot = {
      quantity: newIngredientData.quantity,
      expiry_date: newIngredientData.expiry_date,
      name: newIngredientData.name,
      unit: newIngredientData.unit,
    };

    setItems((prevItems) => ({
      ...prevItems,
      [finalId]: [...(prevItems[finalId] || []), nouveauLot],
    }));

    setShowForm(false);
  };

  return (
    <div className="container-principal">
      {/* --- BLOC PRINCIPAL : INVENTAIRE --- */}
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
                      Aucun ingrédient. Votre frigo est vide (instabilité
                      thermique ?).
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

              {/* BOUTONS D'ACTION (STOCK) */}
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
                    style={{ backgroundColor: "#6c757d" }}
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

      {/* --- BLOC ADMINISTRATION (Conditionnel) --- */}
      {/* Note : Vérifie si ton backend renvoie "Administrateur" ou "admin" */}
      {user && (user.role === "Administrateur" || user.role === "admin") && (
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
                onClick={() => console.log("Gérer ingrédients")}
              >
                Gérer ingrédients
              </button>
              <button
                className="bouton"
                onClick={() => console.log("Gérer stocks")}
              >
                Gérer stocks
              </button>
              <button
                className="bouton"
                onClick={() => console.log("Gérer recettes")}
              >
                Gérer recettes
              </button>
            </div>
          </div>
        </div>
      )}

      {error_message && (
        <div className="sous-container">
          <div className="message message-negatif">🛑 {error_message}</div>
        </div>
      )}
    </div>
  );
}

export default Stock;

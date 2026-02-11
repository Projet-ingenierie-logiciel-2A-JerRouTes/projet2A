import { useState, useEffect } from "react";
import AddIngredientForm from "./AddIngredientForm";

// 1. AJOUT DU DICTIONNAIRE (En dehors du composant)
const unitLabels = {
  GRAM: "g",
  KILOGRAM: "kg",
  MILIGRAM: "mg",
  MILLILITER: "ml",
  LITER: "L",
  CENTIMETER: "cm",
  PIECE: "pcs",
};

function Stock({ user }) {
  const [items, setItems] = useState({});
  const [catalogue, setCatalogue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error_message, setErrorMessage] = useState("");
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    const loadAllData = async () => {
      setLoading(true);
      setErrorMessage("");
      try {
        const resIngr = await fetch("http://localhost:8000/ingredients");
        if (!resIngr.ok) throw new Error("Erreur catalogue");
        const dataIngr = await resIngr.json();
        setCatalogue(dataIngr);

        if (user && user.id_stock) {
          const resStock = await fetch(
            `http://localhost:8000/stock/${user.id_stock}`,
          );
          if (!resStock.ok) throw new Error("Erreur serveur");
          const dataStock = await resStock.json();
          setItems(dataStock.items_by_ingredient || {});
        }
      } catch (err) {
        setErrorMessage(
          err.message === "Failed to fetch"
            ? "Serveur injoignable"
            : err.message,
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
    let finalId = newIngredientData.id_ingredient;

    if (finalId === null) {
      finalId =
        catalogue.length > 0
          ? Math.max(...catalogue.map((i) => i.id_ingredient)) + 1
          : 1;

      const nouvelIngPourCatalogue = {
        id_ingredient: finalId,
        name: newIngredientData.name,
        unit: newIngredientData.unit,
      };
      setCatalogue((prevCatalogue) => [
        ...prevCatalogue,
        nouvelIngPourCatalogue,
      ]);
    }

    const nouveauLot = {
      quantity: newIngredientData.quantity,
      expiry_date: newIngredientData.expiry_date,
      name: newIngredientData.name, // Important pour l'affichage direct
      unit: newIngredientData.unit, // Important pour l'affichage direct
    };

    setItems((prevItems) => {
      const lotsExistants = prevItems[finalId] || [];
      return {
        ...prevItems,
        [finalId]: [...lotsExistants, nouveauLot],
      };
    });

    setShowForm(false);
  };

  return (
    <div className="container-principal">
      <div className="sous-container">
        <div className="login-form" style={{ maxWidth: "800px" }}>
          <h3 className="stock-titre">
            {user ? `Inventaire de ${user.pseudo}` : "Nouveau Stock"}
          </h3>

          {loading ? (
            <p className="message">Chargement...</p>
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
                              {/* CORRECTION NOM : On prend info.name ou lot.name (pour les nouveaux) */}
                              <td
                                className="ingredient-name"
                                style={{ textTransform: "capitalize" }}
                              >
                                {info ? info.name : lot.name || id}
                              </td>

                              {/* CORRECTION UNITÉ : On utilise le dictionnaire unitLabels */}
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
                      Aucun ingrédient dans le stock.
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

              {!showForm && (
                <button
                  type="button"
                  className="bouton"
                  style={{ marginTop: "20px" }}
                  onClick={() => setShowForm(true)}
                >
                  {user ? "Ajouter ingrédient" : "Saisir ingrédient"}
                </button>
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

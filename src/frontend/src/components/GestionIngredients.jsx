import { useState, useEffect } from "react";
import { getAllIngredients } from "../api/stockApi_vers_C";

function GestionIngredients({ onBack }) {
  const [ingredients, setIngredients] = useState([]);
  const [loading, setLoading] = useState(true);

  // Dictionnaire local pour l'affichage propre des unités
  const unitLabels = {
    GRAM: "g",
    KILOGRAM: "kg",
    MILIGRAM: "mg",
    MILLILITER: "ml",
    LITER: "L",
    CENTIMETER: "cm",
    PIECE: "pcs",
  };

  useEffect(() => {
    const fetchIngredients = async () => {
      try {
        const data = await getAllIngredients();
        setIngredients(data);
      } catch (err) {
        console.error("Erreur lors de la récupération du catalogue", err);
      } finally {
        setLoading(false);
      }
    };
    fetchIngredients();
  }, []);

  return (
    <div className="container-principal">
      <div className="sous-container">
        <div className="login-form" style={{ maxWidth: "900px" }}>
          <h3 className="stock-titre">🍎 Référentiel des Ingrédients</h3>

          {/* Bouton d'ajout au-dessus */}
          <div className="admin-actions-header">
            <button
              className="bouton btn-add-admin"
              onClick={() => console.log("Ajouter ingrédient")}
            >
              + Ajouter un Ingrédient
            </button>
          </div>

          {loading ? (
            <p className="message">Chargement du catalogue...</p>
          ) : (
            <div className="admin-table-container">
              <table className="stock-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Nom</th>
                    <th>Unité par défaut</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {ingredients.map((ing) => (
                    <tr key={ing.id_ingredient}>
                      <td>{ing.id_ingredient}</td>
                      <td
                        className="ingredient-name"
                        style={{ textTransform: "capitalize" }}
                      >
                        {ing.name}
                      </td>
                      <td>
                        <span className="role-badge role-generic">
                          {unitLabels[ing.unit] || ing.unit}
                        </span>
                      </td>
                      <td>
                        <button className="action-icon-btn" title="Modifier">
                          ✏️
                        </button>
                        <button className="action-icon-btn" title="Supprimer">
                          🗑️
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Bouton de retour au-dessous */}
          <button
            className="bouton"
            style={{ marginTop: "20px" }}
            onClick={onBack}
          >
            Retour au Tableau de Bord
          </button>
        </div>
      </div>
    </div>
  );
}

export default GestionIngredients;

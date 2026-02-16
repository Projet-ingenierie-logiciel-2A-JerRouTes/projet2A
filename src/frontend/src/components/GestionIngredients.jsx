import React, { useState, useEffect } from "react";
import {
  Wheat,
  PlusCircle,
  Trash2,
  Edit,
  Undo2,
  AlertCircle,
} from "lucide-react";
import { getAllIngredients } from "../api/stockApi";
import "../styles/Gestion.css";

const GestionIngredients = ({ on_back }) => {
  const [ingredients, set_ingredients] = useState([]);
  const [est_en_chargement, set_est_en_chargement] = useState(true);
  const [message_erreur, set_message_erreur] = useState("");

  // Dictionnaire pour l'affichage propre des unités (tiré de ta V2)
  const libelles_unites = {
    GRAM: "g",
    KILOGRAM: "kg",
    MILIGRAM: "mg",
    MILLILITER: "ml",
    LITER: "L",
    CENTIMETER: "cm",
    PIECE: "pcs",
  };

  useEffect(() => {
    const recuperer_ingredients = async () => {
      try {
        set_est_en_chargement(true);
        const data = await getAllIngredients();
        set_ingredients(data);
      } catch (err) {
        console.error("Erreur récupération ingrédients :", err);
        set_message_erreur("Impossible de charger les ingrédients.");
      } finally {
        set_est_en_chargement(false);
      }
    };
    recuperer_ingredients();
  }, []);

  return (
    <div className="carte-centrale gestion-panel">
      <div className="entete-gestion">
        <div className="titre-groupe">
          <Wheat size={32} color="#10b981" />
          <h1 className="titre-principal">Gestion des Ingrédients</h1>
        </div>
        <div className="barre-outils">
          <button
            className="bouton-action"
            style={{ backgroundColor: "#10b981" }}
          >
            <PlusCircle size={18} /> Ajouter un ingrédient
          </button>
        </div>
      </div>

      {message_erreur && (
        <div className="alerte-erreur">
          <AlertCircle size={18} />
          <span>{message_erreur}</span>
        </div>
      )}

      {est_en_chargement ? (
        <p className="message-chargement">Chargement de la liste...</p>
      ) : (
        <div className="conteneur-tableau">
          <table className="tableau-gestion">
            <thead>
              <tr>
                {/* La colonne ID a été supprimée ici */}
                <th>Nom de l'ingrédient</th>
                <th>Catégorie</th>
                <th>Unité de mesure</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {ingredients.map((ing) => (
                <tr key={ing.id_ingredient}>
                  <td
                    className="texte-gras"
                    style={{ textTransform: "capitalize" }}
                  >
                    {ing.name} {/* Utilisation de .name de la V2 */}
                  </td>
                  <td>{ing.categorie || "Général"}</td>
                  <td>
                    <span className="badge-role bg-user">
                      {libelles_unites[ing.unit] || ing.unit}{" "}
                      {/* Utilisation de .unit de la V2 */}
                    </span>
                  </td>
                  <td className="cellule-actions">
                    <button className="btn-icone" title="Modifier">
                      <Edit size={16} />
                    </button>
                    <button className="btn-icone btn-suppr" title="Supprimer">
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <button className="bouton-retour-gestion" onClick={on_back}>
        <Undo2 size={18} /> Retour au menu
      </button>
    </div>
  );
};

export default GestionIngredients;

import React, { useState, useEffect } from "react";
import { Wheat, PlusCircle, Trash2, Edit, Undo2 } from "lucide-react";
import { getAllIngredients } from "../api/stockApi"; // Utilise ton API existante
import CreationIngredientGlobal from "./CreationIngredientGlobal"; 
import "../styles/Gestion.css";

const GestionIngredients = ({ on_back }) => {
  const [ingredients, set_ingredients] = useState([]);
  const [est_en_chargement, set_est_en_chargement] = useState(true);
  const [vue_actuelle, set_vue_actuelle] = useState("liste"); // "liste" ou "ajout"

  // Fonction pour charger et rafraîchir la liste
  const rafraichir_liste = async () => {
    set_est_en_chargement(true);
    try {
      const data = await getAllIngredients();
      set_ingredients(data);
    } catch (err) {
      console.error("Erreur récupération ingrédients", err);
    } finally {
      set_est_en_chargement(false);
    }
  };

  useEffect(() => {
    rafraichir_liste();
  }, []);

  // RENDU DU FORMULAIRE D'AJOUT
  if (vue_actuelle === "ajout") {
    return (
      <CreationIngredientGlobal 
        onAdd={() => {
          set_vue_actuelle("liste");
          rafraichir_liste();
        }}
        onCancel={() => set_vue_actuelle("liste")}
      />
    );
  }

  return (
    <div className="carte-centrale gestion-panel">
      <div className="entete-gestion">
        <div className="titre-groupe">
          <Wheat size={32} color="#22c55e" />
          <h1 className="titre-principal">Gestion des Ingrédients</h1>
        </div>
        <div className="barre-outils">
          {/* Bouton vert pour correspondre à ton design */}
          <button 
            className="bouton-action btn-ingredient-style" 
            onClick={() => set_vue_actuelle("ajout")}
          >
            <PlusCircle size={18} /> Ajouter un ingrédient
          </button>
        </div>
      </div>

      {est_en_chargement ? (
        <p className="message-chargement">Chargement du référentiel...</p>
      ) : (
        <div className="conteneur-tableau">
          <table className="tableau-gestion">
            <thead>
              <tr>
                <th>Nom de l'ingrédient</th>
                <th>Catégorie</th>
                <th>Unité de mesure</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {ingredients.map((ing) => (
                <tr key={ing.ingredient_id}>
                  <td className="texte-gras">{ing.name}</td>
                  <td>{ing.category || "Général"}</td>
                  <td>
                    <span className="badge-role bg-user">
                      {ing.unit}
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
import React, { useState, useEffect } from "react";
import { Wheat, PlusCircle, Undo2, Eye } from "lucide-react";
import { getAllIngredients } from "../api/stockApi"; 
import CreationIngredientGlobal from "./CreationIngredientGlobal"; 
import AfficherIngredient from "./AfficherIngredient"; // Import du nouveau composant
import "../styles/Gestion.css";

const GestionIngredients = ({ on_back }) => {
  const [ingredients, set_ingredients] = useState([]);
  const [est_en_chargement, set_est_en_chargement] = useState(true);
  const [vue_actuelle, set_vue_actuelle] = useState("liste"); // "liste", "ajout", "details"
  const [ingredient_selectionne, set_ingredient_selectionne] = useState(null);

  const rafraichir_liste = async () => {
    set_est_en_chargement(true);
    try {
      const data = await getAllIngredients();
      
      // 📝 LOG CONSOLE : Pour voir toutes les infos (tags, calories, etc.)
      console.log("🌿 Liste complète des ingrédients récupérée :", data);
      
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

  // VUE AJOUT
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

  // VUE DÉTAILS
  if (vue_actuelle === "details" && ingredient_selectionne) {
    return (
      <AfficherIngredient 
        ingredient={ingredient_selectionne}
        on_back={() => {
          set_vue_actuelle("liste");
          set_ingredient_selectionne(null);
        }}
        on_edit={(id) => console.log("Modifier ingrédient ID:", id)}
        on_delete={(id) => console.log("Supprimer ingrédient ID:", id)}
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
                <th>Nom</th>
                <th>Catégorie</th>
                <th>Unité</th>
                <th style={{ textAlign: "center" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {ingredients.map((ing) => (
                <tr key={ing.ingredient_id}>
                  <td className="texte-gras">{ing.name}</td>
                  <td>{ing.category || "Général"}</td>
                  <td>
                    <span className="badge-role bg-user" style={{ backgroundColor: "#94a3b8" }}>
                      {ing.unit}
                    </span>
                  </td>
                  <td className="cellule-actions" style={{ justifyContent: "center" }}>
                    <button 
                      className="btn-icone" 
                      title="Voir la fiche"
                      onClick={() => {
                        set_ingredient_selectionne(ing);
                        set_vue_actuelle("details");
                      }}
                    >
                      <Eye size={16} color="#3b82f6" />
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
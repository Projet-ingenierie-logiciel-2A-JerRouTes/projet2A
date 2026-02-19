import React, { useState, useEffect } from "react";
import { Package, PlusCircle, LogOut, SquarePen, Trash2 } from "lucide-react";
import { getAllStocks, createStock, getAllIngredients } from "../api/stockApi";
import { userStockTable } from "../hooks/userStockTable";
import SelecteurStock from "./SelecteurStock";
import BarreSaisieStock from "./BarreSaisieStock";
import "../styles/Gestion.css";


const Stock = ({ user, on_logout, set_ajout_ingredient, id_stock, set_id_stock, set_chercher_recette , set_list_nom_stock, list_nom_stock, set_catalogue }) => {
  // --- ÉTATS UTILES ---
  const [chargement_initial, set_chargement_initial] = useState(true);
  const [affichage_barre, set_affichage_barre] = useState(false);

  // --- HOOK MÉTIER ---
  const { formatted_stock } = userStockTable(id_stock);

  // --- LOGIQUE DE CRÉATION ---
  const gerer_creation_stock = async (nom) => {
    try {
      console.log("🚀 Création du stock :", nom);
      const data = await createStock(nom); // Envoie {name: nom} en Body JSON
      
      const nouvel_id = data.stock_id; // Format Swagger

      // Mise à jour de la liste locale
      set_list_nom_stock((prev) => [...prev, { stock_id: nouvel_id, name: nom }]);
      
      // Sélection auto du nouveau stock et fermeture barre
      set_id_stock(nouvel_id);
      set_affichage_barre(false);
    } catch (error) {
      console.error("❌ Erreur création stock:", error);
    }
  };

  // --- CHARGEMENT INITIAL ---
  useEffect(() => {
    const initialiser_page = async () => {
      try {
        set_chargement_initial(true);

        // On lance les deux appels API en parallèle pour gagner du temps
        const [ids_noms_stock, data_catalogue] = await Promise.all([
          getAllStocks(user?.user_id || user?.id),
          getAllIngredients()
        ]);

        // Mise à jour de la liste des stocks pour l'inventaire actuel
        set_list_nom_stock(ids_noms_stock);

        // Mise à jour du catalogue dans l'orchestrateur (App.jsx) 
        // pour l'autocomplétion du formulaire
        if (set_catalogue) {
          set_catalogue(data_catalogue);
        }

        // Sélection automatique du premier stock s'il existe
        if (ids_noms_stock.length > 0) {
          set_id_stock(ids_noms_stock[0].stock_id);
        }
      } catch (err) {
        console.error("❌ Erreur initialisation complète:", err);
      } finally {
        set_chargement_initial(false);
      }
    };

    if (user) {
      initialiser_page();
    }
    // Ajout de set_catalogue dans les dépendances pour la remontée d'état
  }, [user, set_id_stock, set_list_nom_stock, set_catalogue]);

  const nom_stock_actuel = list_nom_stock.find(s => s.stock_id === id_stock)?.name || "";

  return (
    <div className="carte-centrale gestion-panel">
      <div className="entete-gestion">
        <div className="titre-groupe">
          <Package size={32} color="#3b82f6" />
          <h1 className="titre-principal">Inventaire de {user?.username}</h1>
        </div>
        <div className="barre-outils">
          <button className="bouton-action btn-ingredient-style" onClick={() => set_ajout_ingredient(true)}>
            <PlusCircle size={18} /> Ajouter un ingrédient dans {nom_stock_actuel}
          </button>
        </div>
      </div>

      {/* BARRE DE SAISIE LOCALE */}
      {affichage_barre && (
        <BarreSaisieStock 
          on_valider={gerer_creation_stock}
          on_annuler={() => set_affichage_barre(false)}
        />
      )}

      <div style={{ marginBottom: "20px" }}>
        <p style={{ color: "#475569", fontSize: "0.9rem", marginBottom: "8px" }}>Choisir un inventaire :</p>
        <SelecteurStock
          list_id_stock={list_nom_stock}
          on_change_stock={(id) => set_id_stock(id)}
        />
      </div>

      <div className="conteneur-tableau">
        <table className="tableau-gestion">
          <thead>
            <tr>
              <th>Nom ingrédient</th>
              <th>Quantité</th>
              <th>Validité</th>
              <th style={{ textAlign: "center" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {formatted_stock.length > 0 ? (
              formatted_stock.map((item) => (
                <tr key={item.stock_item_id}>
                  <td>{item.nom_ingredient}</td>
                  <td>{item.quantite_affichage}</td>
                  <td>{item.validite}</td>
                  <td style={{ textAlign: "center" }}>
                    <div className="barre-outils" style={{ justifyContent: "center" }}>
                      <button className="btn-icone"><SquarePen size={18} color="#1e293b" /></button>
                      <button className="btn-icone btn-suppr"><Trash2 size={18} /></button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4" style={{ textAlign: "center", padding: "30px", color: "#94a3b8" }}>
                  {chargement_initial ? "Chargement..." : "Ce stock est vide."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: "15px" }}>
        <button className="bouton-action btn-stock-style" onClick={() => set_affichage_barre(true)}>
          <PlusCircle size={18} /> Ajouter un stock
        </button>
      </div>

      <div style={{ marginTop: "15px", display: "flex", gap: "10px" }}>
        {/* NOUVEAU BOUTON : RECHERCHE DE RECETTE */}
        <button 
          className="bouton-action btn-recette-style"
          onClick={() => set_chercher_recette(true)}
        >
          🔍 Trouver des recettes
        </button>
      </div>

      <button className="bouton-retour-gestion" onClick={on_logout}>
        <LogOut size={18} /> Déconnexion
      </button>

      
    </div>
  );
};

export default Stock;
import React, { useState, useEffect } from "react";
import { Package, PlusCircle, LogOut, SquarePen, Trash2 } from "lucide-react";

// Imports des appels API
import { getAllStocks, getInfoStock } from "../api/stockApi";

// Import du hook personnalisé pour la logique du tableau
import { userStockTable } from "../hooks/userStockTable";

// Import du sous-composant extrait pour la lisibilité
import SelecteurStock from "./SelecteurStock";

import "../styles/Gestion.css";

const Stock = ({ user, on_logout }) => {
  // --- ÉTATS (STATES) ---
  const [id_stock, set_id_stock] = useState(null); // ID du stock sélectionné (ex: 101)
  const [list_nom_stock, set_list_nom_stock] = useState([]); // Liste de tuples {id_stock, nom_stock}
  const [chargement_initial, set_chargement_initial] = useState(true);

  // --- HOOK MÉTIER ---
  // On récupère le tableau formaté (Nom, Quantité, Validité) via le hook
  // Ce hook se relance automatiquement dès que id_stock change
  const { formatted_stock } = userStockTable(id_stock);

  // --- EFFET : CHARGEMENT INITIAL (IDs + NOMS) ---
  useEffect(() => {
    const initialiser_page = async () => {
      console.log("--- 🏁 1. DÉBUT : Initialisation des stocks ---");
      try {
        set_chargement_initial(true);

        // 1. On récupère les IDs bruts appartenant à l'utilisateur
        const ids_bruts = await getAllStocks(user?.user_id);
        console.log("📋 1. IDs bruts reçus :", ids_bruts);

        // 2. On transforme les IDs en tuples {id, nom} en appelant getInfoStock pour chaque
        const promesses_noms = ids_bruts.map(async (id) => {
          const info = await getInfoStock(id);
          return { id_stock: id, nom_stock: info.name };
        });

        const liste_complete = await Promise.all(promesses_noms);
        console.log("✅ 1. Liste de tuples (ID/Nom) prête :", liste_complete);

        set_list_nom_stock(liste_complete);

        // 3. On sélectionne le premier stock par défaut
        if (liste_complete.length > 0) {
          console.log(
            "🎯 1. Sélection auto du premier stock :",
            liste_complete[0].id_stock,
          );
          set_id_stock(liste_complete[0].id_stock);
        }
      } catch (err) {
        console.error("❌ 1. Erreur initialisation :", err);
      } finally {
        set_chargement_initial(false);
      }
    };

    initialiser_page();
  }, [user]);

  // --- LOG DE SUIVI DU TABLEAU ---
  console.log(
    "📊 Données formatées reçues du hook pour le tableau :",
    formatted_stock,
  );

  return (
    <div className="carte-centrale gestion-panel">
      {/* ENTÊTE AVEC TITRE ET BOUTON AJOUT */}
      <div className="entete-gestion">
        <div className="titre-groupe">
          <Package size={32} color="#3b82f6" />
          <h1 className="titre-principal">
            Inventaire de {user?.username || "Utilisateur"}
          </h1>
        </div>
        <div className="barre-outils">
          <button className="bouton-action btn-ajout-user">
            <PlusCircle size={18} /> Ajouter un ingrédient
          </button>
        </div>
      </div>

      {/* ZONE DE SÉLECTION DU STOCK */}
      <div style={{ marginBottom: "20px" }}>
        <p
          style={{ color: "#475569", fontSize: "0.9rem", marginBottom: "8px" }}
        >
          Choisir un inventaire :
        </p>
        <SelecteurStock
          list_id_stock={list_nom_stock}
          on_change_stock={(id) => {
            console.log("🖱️ Changement de stock demandé :", id);
            set_id_stock(id); // Déclenche la mise à jour du hook userStockTable
          }}
        />
      </div>

      {/* TABLEAU DES INGRÉDIENTS */}
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
                    <div
                      className="barre-outils"
                      style={{ justifyContent: "center" }}
                    >
                      <button
                        className="btn-icone"
                        onClick={() =>
                          console.log("📝 Editer lot :", item.stock_item_id)
                        }
                      >
                        <SquarePen size={18} color="#1e293b" />
                      </button>
                      <button
                        className="btn-icone btn-suppr"
                        onClick={() =>
                          console.log("🗑️ Supprimer lot :", item.stock_item_id)
                        }
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan="4"
                  style={{
                    textAlign: "center",
                    padding: "30px",
                    color: "#94a3b8",
                  }}
                >
                  {chargement_initial
                    ? "Chargement des données..."
                    : "Ce stock est vide."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* BOUTON DE DÉCONNEXION */}
      <button className="bouton-retour-gestion" onClick={on_logout}>
        <LogOut size={18} /> Déconnexion
      </button>
    </div>
  );
};

export default Stock;

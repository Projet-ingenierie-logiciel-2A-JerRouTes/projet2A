import React, { useState, useEffect } from "react";
import {
  Package,
  PlusCircle,
  LogOut,
  SquarePen,
  Trash2,
  ChevronDown,
} from "lucide-react";
import {
  getStockDetails,
  getAllIngredients,
  getAllStocks,
  getInfoStock,
} from "../api/stockApi";
//import AddIngredientForm from "./AddIngredientForm";
//import { useStockData } from "../hooks/useStockData";
import { useStockTable } from "../hooks/userStockTable";
import "../styles/Gestion.css";

const SelecteurStock = ({ list_id_stock, on_change_stock }) => {
  const [est_ouvert, set_est_ouvert] = useState(false);
  // On stocke l'ID sélectionné pour la logique interne
  const [id_selectionne, set_id_selectionne] = useState(null);

  // Initialisation : au chargement, on prend l'ID du premier tuple de la liste
  useEffect(() => {
    if (list_id_stock.length > 0 && !id_selectionne) {
      set_id_selectionne(list_id_stock[0].id_stock);
    }
  }, [list_id_stock]);

  // ÉTAPE CLÉ : On cherche l'objet complet (id + nom) correspondant à l'ID sélectionné
  const stock_actuel = list_id_stock.find((s) => s.id_stock === id_selectionne);

  const choisir_option = (id) => {
    console.log("🖱️ Sélection du stock ID :", id);
    set_id_selectionne(id);
    set_est_ouvert(false);

    // On renvoie l'ID au composant parent (Stock.jsx)
    on_change_stock(id);
  };

  return (
    <div
      className="selecteur_container"
      style={{ position: "relative", display: "inline-block" }}
    >
      {/* BOUTON BULLE */}
      <button
        onClick={() => set_est_ouvert(!est_ouvert)}
        style={{
          display: "flex",
          alignItems: "center",
          gap: "10px",
          padding: "8px 16px",
          backgroundColor: "#f0f4ff",
          border: "2px solid #3b82f6",
          borderRadius: "25px",
          cursor: "pointer",
          color: "#3b82f6",
          fontWeight: "600",
        }}
      >
        {/* MODIFICATION : On affiche le nom_stock trouvé dans le tuple */}
        <span>
          {stock_actuel ? stock_actuel.nom_stock : "Choisir un stock"}
        </span>

        <ChevronDown
          size={18}
          style={{
            transform: est_ouvert ? "rotate(180deg)" : "rotate(0deg)",
            transition: "transform 0.3s",
          }}
        />
      </button>

      {/* LISTE DÉROULANTE */}
      {est_ouvert && (
        <ul
          style={{
            position: "absolute",
            top: "110%",
            left: "0",
            width: "100%",
            backgroundColor: "white",
            border: "1px solid #e2e8f0",
            borderRadius: "12px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
            listStyle: "none",
            padding: "8px 0",
            margin: 0,
            zIndex: 1000,
          }}
        >
          {list_id_stock.map((item) => (
            <li
              key={item.id_stock}
              onClick={() => choisir_option(item.id_stock)}
              style={{
                padding: "10px 16px",
                cursor: "pointer",
                fontSize: "14px",
                color: "#1e293b",
              }}
              onMouseEnter={(e) => (e.target.style.backgroundColor = "#f1f5f9")}
              onMouseLeave={(e) =>
                (e.target.style.backgroundColor = "transparent")
              }
            >
              {/* MODIFICATION : On affiche le nom_stock dans la liste */}
              {item.nom_stock}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

const Stock = ({ user, on_logout }) => {
  // --- ÉTATS ---
  const [add_ingredient_user, set_add_ingredient_user] = useState(false);
  const [list_id_stock, set_list_id_stock] = useState([]);
  const [id_stock, set_id_stock] = useState(null);
  const [list_nom_stock, set_list_nom_stock] = useState([]);
  const [chargement, set_chargement] = useState(true);

  // --- CHARGEMENT DES DONNÉES ---
  console.log(user);

  const { formatted_stock } = useStockTable(id_stock);
  //console.log("📊 Stock actuel (useStockTable) :", stock);
  //console.log("📚 Catalogue d'ingrédients (useStockTable) :", catalogue);

  useEffect(() => {
    const charger_donnees_initiales = async () => {
      console.log("--- 🏁 1. DÉBUT : Chargement Global ---");
      try {
        // 1. Récupération des IDs bruts
        const liste_id_brute = await getAllStocks(user.user_id);
        console.log("📋 1. IDs reçus du Backend :", liste_id_brute);

        // 2. Transformation : Récupération de chaque nom à partir de l'ID
        const promesses_noms = liste_id_brute.map(async (id) => {
          console.log(`📡 1. Envoi requête info pour l'ID #${id}...`);
          const info = await getInfoStock(id);
          console.log(`📦 1. Réponse reçue pour ID #${id} :`, info.name);
          return { id_stock: id, nom_stock: info.name };
        });

        const liste_complete = await Promise.all(promesses_noms);
        console.log("✅ 1. Liste de tuples finale :", liste_complete);

        // Mise à jour de l'état pour ton menu déroulant
        set_list_nom_stock(liste_complete);

        // 3. Sélection automatique du premier de la liste
        if (liste_complete.length > 0) {
          console.log(
            "🎯 1. Sélection automatique de id_stock :",
            liste_complete[0].id_stock,
          );
          set_id_stock(liste_complete[0].id_stock);
        }
      } catch (err) {
        console.error("❌ 1. Erreur lors de l'initialisation :", err);
      }
    };

    charger_donnees_initiales();
  }, []);

  /*
  useEffect(() => {
    // 1. Premier effet : Charger la liste initiale des IDs (une seule fois) (pas de await)
    const charger_ids = async () => {
      console.log("--- 🏁 1. DÉBUT : Chargement de la liste des stocks ---");
      try {
        const liste_id = await getAllStocks();
        console.log("📋 1. Données reçues (getAllStocks) :", liste_id);

        set_list_id_stock(liste_id);

        // Sélection automatique du premier ID :
        if (liste_id?.length > 0) {
          console.log("🎯 1. Sélection automatique du premier stock :", liste_id[0]);
          set_id_stock(liste_id[0]);
        } else {
          console.warn("⚠️ 1. La liste des stocks est vide.");
        }
      } catch (err) {
        console.error("❌ 1. Erreur liste stocks :", err);
      }
    };
    charger_ids();
  }, []);

  // 2. Deuxième effet : Récupération du nom du stock
  useEffect(() => {
    const recuperer_nom_stock = async () => {
      console.log("--- 🔄 2. CHANGEMENT : id_stock détecté ---");
      console.log("🆔 2. Valeur actuelle de id_stock :", id_stock);

      if (!id_stock) {
        console.log("🛑 2. id_stock est vide (null/false), arrêt du chargement des détails.");
        return;
      }

      try {
        set_chargement(true);
        console.log(`📡 2. API : Envoi requête pour les info #${id_stock}...`);

        const info_stock = await getInfoStock(id_stock);
        // name = info_stock.name

      } catch (erreur) {
        console.error("❌ 2. API : Erreur lors de la récupération du stock :", erreur);
      } finally {
        set_chargement(false);
        console.log("--- ✅ 2. FIN : Mise à jour du stock terminée ---");
      }
    };

    recuperer_nom_stock();
  }, [id_stock]);

  // 3. Troisième effet : Charger les détails dès que id_stock change
  useEffect(() => {
    const recuperer_details_stock = async () => {
      console.log("--- 🔄 2. CHANGEMENT : id_stock détecté ---");
      console.log("🆔 2. Valeur actuelle de id_stock :", id_stock);

      if (!id_stock) {
        console.log("🛑 2. id_stock est vide (null/false), arrêt du chargement des détails.");
        return;
      }

      try {
        set_chargement(true);
        console.log(`📡 2. API : Envoi requête pour le stock #${id_stock}...`);

        const donnees_stock = await getStockDetails(id_stock);

        console.log("📦 2. API : Détails complets du stock reçus :", donnees_stock);
        set_stock_actuel(donnees_stock);
      } catch (erreur) {
        console.error("❌ 2. API : Erreur lors de la récupération du stock :", erreur);
      } finally {
        set_chargement(false);
        console.log("--- ✅ 2. FIN : Mise à jour du stock terminée ---");
      }
    };

    recuperer_details_stock();
  }, [id_stock]);*/

  return (
    <div className="carte_centrale gestion_panel">
      <div className="entete_gestion">
        <div className="titre_groupe">
          <Package size={32} color="#3b82f6" />
          <h1 className="titre_principal">
            Inventaire de {user?.username || "Utilisateur"}
          </h1>
        </div>
        <div className="barre_outils">
          <button
            className="bouton_action"
            style={{ backgroundColor: "#6890F0" }}
          >
            <PlusCircle size={18} /> Ajouter un ingrédient
          </button>
        </div>
      </div>

      <div>
        <p style={{ color: "#475569", marginBottom: "10px" }}>
          Sélectionnez un stock pour voir son contenu :
        </p>
      </div>

      {/* AJOUT DU SÉLECTEUR*/}
      <SelecteurStock
        list_id_stock={list_nom_stock} // Ta liste de tuples {id_stock, nom_stock}
        on_change_stock={(id) => {
          console.log("🎯 Choix utilisateur récupéré dans Stock.jsx :", id); // Le log est ici
          set_id_stock(id); // On met à jour l'état pour déclencher l'API
        }}
      />

      <div style={{ marginTop: "20px" }}>
        {chargement ? (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              color: "#3b82f6",
            }}
          ></div>
        ) : (
          <div style={{ color: "#475569" }}>
            {formatted_stock.length > 0 ? (
              <span>Contenu du stock sélectionné :</span>
            ) : (
              <span>Ce stock est actuellement vide.</span>
            )}
          </div>
        )}
      </div>

      {/* AFFICHAGE DE LA TABLE DES LOTS */}
      <div className="conteneur_tableau">
        <table className="tableau_gestion">
          <thead>
            <tr>
              <th>Nom ingrédient</th>
              <th>Quantité</th>
              <th>Validité</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {formatted_stock.map((item) => (
              /* 1. On utilise stock_item_id comme clé unique pour la ligne */
              <tr key={item.stock_item_id}>
                <td>{item.nom_ingredient}</td>
                <td>{item.quantite_affichage}</td>
                <td>{item.validite}</td>

                <td style={{ textAlign: "center" }}>
                  <div
                    className="barre_outils"
                    style={{ justifyContent: "center" }}
                  >
                    {/* Bouton Modifier : on lui passe l'ID */}
                    <button
                      className="btn_icone"
                      onClick={() =>
                        console.log("Modifier :", item.stock_item_id)
                      }
                      style={{ display: "flex", padding: "8px" }}
                    >
                      <SquarePen size={18} color="#1e293b" />
                    </button>

                    {/* Bouton Supprimer : on lui passe l'ID */}
                    <button
                      className="btn_icone btn_suppr"
                      onClick={() =>
                        console.log("Supprimer :", item.stock_item_id)
                      }
                      style={{ display: "flex", padding: "8px" }}
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button
        className="bouton_retour_gestion"
        onClick={on_logout}
        style={{ marginTop: "20px" }}
      >
        <LogOut size={18} /> Déconnexion
      </button>
    </div>
  );
};

export default Stock;

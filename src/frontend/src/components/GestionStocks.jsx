import React, { useState, useEffect } from "react";
import {
  Package,
  PlusCircle,
  Undo2,
  AlertCircle,
  Loader2,
  RefreshCw,
  Eye
} from "lucide-react";
// Import de la fonction administrative et du composant de détail
import { getAllStocksAdmin } from "../api/stockApi"; 
import AfficherStock from "./AfficherStock";
import "../styles/Gestion.css";

const GestionStocks = ({ on_back }) => {
  // --- ÉTATS ---
  const [stocks, set_stocks] = useState([]);
  const [est_en_chargement, set_est_en_chargement] = useState(true);
  const [message_erreur, set_message_erreur] = useState("");
  
  // États pour la navigation interne
  const [vue_actuelle, set_vue_actuelle] = useState("liste"); // "liste" ou "details"
  const [stock_selectionne, set_stock_selectionne] = useState(null);

  // --- LOGIQUE DE RÉCUPÉRATION ---
  const recuperer_stocks = async () => {
    try {
      set_est_en_chargement(true);
      set_message_erreur("");
      
      const data = await getAllStocksAdmin({ limit: 100 });
      
      // Affichage de la liste complète dans la console
      console.log("📦 Liste complète des stocks récupérée :", data);
      
      set_stocks(data);
    } catch (err) {
      console.error("Erreur récupération stocks :", err);
      set_message_erreur("Impossible de charger les stocks (Accès admin requis).");
    } finally {
      set_est_en_chargement(false);
    }
  };

  useEffect(() => {
    recuperer_stocks();
  }, []);

  // --- RENDU CONDITIONNEL : DÉTAILS D'UN STOCK ---
  if (vue_actuelle === "details" && stock_selectionne) {
    return (
      <AfficherStock 
        stock={stock_selectionne}
        on_back={() => {
          set_vue_actuelle("liste");
          set_stock_selectionne(null);
        }}
        on_edit={(id) => console.log("Modifier le stock ID:", id)}
        on_delete={(id) => console.log("Supprimer le stock ID:", id)}
      />
    );
  }

  // --- RENDU DE LA LISTE PRINCIPALE ---
  return (
    <div className="carte-centrale gestion-panel">
      {/* EN-TÊTE */}
      <div className="entete-gestion">
        <div className="titre-groupe">
          <Package size={32} color="#3b82f6" />
          <h1 className="titre-principal">Gestion des Stocks</h1>
        </div>
        
        <div className="barre-outils">
          <button 
            className="bouton-action" 
            onClick={recuperer_stocks}
            title="Actualiser la liste"
            style={{ backgroundColor: "#f1f5f9", color: "#3b82f6", marginRight: "10px" }}
          >
            <RefreshCw size={18} className={est_en_chargement ? "animate-spin" : ""} />
          </button>
          
          <button
            className="bouton-action"
            style={{ backgroundColor: "#3b82f6" }}
            onClick={() => console.log("Ouvrir formulaire création stock")}
          >
            <PlusCircle size={18} /> Ajouter un stock
          </button>
        </div>
      </div>

      {/* MESSAGES D'ERREUR */}
      {message_erreur && (
        <div className="alerte-erreur">
          <AlertCircle size={18} />
          <span>{message_erreur}</span>
        </div>
      )}

      {/* ÉCRAN DE CHARGEMENT */}
      {est_en_chargement ? (
        <div className="chargement-flex" style={{ padding: "40px", textAlign: "center" }}>
          <Loader2 className="animate-spin" size={32} color="#3b82f6" style={{ margin: "40px auto 10px" }} />
          <p className="message-chargement">Chargement du registre des stocks...</p>
        </div>
      ) : (
        <div className="conteneur-tableau">
          <table className="tableau-gestion">
            <thead>
              <tr>
                <th style={{ width: "120px" }}>ID Stock</th>
                <th>Nom du stock</th>
                <th style={{ textAlign: "center", width: "100px" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {stocks.map((stock) => (
                <tr key={stock.stock_id}>
                  <td className="col-id">#{stock.stock_id}</td>
                  <td className="texte-gras">{stock.name}</td>
                  <td className="cellule-actions" style={{ justifyContent: "center" }}>
                    {/* Bouton Oeil pour voir les détails */}
                    <button 
                      className="btn-icone" 
                      title="Voir les détails"
                      onClick={() => {
                        console.log("Détails du stock sélectionné :", stock);
                        set_stock_selectionne(stock);
                        set_vue_actuelle("details");
                      }}
                    >
                      <Eye size={16} color="#3b82f6" />
                    </button>
                  </td>
                </tr>
              ))}

              {/* CAS TABLEAU VIDE */}
              {stocks.length === 0 && !message_erreur && (
                <tr>
                  <td colSpan="3" style={{ textAlign: 'center', padding: '60px', color: '#94a3b8' }}>
                    Aucun stock enregistré dans le système.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* BOUTON RETOUR GÉNÉRAL */}
      <button className="bouton-retour-gestion" onClick={on_back}>
        <Undo2 size={18} /> Retour au menu
      </button>
    </div>
  );
};

export default GestionStocks;
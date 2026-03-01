import React, { useState, useEffect } from "react";
import {
  Package,
  PlusCircle,
  Trash2,
  Edit,
  Undo2,
  AlertCircle,
  Loader2,
  RefreshCw
} from "lucide-react";
// Import de la nouvelle fonction administrative
import { getAllStocksAdmin } from "../api/stockApi"; 
import "../styles/Gestion.css";

const GestionStocks = ({ on_back }) => {
  const [stocks, set_stocks] = useState([]);
  const [est_en_chargement, set_est_en_chargement] = useState(true);
  const [message_erreur, set_message_erreur] = useState("");

  const recuperer_stocks = async () => {
    try {
      set_est_en_chargement(true);
      set_message_erreur("");
      // Appel à l'endpoint GET /api/stocks/all
      const data = await getAllStocksAdmin({ limit: 100 });
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

  return (
    <div className="carte-centrale gestion-panel">
      <div className="entete-gestion">
        <div className="titre-groupe">
          <Package size={32} color="#3b82f6" />
          <h1 className="titre-principal">Gestion des Stocks</h1>
        </div>
        <div className="barre-outils">
          <button 
            className="bouton-action" 
            onClick={recuperer_stocks}
            style={{ backgroundColor: "#f1f5f9", color: "#3b82f6", marginRight: "10px" }}
          >
            <RefreshCw size={18} className={est_en_chargement ? "animate-spin" : ""} />
          </button>
          <button
            className="bouton-action"
            style={{ backgroundColor: "#3b82f6" }}
          >
            <PlusCircle size={18} /> Ajouter un stock
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
        <div className="chargement-flex" style={{ padding: "40px", textAlign: "center" }}>
          <Loader2 className="animate-spin" size={32} color="#3b82f6" style={{ margin: "0 auto 10px" }} />
          <p className="message-chargement">Chargement du registre des stocks...</p>
        </div>
      ) : (
        <div className="conteneur-tableau">
          <table className="tableau-gestion">
            <thead>
              <tr>
                <th style={{ width: "100px" }}>ID Stock</th>
                <th>Nom du stock</th>
                <th style={{ textAlign: "center" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {stocks.map((stock) => (
                <tr key={stock.stock_id}>
                  <td className="col-id">#{stock.stock_id}</td>
                  <td className="texte-gras">
                    {stock.name}
                  </td>
                  <td className="cellule-actions" style={{ justifyContent: "center" }}>
                    <button className="btn-icone" title="Modifier">
                      <Edit size={16} />
                    </button>
                    <button className="btn-icone btn-suppr" title="Supprimer">
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
              {stocks.length === 0 && !message_erreur && (
                <tr>
                  <td colSpan="3" style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
                    Aucun stock enregistré dans le système.
                  </td>
                </tr>
              )}
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

export default GestionStocks;
import React, { useState, useEffect } from "react";
import {
  Package,
  PlusCircle,
  Trash2,
  Edit,
  Undo2,
  AlertCircle,
} from "lucide-react";
import { getAllStocks } from "../api/stockApi";
import "../styles/Gestion.css";

const GestionStocks = ({ on_back }) => {
  const [stocks, set_stocks] = useState([]);
  const [est_en_chargement, set_est_en_chargement] = useState(true);
  const [message_erreur, set_message_erreur] = useState("");

  useEffect(() => {
    const recuperer_stocks = async () => {
      try {
        set_est_en_chargement(true);
        const data = await getAllStocks();
        set_stocks(data);
      } catch (err) {
        console.error("Erreur récupération stocks :", err);
        set_message_erreur("Impossible de charger les stocks.");
      } finally {
        set_est_en_chargement(false);
      }
    };

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
        <p className="message-chargement">Chargement de la liste...</p>
      ) : (
        <div className="conteneur-tableau">
          <table className="tableau-gestion">
            <thead>
              <tr>
                <th>Nom du stock</th>
                <th>Description</th>
                <th>Date de création</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {stocks.map((stock) => (
                <tr key={stock.id_stock}>
                  <td className="texte-gras">
                    {stock.name}
                  </td>
                  <td>
                    {stock.description || "—"}
                  </td>
                  <td>
                    {stock.created_at
                      ? new Date(stock.created_at).toLocaleDateString()
                      : "—"}
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

export default GestionStocks;

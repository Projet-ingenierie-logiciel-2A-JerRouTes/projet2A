import React from "react";
import { Package, Undo2, Hammer } from "lucide-react";
import "../styles/Gestion.css";

const GestionStocks = ({ on_back }) => {
  return (
    <div
      className="carte-centrale gestion-panel"
      style={{ textAlign: "center", padding: "50px" }}
    >
      <div className="entete-gestion">
        <div className="titre-groupe">
          <Package size={32} color="#f59e0b" />
          <h1 className="titre-principal">Gestion des Stocks</h1>
        </div>
      </div>

      <div style={{ margin: "40px 0" }}>
        <Hammer size={64} color="#f59e0b" style={{ marginBottom: "20px" }} />
        <p style={{ color: "#64748b", fontSize: "1.2rem" }}>
          Le module de suivi des stocks est en cours de développement.
        </p>
      </div>

      <button
        className="bouton-retour-gestion"
        onClick={on_back}
        style={{ margin: "0 auto" }}
      >
        <Undo2 size={18} /> Retour au menu
      </button>
    </div>
  );
};

export default GestionStocks;

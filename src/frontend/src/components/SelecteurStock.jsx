import React, { useState, useEffect } from "react";
import { ChevronDown } from "lucide-react";
import "../styles/SelecteurStock.css"; 

const SelecteurStock = ({ list_id_stock, on_change_stock }) => {
  const [est_ouvert, set_est_ouvert] = useState(false);
  const [id_selectionne, set_id_selectionne] = useState(null);

  // Initialisation du premier stock au chargement
  useEffect(() => {

    console.log("Action dans selecteurStock")

    if (list_id_stock.length > 0 && !id_selectionne) {
      set_id_selectionne(list_id_stock[0].stock_id);
    }

  }, [list_id_stock, id_selectionne]);

  // Recherche des informations du stock actuel
  const stock_actuel = list_id_stock.find((s) => s.stock_id === id_selectionne);

  const choisir_option = (id) => {
    set_id_selectionne(id);
    set_est_ouvert(false);
    on_change_stock(id); // Informe le parent du changement
  };

  return (
    <div className="selecteur-container">
      {/* BOUTON BULLE */}
      <button
        className="selecteur-bulle"
        onClick={() => set_est_ouvert(!est_ouvert)}
      >
        <span>
          {stock_actuel ? stock_actuel.name : "Choisir un stock"}
        </span>
        <ChevronDown
          size={18}
          className={`chevron-icon ${est_ouvert ? "ouvert" : ""}`}
        />
      </button>

      {/* MENU DÉROULANT */}
      {est_ouvert && (
        <ul className="selecteur-menu">
          {list_id_stock.map((item) => (
            <li
              key={item.stock_id}
              className="selecteur-item"
              onClick={() => choisir_option(item.stock_id)}
            >
              {item.name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SelecteurStock;

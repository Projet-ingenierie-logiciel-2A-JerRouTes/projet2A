import React, { useState } from "react";
import { PlusCircle, X } from "lucide-react";
import "../styles/Gestion.css";

const BarreSaisieStock = ({ on_valider, on_annuler }) => {
  const [nouveau_nom, set_nouveau_nom] = useState("");

  const gerer_validation = () => {
    if (nouveau_nom.trim() !== "") {
      on_valider(nouveau_nom);
      set_nouveau_nom(""); 
    }
  };

  return (
    <div className="conteneur-saisie-stock">
      <input
        type="text"
        className="entree-stock"
        placeholder="Nom du nouvel inventaire (ex: Cave)..."
        value={nouveau_nom}
        onChange={(e) => set_nouveau_nom(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && gerer_validation()}
        autoFocus
      />
      
      <div className="groupe-boutons-saisie">
        <button 
          className="bouton-valider-saisie" 
          onClick={gerer_validation}
        >
          Confirmer
        </button>

        <button 
          className="bouton-annuler-saisie"
          onClick={() => {
            set_nouveau_nom("");
            on_annuler();
          }}
        >
          Annuler
        </button>
      </div>
    </div>
  );
};

export default BarreSaisieStock;
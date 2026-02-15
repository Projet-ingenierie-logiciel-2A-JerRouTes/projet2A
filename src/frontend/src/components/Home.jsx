import React from "react";
import "../App.css";

const Home = ({ on_clic_bouton }) => {
  return (
    <div className="carte-centrale">
      <h1 className="titre-principal">
        Génération de Recettes à <br />
        partir d'un stock
      </h1>

      <div className="groupe-boutons">
        <button
          className="bouton-custom btn-connexion"
          onClick={() => on_clic_bouton("connexion")}
        >
          Connexion
        </button>

        <button
          className="bouton-custom btn-inscription"
          onClick={() => on_clic_bouton("inscription")}
        >
          Inscription
        </button>

        <button
          className="bouton-custom btn-admin"
          onClick={() => on_clic_bouton("admin")}
        >
          Connexion Administrateur
        </button>

        <button
          className="bouton-custom btn-invite"
          onClick={() => on_clic_bouton("invite")}
        >
          Naviguer en mode invité
        </button>
      </div>
    </div>
  );
};

export default Home;

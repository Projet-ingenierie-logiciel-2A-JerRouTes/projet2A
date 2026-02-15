import React from "react";
import { Users, Wheat, Package, BookOpen, LogOut } from "lucide-react";
import "../styles/InterfaceAdmin.css";

// Note : on ne met plus de console.log ici sur des variables qui n'existent pas
const InterfaceAdmin = ({
  user,
  on_logout,
  on_clic_users,
  on_clic_ingredients,
  on_clic_stocks,
  on_clic_recettes,
}) => {
  return (
    <div className="carte-centrale admin-panel">
      <div className="entete-admin">
        <h1 className="titre-principal">Console d'Administration</h1>
        <p className="sous-titre">
          Bienvenue, {user?.username || "Administrateur"}
        </p>
      </div>

      <div className="groupe-boutons-admin">
        {/* BOUTON UTILISATEURS */}
        <button className="bouton-admin-item btn-users" onClick={on_clic_users}>
          <Users size={32} />
          <span>Gestion des utilisateurs</span>
        </button>

        {/* BOUTON INGRÉDIENTS */}
        <button
          className="bouton-admin-item btn-ingredients"
          onClick={on_clic_ingredients}
        >
          <Wheat size={32} />
          <span>Gestion des ingrédients</span>
        </button>

        {/* BOUTON STOCKS - Maintenant relié */}
        <button
          className="bouton-admin-item btn-stocks"
          onClick={on_clic_stocks}
        >
          <Package size={32} />
          <span>Gestion des stocks</span>
        </button>

        {/* BOUTON RECETTES - Maintenant relié */}
        <button
          className="bouton-admin-item btn-recettes"
          onClick={on_clic_recettes}
        >
          <BookOpen size={32} />
          <span>Gestion des recettes</span>
        </button>

        <button className="bouton-deconnexion-admin" onClick={on_logout}>
          <LogOut size={18} />
          Déconnexion
        </button>
      </div>
    </div>
  );
};

export default InterfaceAdmin;

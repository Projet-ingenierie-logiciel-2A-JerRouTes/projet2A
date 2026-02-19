import React, { useState } from "react";
import "./App.css";

// Composants de base
import Home from "./components/Home";
import Auth from "./components/Auth";
import Register from "./components/Register";

// Composants Admin
import InterfaceAdmin from "./components/InterfaceAdmin";
import GestionUtilisateurs from "./components/GestionUtilisateurs";
import GestionIngredients from "./components/GestionIngredients";
import GestionStocks from "./components/GestionStocks";
import GestionRecettes from "./components/GestionRecettes";

// Composants Utilisateur
import Stock from "./components/Stock";
import AffichageRecettes from "./components/AfficherRecettes";
import AddIngredientForm from "./components/AddIngredientForm"; // Assure-toi que l'import est là

function App() {
  // --- ÉTATS ---
  const [user, set_user] = useState(null);
  const [action, set_action] = useState("accueil");
  const [est_connecte, set_est_connecte] = useState(false);
  const [admin_connecte, set_admin_connecte] = useState(false);
  
  const [list_nom_stock, set_list_nom_stock] = useState([]);
  const [id_stock, set_id_stock] = useState(null);
  const [ajout_ingredient, set_ajout_ingredient] = useState(false);
  const [chercher_recette, set_chercher_recette] = useState(false);
  const [catalogue, set_catalogue] = useState([]);

  const [vue_active_admin, set_vue_active_admin] = useState(null); 

  

  // --- LOGIQUE ---
  const gerer_connexion_reussie = (donnees_utilisateur, est_admin = false) => {
    set_user(donnees_utilisateur);
    set_admin_connecte(est_admin);
    set_est_connecte(true);
  };

  const gerer_deconnexion = () => {
    set_est_connecte(false);
    set_admin_connecte(false);
    set_user(null);
    set_action("accueil");
    set_vue_active_admin(null);
    set_ajout_ingredient(false);
    set_chercher_recette(false);
  };

  // --- FONCTION DE RENDU INTERNE ---
  const rendu_contenu = () => {
    if (!est_connecte) {
      if (action === "connexion") return <Auth on_login={(d) => gerer_connexion_reussie(d, false)} on_back={() => set_action("accueil")} />;
      if (action === "admin") return <Auth est_admin={true} on_login={(d) => gerer_connexion_reussie(d, true)} on_back={() => set_action("accueil")} />;
      if (action === "inscription") return <Register on_register_success={() => set_action("connexion")} on_back={() => set_action("accueil")} />;
      return <Home on_clic_bouton={set_action} />;
    }

    if (admin_connecte) {
      if (vue_active_admin === "utilisateurs") return <GestionUtilisateurs on_back={() => set_vue_active_admin(null)} />;
      if (vue_active_admin === "ingredients") return <GestionIngredients on_back={() => set_vue_active_admin(null)} />;
      if (vue_active_admin === "stocks") return <GestionStocks on_back={() => set_vue_active_admin(null)} />;
      if (vue_active_admin === "recettes") return <GestionRecettes on_back={() => set_vue_active_admin(null)} />;
      
      return (
        <InterfaceAdmin 
          user={user?.user || user} 
          on_clic_users={() => set_vue_active_admin("utilisateurs")}
          on_clic_ingredients={() => set_vue_active_admin("ingredients")}
          on_clic_stocks={() => set_vue_active_admin("stocks")}
          on_clic_recettes={() => set_vue_active_admin("recettes")}
          on_logout={gerer_deconnexion} 
        />
      );
    }

    if (ajout_ingredient) {
      return (
        <AddIngredientForm 
          catalogue={catalogue} 
          liste_stocks={list_nom_stock}
          initial_stock_id={id_stock} 
          onAdd={(data) => { console.log(data); set_ajout_ingredient(false); }}
          onCancel={() => set_ajout_ingredient(false)} 
        />
      );
    }

    if (chercher_recette) {
      return <AffichageRecettes set_chercher_recette={set_chercher_recette} />;
    }

    return (
      <Stock
        user={user?.user || user}
        on_logout={gerer_deconnexion}
        id_stock={id_stock}
        set_id_stock={set_id_stock}
        set_ajout_ingredient={set_ajout_ingredient}
        set_chercher_recette={set_chercher_recette}
        list_nom_stock={list_nom_stock} 
        set_list_nom_stock={set_list_nom_stock} 
        set_catalogue={set_catalogue}
      />
    );
  }; // FIN de rendu_contenu

  // --- LE RETURN FINAL DE APP (Indispensable pour l'affichage) ---
  return (
    <div className="ecran-connexion">
      <div className="fond-image"></div>
      <div className="overlay-sombre"></div>
      {rendu_contenu()}
    </div>
  );
}

export default App;
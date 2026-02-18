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

function App() {
  // --- LES VARIABLES D'ÉTAT ---
  const [user, set_user] = useState(null);
  const [action, set_action] = useState("accueil");
  const [est_connecte, set_est_connecte] = useState(false);
  const [admin_connecte, set_admin_connecte] = useState(false);
  const [id_stock, set_id_stock] =useState(null)
  const [id_ingredient, set_id_ingredient] =useState(null)

  // Variables de gestion d'interface
  const [gestion_utilisateurs, set_gestion_utilisateurs] = useState(false);
  const [gestion_ingredients, set_gestion_ingredients] = useState(false);
  const [gestion_stocks, set_gestion_stocks] = useState(false);
  const [gestion_recettes, set_gestion_recettes] = useState(false);

  // Variable d'ajout et de suppression d'élément
  const [ajout_stock, set_ajout_stock] = useState(false);
  const [ajout_indregient, set_ajout_ingredient] = useState(false);

  // --- LOGIQUE DE LIAISON ---

  const gerer_clic_bouton = (nom_bouton) => {
    console.log(`Bouton cliqué : ${nom_bouton}`);
    set_action(nom_bouton);
  };

  const gerer_connexion_reussie = (donnees_utilisateur, est_admin = false) => {
    console.log("Connexion établie. Admin ?", est_admin);
    set_user(donnees_utilisateur);
    set_admin_connecte(est_admin);
    set_est_connecte(true);
  };

  const gerer_deconnexion = () => {
    set_est_connecte(false);
    set_admin_connecte(false);
    set_user(null);
    set_action("accueil");
    // Réinitialisation des vues de gestion
    set_gestion_utilisateurs(false);
    set_gestion_ingredients(false);
    set_gestion_stocks(false);
    set_gestion_recettes(false);
  };

  return (
    <div className="ecran-connexion">
      {/* Éléments visuels de fond */}
      <div className="fond-image"></div>
      <div className="overlay-sombre"></div>

      {/* Rendu conditionnel : ÉCRAN AVANT CONNEXION */}
      {!est_connecte ? (
        <>
          {action === "accueil" && <Home on_clic_bouton={gerer_clic_bouton} />}

          {action === "connexion" && (
            <Auth
              on_login={(data) => gerer_connexion_reussie(data, false)}
              on_back={() => set_action("accueil")}
            />
          )}

          {action === "admin" && (
            <Auth
              est_admin={true}
              on_login={(data) => gerer_connexion_reussie(data, true)}
              on_back={() => set_action("accueil")}
            />
          )}

          {action === "inscription" && (
            <Register
              on_register_success={(data) => {
                console.log("Inscription réussie !", data);
                set_action("connexion");
              }}
              on_back={() => set_action("accueil")}
            />
          )}
        </>
      ) : (
        /* ÉCRAN APRÈS CONNEXION RÉUSSIE */
        <>
          {gestion_utilisateurs ? (
            <GestionUtilisateurs on_back={() => set_gestion_utilisateurs(false)} />
          ) : gestion_ingredients ? (
            <GestionIngredients on_back={() => set_gestion_ingredients(false)} />
          ) : gestion_stocks ? (
            <GestionStocks on_back={() => set_gestion_stocks(false)} />
          ) : gestion_recettes ? (
            <GestionRecettes on_back={() => set_gestion_recettes(false)} />
          ) : (
            /* NAVIGATION PRINCIPALE */
            <>
              {admin_connecte ? (
                <InterfaceAdmin
                  user={user?.user}
                  on_clic_users={() => set_gestion_utilisateurs(true)}
                  on_clic_ingredients={() => set_gestion_ingredients(true)}
                  on_clic_stocks={() => set_gestion_stocks(true)}
                  on_clic_recettes={() => set_gestion_recettes(true)}
                  on_logout={gerer_deconnexion}
                />
              ) : (
                <Stock
                  user={user?.user || user}
                  on_logout={gerer_deconnexion}
                  id_stock={id_stock}
                  set_id_stock={set_id_stock}
                  set_ajout_ingredient={set_ajout_ingredient}
                />
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}

export default App;
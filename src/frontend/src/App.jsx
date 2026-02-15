import React, { useState } from "react";
import "./App.css";
import Home from "./components/Home";

import Auth from "./components/Auth";

import Register from "./components/Register";

import AdminAuth from "./components/AdminAuth";
import InterfaceAdmin from "./components/InterfaceAdmin";
import GestionUtilisateurs from "./components/GestionUtilisateurs";
import GestionIngredients from "./components/GestionIngredients";
import GestionStocks from "./components/GestionStocks";
import GestionRecettes from "./components/GestionRecettes";

import Stock from "./components/Stock";

function App() {
  // --- LES VARIABLES D'ÉTAT ---
  // 1. Variable user : contiendra l'objet complet renvoyé par l'API (null par défaut)
  const [user, set_user] = useState(null);

  // 2. Variable action : détermine quel bouton a été cliqué pour l'affichage
  const [action, set_action] = useState("accueil");

  // 3. Variable connexion : boolean pour savoir si on bascule sur l'interface stock
  const [est_connecte, set_est_connecte] = useState(false);

  // 4. Savoir si la session actuelle est une session admin
  const [admin_connecte, set_admin_connecte] = useState(false);

  // 5. Variables de gestion
  const [gestion_utilisateurs, set_gestion_utilisateurs] = useState(false);
  const [gestion_ingredients, set_gestion_ingredients] = useState(false);
  const [gestion_stocks, set_gestion_stocks] = useState(false);
  const [gestion_recettes, set_gestion_recettes] = useState(false);

  // --- LOGIQUE DE LIAISON ---

  // Gère le clic sur les boutons de Home.jsx (Connexion, Inscription, etc.)
  const gerer_clic_bouton = (nom_bouton) => {
    console.log(`Bouton cliqué : ${nom_bouton}`);
    set_action(nom_bouton);
  };

  // Gère le succès de l'authentification provenant de Auth.jsx
  const gerer_connexion_reussie = (donnees_utilisateur, est_admin = false) => {
    console.log("Connexion établie. Admin ?", est_admin);
    set_user(donnees_utilisateur);
    set_admin_connecte(est_admin);
    set_est_connecte(true);
  };

  return (
    <div className="ecran-connexion">
      {/* Éléments visuels de fond (fixes pour toute l'app) */}
      <div className="fond-image"></div>
      <div className="overlay-sombre"></div>

      {/* Rendu conditionnel basé sur l'état de connexion */}
      {!est_connecte ? (
        <>
          {action === "accueil" && <Home on_clic_bouton={gerer_clic_bouton} />}

          {action === "connexion" && (
            <Auth
              on_login={gerer_connexion_reussie}
              on_back={() => set_action("accueil")}
            />
          )}

          {action === "inscription" && (
            <Register
              on_register_success={(data) => {
                console.log("Inscription réussie !", data);
                set_action("connexion"); // Redirige vers la connexion après succès
              }}
              on_back={() => set_action("accueil")}
            />
          )}

          {action === "admin" && (
            <AdminAuth
              on_login={(data) => gerer_connexion_reussie(data, true)}
              on_back={() => set_action("accueil")}
            />
          )}

          {/* Fonction des autres boutons */}
        </>
      ) : (
        /* ÉCRAN APRÈS CONNEXION RÉUSSIE */
        <>
          {/* NAVIGATION DES PAGES DE GESTION */}
          {gestion_utilisateurs ? (
            <GestionUtilisateurs
              on_back={() => set_gestion_utilisateurs(false)}
            />
          ) : gestion_ingredients ? (
            <GestionIngredients
              on_back={() => set_gestion_ingredients(false)}
            />
          ) : gestion_stocks ? ( // AJOUTE CE BLOC
            <GestionStocks on_back={() => set_gestion_stocks(false)} />
          ) : gestion_recettes ? ( // AJOUTE CE BLOC
            <GestionRecettes on_back={() => set_gestion_recettes(false)} />
          ) : (
            /* SI AUCUNE PAGE DE GESTION N'EST OUVERTE, ON MONTRE LE MENU */
            <>
              {admin_connecte ? (
                <InterfaceAdmin
                  user={user?.user}
                  on_clic_users={() => set_gestion_utilisateurs(true)}
                  on_clic_ingredients={() => set_gestion_ingredients(true)}
                  on_clic_stocks={() => set_gestion_stocks(true)}
                  on_clic_recettes={() => set_gestion_recettes(true)}
                  on_logout={() => {
                    set_est_connecte(false);
                    set_admin_connecte(false);
                    set_action("accueil");
                  }}
                />
              ) : (
                <>
                  {console.log("APP.JSX - État user complet :", user)}
                  <Stock
                    user={user?.user || user}
                    on_logout={() => {
                      set_est_connecte(false);
                      set_action("accueil");
                    }}
                    on_navigate_admin={() => {}}
                  />
                </>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}

export default App;

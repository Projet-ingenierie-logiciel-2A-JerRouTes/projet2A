import React, { useState } from "react";
import "./App.css";

// --- COMPOSANTS DE BASE ---
import Home from "./components/Home";
import Auth from "./components/Auth";
import Register from "./components/Register";

// --- COMPOSANTS ADMIN ---
import InterfaceAdmin from "./components/InterfaceAdmin";
import GestionUtilisateurs from "./components/GestionUtilisateurs";
import GestionIngredients from "./components/GestionIngredients";
import GestionStocks from "./components/GestionStocks";
import GestionRecettes from "./components/GestionRecettes";

// --- COMPOSANTS UTILISATEUR ---
import Stock from "./components/Stock";
import AffichageRecettes from "./components/AfficherRecettes"; // La grille 3x2
import AfficherRecetteDetail from "./components/AfficherRecetteDetail"; // La fiche détail
import AddIngredientForm from "./components/AddIngredientForm";

// --- COMPOSANTS INVITE ---
import SaisieIngredientsInvite from "./components/SaisieIngredientsInvite";

// --- HOOKS ---
import { useTrouverRecetteInvite } from "./hooks/useTrouverRecetteInvite";

function App() {
  // --- ÉTATS DE NAVIGATION ET AUTH ---
  const [user, set_user] = useState(null);
  const [action, set_action] = useState("accueil");
  const [est_connecte, set_est_connecte] = useState(false);
  const [admin_connecte, set_admin_connecte] = useState(false);

  // --- ÉTATS DE GESTION DES DONNÉES ---
  const [list_nom_stock, set_list_nom_stock] = useState([]);
  const [id_stock, set_id_stock] = useState(null);
  const [ajout_ingredient, set_ajout_ingredient] = useState(false);
  const [chercher_recette, set_chercher_recette] = useState(false);
  const [catalogue, set_catalogue] = useState([]);
  const [vue_active_admin, set_vue_active_admin] = useState(null);
  const [mode_saisie_invite, set_mode_saisie_invite] = useState(false);

  // --- ÉTAT POUR LA RECETTE SÉLECTIONNÉE (Chef d'orchestre) ---
  const [recette_selectionnee, set_recette_selectionnee] = useState(null);

  // --- LOGIQUE DU HOOK (Récupère le tableau de 6 recettes) ---
  const { 
    recettes: recettes_invite, 
    chargement: en_cours_invite, 
    reset_recherche_invite 
  } = useTrouverRecetteInvite(action === "invite" || chercher_recette);

  // --- HANDLERS ---
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
    set_recette_selectionnee(null);
  };

  const gerer_retour_accueil = () => {
    set_action("accueil");
    set_chercher_recette(false);
    set_recette_selectionnee(null);
    if (reset_recherche_invite) reset_recherche_invite();
  };

  // --- FONCTION DE RENDU PRINCIPALE ---
  const rendu_contenu = () => {
    
    // 1. UTILISATEUR NON CONNECTÉ
    if (!est_connecte) {
      if (action === "connexion") 
        return <Auth on_login={(d) => gerer_connexion_reussie(d, false)} on_back={gerer_retour_accueil} />;
      
      if (action === "admin") 
        return <Auth est_admin={true} on_login={(d) => gerer_connexion_reussie(d, true)} on_back={gerer_retour_accueil} />;
      
      if (action === "inscription") 
        return <Register on_register_success={() => set_action("connexion")} on_back={gerer_retour_accueil} />;

      // MODE INVITÉ AVEC SYSTÈME GRILLE/DÉTAIL

      if (action === "invite") {
        // Page de saisie des ingrédients
        if (mode_saisie_invite) {
          return (
            <SaisieIngredientsInvite 
              catalogue={catalogue}
              on_back={() => set_mode_saisie_invite(false)}
              on_rechercher={(liste) => {
                console.log("Recherche pour :", liste);
                set_mode_saisie_invite(false);
                // Ici tu appelleras ta logique de filtrage
              }}
            />
          );
        }

        // Page de détail
        if (recette_selectionnee) {
          return <AfficherRecetteDetail recette={recette_selectionnee} onBack={() => set_recette_selectionnee(null)} />;
        }

        // Grille principale
        return (
          <AffichageRecettes 
            gerer_retour={gerer_retour_accueil} 
            recettes={recettes_invite} 
            chargement={en_cours_invite}
            on_select_recette={(r) => set_recette_selectionnee(r)}
            on_clic_saisir={() => set_mode_saisie_invite(true)} // Ouvre la nouvelle page
          />
        );
      }
      /*
      if (action === "invite") {
        // Si l'utilisateur a cliqué sur un bullet
        if (recette_selectionnee) {
          return (
            <AfficherRecetteDetail 
              recette={recette_selectionnee} 
              onBack={() => set_recette_selectionnee(null)} // Retour à la grille
            />
          );
        }
        // Sinon, on affiche la grille des 6 suggestions
        return (
          <AffichageRecettes 
            gerer_retour={gerer_retour_accueil} 
            recettes={recettes_invite} 
            chargement={en_cours_invite}
            on_select_recette={(r) => set_recette_selectionnee(r)} // Définit la recette à afficher
          />
        );
      }*/

      return <Home on_clic_bouton={set_action} />;
    }

    // 2. INTERFACE ADMINISTRATEUR
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

    // 3. UTILISATEUR CONNECTÉ
    if (ajout_ingredient) {
      return (
        <AddIngredientForm 
          catalogue={catalogue} 
          liste_stocks={list_nom_stock}
          initial_stock_id={id_stock} 
          onAdd={(data) => set_ajout_ingredient(false)}
          onCancel={() => set_ajout_ingredient(false)} 
        />
      );
    }

    if (chercher_recette) {
      if (recette_selectionnee) {
        return (
          <AfficherRecetteDetail 
            recette={recette_selectionnee} 
            onBack={() => set_recette_selectionnee(null)} 
          />
        );
      }
      return (
        <AffichageRecettes 
          gerer_retour={() => set_chercher_recette(false)}
          recettes={recettes_invite} 
          chargement={en_cours_invite}
          on_select_recette={(r) => set_recette_selectionnee(r)}
        />
      );
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
  };

  return (
    <div className="ecran-connexion">
      <div className="fond-image"></div>
      <div className="overlay-sombre"></div>
      {rendu_contenu()}
    </div>
  );
}

export default App;
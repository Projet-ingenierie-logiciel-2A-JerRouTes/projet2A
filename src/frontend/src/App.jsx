import { useState } from "react";
import "./App.css";

import Login from "./components/Login";
import CreationCompte from "./components/CreationCompte";
import Stock from "./components/Stock";
import GestionUtilisateurs from "./components/GestionUtilisateurs";
import GestionIngredients from "./components/GestionIngredients";

function App() {
  // --- ÉTATS DE L'APPLICATION ---
  const [user, setUser] = useState(null);
  const [is_registering, setIsRegistering] = useState(false);
  const [show_stock, setShow_stock] = useState(false);

  // État pour la navigation administrative (null, 'users', 'ingredients', 'stocks', 'recettes')
  const [adminView, setAdminView] = useState(null);

  // --- LOGIQUE DE CONNEXION ---
  const handleLogin = (data) => {
    console.log("--- 🔓 Connexion réussie ---");
    console.log("Utilisateur :", data.pseudo, "| Rôle :", data.role);
    setUser(data);
    setShow_stock(true);
  };

  const handleGoToSignup = () => {
    setIsRegistering(true);
  };

  // --- LOGIQUE DE DÉCONNEXION ---
  const handleLogout = () => {
    console.log("--- 🚪 Déconnexion : Réinitialisation complète ---");
    setUser(null);
    setShow_stock(false);
    setIsRegistering(false);
    setAdminView(null); // On ferme systématiquement les vues admin
  };

  // --- RENDU ---
  return (
    <div className="app">
      <h1>📦 Génération de Recettes à partir d'un stock</h1>

      {/* CAS 1 : UTILISATEUR NON CONNECTÉ */}
      {!show_stock && (
        <>
          {is_registering ? (
            <CreationCompte
              onBack={() => setIsRegistering(false)}
              onRegisterSuccess={() => setShow_stock(true)}
            />
          ) : (
            <Login
              onLogin={handleLogin}
              onGoToSignup={handleGoToSignup}
              onGuestAccess={() => setShow_stock(true)}
            />
          )}
        </>
      )}

      {/* CAS 2 : UTILISATEUR CONNECTÉ */}
      {show_stock && (
        <>
          {/* Si aucune vue admin n'est sélectionnée : Affichage du Stock/Dashboard classique */}
          {!adminView ? (
            <Stock
              user={user}
              onLogout={handleLogout}
              onNavigateAdmin={(view) => setAdminView(view)}
            />
          ) : (
            /* SI UNE VUE ADMIN EST SÉLECTIONNÉE */
            <>
              {adminView === "users" && (
                <GestionUtilisateurs onBack={() => setAdminView(null)} />
              )}

              {adminView === "ingredients" && (
                <GestionIngredients onBack={() => setAdminView(null)} />
              )}

              {/* Espaces réservés pour les futures fonctionnalités */}
              {(adminView === "stocks" || adminView === "recettes") && (
                <div className="container-principal">
                  <div className="sous-container">
                    <div className="login-form">
                      <h3 className="stock-titre">
                        🛠️ Gestion des {adminView}
                      </h3>
                      <p className="message">
                        Module en cours de développement...
                      </p>
                      <button
                        className="bouton"
                        onClick={() => setAdminView(null)}
                      >
                        Retour
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}

export default App;

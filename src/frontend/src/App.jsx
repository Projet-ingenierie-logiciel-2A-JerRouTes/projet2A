import { useState } from "react";
import "./App.css";

import Login from "./components/Login";
import CreationCompte from "./components/CreationCompte";
import Stock from "./components/Stock";
import GestionUtilisateurs from "./components/GestionUtilisateurs";

function App() {
  // --- ÉTATS DE L'APPLICATION ---
  const [user, setUser] = useState(null);
  const [is_registering, setIsRegistering] = useState(false);
  const [show_stock, setShowStock] = useState(false);

  // Nouvel état pour la navigation administrative
  const [adminView, setAdminView] = useState(null); // peut être 'users', 'ingredients', etc.

  // --- LOGIQUE DE CONNEXION ---
  const handleLogin = (data) => {
    console.log("--- 🔓 Connexion réussie ---");
    console.log("Utilisateur :", data.pseudo, "| Rôle :", data.role);
    setUser(data);
    setShowStock(true);
  };

  const handleGoToSignup = () => {
    setIsRegistering(true);
  };

  // --- LOGIQUE DE DÉCONNEXION ---
  const handleLogout = () => {
    console.log("--- 🚪 Déconnexion : Réinitialisation complète ---");
    setUser(null);
    setShowStock(false);
    setIsRegistering(false);
    setAdminView(null); // On ferme aussi les vues admin
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
              onRegisterSuccess={() => setShowStock(true)}
            />
          ) : (
            <Login
              onLogin={handleLogin}
              onGoToSignup={handleGoToSignup}
              onGuestAccess={() => setShowStock(true)}
            />
          )}
        </>
      )}

      {/* CAS 2 : UTILISATEUR CONNECTÉ */}
      {show_stock && (
        <>
          {/* Si aucune vue admin n'est sélectionnée, on affiche le Stock classique */}
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

              {/* On peut ajouter d'autres vues ici plus tard (ingredients, recettes) */}
              {adminView === "ingredients" && (
                <div className="sous-container">
                  <div className="login-form">
                    <h3>🛠️ Gestion des Ingrédients (À venir)</h3>
                    <button
                      className="bouton"
                      onClick={() => setAdminView(null)}
                    >
                      Retour
                    </button>
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

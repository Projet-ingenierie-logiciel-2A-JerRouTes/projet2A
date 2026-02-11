import { useState } from "react";
import "./App.css";

import Login from "./components/Login";
import CreationCompte from "./components/CreationCompte";
import Stock from "./components/Stock";

function App() {
  // États de l'application
  const [user, setUser] = useState(null);
  const [is_registering, setIsRegistering] = useState(false);
  const [show_stock, setShowStock] = useState(false);

  // Fonction pour valider la connexion
  const handleLogin = (data) => {
    console.log("Connexion réussie pour l'utilisateur :", data.pseudo);
    setUser(data);
    setShowStock(true);
  };

  // Basculer vers la création de compte
  const handleGoToSignup = () => {
    setIsRegistering(true);
  };

  // 🚪 Fonction de déconnexion
  const handleLogout = () => {
    console.log("--- 🚪 Déconnexion : Réinitialisation de l'état ---");
    setUser(null);
    setShowStock(false);
    setIsRegistering(false);
  };

  return (
    <div className="app">
      <h1>📦 Génération de Recettes à partir d'un stock</h1>

      {/* Cas 1 : Utilisateur non connecté ou en cours d'inscription */}
      {!show_stock && (
        <>
          {is_registering ? (
            <CreationCompte
              onBack={() => setIsRegistering(false)}
              // On aligne le nom de la prop avec l'appel dans CreationCompte
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

      {/* Cas 2 : Affichage du Stock */}
      {show_stock && <Stock user={user} onLogout={handleLogout} />}
    </div>
  );
}

export default App;

import React, { useState } from 'react';

import './App.css';

import Login from './components/Login';
import CreationCompte from './components/CreationCompte';
import Stock from './components/Stock';

function App() {
  // Initialisation des variables d'état pour gérer l'état de l'application
  const [user, setUser] = useState(null);
  const [is_registering, setIsRegistering] = useState(false);
  const [show_stock, setShowStock] = useState(false);

  // Fonction pour valider la connexion
  const handleLogin = (data) => {
    setUser(data);
    setShowStock(true); // Affiche le stock après une connexion réussie
  };

  // Fonction pour basculer vers la création de compte
  const handleGoToSignup = () => {
    setIsRegistering(true);
  };

return (
  <div className="app">
    <h1>📦 Génération de Recettes à partir d'un stock</h1>

    {/*Cas 1 : utilisateur non connecté */}
    {!show_stock && (
      <>
        {is_registering ? (
          /* SI is_registering est vrai : on affiche la création de compte */
          <CreationCompte
            onBack={() => setIsRegistering(false)}
            onGoToStockCreation={() => setShowStock(true)}
          />
        ) : (
          /* SINON (:) : on affiche le Login habituel */
          <Login
            onLogin={handleLogin}
            onGoToSignup={handleGoToSignup}
            onGuestAccess={() => setShowStock(true)}
          />
        )}
      </>
    )}

    {/*Cas 2 : utilisateur connecté */}
    {show_stock && (
        <Stock user={user} />
    )}

  </div>
);
}
export default App;

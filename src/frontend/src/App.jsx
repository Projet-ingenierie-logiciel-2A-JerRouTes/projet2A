import React, { useState } from "react";
import Login from "./components/Login";
import Test from "./components/Test";
import InventaireFrigo from "./components/InventaireFrigo";
import "./App.css";

const App = () => {
  const [user, setUser] = useState(null); // null = pas connecté

  return (
    <div className="app">
      {!user ? (
        <Login onLogin={(userData) => setUser(userData)} />
      ) : (
        <>
          <h1>Frigo App</h1>
          {/* Correction : on accède à la propriété .pseudo de l'objet */}
          <p>Bienvenue, <strong>{user.pseudo}</strong> !</p>
          <p style={{ fontSize: '0.9rem', fontStyle: 'italic' }}>
            Session : {user.role}
          </p>

          {/* --- ANCIEN AFFICHAGE (COMMENTÉ) ---
          <Test />
          ------------------------------------- */}

          <InventaireFrigo />

          <button onClick={() => setUser(null)} className="logout-btn">
            Déconnexion
          </button>
        </>
      )}
    </div>
  );
};

export default App;

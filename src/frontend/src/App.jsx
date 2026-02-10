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
        <Login onLogin={(pseudo) => setUser(pseudo)} />
      ) : (
        <>
          <h1>Frigo App</h1>
          <p>Bienvenue, {user} !</p>

          {/* --- ANCIEN AFFICHAGE (COMMENTÉ) ---
          <Test />
          ------------------------------------- */}

          {/* NOUVEL AFFICHAGE : SAISIE D'INGRÉDIENTS */}
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

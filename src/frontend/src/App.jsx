import React, { useState } from "react";
import Login from "./components/Login";
import Test from "./components/Test";
import "./App.css";

const App = () => {
  const [user, setUser] = useState(null); // null = pas connecté

  return (
    <div className="app">
      {!user ? (
        // Si pas d'utilisateur, on affiche le Login
        <Login onLogin={(pseudo) => setUser(pseudo)} />
      ) : (
        // Si connecté, on affiche le contenu
        <>
          <h1>Frigo App</h1>
          <p>Bienvenue, {user} !</p>
          <Test />
          <button onClick={() => setUser(null)} className="logout-btn">Déconnexion</button>
        </>
      )}
    </div>
  );
};

export default App;

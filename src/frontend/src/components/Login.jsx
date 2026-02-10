import React, { useState } from 'react';

function Login({ onLogin }) {
  const [pseudo, setPseudo] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      // 1. Appel au backend FastAPI
      const response = await fetch('http://127.0.0.1:8000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pseudo, password }), // On envoie les données au format JSON
      });

      // 2. Récupération de la réponse
      const data = await response.json();

      if (response.ok) {
        // Succès : on transmet l'objet utilisateur (pseudo, role, etc.) à App.jsx
        onLogin(data);
      } else {
        // Erreur : on affiche le message d'erreur renvoyé par FastAPI (ex: "Mot de passe incorrect")
        alert(data.detail || "Erreur lors de la connexion");
      }
    } catch (error) {
      console.error("Erreur réseau :", error);
      alert("Impossible de contacter le serveur backend. Est-il lancé ?");
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">
        <h2>Connexion</h2>
        <input
          type="text"
          placeholder="Pseudo"
          value={pseudo}
          onChange={(e) => setPseudo(e.target.value)}
        />
        <input
          type="password"
          placeholder="Mot de passe"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Se connecter</button>
      </form>
    </div>
  );
}

export default Login;

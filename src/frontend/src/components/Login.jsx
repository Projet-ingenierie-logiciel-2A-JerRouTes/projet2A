import React, { useState } from 'react';

function Login({ onLogin }) {
  const [pseudo, setPseudo] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage(''); // Réinitialise l'erreur à chaque tentative

    try {
      // 1. Appel au backend FastAPI sur le port 8000
      const response = await fetch('http://127.0.0.1:8000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // Envoie du pseudo et password au format JSON attendu par Pydantic
        body: JSON.stringify({ pseudo, password }),
      });

      const data = await response.json();

      if (response.ok) {
        // Succès : on transmet l'objet utilisateur complet à App.jsx
        onLogin(data);
      } else {
        // Erreur côté serveur (ex: 401 ou 404)
        setErrorMessage(data.detail || "Erreur lors de la connexion");
      }
    } catch (error) {
      // Erreur réseau (ex: le serveur backend n'est pas lancé)
      console.error("Erreur réseau :", error);
      setErrorMessage("Impossible de contacter le serveur backend. Est-il lancé ?");
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">
        <h2>Connexion</h2>

        {/* Affichage du message d'erreur en jaune s'il existe */}
        {errorMessage && (
          <div className="login-error-box">
            ⚠️ {errorMessage}
          </div>
        )}

        <div className="input-group">
          <input
            type="text"
            placeholder="Pseudo"
            value={pseudo}
            onChange={(e) => setPseudo(e.target.value)}
            required
          />
        </div>

        <div className="input-group">
          <input
            type="password"
            placeholder="Mot de passe"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button type="submit" className="login-button">
          Se connecter
        </button>
      </form>
    </div>
  );
}

export default Login;

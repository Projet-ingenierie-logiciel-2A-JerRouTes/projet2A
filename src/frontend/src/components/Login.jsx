import React, { useState } from 'react';

function Login({ onLogin }) {
  const [pseudo, setPseudo] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');

    try {
      const response = await fetch('http://127.0.0.1:8000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pseudo, password }),
      });

      const data = await response.json();

      if (response.ok) {
        onLogin(data);
      } else {
        if (response.status === 404) {
          setErrorMessage("Utilisateur inconnu");
        } else if (response.status === 401) {
          setErrorMessage("Mot de passe incorrect");
        } else {
          setErrorMessage(data.detail || "Erreur de connexion");
        }
      }
    } catch (error) {
      setErrorMessage("Serveur injoignable");
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">
        <h2>Connexion</h2>

        {/* Cette div réserve l'espace pour que la boîte violette ne bouge JAMAIS */}
        <div className="login-error-container">
          {errorMessage && (
            <div className="login-error-box">
              ⚠️ {errorMessage}
            </div>
          )}
        </div>

        <input
          type="text"
          placeholder="Pseudo"
          value={pseudo}
          onChange={(e) => setPseudo(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Mot de passe"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button type="submit">Se connecter</button>
      </form>
    </div>
  );
}

export default Login;

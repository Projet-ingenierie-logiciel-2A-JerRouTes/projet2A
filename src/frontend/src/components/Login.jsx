import React, { useState } from 'react';

function Login({ onLogin, onGoToSignup, onGuestAccess }) {
  // Initalisation des variables d'état pour le pseudo, le mot de passe et les messages d'erreur
  const [pseudo, setPseudo] = useState('');
  const [password, setPassword] = useState('');
  const [error_message, setErrorMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault(); // Empêche le rechargement de la page
    setErrorMessage(''); // Réinitialise l'erreur à chaque tentative

    try {
      // Communication avec le backend pour la connexion
      const response = await fetch('http://localhost:8000/login', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pseudo, password }),
    });


      const data = await response.json();

      if (response.ok) {
        onLogin(data); // Succès ! On envoie les infos de l'utilisateur à App.jsx
      } else {
        // Gestion des codes erreurs HTTP renvoyés par FastAPI (404, 401)
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
  <div className="container-principal"> {/* Conteneur global */}

    <div className="sous-container">
      <form onSubmit={handleSubmit} className="login-form">
        <h2>Connexion</h2>

        <div className="input-group">
          <input
            type="text"
            placeholder="Pseudo ou Email"
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

        <button type="submit" className="bouton">
          Se connecter
        </button>

        <div style={{ textAlign: 'center', margin: '10px 0' }}>Pas encore de compte</div>

        <button type="button" className="bouton" onClick={onGoToSignup}>
          Créer un compte
        </button>

        <button type="button" className="bouton" onClick={onGuestAccess}>
          Chercher des recettes sans compte
        </button>

      </form>
    </div>

    {/* Boite d'erreur séparée */}
    <div className="sous-container">
    {error_message && (
      <div className="message">
        🛑 {error_message}
      </div>
    )}
    </div>

  </div>
);
}

export default Login;

import React, { useState } from 'react';

function CreationCompte({ onBack, onRegisterSuccess }) {
    const [isRegistered, setIsRegistered] = useState(false);
    const [pseudo, setPseudo] = useState('');
    const [password, setPassword] = useState('');
    const [confirm_password, setconfirmPassword] = useState('');
    const [error_message, setErrorMessage] = useState('');
    const [message, setMessage] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrorMessage('');
        setMessage('');

    try {
      const response = await fetch('http://127.0.0.1:8000/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pseudo, password, confirm_password }),
      });

      const data = await response.json();

      if (response.ok) {
        // En cas de succès, on informe l'utilisateur ou on le redirige
        setMessage("Compte créé avec succès !");
        setErrorMessage('');
        // 2. On bascule l'affichage
        setIsRegistered(true);
      } else {
            // Ici, on récupère le message "detail" envoyé par FastAPI
            setErrorMessage(data.detail || "Erreur lors de l'inscription");
        }
    } catch (error) {
      setErrorMessage("Serveur backend injoignable");
    }
  };

  return (
      <div className="container-principal"> {/* Conteneur global */}

        {!isRegistered ? (
            <div className="sous-container">
                <form onSubmit={handleSubmit} className="login-form">
                    <h2>Créer un compte</h2>

                    <div className="input-group">
                        <input
                            type="text"
                            placeholder="Choisir un Pseudo"
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

                    <div className="input-group">
                        <input
                            type="password"
                            placeholder="Confirmer le mot de passe"
                            value={confirm_password}
                            onChange={(e) => setconfirmPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button type="submit" className="bouton">
                        S'inscrire
                    </button>

                    <button type="button" className="bouton" onClick={onBack}>
                    Retour
                    </button>
                </form>
            </div>

        ):(

            <div className="sous-container">
                <button type="submit" className="bouton">
                    Construire mon stock
                </button>
            </div>
        )}


        {/* Une seule zone de message qui change de style selon le contenu */}
        {(error_message || message) && (
        <div className="sous-container">
            <div className={error_message ? "message-negatif" : "message-positif"}>
            {error_message ? `🛑 ${error_message}` : `✅ ${message}`}
            </div>
        </div>
        )}
    </div>
  );
}

export default CreationCompte;

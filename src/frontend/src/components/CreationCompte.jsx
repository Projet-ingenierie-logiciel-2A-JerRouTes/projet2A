import { useState } from "react";
import { register } from "../api/authApi";

function CreationCompte({ onBack, onRegisterSuccess }) {
  const [isRegistered, setIsRegistered] = useState(false);
  const [pseudo, setPseudo] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm_password, setconfirmPassword] = useState("");
  const [error_message, setErrorMessage] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage("");
    setMessage("");

    // Validation front simple
    if (password !== confirm_password) {
      setErrorMessage("Les mots de passe ne sont pas identiques");
      return;
    }

    try {
      // Backend JWT : username/email/password
      await register({ username: pseudo, email, password });

      setMessage("Compte créé avec succès !");
      setIsRegistered(true);

      // Si ton App veut être notifié (optionnel)
      if (onRegisterSuccess) {
        onRegisterSuccess();
      }
    } catch (error) {
      const status = error?.response?.status;
      const detail = error?.response?.data?.detail;

      if (status === 409) {
        setErrorMessage("Email déjà utilisé");
      } else if (status === 400) {
        setErrorMessage(detail || "Erreur lors de l'inscription");
      } else if (status === 422) {
        setErrorMessage("Champs invalides (pseudo/email/mot de passe)");
      } else {
        setErrorMessage(detail || "Serveur backend injoignable");
      }
    }
  };

  return (
    <div className="container-principal">
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
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
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
      ) : (
        <div className="sous-container">
          <button type="button" className="bouton">
            Construire mon stock
          </button>
        </div>
      )}

      {(error_message || message) && (
        <div className="sous-container">
          <div
            className={error_message ? "message-negatif" : "message-positif"}
          >
            {error_message ? `🛑 ${error_message}` : `✅ ${message}`}
          </div>
        </div>
      )}
    </div>
  );
}

export default CreationCompte;

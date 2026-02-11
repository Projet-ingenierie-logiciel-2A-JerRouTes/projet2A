import { useState } from "react";
import { register } from "../api/authApi_vers_C";

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

    // 1. Log des états locaux avant préparation
    console.log("--- Tentative d'inscription ---");
    console.log("Données saisies :", {
      pseudo,
      email,
      password,
      confirm_password,
    });

    try {
      const payload = {
        pseudo: pseudo,
        password: password,
        confirm_password: confirm_password,
      };

      console.log("Payload envoyé à authApi.register :", payload);
      const response = await register(payload);

      // 3. Log du succès
      console.log("Réponse succès du serveur :", response);

      setMessage("Compte créé avec succès !");
      setIsRegistered(true);

      if (onRegisterSuccess) {
        onRegisterSuccess();
      }
    } catch (error) {
      // 4. Log détaillé de l'erreur
      console.error("Erreur capturée lors de l'inscription :");
      if (error.response) {
        // Le serveur a répondu avec un code hors 2xx
        console.error("Status Code :", error.response.status);
        console.error("Data (Détails FastAPI) :", error.response.data);
      } else if (error.request) {
        // La requête est partie mais pas de réponse (CORS ou Serveur éteint)
        console.error("Aucune réponse reçue (problème réseau/CORS)");
      } else {
        console.error("Erreur de configuration requête :", error.message);
      }

      const status = error?.response?.status;
      const detail = error?.response?.data?.detail;

      if (status === 409) {
        setErrorMessage("Email déjà utilisé");
      } else if (status === 400) {
        setErrorMessage(detail || "Erreur lors de l'inscription");
      } else if (status === 422) {
        // Très utile pour voir quel champ Pydantic rejette
        setErrorMessage("Champs invalides : vérifiez le format des données");
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

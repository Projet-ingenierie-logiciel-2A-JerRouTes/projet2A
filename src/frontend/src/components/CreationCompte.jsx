import { useState } from "react";
import { register } from "../api/authApi";

const MIN_PASSWORD_LENGTH = 8;

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

    // Vérification de la longueur minimale
    if (password.length < MIN_PASSWORD_LENGTH) {
      setErrorMessage(
        `Le mot de passe doit contenir au moins ${MIN_PASSWORD_LENGTH} caractères.`,
      );
      return; // On stoppe la fonction ici
    }

    // --- VÉRIFICATION DE LA CONFIRMATION ---
    if (password !== confirm_password) {
      setErrorMessage("Les mots de passe ne correspondent pas.");
      return;
    }

    try {
      const payload = {
        username: pseudo,
        email: email,
        password: password,
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
                placeholder={`Mot de passe (minimum ${MIN_PASSWORD_LENGTH} caractères)`}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <div className="input-group">
              <input
                type="password"
                placeholder={`Confirmer le mot de passe (minimum ${MIN_PASSWORD_LENGTH} caractères)`}
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

      {/* Boite d'erreur séparée */}
      <div className="sous-container">
        {error_message && <div className="message">🛑 {error_message}</div>}
      </div>
    </div>
  );
}

export default CreationCompte;

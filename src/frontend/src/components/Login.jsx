import { useState } from "react";
import { login } from "../api/authApi_vers_C";
import { me } from "../api/usersApi";

function Login({ onLogin, onGoToSignup, onGuestAccess }) {
  // Initalisation des variables d'état pour le pseudo/email, le mot de passe et les messages d'erreur
  const [pseudo, setPseudo] = useState("");
  const [password, setPassword] = useState("");
  const [error_message, setErrorMessage] = useState("");

  const handleSubmit = async (e) => {
    // DEBUG : On vérifie ce qu'on a dans le State React avant d'envoyer
    console.log("État actuel du pseudo :", pseudo);
    console.log("État actuel du password :", password);

    e.preventDefault(); // Empêche le rechargement de la page
    console.log("Tentative de soumission avec :", pseudo);
    setErrorMessage(""); // Réinitialise l'erreur à chaque tentative

    try {
      // On s'assure d'envoyer un objet avec les DEUX clés
      const credentials = {
        pseudo: pseudo.trim(), // trim() enlève les espaces inutiles
        password: password,
      };

      console.log("Envoi des credentials :", credentials);
      const userData = await login(credentials);

      onLogin(userData);
    } catch (error) {
      // Axios error handling
      console.error("Erreur capturée :", error);
      const status = error?.response?.status;
      const detail = error?.response?.data?.detail;

      if (status === 404) {
        setErrorMessage("Utilisateur inconnu");
      } else if (status === 401) {
        setErrorMessage("Mot de passe incorrect");
      } else if (status === 422) {
        setErrorMessage("Champs invalides");
      } else {
        setErrorMessage(detail || "Erreur de connexion");
      }
    }
  };

  return (
    <div className="container-principal">
      {" "}
      {/* Conteneur global */}
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

          <div style={{ textAlign: "center", margin: "10px 0" }}>
            Pas encore de compte
          </div>

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
        {error_message && <div className="message">🛑 {error_message}</div>}
      </div>
    </div>
  );
}

export default Login;

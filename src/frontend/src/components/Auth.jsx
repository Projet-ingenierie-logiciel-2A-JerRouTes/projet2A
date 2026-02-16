import React, { useState } from "react";
import { Eye, EyeOff, LogIn, Undo2, AlertCircle } from "lucide-react";
import { login_v2 } from "../api/authApi";
import "../styles/Auth.css";

const Auth = ({ on_login, on_back }) => {
  const [identifiant, set_identifiant] = useState("");
  const [mot_de_passe, set_mot_de_passe] = useState("");
  const [voir_mdp, set_voir_mdp] = useState(false);
  const [message_erreur, set_message_erreur] = useState("");
  const [est_en_chargement, set_est_en_chargement] = useState(false);

  const gerer_soumission = async (e) => {
    e.preventDefault();
    set_message_erreur("");
    set_est_en_chargement(true);

    console.log("Données saisies :", { identifiant, mot_de_passe });

    try {
      const credentials = { login: identifiant, password: mot_de_passe };
      const user_data = await login_v2(credentials);

      console.log("Réponse du endpoint (succès) :", user_data);

      on_login(user_data);
    } catch (error) {
      console.error(
        "Erreur renvoyée par le endpoint :",
        error?.response?.data || error.message,
      );
      const status = error?.response?.status;
      const detail = error?.response?.data?.detail;

      if (status === 404) set_message_erreur("Utilisateur inconnu");
      else if (status === 401) set_message_erreur("Mot de passe incorrect");
      else set_message_erreur(detail || "Erreur de connexion");
    } finally {
      set_est_en_chargement(false);
    }
  };

  return (
    <div className="conteneur-auth">
      <div className="carte-auth">
        <div className="entete-auth">
          <LogIn size={28} color="#345371" />
          <h2 className="titre-auth">Connexion</h2>
        </div>

        {message_erreur && (
          <div className="alerte-erreur">
            <AlertCircle size={18} />
            <span>{message_erreur}</span>
          </div>
        )}

        <form onSubmit={gerer_soumission} className="formulaire-auth">
          <div className="groupe-champ">
            <label htmlFor="identifiant-input">Identifiant</label>
            <input
              id="identifiant-input"
              type="text"
              placeholder="Email ou pseudo"
              value={identifiant}
              onChange={(e) => set_identifiant(e.target.value)}
              className="entree-texte"
              required
              autoFocus
            />
          </div>

          <div className="groupe-champ">
            <label htmlFor="mdp-input">Mot de passe</label>
            <div className="conteneur-mdp">
              <input
                id="mdp_input"
                type={voir_mdp ? "text" : "password"}
                placeholder="••••••••"
                value={mot_de_passe}
                onChange={(e) => set_mot_de_passe(e.target.value)}
                className="entree-texte"
                required
              />
              <button
                type="button"
                className="bouton-oeil"
                onClick={() => set_voir_mdp(!voir_mdp)}
                title={voir_mdp ? "Masquer" : "Afficher"}
              >
                {voir_mdp ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          <div className="barre-actions">
            <button
              type="submit"
              className="bouton-valider"
              disabled={est_en_chargement}
            >
              {est_en_chargement ? "Connexion..." : "Valider"}
            </button>
            <button type="button" onClick={on_back} className="bouton-retour">
              <Undo2 size={18} />
              Retour
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Auth;

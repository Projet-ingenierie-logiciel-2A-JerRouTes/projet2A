import React, { useState } from "react";
import { Eye, EyeOff, LogIn, ShieldCheck, Undo2, AlertCircle } from "lucide-react";
import { login } from "../api/authApi";
import "../styles/Auth.css";

const Auth = ({ on_login, on_back, est_admin = false }) => {
  const [identifiant, set_identifiant] = useState("");
  const [mot_de_passe, set_mot_de_passe] = useState("");
  const [voir_mdp, set_voir_mdp] = useState(false);
  const [message_erreur, set_message_erreur] = useState("");
  const [est_en_chargement, set_est_en_chargement] = useState(false);

  const gerer_soumission = async (e) => {
    e.preventDefault();
    set_message_erreur("");
    set_est_en_chargement(true);

    try {
      const credentials = { login: identifiant, password: mot_de_passe };
      
      // On utilise la fonction login factorisée qui récupère tokens + profil
      const user_data = await login(credentials);

      // Vérification spécifique pour l'accès Admin
      if (est_admin) {
        // On vérifie le statut dans l'objet user fusionné par auth.js
        const statut_utilisateur = user_data.user?.status; 

        if (statut_utilisateur !== "admin") {
          set_message_erreur("Compte non autorisé (pas de droit administrateur)");
          set_est_en_chargement(false);
          return; // Bloque la redirection
        }
      }

      console.log(`Connexion ${est_admin ? "Admin" : "User"} réussie :`, user_data);
      on_login(user_data);

    } catch (error) {
      console.error("Erreur de connexion :", error);
      const status = error?.response?.status;
      const detail = error?.response?.data?.detail;

      if (status === 404) {
        set_message_erreur(est_admin ? "Administrateur inconnu" : "Utilisateur inconnu");
      } else if (status === 401) {
        set_message_erreur("Mot de passe incorrect");
      } else {
        set_message_erreur(detail || "Erreur de connexion au serveur");
      }
    } finally {
      set_est_en_chargement(false);
    }
  };

  // Configuration visuelle dynamique
  const couleur_theme = est_admin ? "#ef4444" : "#345371";

  return (
    <div className="conteneur-auth">
      <div 
        className="carte-auth" 
        style={est_admin ? { borderTop: `5px solid ${couleur_theme}` } : {}}
      >
        <div className="entete-auth">
          {est_admin ? (
            <ShieldCheck size={32} color={couleur_theme} />
          ) : (
            <LogIn size={28} color={couleur_theme} />
          )}
          <h2 className="titre-auth">
            {est_admin ? "Espace Admin" : "Connexion"}
          </h2>
        </div>

        {message_erreur && (
          <div className="alerte-erreur">
            <AlertCircle size={18} />
            <span>{message_erreur}</span>
          </div>
        )}

        <form onSubmit={gerer_soumission} className="formulaire-auth">
          <div className="groupe-champ">
            <label htmlFor="id-input">
              {est_admin ? "Identifiant Admin" : "Identifiant"}
            </label>
            <input
              id="id-input"
              type="text"
              placeholder={est_admin ? "Pseudo ou Email admin" : "Email ou pseudo"}
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
                id="mdp-input"
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
              style={{ backgroundColor: couleur_theme }}
              disabled={est_en_chargement}
            >
              {est_en_chargement 
                ? "Vérification..." 
                : est_admin ? "Accéder au Dashboard" : "Valider"
              }
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
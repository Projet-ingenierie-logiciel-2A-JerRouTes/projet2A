import React, { useState } from "react";
import { Eye, EyeOff, ShieldCheck, Undo2, AlertCircle } from "lucide-react";
import { login_v2 } from "../api/authApi";
import "../styles/Auth.css"; // On réutilise le même CSS pour la cohérence

const AdminAuth = ({ on_login, on_back }) => {
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
      // IMPORTANT : on passe "true" en 2ème argument pour le mode admin
      const user_data = await login_v2(credentials, true);
      on_login(user_data, true);
    } catch (error) {
      const status = error?.response?.status;
      const detail = error?.response?.data?.detail;

      if (status === 403)
        set_message_erreur("Accès refusé : Droits administrateur requis");
      else if (status === 404) set_message_erreur("Administrateur inconnu");
      else if (status === 401) set_message_erreur("Mot de passe incorrect");
      else set_message_erreur(detail || "Erreur de connexion");
    } finally {
      set_est_en_chargement(false);
    }
  };

  return (
    <div className="conteneur-auth">
      <div className="carte-auth" style={{ borderTop: "5px solid #ef4444" }}>
        {" "}
        {/* Touche rouge admin */}
        <div className="entete-auth">
          <ShieldCheck size={32} color="#ef4444" />
          <h2 className="titre-auth">Espace Admin</h2>
        </div>
        {message_erreur && (
          <div className="alerte-erreur">
            <AlertCircle size={18} />
            <span>{message_erreur}</span>
          </div>
        )}
        <form onSubmit={gerer_soumission} className="formulaire-auth">
          <div className="groupe-champ">
            <label htmlFor="admin-id">Identifiant Admin</label>
            <input
              id="admin_id"
              type="text"
              placeholder="Pseudo ou Email admin"
              value={identifiant}
              onChange={(e) => set_identifiant(e.target.value)}
              className="entree-texte"
              required
              autoFocus
            />
          </div>

          <div className="groupe-champ">
            <label htmlFor="admin-mdp">Mot de passe</label>
            <div className="conteneur-mdp">
              <input
                id="admin_mdp"
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
              >
                {voir_mdp ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          <div className="barre-actions">
            <button
              type="submit"
              className="bouton-valider"
              style={{ backgroundColor: "#ef4444" }} // Bouton rouge pour l'admin
              disabled={est_en_chargement}
            >
              {est_en_chargement ? "Vérification..." : "Accéder au Dashboard"}
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

export default AdminAuth;

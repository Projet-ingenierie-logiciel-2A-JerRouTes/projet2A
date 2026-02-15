import React, { useState } from "react";
import {
  UserPlus,
  Undo2,
  Eye,
  EyeOff,
  AlertCircle,
  Mail,
  User,
  Lock,
} from "lucide-react";
import { register } from "../api/authApi";
import "../styles/Register.css";

const Register = ({ on_register_success, on_back }) => {
  const [pseudo, set_pseudo] = useState("");
  const [email, set_email] = useState("");
  const [mdp, set_mdp] = useState("");
  const [confirmer_mdp, set_confirmer_mdp] = useState("");
  const [voir_mdp, set_voir_mdp] = useState(false);
  const [message_erreur, set_message_erreur] = useState("");
  const [est_en_chargement, set_est_en_chargement] = useState(false);

  const gerer_soumission = async (e) => {
    e.preventDefault();
    set_message_erreur("");

    // Vérifications locales
    if (mdp.length < 8) {
      set_message_erreur("Le mot de passe doit faire au moins 8 caractères.");
      return;
    }
    if (mdp !== confirmer_mdp) {
      set_message_erreur("Les mots de passe ne correspondent pas.");
      return;
    }

    set_est_en_chargement(true);
    try {
      const payload = { username: pseudo, email: email, password: mdp };
      const response = await register(payload);
      on_register_success(response);
    } catch (error) {
      set_message_erreur(
        error?.response?.data?.detail || "Erreur lors de l'inscription.",
      );
    } finally {
      set_est_en_chargement(false);
    }
  };

  return (
    <div className="conteneur-register">
      <div className="carte-register">
        <div className="entete-register">
          <UserPlus size={28} color="#345371" />
          <h2 className="titre-register">Inscription</h2>
        </div>

        {message_erreur && (
          <div className="alerte-erreur">
            <AlertCircle size={18} />
            <span>{message_erreur}</span>
          </div>
        )}

        <form onSubmit={gerer_soumission} className="formulaire-register">
          <div className="groupe-champ">
            <label>
              <User size={16} /> Pseudo
            </label>
            <input
              type="text"
              placeholder="Votre pseudo"
              value={pseudo}
              onChange={(e) => set_pseudo(e.target.value)}
              className="entree-texte"
              required
            />
          </div>

          <div className="groupe-champ">
            <label>
              <Mail size={16} /> Email
            </label>
            <input
              type="email"
              placeholder="exemple@mail.com"
              value={email}
              onChange={(e) => set_email(e.target.value)}
              className="entree-texte"
              required
            />
          </div>

          <div className="groupe-champ">
            <label>
              <Lock size={16} /> Mot de passe
            </label>
            <div className="conteneur-mdp">
              <input
                type={voir_mdp ? "text" : "password"}
                placeholder="••••••••"
                value={mdp}
                onChange={(e) => set_mdp(e.target.value)}
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

          <div className="groupe-champ">
            <label>Confirmer le mot de passe</label>
            <input
              type={voir_mdp ? "text" : "password"}
              placeholder="••••••••"
              value={confirmer_mdp}
              onChange={(e) => set_confirmer_mdp(e.target.value)}
              className="entree-texte"
              required
            />
          </div>

          <div className="barre-actions">
            <button
              type="submit"
              className="bouton-valider"
              disabled={est_en_chargement}
            >
              {est_en_chargement ? "Inscription..." : "Créer mon compte"}
            </button>
            <button type="button" onClick={on_back} className="bouton-retour">
              <Undo2 size={18} /> Retour
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;

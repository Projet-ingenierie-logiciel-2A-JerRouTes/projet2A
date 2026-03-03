import React, { useState, useEffect } from "react";
import { Users, UserPlus, ShieldPlus, Trash2, Edit, Undo2, Eye } from "lucide-react";
import { getAllUsers } from "../api/usersApi";
import Register from "./Register";
import "../styles/Gestion.css";
import AfficherUtilisateur from "./AfficherUtilisateur";

const GestionUtilisateurs = ({ on_back }) => {
  // --- ÉTATS ---
  const [utilisateurs, set_utilisateurs] = useState([]);
  const [est_en_chargement, set_est_en_chargement] = useState(true);
  const [vue_actuelle, set_vue_actuelle] = useState("liste"); // "liste", "ajout_user", "ajout_admin"
  const [utilisateur_selectionne, set_utilisateur_selectionne] = useState(null);

  // --- LOGIQUE DE RÉCUPÉRATION (RAFRAÎCHISSEMENT) ---
  const rafraichir_liste = async () => {
    set_est_en_chargement(true);
    try {
      const data = await getAllUsers();
      
      // AJOUT DU LOG ICI
      console.log("🔍 Données brutes reçues de getAllUsers :", data);
      
      set_utilisateurs(data);
    } catch (err) {
      console.error("Erreur récupération utilisateurs", err);
    } finally {
      set_est_en_chargement(false);
    }
  };

  // Chargement initial au montage du composant
  useEffect(() => {
    rafraichir_liste();
  }, []);

  // --- RENDU CONDITIONNEL DU FORMULAIRE D'AJOUT ---
if (vue_actuelle === "ajout_user" || vue_actuelle === "ajout_admin") {
  return (
    <Register 
      cre_admin={vue_actuelle === "ajout_admin"}
      on_back={() => set_vue_actuelle("liste")}
      on_register_success={() => {
        set_vue_actuelle("liste");
        rafraichir_liste();
      }}
    />
  );
}

// --- AJOUTE CE BLOC ICI : RENDU DU COMPOSANT DÉTAILS ---
if (vue_actuelle === "details" && utilisateur_selectionne) {
  return (
    <AfficherUtilisateur 
      utilisateur={utilisateur_selectionne}
      on_back={() => {
        set_vue_actuelle("liste");
        set_utilisateur_selectionne(null); // On nettoie la sélection
      }}
      on_edit={(id) => console.log("Modifier l'ID:", id)}
      on_delete={(id) => console.log("Supprimer l'ID:", id)}
    />
  );
}

// --- RENDU DE LA LISTE PRINCIPALE  ---
  return (
    <div className="carte-centrale gestion-panel">
      {/* ENTÊTE AVEC BOUTONS COLORÉS */}
      <div className="entete-gestion">
        <div className="titre-groupe">
          <Users size={32} color="#3b82f6" />
          <h1 className="titre-principal">Gestion des Utilisateurs</h1>
        </div>
        <div className="barre-outils">
          {/* Bouton Rouge pour Admin */}
          <button 
            className="bouton-action btn-ajout-admin" 
            onClick={() => set_vue_actuelle("ajout_admin")}
          >
            <ShieldPlus size={18} /> Ajouter un Admin
          </button>
          {/* Bouton Bleu pour User */}
          <button 
            className="bouton-action btn-ajout-user" 
            onClick={() => set_vue_actuelle("ajout_user")}
          >
            <UserPlus size={18} /> Ajouter un Utilisateur
          </button>
        </div>
      </div>

      {est_en_chargement ? (
        <p className="message-chargement">Mise à jour de la base de données...</p>
      ) : (
        <div className="conteneur-tableau">
          <table className="tableau-gestion">
            <thead>
              <tr>
                <th>ID</th>
                <th>Pseudo</th>
                <th>Email</th>
                <th>Rôle</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {utilisateurs.map((u) => (
                <tr key={u.user_id}>
                  <td>{u.user_id}</td>
                  <td className="texte-gras">{u.username}</td>
                  <td>{u.email}</td>
                  <td>
                    <span
                      className={`badge-role ${u.status === "admin" ? "bg-admin" : "bg-user"}`}
                    >
                      {u.status}
                    </span>
                  </td>
                  <td className="cellule-actions">
                  {/* Nouveau bouton Oeil */}
                  <button 
                    className="btn-icone" 
                    title="Voir le profil"
                    onClick={() => {
                      set_utilisateur_selectionne(u); // On stocke le user cliqué
                      set_vue_actuelle("details");    // On change la vue
                    }}
                  >
                    <Eye size={16} color="#3b82f6" />
                  </button>
                </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* BOUTON RETOUR AU MENU ADMIN */}
      <button className="bouton-retour-gestion" onClick={on_back}>
        <Undo2 size={18} /> Retour au menu
      </button>
    </div>
  );
};

export default GestionUtilisateurs;
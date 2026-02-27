import React, { useState, useEffect } from "react";
import { Users, UserPlus, ShieldPlus, Trash2, Edit, Undo2 } from "lucide-react";
import { getAllUsers } from "../api/usersApi";
import Register from "./Register";
import "../styles/Gestion.css";

const GestionUtilisateurs = ({ on_back }) => {
  // --- ÉTATS ---
  const [utilisateurs, set_utilisateurs] = useState([]);
  const [est_en_chargement, set_est_en_chargement] = useState(true);
  const [vue_actuelle, set_vue_actuelle] = useState("liste"); // "liste", "ajout_user", "ajout_admin"

  // --- LOGIQUE DE RÉCUPÉRATION (RAFRAÎCHISSEMENT) ---
  const rafraichir_liste = async () => {
    set_est_en_chargement(true);
    try {
      const data = await getAllUsers();
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
      cre_admin={vue_actuelle === "ajout_admin"} // Passé ici en paramètre
      on_back={() => set_vue_actuelle("liste")}
      on_register_success={() => {
        set_vue_actuelle("liste");
        rafraichir_liste();
      }}
    />
  );
}

  // --- RENDU DE LA LISTE PRINCIPALE ---
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
                    <button className="btn-icone" title="Modifier">
                      <Edit size={16} />
                    </button>
                    <button className="btn-icone btn-suppr" title="Supprimer">
                      <Trash2 size={16} />
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
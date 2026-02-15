import React, { useState, useEffect } from "react";
import { Users, UserPlus, ShieldPlus, Trash2, Edit, Undo2 } from "lucide-react";
import { getAllUsers } from "../api/usersApi";
import "../styles/Gestion.css";

const GestionUtilisateurs = ({ on_back }) => {
  const [utilisateurs, set_utilisateurs] = useState([]);
  const [est_en_chargement, set_est_en_chargement] = useState(true);

  useEffect(() => {
    const recuperer_utilisateurs = async () => {
      try {
        const data = await getAllUsers();
        set_utilisateurs(data);
      } catch (err) {
        console.error("Erreur récupération utilisateurs", err);
      } finally {
        set_est_en_chargement(false);
      }
    };
    recuperer_utilisateurs();
  }, []);

  return (
    <div className="carte-centrale gestion-panel">
      <div className="entete-gestion">
        <div className="titre-groupe">
          <Users size={32} color="#3b82f6" />
          <h1 className="titre-principal">Gestion des Utilisateurs</h1>
        </div>
        <div className="barre-outils">
          <button className="bouton-action btn-ajout-admin">
            <ShieldPlus size={18} /> Ajouter un Admin
          </button>
          <button className="bouton-action btn-ajout-user">
            <UserPlus size={18} /> Ajouter un Utilisateur
          </button>
        </div>
      </div>

      {est_en_chargement ? (
        <p className="message-chargement">Chargement des comptes...</p>
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

      <button className="bouton-retour-gestion" onClick={on_back}>
        <Undo2 size={18} /> Retour au menu
      </button>
    </div>
  );
};

export default GestionUtilisateurs;

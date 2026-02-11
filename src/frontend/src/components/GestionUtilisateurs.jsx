import { useState, useEffect } from "react";
import { getAllUsers } from "../api/authApi_vers_C";

function GestionUtilisateurs({ onBack }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await getAllUsers();
        setUsers(data);
      } catch (err) {
        console.error("Erreur lors de la récupération des utilisateurs", err);
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  return (
    <div className="container-principal">
      <div className="sous-container">
        <div className="login-form" style={{ maxWidth: "900px" }}>
          <h3 className="stock-titre">👥 Gestion des Utilisateurs</h3>

          <div className="admin-actions-header">
            <button className="bouton btn-add-admin">+ Ajouter Admin</button>
            <button className="bouton btn-add-user">
              + Ajouter Utilisateur
            </button>
          </div>

          {loading ? (
            <p className="message">Chargement des comptes...</p>
          ) : (
            <div className="admin-table-container">
              <table className="stock-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Pseudo</th>
                    <th>Rôle</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id_user}>
                      <td>{u.id_user}</td>
                      <td style={{ fontWeight: "bold" }}>{u.pseudo}</td>
                      <td>
                        <span
                          className={`role-badge ${
                            u.role === "Administrateur"
                              ? "role-admin"
                              : "role-generic"
                          }`}
                        >
                          {u.role}
                        </span>
                      </td>
                      <td>
                        <button className="action-icon-btn" title="Modifier">
                          ✏️
                        </button>
                        <button className="action-icon-btn" title="Supprimer">
                          🗑️
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <button
            className="bouton"
            style={{ marginTop: "20px" }}
            onClick={onBack}
          >
            Retour au Tableau de Bord
          </button>
        </div>
      </div>
    </div>
  );
}

export default GestionUtilisateurs;

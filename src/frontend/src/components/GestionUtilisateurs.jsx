import { useState, useEffect } from "react";
// Assure-tu que l'import pointe vers le bon fichier (userApi ou authApi selon ton organisation)
import { getAllUsers } from "../api/usersApi";

function GestionUtilisateurs({ onBack }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await getAllUsers();
        // data est une liste d'objets : [{user_id, username, email, status}, ...]
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
                    <th>Email</th>
                    <th>Rôle/Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    // On utilise user_id car c'est la clé renvoyée par UserPublic
                    <tr key={u.user_id}>
                      <td>{u.user_id}</td>
                      <td style={{ fontWeight: "bold" }}>{u.username}</td>
                      <td>{u.email}</td>
                      <td>
                        <span
                          className={`role-badge ${
                            u.status === "admin" ||
                            u.status === "Administrateur"
                              ? "role-admin"
                              : "role-generic"
                          }`}
                        >
                          {u.status}
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
            style={{ marginTop: "20px", backgroundColor: "#6c757d" }}
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

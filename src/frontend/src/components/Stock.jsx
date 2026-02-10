import React from 'react';

function Stock({ user }) {
  return (
    <div className="container-principal">
      <div className="sous-container">
        {user ? (
          /* CAS 1 : On a un utilisateur (Connexion réussie) */
          <div className="login-form">
            <h3>Recherche de recettes à partir de ton inventaire {user.pseudo}</h3>
          </div>
        ) : (
          /* CAS 2 : On n'a pas d'utilisateur (Création de stock sans compte ou erreur) */
          <div className="login-form">
            <h3>Recherche de recettes - Sans compte</h3>
          </div>
        )}
      </div>
    </div>
  );
}

export default Stock;

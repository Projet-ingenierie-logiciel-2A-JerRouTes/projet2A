import React from 'react';

function Stock({ user }) {
  return (
    <div className="container-principal">
      <div className="sous-container">
        <div className="login-form">
          <h2>Mon Stock</h2>
          <p>Bienvenue dans ton inventaire, {user?.pseudo} !</p>
        </div>
      </div>
    </div>
  );
}

export default Stock;

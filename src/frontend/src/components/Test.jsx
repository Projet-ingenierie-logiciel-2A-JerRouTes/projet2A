import React from 'react';

function Test() {
  const info = {
    titre: "Un truc en plus",
    etat: "du blabla"
  };

  return (
    <div style={{ border: '1px solid red', padding: '10px', marginTop: '10px' }}>
      <h2>{info.titre}</h2>
      <p>Statut : <strong>{info.etat}</strong></p>
    </div>
  );
}

// ICI : remplace RapportTechnique par Test
export default Test;

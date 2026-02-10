import React, { useState, useEffect } from 'react';

function Stock({ user }) {
  const [items, setItems] = useState({});
  const [catalogue, setCatalogue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error_message, setErrorMessage] = useState('');

  useEffect(() => {
    const loadAllData = async () => {
      setLoading(true);
      setErrorMessage('');
      try {
        const resIngr = await fetch('http://localhost:8000/ingredients');
        if (!resIngr.ok) throw new Error("Erreur catalogue");
        const dataIngr = await resIngr.json();
        setCatalogue(dataIngr);

        if (user && user.id_stock) {
          const resStock = await fetch(`http://localhost:8000/stock/${user.id_stock}`);
          if (!resStock.ok) throw new Error("Erreur serveur");
          const dataStock = await resStock.json();
          setItems(dataStock.items_by_ingredient || {});
        }
      } catch (err) {
        setErrorMessage("Serveur injoignable");
      } finally {
        setLoading(false);
      }
    };
    loadAllData();
  }, [user]);

  const getIngredientInfo = (id) => {
    return catalogue.find(i => String(i.id_ingredient) === String(id));
  };

  return (
    <div className="container-principal">
      <div className="sous-container">
        <div className="login-form" style={{ maxWidth: '800px' }}>
          <h3 className="stock-titre">
            {user ? `Inventaire de ${user.pseudo}` : "Nouveau Stock"}
          </h3>

          {loading ? (
            <p className="loading-text">Chargement...</p>
          ) : (
            <div className="stock-table-container">
              {Object.keys(items).length > 0 ? (
                <table className="stock-table">
                  <thead>
                    <tr>
                      <th>Ingrédient</th>
                      <th>Quantité</th>
                      <th>Expiration</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(items).map(([id, lots]) => {
                      const info = getIngredientInfo(id);
                      return lots.map((lot, i) => (
                        <tr key={`${id}-${i}`}>
                          <td className="ingredient-name">{info ? info.name : id}</td>
                          <td>{lot.quantity} {info ? info.unit : ""}</td>
                          <td className="expiry-date">{lot.expiry_date}</td>
                        </tr>
                      ));
                    })}
                  </tbody>
                </table>
              ) : (
                <p className="empty-message">Aucun ingrédient dans le stock.</p>
              )}
            </div>
          )}

          <button type="button" className="bouton" style={{ marginTop: '20px' }}>
            {user ? "Ajouter ingrédient" : "Saisir ingrédient"}
          </button>
        </div>
      </div>

      <div className="sous-container">
        {error_message && (
          <div className="message">
            🛑 {error_message}
          </div>
        )}
      </div>
    </div>
  );
}

export default Stock;

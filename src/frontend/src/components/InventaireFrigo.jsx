import { useState } from "react";

function InventaireFrigo() {
  const [ingredient, setIngredient] = useState("");
  const [quantite, setQuantite] = useState("");
  const [stock, setStock] = useState([]);

  // Fonction pour ajouter un produit au tableau
  const enregistrerProduit = (e) => {
    e.preventDefault();
    if (ingredient && quantite) {
      const nouvelArticle = {
        id: Date.now(), // Génère un ID unique basé sur le temps
        nom: ingredient,
        qte: quantite,
      };
      setStock([...stock, nouvelArticle]); // Ajoute l'article à la liste existante
      setIngredient(""); // Réinitialise le champ produit
      setQuantite(""); // Réinitialise le champ quantité
    }
  };

  // Fonction pour supprimer un produit de la liste
  const supprimerArticle = (id) => {
    setStock(stock.filter((item) => item.id !== id));
  };

  return (
    <div className="inventory-container">
      <h2>📦 Saisie du Stock Frigo</h2>

      <form onSubmit={enregistrerProduit} className="inventory-form">
        <input
          type="text"
          placeholder="Produit (ex: Œufs)"
          value={ingredient}
          onChange={(e) => setIngredient(e.target.value)}
        />
        <input
          type="text"
          placeholder="Quantité (ex: 6)"
          value={quantite}
          onChange={(e) => setQuantite(e.target.value)}
        />
        <button type="submit">Enregistrer</button>
      </form>

      <div className="inventory-list">
        {stock.length === 0 ? (
          <p>Le frigo est vide.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Produit</th>
                <th>Quantité</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {stock.map((item) => (
                <tr key={item.id}>
                  <td>{item.nom}</td>
                  <td>{item.qte}</td>
                  <td>
                    <button
                      onClick={() => supprimerArticle(item.id)}
                      className="delete-btn"
                    >
                      ❌
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default InventaireFrigo;

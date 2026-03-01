import React, { useState } from "react";
import { Trash2, Utensils, Plus, Loader2 } from "lucide-react";
import "../styles/SaisieIngredients.css";

const SaisieIngredientsInvite = ({ on_back, on_rechercher }) => {
  const [saisie, set_saisie] = useState("");
  const [ingredients_choisis, set_ingredients_choisis] = useState([]);
  const [chargement, set_chargement] = useState(false);

  // Ajoute l'ingrédient saisi à la liste locale (sans forcer le lowercase pour rester flexible)
  const ajouter_ingredient = () => {
    const nom = saisie.trim(); 
    if (nom && !ingredients_choisis.includes(nom)) {
      set_ingredients_choisis([...ingredients_choisis, nom]);
      set_saisie(""); 
    }
  };

  // Permet d'ajouter un ingrédient avec la touche "Entrée"
  const gerer_touche_clavier = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      ajouter_ingredient();
    }
  };

  // Supprime un ingrédient de la liste locale
  const supprimer_ingredient = (index) => {
    set_ingredients_choisis(ingredients_choisis.filter((_, i) => i !== index));
  };

  // Vide toute la liste d'un coup
  const vider_liste = () => {
    set_ingredients_choisis([]);
  };

  // --- TRANSMISSION AU PARENT ---
  const gerer_clic_recherche = async () => {
    if (ingredients_choisis.length === 0) return;
    
    set_chargement(true);
    
    // On simule un léger délai pour le feedback visuel avant de basculer
    // Cette fonction mettra à jour 'ingredients_filtres' dans App.jsx
    await on_rechercher(ingredients_choisis);
    
    set_chargement(false);
  };

  return (
    <div className="container-saisie-invite">
      {/* Bouton de retour vers la grille de suggestions */}
      <button className="bouton-retour-simple" onClick={on_back}>
        ← Retour
      </button>
      
      <h1 className="titre-principal-pluriel">Ingrédients disponibles</h1>

      <div className="zone-saisie">
        <div style={{ display: 'flex', gap: '10px', width: '100%' }}>
          <input 
            type="text" 
            placeholder="Ex: butter, bread slice, cheddar..." 
            value={saisie}
            onChange={(e) => set_saisie(e.target.value)}
            onKeyDown={gerer_touche_clavier}
            style={{ 
              flex: 1, 
              padding: '12px', 
              borderRadius: '8px', 
              border: '1px solid #ccc',
              fontSize: '16px' 
            }}
          />
          <button 
            onClick={ajouter_ingredient}
            className="btn-ajouter-action"
            style={{ 
              backgroundColor: '#4A90E2', 
              color: 'white', 
              border: 'none', 
              borderRadius: '8px', 
              padding: '0 20px', 
              cursor: 'pointer' 
            }}
          >
            <Plus size={20} />
          </button>
        </div>
      </div>

      <div className="tableau-ingredients-container" style={{ marginTop: '20px', minHeight: '200px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <span style={{ fontSize: '14px', color: '#666' }}>
            {ingredients_choisis.length} ingrédient(s) ajouté(s)
          </span>
          {ingredients_choisis.length > 0 && (
            <button onClick={vider_liste} style={{ background: 'none', border: 'none', color: '#999', cursor: 'pointer', fontSize: '12px', textDecoration: 'underline' }}>
              Tout effacer
            </button>
          )}
        </div>

        <table className="tableau-ingredients">
          <thead>
            <tr>
              <th>Nom de l'ingrédient</th>
              <th style={{ width: "80px", textAlign: 'center' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {ingredients_choisis.map((ing, index) => (
              <tr key={index}>
                <td style={{ textTransform: 'capitalize' }}>{ing}</td>
                <td style={{ textAlign: 'center' }}>
                  <button 
                    onClick={() => supprimer_ingredient(index)}
                    className="btn-suppr-table"
                    style={{ background: 'none', border: 'none', color: '#e74c3c', cursor: 'pointer' }}
                  >
                    <Trash2 size={18} />
                  </button>
                </td>
              </tr>
            ))}
            {/* Message si le tableau est vide */}
            {ingredients_choisis.length === 0 && (
              <tr>
                <td colSpan="2" style={{ textAlign: 'center', padding: '40px', color: '#999', fontStyle: 'italic' }}>
                  Votre liste est vide. Ajoutez des ingrédients pour cuisiner !
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* BOUTON D'ACTION : Envoie la liste au parent */}
      <button 
        className="bouton-trouver-recettes" 
        disabled={ingredients_choisis.length === 0 || chargement}
        onClick={gerer_clic_recherche}
        style={{ 
          backgroundColor: ingredients_choisis.length > 0 ? '#27ae60' : '#bdc3c7',
          color: 'white',
          width: '100%',
          padding: '15px',
          border: 'none',
          borderRadius: '8px',
          fontWeight: 'bold',
          fontSize: '18px',
          cursor: (ingredients_choisis.length > 0 && !chargement) ? 'pointer' : 'not-allowed',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '10px',
          marginTop: '25px',
          transition: 'all 0.3s ease'
        }}
      >
        {chargement ? (
          <> <Loader2 className="animate-spin" size={20} /> Mise à jour... </>
        ) : (
          <> <Utensils size={20} /> Trouver des recettes </>
        )}
      </button>
    </div>
  );
};

export default SaisieIngredientsInvite;
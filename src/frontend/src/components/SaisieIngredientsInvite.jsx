import React, { useState } from "react";
import { Trash2, Utensils, Plus, Loader2 } from "lucide-react";
// 1. IMPORTATION DIRECTE DE L'API
import { findRecipe } from "../api/recetteApi"; 
import "../styles/SaisieIngredients.css";

const SaisieIngredientsInvite = ({ on_back }) => {
  const [saisie, set_saisie] = useState("");
  const [ingredients_choisis, set_ingredients_choisis] = useState([]);
  const [chargement, set_chargement] = useState(false);

  const ajouter_ingredient = () => {
    const nom = saisie.trim(); 
    if (nom && !ingredients_choisis.includes(nom)) {
        set_ingredients_choisis([...ingredients_choisis, nom]);
        set_saisie(""); 
    }
  };

  const gerer_touche_clavier = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      ajouter_ingredient();
    }
  };

  const supprimer_ingredient = (index) => {
    set_ingredients_choisis(ingredients_choisis.filter((_, i) => i !== index));
  };

  // --- LOGIQUE DE RECHERCHE AUTONOME ---
  const gerer_clic_recherche = async () => {
    set_chargement(true);
    
    // On affiche ce qui va être envoyé (identique à ton Swagger)
    console.log("🚀 Tentative d'appel DIRECT depuis le composant :");
    console.log(JSON.stringify({ ingredients: ingredients_choisis }));

    try {
      // 2. APPEL DIRECT DE LA FONCTION API
      const reponse = await findRecipe(ingredients_choisis);
      
      console.log("✅ RÉPONSE DU SERVEUR REÇUE :");
      
      if (reponse && reponse.length > 0) {
        // Affiche les recettes sous forme de tableau (comme dans ton Swagger)
        console.table(reponse); 
      } else {
        console.warn("⚠️ Le serveur a répondu, mais la liste est vide [].");
        console.log("Contenu de la réponse :", reponse);
      }
    } catch (error) {
      console.error("❌ Erreur lors de l'appel API :", error);
    } finally {
      set_chargement(false);
    }
  };

  return (
    <div className="container-saisie-invite">
      <button className="bouton-retour-simple" onClick={on_back}>
        ← Retour
      </button>
      
      <h1 className="titre-principal-pluriel">Ingrédients disponibles</h1>

      <div className="zone-saisie">
        <div style={{ display: 'flex', gap: '10px', width: '100%' }}>
          <input 
            type="text" 
            placeholder="Ex: butter, bread slice..." 
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
            style={{ backgroundColor: '#4A90E2', color: 'white', border: 'none', borderRadius: '8px', padding: '0 20px', cursor: 'pointer' }}
          >
            <Plus size={20} />
          </button>
        </div>
      </div>

      <div className="tableau-ingredients-container" style={{ marginTop: '20px', minHeight: '200px' }}>
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
                    style={{ background: 'none', border: 'none', color: '#e74c3c', cursor: 'pointer' }}
                  >
                    <Trash2 size={18} />
                  </button>
                </td>
              </tr>
            ))}
            {ingredients_choisis.length === 0 && (
              <tr>
                <td colSpan="2" style={{ textAlign: 'center', padding: '40px', color: '#999', fontStyle: 'italic' }}>
                  Votre liste est vide.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

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
          marginTop: '25px'
        }}
      >
        {chargement ? (
          <> <Loader2 className="animate-spin" size={20} /> Recherche... </>
        ) : (
          <> <Utensils size={20} /> Trouver des recettes </>
        )}
      </button>
    </div>
  );
};

export default SaisieIngredientsInvite;
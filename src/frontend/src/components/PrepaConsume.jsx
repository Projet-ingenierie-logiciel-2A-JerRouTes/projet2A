import React, { useState, useMemo } from "react";
import { 
  Undo2, 
  Utensils, 
  ClipboardList, 
  Database, 
  Users, 
  Loader2, 
  CheckCircle, 
  XCircle 
} from "lucide-react";
import { useIngredientsRecette } from "../hooks/useIngredientsRecette";
// Import mis à jour selon ta consigne
import { consumeIngredientFefo } from "../api/stockApi";
import Confirmation from "./Confirmation"; 

const PrepaConsume = ({ recette, on_back, liste_ingredients_complet }) => {
  const [nb_personnes, set_nb_personnes] = useState(recette?.portions || 2);
  const [en_cours_de_consommation, set_en_cours_de_consommation] = useState(false);
  
  // État pour gérer l'affichage de ta modale de confirmation
  const [modale_ouverte, set_modale_ouverte] = useState(false);
  
  const { ingredients_complets, chargement_ing } = useIngredientsRecette(recette);

  // --- LOGIQUE DE STOCK ---
  const obtenir_stock_reel = (id_recherche) => {
    const match = liste_ingredients_complet?.find(
      (item) => Number(item.ingredient_id) === Number(id_recherche)
    );
    return match || null;
  };

  // Calcul automatique de la disponibilité et préparation du payload
  const { tout_est_disponible, liste_a_consommer } = useMemo(() => {
    if (!ingredients_complets) return { tout_est_disponible: false, liste_a_consommer: [] };

    let ok = true;
    const liste = ingredients_complets.map(ing => {
      const qte_requise = (ing.quantity / (recette.portions || 1)) * nb_personnes;
      const info_stock = obtenir_stock_reel(ing.ingredient_id);
      
      // Si l'ingrédient n'est pas en stock ou en quantité insuffisante
      if (!info_stock || info_stock.total_quantity < qte_requise) ok = false;

      return {
        ingredient_id: ing.ingredient_id,
        quantity: Number(qte_requise.toFixed(2))
      };
    });
    return { tout_est_disponible: ok, liste_a_consommer: liste };
  }, [ingredients_complets, nb_personnes, liste_ingredients_complet]);

  // --- ACTION DE CONSOMMATION (Déclenchée par "on_confirmer" de la modale) ---
  const gerer_consommation_totale = async () => {
    set_modale_ouverte(false); // Ferme la modale
    set_en_cours_de_consommation(true);
    
    try {
      // Boucle sur les ingrédients pour appeler l'API de manière séquentielle
      for (const item of liste_a_consommer) {
        await consumeIngredientFefo(item.ingredient_id, item.quantity);
      }
      // Succès : on retourne à la fiche
      on_back(); 
    } catch (err) {
      console.error("❌ Erreur lors de la consommation :", err);
      alert("Une erreur est survenue lors de la mise à jour des stocks.");
    } finally {
      set_en_cours_de_consommation(false);
    }
  };

  return (
    <div className="carte-centrale-detail shadow-2xl animate-fade" style={{ background: "white", borderRadius: "30px", padding: "30px" }}>
      
      {/* MODALE DE CONFIRMATION PERSONNALISÉE */}
      <Confirmation 
        ouvert={modale_ouverte}
        on_annuler={() => set_modale_ouverte(false)}
        on_confirmer={gerer_consommation_totale}
        titre="Confirmer la préparation"
        message={`Voulez-vous déduire du stock les ingrédients pour ${nb_personnes} personnes ?`}
        texte_confirmer="Oui, consommer"
        couleur_confirmer="bleu"
      />

      {/* TITRE */}
      <div style={{ textAlign: "center", marginBottom: "20px" }}>
        <h1 style={{ color: "#000", fontSize: "2.2rem", fontWeight: "800", marginBottom: "0" }}>
          Préparation : {recette.name}
        </h1>
      </div>

      {/* ZONE DE SCROLL */}
      <div className="scroll-contenu" style={{ overflowY: "auto", maxHeight: "60vh" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "25px", padding: "0 10px" }}>
          
          {/* SECTION 1 : BESOINS CALCULÉS */}
          <div style={{ backgroundColor: "#f8fafc", padding: "20px", borderRadius: "15px", border: "1px solid #e2e8f0" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "15px", color: "#334155" }}>
              <ClipboardList size={20} color="#3b82f6" /> Ingrédients nécessaires
            </h3>
            {chargement_ing ? (
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <Loader2 className="animate-spin" size={18} /> Calcul...
              </div>
            ) : (
              <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                {ingredients_complets?.map((ing, i) => (
                  <li key={i} style={{ padding: "10px 0", borderBottom: "1px solid #e2e8f0", display: "flex", justifyContent: "space-between" }}>
                    <strong style={{ color: "#1e293b" }}>{ing.name}</strong> 
                    <span style={{ color: "#3b82f6", fontWeight: "600" }}>
                      {((ing.quantity / recette.portions) * nb_personnes).toFixed(1)} {ing.unit}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* SECTION 2 : DISPONIBILITÉ RÉELLE */}
          <div style={{ backgroundColor: "#f0fdf4", padding: "20px", borderRadius: "15px", border: "1px solid #dcfce7" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "15px", color: "#166534" }}>
              <Database size={20} color="#22c55e" /> Vos stocks actuels
            </h3>
            <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
              {ingredients_complets?.map((ing, i) => {
                const qte_requise = (ing.quantity / (recette.portions || 1)) * nb_personnes;
                const info_stock = obtenir_stock_reel(ing.ingredient_id);
                const qte_stock = info_stock ? info_stock.total_quantity : 0;
                const est_disponible = qte_stock >= qte_requise;

                return (
                  <li key={i} style={{ padding: "10px 0", borderBottom: "1px solid #dcfce7", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div style={{ display: "flex", flexDirection: "column", textAlign: "left" }}>
                      <span style={{ fontWeight: "600", color: "#166534" }}>{ing.name}</span>
                      <span style={{ fontSize: "0.85rem", color: "#64748b" }}>
                        {info_stock ? `En stock : ${qte_stock} ${info_stock.unit}` : "Absent du stock"}
                      </span>
                    </div>
                    {est_disponible ? <CheckCircle size={22} color="#22c55e" /> : <XCircle size={22} color="#ef4444" />}
                  </li>
                );
              })}
            </ul>
          </div>

          {/* SÉLECTEUR DE PORTIONS */}
          <div style={{ backgroundColor: "#f1f5f9", padding: "20px", borderRadius: "15px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "15px" }}>
              <Users size={22} color="#3b82f6" />
              <span style={{ fontWeight: "700" }}>Ajuster pour</span>
              <input 
                type="number" 
                value={nb_personnes} 
                onChange={(e) => set_nb_personnes(Math.max(1, parseInt(e.target.value) || 1))}
                style={{ width: "70px", padding: "8px", borderRadius: "10px", border: "2px solid #3b82f6", textAlign: "center", fontWeight: "bold" }}
              />
              <span style={{ fontWeight: "700" }}>personnes</span>
            </div>
          </div>
        </div>
      </div>

      {/* PIED DE PAGE FIXE */}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "12px", marginTop: "20px" }}>
        <button 
          className="bouton-action" 
          disabled={!tout_est_disponible || en_cours_de_consommation}
          style={{ 
            backgroundColor: (!tout_est_disponible || en_cours_de_consommation) ? "#94a3b8" : "#3b82f6", 
            padding: "12px 60px", borderRadius: "30px", color: "white", fontWeight: "700", border: "none", cursor: (tout_est_disponible && !en_cours_de_consommation) ? "pointer" : "not-allowed", display: "flex", alignItems: "center", gap: "10px" 
          }}
          onClick={() => set_modale_ouverte(true)}
        >
          {en_cours_de_consommation ? <Loader2 className="animate-spin" size={20} /> : <Utensils size={20} />}
          {!tout_est_disponible ? "Stock insuffisant" : en_cours_de_consommation ? "Mise à jour..." : `Valider pour ${nb_personnes} pers.`}
        </button>

        <button onClick={on_back} style={{ background: "none", border: "none", color: "#64748b", textDecoration: "underline", cursor: "pointer", display: "flex", alignItems: "center", gap: "5px" }}>
          <Undo2 size={18} /> Retour à la fiche
        </button>
      </div>
    </div>
  );
};

export default PrepaConsume;
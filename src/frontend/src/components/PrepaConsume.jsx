import React, { useState } from "react";
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

const PrepaConsume = ({ recette, on_back, stock_utilisateur, liste_ingredients_complet }) => {
  // Debug pour vérifier la réception des données
  console.log("📊 Données brutes reçues :", liste_ingredients_complet);
  console.log(recette)

  const [nb_personnes, set_nb_personnes] = useState(recette?.portions || 2);
  
  // Hook pour obtenir les noms et unités lisibles des ingrédients de la recette
  const { ingredients_complets, chargement_ing } = useIngredientsRecette(recette);

  // ----------------------------------------------------------------------------------------
  // On va avoir un pb il n'y a pas unit dans la description des ingredients d'une recette
  // -----------------------------------------------------------------------------

  // --- LOGIQUE DE COMPARAISON ---
  // On construit la liste à chaque rendu en fonction de nb_personnes
  const ingredients_necessaires = recette?.ingredients?.map((ing) => {
    // Calcul de la quantité ajustée : (Qté de base / Portions de base) * Portions voulues
    const quantite_calculee = (ing.quantity / (recette.portions || 1)) * nb_personnes;

    return {
      ingredient_id: ing.ingredient_id,
      quantity: Number(quantite_calculee.toFixed(2)) // On arrondit pour éviter les 0.000000004
    };
  }) || [];

  console.log("📋 Ingrédients nécessaires calculés :", ingredients_necessaires);

  // 2. Fonction de recherche dans l'objet AGGRÉGÉ (liste_ingredients_complet)
  const obtenir_stock_reel = (id_recherche) => {
    const match = liste_ingredients_complet?.find(
      (item) => Number(item.ingredient_id) === Number(id_recherche)
    );
    // On retourne l'objet complet pour avoir accès à total_quantity et unit
    return match || null;
  };

  return (
    <div className="carte-centrale-detail shadow-2xl animate-fade">
      {/* TITRE FIXE (Ne défile pas) */}
      <div style={{ textAlign: "center", marginBottom: "20px" }}>
        <h1 className="titre-principal" style={{ color: "#000", fontSize: "2.2rem", fontWeight: "800", marginBottom: "0" }}>
          Préparation : {recette.name}
        </h1>
      </div>

      {/* --- ZONE DE SCROLL INTERNE (CSS: .scroll-contenu) --- */}
      <div className="scroll-contenu">
        <div className="details-container" style={{ padding: "0 10px", display: "flex", flexDirection: "column", gap: "25px" }}>
          
          {/* SECTION 1 : BESOINS CALCULÉS */}
          <div style={{ backgroundColor: "#f8fafc", padding: "20px", borderRadius: "15px", border: "1px solid #e2e8f0", width: "100%" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "15px", color: "#334155" }}>
              <ClipboardList size={20} color="#3b82f6" /> Ingrédients nécessaires
            </h3>

            {chargement_ing ? (
              <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "#64748b" }}>
                <Loader2 className="animate-spin" size={18} /> Calcul des besoins...
              </div>
            ) : (
              <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                {ingredients_complets?.map((ing, i) => {
                  const qte_requise = (ing.quantity / recette.portions) * nb_personnes;
                  return (
                    <li key={i} style={{ padding: "10px 0", borderBottom: "1px solid #e2e8f0", display: "flex", justifyContent: "space-between" }}>
                      <strong style={{ color: "#1e293b" }}>{ing.name}</strong> 
                      <span style={{ color: "#3b82f6", fontWeight: "600" }}>
                        {qte_requise.toFixed(1)} {ing.unit}
                      </span>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          {/* SECTION 2 : DISPONIBILITÉ RÉELLE */}
          <div style={{ backgroundColor: "#f0fdf4", padding: "20px", borderRadius: "15px", border: "1px solid #dcfce7", width: "100%" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "15px", color: "#166534" }}>
              <Database size={20} color="#22c55e" /> Vos stocks actuels
            </h3>

            <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
              {ingredients_complets?.map((ing, i) => {
                // Calcul du besoin pour cet ingrédient précis
                const qte_requise = (ing.quantity / (recette.portions || 1)) * nb_personnes;
                
                // RÉCUPÉRATION DE LA QUANTITÉ DEPUIS TA LISTE COMPLÈTE (Agrégée)
                const info_stock = obtenir_stock_reel(ing.ingredient_id);
                const qte_stock = info_stock ? info_stock.total_quantity : 0;
                
                const est_disponible = qte_stock >= qte_requise;

                return (
                  <li key={i} style={{ padding: "10px 0", borderBottom: "1px solid #dcfce7", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div style={{ display: "flex", flexDirection: "column", textAlign: "left" }}>
                      <span style={{ fontWeight: "600", color: "#166534" }}>{ing.name}</span>
                      <span style={{ fontSize: "0.85rem", color: "#64748b" }}>
                        {info_stock 
                          ? `En stock : ${qte_stock} ${info_stock.unit}` 
                          : "Non trouvé en stock"}
                      </span>
                    </div>
                    {est_disponible ? (
                      <CheckCircle size={22} color="#22c55e" />
                    ) : (
                      <XCircle size={22} color="#ef4444" />
                    )}
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
      {/* --- FIN DE LA ZONE DE SCROLL --- */}

      {/* PIED DE PAGE FIXE (Boutons toujours visibles) */}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "12px", marginTop: "20px", paddingBottom: "10px" }}>
        <button 
          className="bouton-action" 
          style={{ backgroundColor: "#3b82f6", padding: "12px 60px", borderRadius: "30px", color: "white", fontWeight: "700", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: "10px" }}
          onClick={() => console.log("Action : Soustraction des stocks demandée")}
        >
          <Utensils size={20} /> Mise à jour stock pour {nb_personnes} pers.
        </button>

        <button className="bouton-retour-gestion" onClick={on_back}>
          <Undo2 size={18} /> Retour à la fiche
        </button>
      </div>
    </div>
  );
};

export default PrepaConsume;
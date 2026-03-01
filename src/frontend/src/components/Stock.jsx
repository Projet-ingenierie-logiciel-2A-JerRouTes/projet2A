import React, { useState, useEffect } from "react";
import { Package, PlusCircle, LogOut, SquarePen, Trash2, Eraser, Search } from "lucide-react";
import { 
  getAllStocks, 
  createStock, 
  getAllIngredients, 
  deleteLotsStock, 
  deleteStock 
} from "../api/stockApi";
import { userStockTable } from "../hooks/userStockTable";
import SelecteurStock from "./SelecteurStock";
import BarreSaisieStock from "./BarreSaisieStock";
import Confirmation from "./Confirmation"; // Ton nouveau composant
import "../styles/Gestion.css";
import "../styles/Confirmation.css"; // Ton nouveau CSS

const Stock = ({ 
  user, 
  on_logout, 
  set_ajout_ingredient, 
  id_stock, 
  set_id_stock, 
  set_chercher_recette, 
  set_list_nom_stock, 
  list_nom_stock, 
  set_catalogue 
}) => {
  // --- ÉTATS ---
  const [chargement_initial, set_chargement_initial] = useState(true);
  const [affichage_barre, set_affichage_barre] = useState(false);
  
  // État pour gérer la modale de confirmation
  const [etat_confirmation, set_etat_confirmation] = useState({
    ouvert: false,
    action: null, // "vider" ou "supprimer"
    nom_cible: ""
  });

  // --- HOOK MÉTIER ---
  const { formatted_stock, refresh_stock } = userStockTable(id_stock);

  // --- LOGIQUE DE GESTION DES STOCKS ---

  const gerer_creation_stock = async (nom) => {
    try {
      const data = await createStock(nom);
      const nouvel_id = data.stock_id;
      set_list_nom_stock((prev) => [...prev, { stock_id: nouvel_id, name: nom }]);
      set_id_stock(nouvel_id);
      set_affichage_barre(false);
    } catch (error) {
      console.error("❌ Erreur création stock:", error);
    }
  };

  // Fonctions pour ouvrir la modale
  const preparer_vidage = () => {
    set_etat_confirmation({ ouvert: true, action: "vider", nom_cible: nom_stock_actuel });
  };

  const preparer_suppression = () => {
    set_etat_confirmation({ ouvert: true, action: "supprimer", nom_cible: nom_stock_actuel });
  };

  const fermer_confirmation = () => {
    set_etat_confirmation({ ouvert: false, action: null, nom_cible: "" });
  };

  // Exécution réelle après confirmation dans la modale
  const confirmer_action = async () => {
    try {
      if (etat_confirmation.action === "vider") {
        await deleteLotsStock(id_stock);
        if (refresh_stock) await refresh_stock();
      } 
      else if (etat_confirmation.action === "supprimer") {
        await deleteStock(id_stock);
        const nouvelle_liste = list_nom_stock.filter(s => s.stock_id !== id_stock);
        set_list_nom_stock(nouvelle_liste);
        set_id_stock(nouvelle_liste.length > 0 ? nouvelle_liste[0].stock_id : null);
      }
    } catch (error) {
      console.error(`❌ Erreur lors de l'action ${etat_confirmation.action}:`, error);
    } finally {
      fermer_confirmation(); // Ferme la modale et supprime le deuxième affichage (pas d'alert)
    }
  };

  // --- CHARGEMENT INITIAL ---
  useEffect(() => {
    const initialiser_page = async () => {
      try {
        set_chargement_initial(true);
        const [ids_noms_stock, data_catalogue] = await Promise.all([
          getAllStocks(user?.user_id || user?.id),
          getAllIngredients()
        ]);
        set_list_nom_stock(ids_noms_stock);
        if (set_catalogue) set_catalogue(data_catalogue);
        if (ids_noms_stock.length > 0 && !id_stock) {
          set_id_stock(ids_noms_stock[0].stock_id);
        }
      } catch (err) {
        console.error("❌ Erreur initialisation:", err);
      } finally {
        set_chargement_initial(false);
      }
    };
    if (user) initialiser_page();
  }, [user, set_id_stock, set_list_nom_stock, set_catalogue, id_stock]);

  const nom_stock_actuel = list_nom_stock.find(s => s.stock_id === id_stock)?.name || "";

  return (
    <div className="carte-centrale gestion-panel">
      {/* ENTÊTE */}
      <div className="entete-gestion">
        <div className="titre-groupe">
          <Package size={32} color="#3b82f6" />
          <h1 className="titre-principal">Inventaire de {user?.username}</h1>
        </div>
        <div className="barre-outils">
          <button className="bouton-action btn-ingredient-style" onClick={() => set_ajout_ingredient(true)}>
            <PlusCircle size={18} /> Ajouter un ingrédient dans {nom_stock_actuel}
          </button>
        </div>
      </div>

      {affichage_barre && (
        <BarreSaisieStock on_valider={gerer_creation_stock} on_annuler={() => set_affichage_barre(false)} />
      )}

      <div style={{ marginBottom: "20px" }}>
        <p style={{ color: "#475569", fontSize: "0.9rem", marginBottom: "8px" }}>Choisir un inventaire :</p>
        <SelecteurStock list_id_stock={list_nom_stock} on_change_stock={(id) => set_id_stock(id)} />
      </div>

      {/* TABLEAU */}
      <div className="conteneur-tableau">
        <table className="tableau-gestion">
          <thead>
            <tr>
              <th>Nom ingrédient</th>
              <th>Quantité</th>
              <th>Validité</th>
              <th style={{ textAlign: "center" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {formatted_stock.length > 0 ? (
              formatted_stock.map((item) => (
                <tr key={item.stock_item_id}>
                  <td>{item.nom_ingredient}</td>
                  <td>{item.quantite_affichage}</td>
                  <td>{item.validite}</td>
                  <td style={{ textAlign: "center" }}>
                    <div className="barre-outils" style={{ justifyContent: "center" }}>
                      <button className="btn-icone"><SquarePen size={18} color="#1e293b" /></button>
                      <button className="btn-icone btn-suppr"><Trash2 size={18} /></button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4" style={{ textAlign: "center", padding: "30px", color: "#94a3b8" }}>
                  {chargement_initial ? "Chargement..." : "Ce stock est vide."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* BOUTONS ACTIONS STOCKS */}
      <div style={{ marginTop: "20px", display: "flex", gap: "10px", flexWrap: "wrap" }}>
        <button className="bouton-action btn-ajout-user" onClick={() => set_affichage_barre(true)}>
          <PlusCircle size={18} /> Ajouter un stock
        </button>

        {id_stock && (
          <>
            <button className="bouton-action" onClick={preparer_vidage} style={{ backgroundColor: "#f59e0b" }}>
              <Eraser size={18} /> Vider {nom_stock_actuel}
            </button>
            <button className="bouton-action" onClick={preparer_suppression} style={{ backgroundColor: "#ef4444" }}>
              <Trash2 size={18} /> Supprimer {nom_stock_actuel}
            </button>
          </>
        )}
      </div>

      {/* BOUTON RECETTES */}
      <div style={{ marginTop: "15px" }}>
        <button 
          className="bouton-action btn-ingredient-style"
          onClick={() => set_chercher_recette(true)}
          style={{ width: "100%", justifyContent: "center" }}
        >
          <Search size={18} /> Trouver des recettes
        </button>
      </div>

      <button className="bouton-retour-gestion" onClick={on_logout}>
        <LogOut size={18} /> Déconnexion
      </button>

      {/* COMPOSANT DE CONFIRMATION UNIQUE */}
      <Confirmation
        ouvert={etat_confirmation.ouvert}
        on_annuler={fermer_confirmation}
        on_confirmer={confirmer_action}
        titre={etat_confirmation.action === "vider" ? "Vider l'inventaire" : "Supprimer l'inventaire"}
        message={`Vous êtes sur le point de ${etat_confirmation.action} "${etat_confirmation.nom_cible}". Voulez-vous confirmer ?`}
        texte_confirmer={etat_confirmation.action === "vider" ? `Vider ${etat_confirmation.nom_cible}` : `Supprimer ${etat_confirmation.nom_cible}`}
        couleur_bouton="rouge"
      />
    </div>
  );
};

export default Stock;
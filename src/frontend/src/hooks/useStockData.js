import { useState, useEffect } from "react";
import {
  getAllIngredients,
  getStockDetails,
  getAllStocks,
} from "../api/stockApi";

export function useStockData(user, unitLabels) {
  const [items, setItems] = useState({});
  const [catalogue, setCatalogue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        // On récupère catalogue et IDs de stocks en parallèle
        const [dataIngr, stockIds] = await Promise.all([
          getAllIngredients(),
          getAllStocks(),
        ]);
        setCatalogue(dataIngr);

        const profile = user?.user || user;
        const targetStockId =
          stockIds && stockIds.length > 0 ? stockIds[0] : profile.id_stock;

        if (targetStockId) {
          const dataStock = await getStockDetails(targetStockId);
          // On transforme la liste plate en dictionnaire par ID d'ingrédient
          const mapped = {};
          if (Array.isArray(dataStock)) {
            dataStock.forEach((lot) => {
              const ingId = String(lot.ingredient_id);
              if (!mapped[ingId]) mapped[ingId] = [];
              mapped[ingId].push({
                ...lot,
                expiry_date: lot.expiration_date, // Correction du mapping
              });
            });
          }
          setItems(mapped);
        }
      } catch (err) {
        setError(err.message || "Erreur de chargement");
      } finally {
        setLoading(false);
      }
    };

    if (user) loadData();
  }, [user]);

  // --- CONSTRUCTION DU TABLEAU FORMATÉ ---
  const formattedStock = [];
  Object.entries(items).forEach(([ingId, lots]) => {
    // On transforme l'identifiant du stock en nombre avant la comparaison
    const idNumerique = Number(ingId);

    // 2. Recherche dans le catalogue (on définit 'i' à l'intérieur du find)
    const info = catalogue.find(
      (itemDansCatalogue) =>
        Number(itemDansCatalogue.ingredient_id) === idNumerique,
    );

    lots.forEach((lot, index) => {
      formattedStock.push({
        id: lot.stock_item_id || `${ingId}-${index}`,
        nom: info ? info.name : lot.name || `Ingrédient ${ingId}`,
        qte: `${lot.quantity} ${unitLabels[info?.unit] || info?.unit || ""}`,
        expiration: lot.expiry_date || "Non renseignée",
      });
    });
  });

  return { formattedStock, catalogue, loading, error, setItems, setCatalogue };
}

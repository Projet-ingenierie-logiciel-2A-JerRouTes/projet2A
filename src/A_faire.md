# Structure

## Pb structure objet API / business_objects pour utilisateur

**harmoniser la liaison stock / user**

Dans API : liste id_stock
Dans backend : id_stock

# Frontend

## Pb de connexion

connection que avec admin même si login et user différent

## Mise en place effectif de la déconnection

Lie l'action du bouton à la déconnection

## Associer bouton modification dans tableau

Dans chaque tableau associer l'action a effectuer (modifier supprimer)

Utilisation Hook ?

Dans stock.jsx; GestionIngredients; GestionUtilisateurs

## Associer ajouter ligne dans un tableau

Affecter l'action nécessaire

Dans stock.jsx; GestionIngredients; GestionUtilisateurs

## Dans stock.jsx

Gérer les cas :

- liste stocks vide (pas de stock enregistrer)
- liste item_stock vide (pas d'item dans le stock)

# Ajouter fonctionnalités

## Endpoont GET stock/{id_stock} / get_stock_info

Implémenter pour BDD

## Endpoont GET stock/user/{id_user} / get_user_stock_ids

Implémenter pour BDD

______________________________________________________________________

# Fonctionnalités

- Ajouter ingredient -> coté frontend utiliser AddIngredientForm_amodif
- Gérer recherche de recette
- Afficher recette

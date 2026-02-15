## API

### User Story : GET stock/{id_stock} src/backend/api/routers/stocks :: get_stock_info

- **Tâche** : Implémenter l'endpoint pour la partie BDD.
- **Critères d'acceptation** :
  - L'appel à l'endpoint avec un id_stock valide doit retourner un code 200 OK et les détails complets du stock (nom, inventaire, date de création).
  - L'implémentation doit utiliser la fonction get_stock_info définie dans src/backend/api/routers/stocks.
  - Si l'identifiant n'existe pas en base de données, l'API doit retourner une erreur 404 Not Found.

______________________________________________________________________

### User Story : GET stock/user/{id_user} src/backend/api/routers/stocks :: get_user_stock_ids

- **Tâche** : Implémenter l'endpoint pour la partie BDD.
- **Critères d'acceptation** :
  - L'appel doit retourner la liste exhaustive des id_stock associés à l'utilisateur spécifié.
  - La fonction get_user_stock_ids doit être utilisée pour effectuer la requête en base de données.
  - Si l'utilisateur n'a aucun stock, l'API doit renvoyer une liste vide [] avec un code 200 OK.

______________________________________________________________________

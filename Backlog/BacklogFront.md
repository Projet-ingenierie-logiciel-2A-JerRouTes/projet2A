## Frontend

### User Story : Action déconnection

- **Tâche** : Lier l'action du bouton à la fin de session.
- **Critères d'acceptation** :
  - Lors du clic sur le bouton "Déconnexion", le token d'authentification ou les données de session doivent être supprimés du stockage local (localStorage/sessionStorage).
  - L'utilisateur doit voir un message type "au revoir name" et les 4 boutons de l'acceuil

______________________________________________________________________

### User Story : Actions rapides - Suppresion

- **Tâche** : Associer les actions "Supprimer"
- **Critères d'acceptation** :
  - Lors du clic sur "Supprimer", une boîte de dialogue de confirmation doit apparaître avant l'appel à l'API.
  - La ligne correspondante disparait de l'affichage

______________________________________________________________________

### User Story : Actions rapides - Modification

- **Tâche** : Associer les actions "Modifier"
- **Critères d'acceptation** :
  - Les différents champs de la ligne deviennent accessibles (texte, menu déroulant, calendrier, etc)
  - Si au moins une modification apparation d'un bouton validation
  - La ligne correspondante se modifie

______________________________________________________________________

### User Story : Action ajouter ingrédient - pour user

- **Tâche** :
- **Critères d'acceptation** :
  - Apparition d'une nouvelle fenetre pour ajouter ingrédient avec formulaire :
    - Ligne 1 : Choix du stock -> menu deroulant
    - Ligne 2 : Choix du nom de l'ingredient (auto-implémentation si possible)
    - Ligne 3 : Choix de la quantité (texte saisi) + choix unité (menu déroulant - fixé si auto-implémentation)
    - Ligne 4 : Choix date d'expiration (calendrier)
  - Apparition d'un bouton "valider"
  - Si "valider" retour au tableau des ingrédients et apparition de la nouvelle ligne

______________________________________________________________________

### User Story : Action ajouter ingrédient - pour admin

- **Tâche** :
- **Critères d'acceptation** :
  - Apparition d'une nouvelle fenetre pour ajouter ingrédient avec formulaire :
    - Ligne 1 : Choix du nom de l'ingredient (Si nom déjà présent impossible de valider)
    - Ligne 2 : Choix choix unité (menu déroulant)
  - Apparition d'un bouton "valider"
  - Si "valider" retour au tableau des ingrédients et apparition de la nouvelle ligne

______________________________________________________________________

<span style="color:red">A faire quand probème de connexion réglé</span>

- **User Story** : En tant qu'utilisateur, je veux une interface claire, même lorsque mes stocks sont vides.
- **Tâche** : Gérer les cas "liste stocks vide" et "liste item\_\_stock vide" dans stock.jsx.
- **Critère d acceptation** :
  - Étant donné un utilisateur n'ayant aucun stock enregistré, quand il accède à stock.jsx, alors un message "Aucun stock enregistré" doit s'afficher à la place d'un tableau vide.
  - Le bouton "Ajouter un stock" doit rester visible et fonctionnel, même si la liste est vide.

______________________________________________________________________

[⬅ Retour au README](../../README.md)

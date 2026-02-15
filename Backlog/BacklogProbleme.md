## Problème à régler

- **User Story** : En tant qu'utilisateur, je veux me connecter avec mes propres identifiants pour ne plus être systématiquement identifié comme admin.
- **Tâche** : Corriger le bug de redirection forcée vers le profil administrateur.
- **Fonctionnement actuel** :
  - *swagger* en mode démo : conection user1 OK -> récupérationnliste_id_stock OK
  - *react* en mode démo : connection user1 affiche ok mais renvoie stock de admin
- **Critère d acceptation** :
  - Étant donné un utilisateur avec les identifiants user_test / password123, quand il se connecte, alors il doit être redirigé vers son propre tableau de bord et non celui de l'admin.
  - Le nom de l'utilisateur affiché dans le header doit correspondre au compte connecté.

______________________________________________________________________

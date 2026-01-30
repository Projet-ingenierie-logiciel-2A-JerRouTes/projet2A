# Réunion 1 - Vendredi 30 janvier

______________________________________________________________________

## Ordre du jour

- Validation/modification base de données
- Validation/modification objet métier
- Méthodes de recherche -> service
- Methode pour score pour recette
- Dispatch de taches

______________________________________________________________________

## Base de données

- Ajout table substitute
- Mise en accord des noms

## Objets métier

Mise au point des modifs à faire sur les objets métiers

## Services

### ingredient

méthodes :

- ajouter ingredient total pour admin (pour user si création recette avec vérification admin)

### recipe

methodes :

- créer
- modifier
- supprimer
- dupliquer
- changer_statut

### find_recipe à coder

cf fichier find_recipe.py

### stock

méthodes :

- créer_stock
- modifier_stock
- supprimer_stock
- ajouter_stock_item
- modifier_stock_item
- supprimer_stock_item
- afficher_stock

### Utilisateur

methodes :

- creer_utilisateur
- supprimer_utilisateur
- modifier_nom
- modifier_username
- modifier_mdp

## Notion de score

????

## Dispatch

- Maxime : recherche fonctionnement API
- Khalid : création BDD avec fichier init
- Christelle : modifier classe objets-metier + creation service

______________________________________________________________________

## 📅 Prochain point

📍 **6/02 matin**

[⬅ Retour au README](../../README.md)

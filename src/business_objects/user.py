from abc import ABC, abstractmethod


class User(ABC):
    """
    Classe abstraite représentant un utilisateur.
    """

    def __init__(self, pseudo: str, password: str, id_stock: int | None = None):
        self.pseudo = pseudo
        self.password = password
        self.id_stock = id_stock

    @abstractmethod
    def display_role(self) -> str:
        """
        Méthode abstraite pour afficher le rôle de l'utilisateur.
        """
        pass

    def change_password(self, old_password: str, new_password: str):
        """
        Modifier son propre mot de passe après vérification de l'ancien.
        """
        if self.password != old_password:
            print(
                "Mot de passe actuel incorrect. Impossible de changer le mot de passe."
            )
            return False
        self.password = new_password
        print(f"Mot de passe de {self.pseudo} modifié avec succès.")
        return True


class GenericUser(User):
    """
    Classe représentant un utilisateur générique.
    Peut gérer d'autres utilisateurs (créer/supprimer).
    """

    # Liste globale des utilisateurs créés
    users: list["GenericUser"] = []

    def display_role(self) -> str:
        return "Generic User"

    # -----------------------------
    # Méthodes de gestion d'utilisateurs
    # -----------------------------
    @classmethod
    def create_user(cls, pseudo: str, password: str) -> "GenericUser":
        user = GenericUser(pseudo, password)
        cls.users.append(user)
        print(f"Utilisateur {pseudo} créé.")
        return user

    @classmethod
    def delete_user(cls, user: "GenericUser"):
        if user in cls.users:
            cls.users.remove(user)
            print(f"Utilisateur {user.pseudo} supprimé.")
        else:
            print(f"Utilisateur {user.pseudo} non trouvé.")


class Admin(User):
    """
    Classe représentant un administrateur.
    """

    def display_role(self) -> str:
        return "Admin"

    def change_admin_password(self, new_password: str):
        self.password = new_password
        print(f"Mot de passe admin {self.pseudo} modifié.")


class Vide(User):
    pass

from abc import ABC, abstractmethod


class User(ABC):
    """Classe abstraite représentant un utilisateur."""

    def __init__(
        self, id_user: int, pseudo: str, password: str, id_stock: int | None = None
    ):
        if not pseudo or len(pseudo) < 3:
            raise ValueError("Le pseudo doit contenir au moins 3 caractères.")

        self._id_user = id_user
        self.pseudo = pseudo
        self._password = password
        self.id_stock = id_stock

    @property
    def id_user(self) -> int:
        return self._id_user

    def check_password(self, password_to_test: str) -> bool:
        """Vérifie le mot de passe sans l'exposer."""
        return self._password == password_to_test

    def change_password(self, old_password: str, new_password: str) -> bool:
        """Modifier son propre mot de passe après vérification de l'ancien."""
        if not self.check_password(old_password):
            print(
                "Mot de passe actuel incorrect. Impossible de changer le mot de passe."
            )
            return False

        if len(new_password) < 4:
            print("Échec : le nouveau mot de passe est trop court.")
            return False

        self._password = new_password
        print(f"Mot de passe de {self.pseudo} modifié avec succès.")
        return True

    def __str__(self) -> str:
        return f"[{self.display_role()}] {self.pseudo} (ID: {self._id_user})"

    def __repr__(self) -> str:
        """Représentation technique pour les listes et le débug."""
        return f"{self.__class__.__name__}(id={self._id_user}, pseudo='{self.pseudo}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return self._id_user == other._id_user

    @abstractmethod
    def display_role(self) -> str:
        pass


class GenericUser(User):
    """Utilisateur standard pouvant gérer la liste des utilisateurs."""

    users: list["User"] = []

    def display_role(self) -> str:
        return "Utilisateur Générique"

    @classmethod
    def create_user(
        cls, id_user: int, pseudo: str, password: str, id_stock: int | None = None
    ) -> "GenericUser":
        user = cls(id_user, pseudo, password, id_stock)
        cls.users.append(user)
        print(f"Utilisateur {pseudo} créé.")
        return user

    @classmethod
    def delete_user(cls, user: "User"):
        if user in cls.users:
            cls.users.remove(user)
            print(f"Utilisateur {user.pseudo} supprimé.")
        else:
            print(f"Utilisateur {user.pseudo} non trouvé.")


class Admin(User):
    """Administrateur avec gestion de mot de passe spécifique."""

    def display_role(self) -> str:
        return "Administrateur"

    @property
    def password(self):
        return "********"

    @password.setter
    def password(self, value):
        self._password = value

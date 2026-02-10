from abc import ABC, abstractmethod


class User(ABC):
    """
    Classe abstraite représentant un utilisateur.
    """

    def __init__(
        self,
        id_user: int,
        pseudo: str,
        password: str,
        email: str | None = None,
        status: str = "user",
        id_stock: int | None = None,
    ):
        """
        Initialise un utilisateur avec validation du pseudo.

        Args:
            id_user (int): Identifiant unique de l'utilisateur.
            pseudo (str): Pseudonyme de l'utilisateur (au moins 3 caractères).
            password (str): Mot de passe (ou hash selon ton design).
            email (str | None, optional): Email de l'utilisateur. Défaut: None.
            status (str, optional): Statut/role (ex: "user", "admin"). Défaut: "user".
            id_stock (int | None, optional): Identifiant du stock associé. Défaut: None.

        Raises:
            ValueError: Si le pseudo est vide ou contient moins de 3 caractères.
        """
        if not pseudo or len(pseudo) < 3:
            raise ValueError("Le pseudo doit contenir au moins 3 caractères.")

        self._id_user = id_user
        self.pseudo = pseudo
        self._password = password

        # Champs utiles côté API
        self.email = email
        self.status = status

        self.id_stock = id_stock

    # -------------------------
    # Champs historiques
    # -------------------------
    @property
    def id_user(self) -> int:
        """Retourne l'identifiant de l'utilisateur."""
        return self._id_user

    # -------------------------
    # Aliases attendus par l'API
    # -------------------------
    @property
    def user_id(self) -> int:
        """Alias pour compatibilité API."""
        return self._id_user

    @property
    def username(self) -> str:
        """Alias pour compatibilité API."""
        return self.pseudo

    # Si la DAO/DB utilise password_hash, ça évite des AttributeError
    @property
    def password_hash(self) -> str:
        """Alias (si le projet manipule un hash en DB)."""
        return self._password

    def check_password(self, password_to_test: str) -> bool:
        """
        Vérifie le mot de passe sans l'exposer.
        """
        return self._password == password_to_test

    def change_password(self, old_password: str, new_password: str) -> bool:
        """
        Modifie le mot de passe après vérification de l'ancien.
        """
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
        """Retourne une représentation lisible de l'utilisateur."""
        return f"[{self.display_role()}] {self.pseudo} (ID: {self._id_user})"

    def __repr__(self) -> str:
        """Retourne une représentation technique pour le débogage."""
        return f"{self.__class__.__name__}(id={self._id_user}, pseudo='{self.pseudo}')"

    def __eq__(self, other) -> bool:
        """Compare deux utilisateurs par leur identifiant."""
        if not isinstance(other, User):
            return False
        return self._id_user == other._id_user

    @abstractmethod
    def display_role(self) -> str:
        """Retourne le rôle de l'utilisateur."""
        pass


class GenericUser(User):
    """
    Utilisateur standard pouvant gérer la liste des utilisateurs.
    """

    users: list["User"] = []

    def __init__(
        self,
        id_user: int,
        pseudo: str,
        password: str,
        email: str | None = None,
        status: str = "user",
        id_stock: int | None = None,
    ):
        super().__init__(
            id_user, pseudo, password, email=email, status=status, id_stock=id_stock
        )

    def display_role(self) -> str:
        """Retourne le rôle de l'utilisateur générique."""
        return "Utilisateur Générique"

    @classmethod
    def create_user(
        cls,
        id_user: int,
        pseudo: str,
        password: str,
        email: str | None = None,
        status: str = "user",
        id_stock: int | None = None,
    ) -> "GenericUser":
        """
        Crée et enregistre un nouvel utilisateur générique.
        """
        user = cls(
            id_user, pseudo, password, email=email, status=status, id_stock=id_stock
        )
        cls.users.append(user)
        print(f"Utilisateur {pseudo} créé.")
        return user

    @classmethod
    def delete_user(cls, user: "User"):
        """Supprime un utilisateur de la liste des utilisateurs."""
        if user in cls.users:
            cls.users.remove(user)
            print(f"Utilisateur {user.pseudo} supprimé.")
        else:
            print(f"Utilisateur {user.pseudo} non trouvé.")


class Admin(User):
    """
    Administrateur avec gestion de mot de passe spécifique.
    """

    def __init__(
        self,
        id_user: int,
        pseudo: str,
        password: str,
        email: str | None = None,
        status: str = "admin",
        id_stock: int | None = None,
    ):
        super().__init__(
            id_user, pseudo, password, email=email, status=status, id_stock=id_stock
        )

    def display_role(self) -> str:
        """Retourne le rôle administrateur."""
        return "Administrateur"

    @property
    def password(self):
        """Retourne une valeur masquée du mot de passe."""
        return "********"

    @password.setter
    def password(self, value):
        """Modifie directement le mot de passe."""
        self._password = value

class BaseAppError(Exception):
    """Base pour toutes les exceptions de l'application."""

    pass


# --- Exceptions Token
class InvalidRefreshTokenError(BaseAppError):
    """
    Levée quand le refresh token est expiré, révoqué ou formaté de manière incorrecte.
    """

    pass


# --- Exceptions Utilisateur ---
class UserNotFoundError(BaseAppError):
    """Levée quand l'utilisateur n'existe pas dans la base."""

    pass


class UserAlreadyExistsError(BaseAppError):
    """Levée lors de l'inscription si le pseudo est pris."""

    pass


class UserEmailAlreadyExistsError(BaseAppError):
    """Levée lors de l'inscription si l'email est pris."""

    pass


# --- Exceptions Authentification ---
class InvalidPasswordError(BaseAppError):
    """Levée quand le mot de passe est incorrect."""

    pass

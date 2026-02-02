# Retirer étapes
# Modifier is_status en print_status
# Ajouter afficher_recette, __str__, changer_statut


class Recipe:
    """
    Represents a cooking recipe.

    This class models the core business logic of a recipe, independently
    of any database or persistence layer. It stores structural data
    (status, preparation time, portions) as well as relationships
    to ingredients, steps, tags, and translations.

    A Recipe:
    - is created by a single user
    - can have multiple ingredients with quantities
    - can be described in multiple languages
    - can be scaled to a different number of portions
    """

    def __init__(
        self,
        recipe_id: int,
        creator_id: int,
        status: str,
        prep_time: int,
        portions: int,
    ):
        """
        Initializes a Recipe instance.

        :param recipe_id: Unique identifier of the recipe
        :param creator_id: Identifier of the user who created the recipe
        :param status: Current status of the recipe
                       (e.g. 'draft', 'public', 'private', 'archived')
        :param prep_time: Preparation time in minutes
        :param portions: Number of portions the recipe is designed for
        """

        # --- Core attributes ---
        self.recipe_id = recipe_id
        self.creator_id = creator_id
        self.status = status
        self.prep_time = prep_time
        self.portions = portions

        # --- Relationships ---
        # List of tuples (ingredient_id, quantity)
        self.ingredients = []

        # List of associated tag identifiers
        self.tags = []

        # List of steps as tuples (step_order, description)
        self.steps = []

        # Dictionary of translations indexed by language code
        # Example:
        # {
        #   "en": {"name": "Pancakes", "description": "Easy recipe"},
        #   "fr": {"name": "Crêpes", "description": "Recette simple"}
        # }
        self.translations = {}

    def add_ingredient(self, ingredient_id: int, quantity: float):
        """
        Adds an ingredient to the recipe.

        :param ingredient_id: Identifier of the ingredient
        :param quantity: Quantity required for the current number of portions
        """

        self.ingredients.append((ingredient_id, quantity))

    def add_step(self, step_order: int, description: str):
        """
        Adds a preparation step to the recipe.

        Steps are automatically kept ordered according to step_order.

        :param step_order: Order number of the step (starting at 1)
        :param description: Textual description of the step
        """

        self.steps.append((step_order, description))
        # Ensure steps remain ordered
        self.steps.sort(key=lambda x: x[0])

    def add_translation(self, language_code: str, name: str, description: str):
        """
        Adds or updates a translation for the recipe.

        :param language_code: ISO language code (e.g. 'en', 'fr')
        :param name: Localized name of the recipe
        :param description: Localized description of the recipe
        """

        self.translations[language_code] = {"name": name, "description": description}

    def is_public(self) -> bool:
        """
        Checks whether the recipe is publicly visible.

        :return: True if the recipe status is 'public', False otherwise
        """

        return self.status == "public"

    def scale_portions(self, new_portions: int):
        """
        Scales ingredient quantities to match a new number of portions.

        Quantities are multiplied by the ratio:
            new_portions / current_portions

        :param new_portions: Desired number of portions
        """

        factor = new_portions / self.portions

        # Update quantities proportionally
        self.ingredients = [
            (ingredient_id, quantity * factor)
            for ingredient_id, quantity in self.ingredients
        ]

        self.portions = new_portions

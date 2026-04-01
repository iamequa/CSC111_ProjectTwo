"""CSC111 Project 2: The Ultimate Recipe Index - Vertex

===============================

This Python module contains code representing all vertices within the recipe index graph and
tree.
"""

from __future__ import annotations


class Vertex:
    """
    Represents a vertex for a recipe graph, which at the most basic level contains just a name.

    Representation Invariants:
        - every ID of a vertex is UNIQUE and is not the ID of any other vertex
    """
    # Private Instance Attributes:
    #   - _name: the name of this vertex.

    _name: str

    def __init__(self, name: str) -> None:
        self._name = name

    def get_name(self) -> str:
        """Return the name of this vertex"""
        return self._name


class Recipe(Vertex):
    """
    Represents a recipe vertex in a recipe graph.

    Representation Invariants:
        - self not in self._paired_recipes[category] for category in self._paired_recipes
        - self in category.get_recipes() for category in self._categories
        - self in ingredient.get_recipes() for ingredient in self._ingredients
        - self in name_token.get_recipes() for name_token in self._name_tokens
    """
    # Private Instance Attributes:
    #   - _uid: the unique ID of this recipe
    #   - _steps: the steps needed to prepare this recipe
    #   - _categories: the categories which this recipe is a part of
    #   - _ingredients: the ingredients contained within this recipe
    #   - _name_tokens: any additional information about the recipe
    #   - _paired_recipes: a mapping of categories and recipes which satisfy those categories

    _uid: int
    _steps: str
    _categories: set[Category]
    _ingredients: set[Ingredient]
    _name_tokens: set[NameToken]
    _paired_recipes: dict[Category, set[Recipe]]

    def __init__(self, name: str, uid: int, steps: str) -> None:
        super().__init__(name)
        self._uid = uid
        self._steps = steps
        self._categories, self._ingredients, self._name_tokens, self._paired_recipes = set(), set(), set(), {}

    # NOTE: For every getter, do NOT use it in a manner such recipe.get_categories.add(category),
    # use recipe.add_category(category)
    def get_id(self) -> int:
        """Returns the ID of this recipe"""
        return self._uid

    def get_categories(self) -> set[Category]:
        """Returns the categories this recipe is a part of"""
        return self._categories

    def get_ingredients(self) -> set[Ingredient]:
        """Returns the ingredients contained within this recipe"""
        return self._ingredients

    def get_name_tokens(self) -> set[NameToken]:
        """Returns additional information about this recipe"""
        return self._name_tokens

    def get_steps(self) -> str:
        """Return the steps needed to make this recipe"""
        return self._steps

    def get_paired_recipes(self) -> dict[Category, set[Recipe]]:
        """Returns all the paired recipes and replacements for this recipe"""
        return self._paired_recipes

    def add_category(self, category: Category) -> None:
        """
        Adds the category if the category is not already added and updates the category to reflect this, does
        nothing if the category is already in this recipe's categories
        """
        self._categories.add(category)
        category.add_recipe(self)

    def add_ingredient(self, ingredient: Ingredient) -> None:
        """
        Adds the ingredient if the ingredient is not already added and updates the ingredient to reflect this, does
        nothing if the ingredient is already in this recipe's ingredients
        """
        self._ingredients.add(ingredient)
        ingredient.add_recipe(self)

    def add_name_token(self, name_token: NameToken) -> None:
        """
        Adds the name token if the name token is not already added and updates the name token to reflect this, does
        nothing if the name token is already in this recipe's name tokens
        """
        self._name_tokens.add(name_token)
        name_token.add_recipe(self)

    def add_paired_recipe(self, category: Category, recipe: Recipe) -> None:
        """
        Adds the replacement recipe for the given category to the paired recipes dictionary
        If the category is not already inside the dictionary, add it

        Preconditions:
            - recipe is not self
        """
        if category not in self._paired_recipes:
            self._paired_recipes[category] = set()
        self._paired_recipes[category].add(recipe)


class Attribute(Vertex):
    """
    Represents a non-recipe vertex within a recipe graph.
    """
    # Private Instance Attributes:
    #   - _recipes: all the recipes associated with this attribute
    _recipes: set[Recipe]

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._recipes = set()

    def __contains__(self, recipe: Recipe) -> bool:
        return recipe in self._recipes

    def __len__(self) -> int:
        return len(self._recipes)

    def get_recipes(self) -> set[Recipe]:
        """Get all the recipes connected to this attribute"""
        return self._recipes

    # NOTE: Do NOT call this method directly outside of this file, creation of the graph will handle the
    # bidirectional design through the Recipe class
    def add_recipe(self, recipe: Recipe) -> None:
        """Adds the recipe to the current recipes, does nothing if the recipe is already in"""
        self._recipes.add(recipe)


class Category(Attribute):
    """A category vertex, same as attribute but made for design purposes"""


class Ingredient(Attribute):
    """An ingredient vertex, same as attribute but made for design purposes"""


class NameToken(Attribute):
    """A name token vertex, same as attribute but made for design purposes"""

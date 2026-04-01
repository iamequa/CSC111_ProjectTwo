"""CSC111 Project 2: The Ultimate Recipe Index - Recipe Tree

===============================

This Python module contains code for a recipe tree data structure in our recipe index application.
"""

from __future__ import annotations
from Data import vertex

# Constants for the current filters, check below for more information
NAME_TOKENS = "name_tokens"
CATEGORIES = "categories"
INGREDIENTS = "ingredients"


class RecipeTree:
    """
    A tree data structure which represents recipes by how they can be classified in terms of categories, ingredients,
    and any words in their name. This is how the hierarchy looks:

    Depth Zero - Every recipe in the dataset, no filters
    Depth One - Recipes get filtered by the name_tokens in their name, meaning at this level,
    if we have a "yogurt" name token, that node in the second layer will contain a mapping
    to ONLY recipes whose names contain "yogurt"
    Depth Two - Recipes get filtered by the categories they fall within
    Depth Three - Recipes get filtered by the ingredients they contain

    No filters -> Filtered by name_tokens -> Filtered by categories -> Filtered by ingredients

    How this works in practice is that if someone wants to find a dairy-free yogurt recipe with almonds,
    the tree first recognizes the user is looking for "yogurt" (a name token) and filters down to only
    recipes whose names contain that word. Then, it recognizes that it must be "dairy free" and filters
    down even further by category. Finally, it recognizes the user wants "almonds" and filters down by
    ingredients. At that point, you have a mapping of every recipe which satisfies the given requirements.

    Instance Attributes:
        - recipes: a mapping of every recipe UID to the recipe object it represents
        - filters: a mapping of the string name of every filter which is of the self.current_filter to the RecipeTree
        corresponding to that filtration
        - current_filter: a string representing what kind of filter occurs in self.filters, None if at a leaf

    Representation Invariants:
        - self.current_filter is None or self.current_filter in {NAME_TOKENS, CATEGORIES, INGREDIENTS}
    """

    recipes: dict[int, vertex.Recipe]
    filters: dict[str, RecipeTree]
    current_filter: str | None

    def __init__(self, current_filter: str | None) -> None:
        self.recipes = {}
        self.filters = {}
        self.current_filter = current_filter

    def add_vertex(self, recipe: vertex.Recipe) -> None:
        """
        Adds the vertex to the following recipe tree if it is not already in by first
        adding the vertex to the current layer, then adding it to the next layer depending
        on the condition of the current filter.
        """

        # Handle the case when the recipe is already in the tree
        if recipe.get_id() in self.recipes:
            return

        # Add the recipe to the tree
        self.recipes[recipe.get_id()] = recipe

        # If no more filtration can occur, return (this is the base case)
        if self.current_filter is None:
            return

        # Add the recipe according to the current filter, and move on to the next filter
        if self.current_filter == NAME_TOKENS:
            self._add_to_children(recipe.get_name_tokens(), CATEGORIES, recipe)

        elif self.current_filter == CATEGORIES:
            self._add_to_children(recipe.get_categories(), INGREDIENTS, recipe)

        elif self.current_filter == INGREDIENTS:
            self._add_to_children(recipe.get_ingredients(), None, recipe)

    def _add_to_children(self, items: set[vertex.Attribute], next_filter: str | None, recipe: vertex.Recipe) -> None:
        """Takes the recipe and recursively fully adds the recipe to every filter it is in"""
        for item in items:
            name = item.get_name()
            # If the filter is already found in filters, meaning other recipes have been filtered in the same way,
            # otherwise, create the filter, then recursively add the vertex
            if name not in self.filters:
                self.filters[name] = RecipeTree(next_filter)
            self.filters[name].add_vertex(recipe)

    def search_by_name(self, name: str | None = None) -> list[vertex.Recipe]:
        """
        Return a list of recipes whose names partially match the given query.

        The search is case-insensitive and supports partial matching:
        - The input string is split into tokens
        - Each token is matched against name_tokens in the tree using prefix matching
        - Only recipes that match ALL tokens are returned
        """
        if not name:
            return []

        cleaned_name = name.lower().strip()
        # Split the recipe name into all of its words
        name_tokens = cleaned_name.split()
        token_recipe_sets = []
        # For every word (or partial word, such as "car" instead of "carrot"), find all recipes
        # which contain a bit of that word in their name
        for word in name_tokens:
            matched_recipes = set()
            for candidate in self.filters:
                # If the current name_token in the filters starts with the word or partial word
                # we are looking for, add all the recipes with that name_token to the current set of recipes
                if candidate.startswith(word):
                    matched_recipes.update(self.filters[candidate].recipes.values())
            # Once we have gone through every possible candidate for the current word that the user inputted, we
            # return all the recipes which contain in them that word/partial word
            token_recipe_sets.append(matched_recipes)

        # If no recipes are found that contain ANY of the words the user inputted, we have found no recipes
        if not token_recipe_sets:
            return []
        # Get all the recipes which contain a bit of EVERY WORD in the name the user inputted. For example,
        # "chick car" could refer to "chicken carrot" or "chickpea caramel", and the program will return both
        # as they both contain a word which begins with "chick" and a word that begins with "car"
        result = set.intersection(*token_recipe_sets)
        return list(result)

    def search_by_filters(self, ingredients: list[str], categories: list[str], name: str | None = None
                          ) -> list[vertex.Recipe]:
        """
           Return a list of recipes that match the given ingredient, category, and optional name filters.

           The filtering process works as follows:
           - If a name is provided, first narrow down candidates using search_by_name
           - Otherwise, consider all recipes in the current tree
           - Then filter recipes such that:
               * All specified ingredients are present in the recipe
               * All specified categories are present in the recipe

           Parameters:
               - ingredients: a list of ingredient names that must be included
               - categories: a list of category names that must be included
               - name: an optional name query for partial matching

           Returns:
               - a list of Recipe objects satisfying all given filters
           """
        ingredients_set = set(ingredients)
        categories_set = set(categories)

        # If the user did not input a name, then the candidates are every single recipe
        # Otherwise, the candidates are every single recipe which is similar enough to name (check function
        # search_by_name for more details)
        if name is None:
            candidates = list(self.recipes.values())
        else:
            candidates = self.search_by_name(name)

        results = []
        for recipe in candidates:
            # Go through every possible candidate for the search, and if the ingredients and categories
            # inputted by the user match the recipes ingredients and categories, we add it to the search results
            ingredient_names = {ingredient.get_name() for ingredient in recipe.get_ingredients()}
            category_names = {category.get_name() for category in recipe.get_categories()}
            if ingredients_set.issubset(ingredient_names) and categories_set.issubset(category_names):
                results.append(recipe)

        return results

"""CSC111 Project 2: The Ultimate Recipe Index - Recipe Graph

===============================

This Python module contains code for a recipe graph data structure in our recipe index application.
"""

from __future__ import annotations
import Data.vertex as v

# Tuples are created later which contain in index 0 a similarity score between a recipe and a replacement
SIMILARITY_SCORE_INDEX = 0

# We weight similarity based off of ingredients and categories differently, with categories weighted more heavily
INGREDIENT_SIMILARITY_WEIGHT = 2
CATEGORY_SIMILARITY_WEIGHT = 3

# MAXIMUM NUMBER OF RECIPE RECOMMENDATIONS ALLOWED TO BE RETURNED
MAX_RECIPES = 50


class RecipeGraph:
    """
    A recipe graph which is meant to connect recipes in terms of categories and ingredients they
    are similar in. The way the structure works is very simple:

    Every recipe vertex is connected to its ingredients and categories, and the ingredients and categories are
    connected to all the recipes they are a part of. This makes comparing recipes very simple, as a similarity
    algorithm similar to the ones made in the previous course assignments can be used

    Instance Attributes:
        - vertices: a mapping of recipe UIDs or ingredient/category names to their respective vertices
        - recipe_name_to_id: a mapping of recipe names to their corresponding UID in the graph
    """
    vertices: dict[int | str, v.Vertex]
    recipe_name_to_id: dict[str, int]

    def __init__(self) -> None:
        self.vertices = {}
        self.recipe_name_to_id = {}

    def add_vertex(self, vertex: v.Vertex) -> None:
        """Adds the given vertex to the graph if it is not already contained."""
        # If the vertex is a recipe that is not in the graph, create a reference to it in the graph
        if isinstance(vertex, v.Recipe) and vertex.get_id() not in self.vertices:
            self.vertices[vertex.get_id()] = vertex
            self.recipe_name_to_id[vertex.get_name()] = vertex.get_id()
        # If the vertex is an ingredient or category, add the attribute to the graph
        elif isinstance(vertex, v.Attribute) and vertex.get_name() not in self.vertices:
            self.vertices[vertex.get_name()] = vertex

    def add_recipe_pair(self, base_uid: int, target_uid: int, category_uids: list[str]) -> None:
        """
        Adds the base recipe as a recipe pair for the target recipe based off the categories specified. If either
        the base or target recipe do not exist in this graph, do not add any recipe pair. If any of the categories does
        not exist in this graph, that category does not get added.
        """
        # If the recipe or its replacement do not exist within the graph, do not add anything
        if base_uid not in self.vertices or target_uid not in self.vertices:
            return
        base = self.vertices[base_uid]
        target = self.vertices[target_uid]

        # For the recipe, if the replacement category exists in the graph, add a recipe pair relationship
        for category_uid in category_uids:
            if category_uid in self.vertices:
                category = self.vertices[category_uid]
                if isinstance(category, v.Category) and isinstance(base, v.Recipe) and isinstance(target, v.Recipe):
                    target.add_paired_recipe(category, base)

    def find_recommendations(self, categories: list[str], ingredients: list[str],
                             allergies: list[str]) -> list[v.Recipe]:
        """Return a list of the top 3 recipes that best match the given user preferences.

            Uses the graph structure for efficient candidate retrieval by directly looking up
            ingredient and category vertices and collecting the recipes connected to them.
            This avoids scanning all recipes entirely.

            Matches contribute to the score as follows:
                - Each matching ingredient contributes 2 points
                - Each matching category contributes 3 points
            """

        # Clean the user input for any leading/trailing whitespaces and capitalization
        ingredients_lower = {i.lower().strip() for i in ingredients}
        categories_lower = {c.lower().strip() for c in categories}
        allergies_lower = {a.lower().strip() for a in allergies}

        # For every ingredient in the given ingredients, find the recipes which contain at least
        # ONE of the users desired ingredients. Do the same for candidates, and allergies
        ingredient_candidates = self._collect_recipes_from_vertices(ingredients_lower, v.Ingredient)
        categories_candidates = self._collect_recipes_from_vertices(categories_lower, v.Category)
        allergen_recipes = self._collect_recipes_from_vertices(allergies_lower, v.Ingredient)


        positive_candidates = ingredient_candidates | categories_candidates
        if not positive_candidates and allergies_lower:
            positive_candidates = {vertex for vertex in self.vertices.values()
                                   if isinstance(vertex, v.Recipe)}

        # Keep only recipes which have at least one ingredient or category from the user's preferences
        # which do not contain any of the user's allergies
        candidates = positive_candidates - allergen_recipes
        scores = []
        for recipe in candidates:
            # Calculate how good of a recommendation every candidate is to the desired recipe and then
            # add a tuple of the score and the recipe object to the scores list
            recommendation_score = self._recommendation_score(recipe, ingredients_lower, categories_lower)
            scores.append((recommendation_score, recipe))

        # Sort the recipes based on their scores from highest to lowest, and return up to "MAX_RECIPES" amount of
        # recipes
        scores.sort(reverse=True, key=lambda x: x[SIMILARITY_SCORE_INDEX])
        return [recommendation for _, recommendation in scores[:MAX_RECIPES]]

    def compute_alternative_recipe(self, categories: list[str], ingredients: list[str], allergies: list[str],
                                   recipe: int) -> list[v.Recipe]:
        """
        Find an alternative recipe for the recipe id given based on the categories, ingredients, and allergies the
        user has selected.
        """
        # See if the recipe has any immediate replacements based on the categories, ingredients, and allergies
        paired = self.find_paired_recipe(categories, ingredients, allergies, recipe)
        if paired:
            return paired
        # If the recipe has no immediate replacements, find the most similar recipes
        else:
            return self.find_similar_recipe(categories, ingredients, allergies, recipe)

    def find_similar_recipe(self, categories: list[str], ingredients: list[str], allergies: list[str], recipe: int
                            ) -> list[v.Recipe]:
        """
        Return recipes similar to the given recipe based on shared ingredients
        and categories, filtered to match user preferences.

        Similarity is determined by the overlap between:
            - ingredients
            - categories

        After computing similarity, only recipes that contain at least one of the
        specified ingredients or categories are returned.
        """

        base_recipe = self._get_recipe_vertex(recipe)

        # If the recipe is not in the graph, that means that there are no recipe replacements
        if not base_recipe:
            return []

        # Get all the ingredients and categories contained in the recipe
        base_ingredients = {i.get_name().lower() for i in base_recipe.get_ingredients()}
        base_categories = {c.get_name().lower() for c in base_recipe.get_categories()}

        candidate_recipes = self._get_similar_candidates(base_recipe)

        # A list of tuples, with the first index being the similarity score between the candidate and the recipe
        # and the second being the candidate recipe object
        similarities = []
        for other in candidate_recipes:
            other_ingredients = {i.get_name().lower() for i in other.get_ingredients()}
            other_categories = {c.get_name().lower() for c in other.get_categories()}

            # Compute how similar the candidate recipe is to the desired recipe
            score = self._compute_similarity_score(base_ingredients, base_categories,
                                                   other_ingredients, other_categories)

            # Add to the similarities vertex if the candidate matches the user's preferences
            if self._matches_user_preferences_sets(categories, ingredients, allergies,
                                                   other_ingredients, other_categories):
                similarities.append((score, other))

        # Sort by similarity and return all the recipes up to a certain limit, "MAX_RECIPES"
        similarities.sort(reverse=True, key=lambda x: x[SIMILARITY_SCORE_INDEX])
        return [recommendation for _, recommendation in similarities[:MAX_RECIPES]]

    def find_paired_recipe(self, categories: list[str], ingredients: list[str], allergies: list[str], recipe: int
                           ) -> list[v.Recipe]:
        """
        Return recipes that are explicitly paired with the given recipe and also match the user’s preferences.

        The method first retrieves all recipes previously linked via add_recipe_pair, then filters them to include only
        recipes that contain at least one of the specified ingredients, categories, and do not contain the specified
        allergies
        """

        if recipe not in self.vertices:
            return []

        recipe_vertex = self.vertices[recipe]

        if not isinstance(recipe_vertex, v.Recipe):
            return []

        paired_mapping = recipe_vertex.get_paired_recipes()
        paired_recipes = set()

        for recipes in paired_mapping.values():
            paired_recipes.update(recipes)

        # Filter based on user preferences
        filtered = [paired_recipe for paired_recipe in paired_recipes if isinstance(paired_recipe, v.Recipe)
                    and self._matches_user_preferences(categories, ingredients, allergies, paired_recipe)]
        return filtered

    def _matches_user_preferences(self, categories: list[str], ingredients: list[str],
                                  allergies: list[str], recipe: v.Recipe) -> bool:
        """
        Return if the given recipe matches the users preferences of categories, ingredients, and allergies.
        """
        # Get every ingredient and category within the recipe
        recipe_ingredients = {ingredient.get_name() for ingredient in recipe.get_ingredients()}
        recipe_categories = {category.get_name() for category in recipe.get_categories()}
        return self._matches_user_preferences_sets(categories, ingredients, allergies,
                                                   recipe_ingredients, recipe_categories)

    @staticmethod
    def _matches_user_preferences_sets(categories: list[str], ingredients: list[str], allergies: list[str],
                                       recipe_ingredients: set[str], recipe_categories: set[str]) -> bool:
        """
        Helper function for _matches_user_preferences, returns if the recipe is clear of the allergies the user
        has and contains the ingredients and categories the user wanted.
        """
        # If the user has allergies, make sure the recipe has none of their allergies
        if allergies and any(allergy in recipe_ingredients for allergy in allergies):
            return False
        # If the user inputted any ingredients, make sure that all the ingredients are present within the recipe
        if ingredients and not set(ingredients).issubset(recipe_ingredients):
            return False
        # If the user inputted any categories, make sure that the recipe falls under all the categories
        if categories and not set(categories).issubset(recipe_categories):
            return False
        return True

    def _get_recipe_vertex(self, recipe_id: int) -> v.Recipe | None:
        """Return the recipe vertex for recipe_id, or None if invalid."""
        # If the recipe is not in the graph, return no recipe
        if recipe_id not in self.vertices:
            return None

        # Extra check to get rid of annoying syntax complaints
        recipe = self.vertices[recipe_id]
        if not isinstance(recipe, v.Recipe):
            return None

        return recipe

    @staticmethod
    def _get_similar_candidates(base_recipe: v.Recipe) -> set[v.Recipe]:
        """Return recipes sharing at least one ingredient or category with base_recipe."""
        candidates = set()
        base_id = base_recipe.get_id()

        # Go through every ingredient in the base recipe and return all the recipes linked to that ingredient,
        # except the base recipe
        for ingredient in base_recipe.get_ingredients():
            for recipe in ingredient.get_recipes():
                if recipe.get_id() != base_id:
                    candidates.add(recipe)

        # Go through every category in the base recipe and return all the recipes linked to that category,
        # except the base recipe
        for category in base_recipe.get_categories():
            for recipe in category.get_recipes():
                if recipe.get_id() != base_id:
                    candidates.add(recipe)

        return candidates

    @staticmethod
    def _compute_similarity_score(base_ingredients: set[str], base_categories: set[str],
                                  other_ingredients: set[str], other_categories: set[str]) -> float:
        # Take the ingredients and categories contained in each recipe and join all of them together
        ingredient_union = base_ingredients | other_ingredients
        category_union = base_categories | other_categories

        # Weights the ingredient score and category score by checking how many ingredients/categories are contained
        # in both simultaneously and how many ingredients/categories are contained in both total,
        # then weights the categories more heavily than the ingredients
        ingredient_score = len(base_ingredients & other_ingredients) / max(1, len(ingredient_union))
        category_score = len(base_categories & other_categories) / max(1, len(category_union))
        # Return the weighted score
        return ingredient_score * INGREDIENT_SIMILARITY_WEIGHT + category_score * CATEGORY_SIMILARITY_WEIGHT

    def _collect_recipes_from_vertices(self, names: set[str], vertex_type: type[v.Attribute]) -> set[v.Recipe]:
        """Return all recipes connected to vertices of the given names and type."""
        recipes = set()

        # Check every vertex name in "names" and if they are an instance of the given vertex type, and if so, add
        # to the current recipes the recipes which the attribute name is linked to
        for name in names:
            vertex = self.vertices.get(name)
            if isinstance(vertex, vertex_type):
                recipes.update(vertex.get_recipes())

        return recipes

    @staticmethod
    def _recommendation_score(recipe: v.Recipe, ingredients: set[str], categories: set[str]) -> float:
        """
        Based on the recipe, return how "good" of a recommendation the recipe is based of the restrictions
        of ingredients, categories, and return a decimal value of this score. The algorithm works by seeing
        how many ingredients the recipe shares and how many categories the recipe shares with the user preferences.
        There is a slight bias towards categories, as we consider them to be more important in the algorithm
        than the ingredients.
        """
        # Get all the recipe's ingredients and categories
        recipe_ingredients = {ingredient.get_name().lower() for ingredient in recipe.get_ingredients()}
        recipe_categories = {category.get_name().lower() for category in recipe.get_categories()}

        # Check how many of the ingredients wanted are in the recipes ingredients, and weight it
        ingredient_score = len(ingredients & recipe_ingredients) * INGREDIENT_SIMILARITY_WEIGHT
        # Check how many of the categories wanted are in the recipes categories, and weight it
        category_score = len(categories & recipe_categories) * CATEGORY_SIMILARITY_WEIGHT
        return ingredient_score + category_score

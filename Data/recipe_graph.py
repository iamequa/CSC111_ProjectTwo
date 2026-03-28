"""CSC111 Project 2: The Ultimate Recipe Index - Recipe Graph

===============================

This Python module contains code for a recipe graph data structure in our recipe index application.
"""
from __future__ import annotations

import file_reader
import vertex as v

UID_INDEX = 0
NAME_INDEX = 1
STEPS_INDEX = 2
INGREDIENTS_INDEX = 3
CATEGORIES_INDEX = 4
NAME_TOKENS_INDEX = 5

BASE_INDEX = 0
TARGET_INDEX = 1
NAME_OVERLAP_INDEX = 2
NAME_SIMILARITY_INDEX = 3


def build_recipe_graph(recipes_path: str, is_recipes_csv: bool, pairs_path: str, is_pairs_csv: bool) -> RecipeGraph:
    """
    Builds a recipe graph based off a file of recipes and recipe pairs

    Preconditions:
        - recipes_path and pairs_path are valid paths to the recipes and recipe_pairs csv/parquet
    """
    recipes = file_reader.read_recipes_data(recipes_path, is_recipes_csv)
    recipe_pairs = file_reader.read_pairs_data(pairs_path, is_pairs_csv)
    graph = RecipeGraph()
    seen_vertices = {}
    for recipe in recipes:
        vertices = build_vertices(recipe, seen_vertices)
        for vertex in vertices:
            if isinstance(vertex, v.Recipe) and vertex.get_id() not in seen_vertices:
                seen_vertices[vertex.get_id()] = vertex
            elif vertex.get_name() not in seen_vertices:
                seen_vertices[vertex.get_name()] = vertex
            graph.add_vertex(vertex)

    for pair in recipe_pairs:
        graph.add_recipe_pair(pair[BASE_INDEX], pair[TARGET_INDEX], pair[CATEGORIES_INDEX])

    return graph


def build_vertices(recipe: list, seen_vertices: dict[int | str, v.Vertex]) -> list[v.Vertex]:
    """
    Builds vertices based off the given recipe, ignoring the vertices if they've already been seen

    Preconditions
        - Recipe is a valid recipe list based off the format specified in file_reader.py's read_recipes_data method
    """
    vertices = []
    recipe_vertex = v.Recipe(recipe[NAME_INDEX], recipe[UID_INDEX], recipe[STEPS_INDEX])
    vertices.append(recipe_vertex)
    for ingredient in recipe[INGREDIENTS_INDEX]:
        if ingredient not in seen_vertices:
            seen_vertices[ingredient] = v.Ingredient(ingredient)
            vertices.append(seen_vertices[ingredient])
        ingredient_vertex = seen_vertices[ingredient]
        if isinstance(ingredient_vertex, v.Ingredient):
            recipe_vertex.add_ingredient(ingredient_vertex)
    for category in recipe[CATEGORIES_INDEX]:
        if category not in seen_vertices:
            seen_vertices[category] = v.Category(category)
            vertices.append(seen_vertices[category])
        category_vertex = seen_vertices[category]
        if isinstance(category_vertex, v.Category):
            recipe_vertex.add_category(category_vertex)

    return vertices


class RecipeGraph:
    """
    A recipe graph which is meant to connect recipes in terms of categories and ingredients they
    are similar in. The way the structure works is very simple:

    Every recipe vertex is connected to its ingredients and categories, and the ingredients and categories are
    connected to all the recipes they are a part of. This makes comparing recipes very simple, as a Jaccard similarity
    algorithm is all that is needed.

    Instance Attributes:
        - vertices: a mapping of recipe UIDs or ingredient/category names to their respective vertices
    """
    vertices: dict[int | str, v.Vertex]

    def __init__(self):
        self.vertices = {}

    def add_vertex(self, vertex: v.Vertex) -> None:
        """Adds the given vertex to the graph if it is not already contained."""
        if isinstance(vertex, v.Recipe) and vertex.get_id() not in self.vertices:
            self.vertices[vertex.get_id()] = vertex
        elif isinstance(vertex, v.Attribute) and vertex.get_name() not in self.vertices:
            self.vertices[vertex.get_name()] = vertex

    def add_recipe_pair(self, base_uid: int, target_uid: int, category_uids: list[str]) -> None:
        """
        Adds the base recipe as a recipe pair for the target recipe based off the categories specified. If either
        the base or target recipe do not exist in this graph, do not add any recipe pair. If any of the categories does
        not exist in this graph, that category does not get added.
        """
        if base_uid not in self.vertices or target_uid not in self.vertices:
            return
        base = self.vertices[base_uid]
        target = self.vertices[target_uid]
        for category_uid in category_uids:
            if category_uid in self.vertices:
                category = self.vertices[category_uid]
                if isinstance(category, v.Category) and isinstance(base, v.Recipe) and isinstance(target, v.Recipe):
                    target.add_paired_recipe(category, base)

    def _matches_user_preferences_sets(self, categories, ingredients, allergies,
                                       recipe_ingredients: set, recipe_categories: set) -> bool:
        if allergies and any(a.lower() in recipe_ingredients for a in allergies):
            return False
        if ingredients and not any(i.lower() in recipe_ingredients for i in ingredients):
            return False
        if categories and not any(c.lower() in recipe_categories for c in categories):
            return False
        return True

    def _matches_user_preferences(self, categories, ingredients, allergies, recipe: v.Recipe) -> bool:

        recipe_ingredients = {i.get_name().lower() for i in recipe.get_ingredients()}
        recipe_categories = {c.get_name().lower() for c in recipe.get_categories()}
        return self._matches_user_preferences_sets(categories, ingredients, allergies,
                                                   recipe_ingredients, recipe_categories)

    def find_paired_recipe(self,categories: list[str], ingredients: list[str], allergies:list[str],recipe:int
                           ) -> list[v.Recipe]:
        """
        Return recipes that are explicitly paired with the given recipe
        and also match the user’s preferences.

        The method first retrieves all recipes previously linked via add_recipe_pair,
        then filters them to include only recipes that contain at least one of the
        specified ingredients, categories, and doesn't contain any of †he specified ingredients in allergies.

        Returns:
            - a list of paired Recipe objects that match the user preferences
            - returns an empty list if no paired recipes exist or none match the filters
        """

        if recipe not in self.vertices:
            return []

        recipe_vertex = self.vertices[recipe]

        if not isinstance(recipe_vertex, v.Recipe):
            return []

        paired = list(recipe_vertex.get_paired_recipes())

        # Filter based on user preferences
        filtered = [r for r in paired if isinstance(r, v.Recipe) and self._matches_user_preferences(categories, ingredients, allergies,
                                                                                                    r)]

        return filtered

    def find_similar_recipe(self,categories: list[str], ingredients: list[str], allergies:list[str],recipe: int
                            ) -> list[v.Recipe]:
        """
        Return recipes similar to the given recipe based on shared ingredients
        and categories, filtered to match user preferences.

        Similarity is determined by the overlap between:
            - ingredients
            - categories

        After computing similarity, only recipes that contain at least one of the
        specified ingredients, categories, or name tokens are returned.

        Parameters:
            - recipe: UID of the reference recipe
            - ingredients: list of ingredient names to filter by (optional)
            - categories: list of category names to filter by (optional)
            - name_tokens: list of tokens to match in the recipe name (optional)

        Returns:
            - a list of Recipe objects sorted by similarity (most similar first)
            - only includes recipes matching the user preferences
            - returns an empty list if no candidates exist or none match the filters
        """

        if recipe not in self.vertices:
            return []

        base_recipe = self.vertices[recipe]

        if not isinstance(base_recipe, v.Recipe):
            return []

        base_ingredients = {i.get_name().lower() for i in base_recipe.get_ingredients()}
        base_categories = {c.get_name().lower() for c in base_recipe.get_categories()}

        candidate_recipes = set()

        for ingredient in base_recipe.get_ingredients():
            for rec in ingredient.get_recipes():
                if rec.get_id() != recipe:
                    candidate_recipes.add(rec)

        for category in base_recipe.get_categories():
            for rec in category.get_recipes():
                if rec.get_id() != recipe:
                    candidate_recipes.add(rec)

        similarities = []
        for other in candidate_recipes:
            other_ingredients = {i.get_name().lower() for i in other.get_ingredients()}
            other_categories = {c.get_name().lower() for c in other.get_categories()}

            # Compute similarity
            ingredient_union = base_ingredients | other_ingredients
            category_union = base_categories | other_categories

            ingredient_score = len(base_ingredients & other_ingredients) / max(1, len(ingredient_union))
            category_score = len(base_categories & other_categories) / max(1, len(category_union))

            score = ingredient_score + category_score

            # Only include if matches user preferences
            if self._matches_user_preferences_sets(categories, ingredients, allergies,
                                                   other_ingredients, other_categories):
                similarities.append((score, other))

        # Sort by similarity
        similarities.sort(reverse=True, key=lambda x: x[0])
        return [r for _, r in similarities]

    def compute_alternative_recipe(self,categories: list[str], ingredients: list[str], allergies:list[str],recipe:int
                                   ) -> list[v.Recipe]:

        paired = self.find_paired_recipe(categories,ingredients,allergies,recipe)
        if not paired == []:
            return paired
        else:
            return self.find_similar_recipe(categories,ingredients,allergies,recipe)


    #to be implemented gang
    def find_recommendations(self, ingredients: list[str], categories: list[str],
                             allergies: list[str]) -> list[v.Recipe]:
        """Return a list of the top 3 recipes that best match the given user preferences.

            Uses the graph structure for efficient candidate retrieval by directly looking up
            ingredient and category vertices and collecting the recipes connected to them.
            This avoids scanning all recipes entirely.

            Matches contribute to the score as follows:
                - Each matching ingredient contributes 2 points
                - Each matching category contributes 3 points

            Parameters:
                - ingredients: a list of ingredient names to match against
                - categories: a list of category names to match against
                - allergies: a list of ingredient names to exclude recipes by

            Returns:
                - a list of up to 3 Recipe objects with the highest scores
                - returns an empty list if no recipes match or all are excluded by allergies
            """

        ingredients_lower = {i.lower() for i in ingredients}
        categories_lower = {c.lower() for c in categories}
        allergies_lower = {a.lower() for a in allergies}

        # Collect all recipes connected to matching ingredient vertices
        ingredient_candidates = set()
        for ing_name in ingredients_lower:
            if ing_name in self.vertices:
                ing_vertex = self.vertices[ing_name]
                if isinstance(ing_vertex, v.Ingredient):
                    ingredient_candidates.update(ing_vertex.get_recipes())

        # Collect all recipes connected to matching ingredient vertices
        categeoories_candidates = set()
        for cat_name in categories_lower: #meow :3
            if cat_name in self.vertices:
                cat_vertex = self.vertices[cat_name]
                if isinstance(cat_vertex, v.Ingredient):
                    categeoories_candidates.update(cat_vertex.get_recipes())

        allergen_recipes = set()
        for allergy in allergies_lower:
            if allergy in self.vertices and isinstance(self.vertices[allergy], v.Ingredient):
                allergen_recipes.update(self.vertices[allergy].get_recipes())

        # Score by most matches
        candidates = (ingredient_candidates | categeoories_candidates) - allergen_recipes
        scores = []
        for r in candidates:
            recipe_ingredients = {i.get_name().lower() for i in r.get_ingredients()}
            recipe_categories = {c.get_name().lower() for c in r.get_categories()}

            ingredient_score = len(ingredients_lower & recipe_ingredients) * 2
            category_score = len(categories_lower & recipe_categories) * 3
            total = ingredient_score + category_score

            if total > 0:
                scores.append((total, r))

        scores.sort(reverse=True, key=lambda x: x[0])
        return [r for _, r in scores[:3]]
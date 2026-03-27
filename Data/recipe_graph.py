"""CSC111 Project 2: The Ultimate Recipe Index - Recipe Graph

===============================

This Python module contains code for a recipe graph data structure in our recipe index application.
"""
from __future__ import annotations
import vertex as v
import file_reader

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

    def find_paired_recipe(self,recipe: int) -> list[v.Recipe]:
        """
        Return direct recipes that are paired with the given recipe.
        This retrieves all recipes that were previously linked using add_recipe_pair.

        Parameters:
            - recipe: UID of the recipe to find pairings for

        Returns:
            - a list of paired Recipe objects
            - returns an empty list if the recipe does not exist
        """

        if recipe not in self.vertices:
            return []

        recipe_vertex = self.vertices[recipe]

        if not isinstance(recipe_vertex, v.Recipe):
            return []

        return list(recipe_vertex.get_paired_recipes())

    def find_similar_recipe(self,recipe: int) -> list[v.Recipe]:
        """
        Return recipes similar to the given recipe based on shared ingredients and categories.

        Similarity is determined using overlap between:
        - ingredients
        - categories

        Parameters:
            - recipe: UID of the reference recipe

        Returns:
            - a list of Recipe objects sorted by similarity (most similar first)
        """
        if recipe not in self.vertices:
            return []

        base_recipe = self.vertices[recipe]

        if not isinstance(base_recipe, v.Recipe):
            return []

        #Step 1: Get base sets
        base_ingredients = {i.get_name() for i in base_recipe.get_ingredients()}
        base_categories = {c.get_name() for c in base_recipe.get_categories()}

        #Step 2: Collect candidate recipes using graph
        candidate_recipes = set()

        # From shared ingredients
        for ingredient in base_recipe.get_ingredients():
            for rec in ingredient.get_recipes():
                if rec.get_id() != recipe:
                    candidate_recipes.add(rec)

        # From shared categories
        for category in base_recipe.get_categories():
            for rec in category.get_recipes():
                if rec.get_id() != recipe:
                    candidate_recipes.add(rec)

        # Step 3: Compute similarity only for candidates
        similarities = []

        for other in candidate_recipes:
            other_ingredients = {i.get_name() for i in other.get_ingredients()}
            other_categories = {c.get_name() for c in other.get_categories()}

            # Jaccard similarity
            ingredient_union = base_ingredients | other_ingredients
            category_union = base_categories | other_categories

            ingredient_score = len(base_ingredients & other_ingredients) / max(1, len(ingredient_union))
            category_score = len(base_categories & other_categories) / max(1, len(category_union))

            score = ingredient_score + category_score

            similarities.append((score, other))

        #Step 4: Sort by similarity
        similarities.sort(reverse=True, key=lambda x: x[0])
        return [recipe for _, recipe in similarities]


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
    vertices: dict[int | str, v.Vertex]

    def __init__(self):
        self.vertices = {}

    def add_vertex(self, vertex: v.Vertex) -> None:
        if isinstance(vertex, v.Recipe) and vertex.get_id() not in self.vertices:
            self.vertices[vertex.get_id()] = vertex
        elif isinstance(vertex, v.Attribute) and vertex.get_name() not in self.vertices:
            self.vertices[vertex.get_name()] = vertex

    def add_recipe_pair(self, base_uid: int, target_uid: int, category_uids: list[str]):
        base = self.vertices[base_uid]
        target = self.vertices[target_uid]
        for category_uid in category_uids:
            category = self.vertices[category_uid]
            if isinstance(category, v.Category) and isinstance(base, v.Recipe) and isinstance(target, v.Recipe):
                target.add_paired_recipe(category, base)

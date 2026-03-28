"""CSC111 Project 2: The Ultimate Recipe Index - Recipe Tree

===============================

This Python module contains code for a recipe tree data structure in our recipe index application.
"""
from __future__ import annotations
import vertex
import file_reader

UID_INDEX = 0
NAME_INDEX = 1
STEPS_INDEX = 2
INGREDIENTS_INDEX = 3
CATEGORIES_INDEX = 4
NAME_TOKENS_INDEX = 5

INGREDIENTS = "i"
CATEGORIES = "c"
NAME_TOKENS = "n"


def build_recipe_tree(file_path: str, is_csv: bool) -> RecipeTree:
    """
    Builds a recipe tree based off the csv/parquet file of the recipe dataset.

    The logic is that for every row (aka. every recipe), we add the recipe as a vertex to the tree, making
    sure that the categories, ingredients, and name_tokens are not recreated by keeping track of what we have
    seen so far. Check the recipe_tree class for more info.

    Preconditions:
        - file_path is the path to the parquet file of the recipe dataset
    """
    recipes = file_reader.read_recipes_data(file_path, is_csv)
    tree = RecipeTree(INGREDIENTS)
    seen_categories, seen_ingredients, seen_name_tokens = {}, {}, {}
    for recipe in recipes:
        tree.add_vertex(make_recipe_vertex(recipe, seen_categories, seen_ingredients, seen_name_tokens))
    return tree


def make_recipe_vertex(recipe: list, categories: dict[str, vertex.Category], ingredients: dict[str, vertex.Ingredient],
                       name_tokens: dict[str, vertex.NameToken]) -> vertex.Recipe:
    """
    Makes a recipe vertex using a recipe row (see file_reader.py for information on how the rows are structured)
    by first making an empty recipe vertex using the name and UID, then adding every category, ingredient, and
    name_token to the vertex, making sure that if we have already seen the categories, ingredients, or name_tokens
    before, we do not add them.

    Precondition:
        - recipe is a valid list of the form specified in file_reader.py
    """
    recipe_vertex = vertex.Recipe(recipe[NAME_INDEX], recipe[UID_INDEX], recipe[STEPS_INDEX])
    for category in recipe[CATEGORIES_INDEX]:
        if category not in categories:
            categories[category] = vertex.Category(category)
        recipe_vertex.add_category(categories[category])
    for ingredient in recipe[INGREDIENTS_INDEX]:
        if ingredient not in ingredients:
            ingredients[ingredient] = vertex.Ingredient(ingredient)
        recipe_vertex.add_ingredient(ingredients[ingredient])
    for name_token in recipe[NAME_TOKENS_INDEX]:
        if name_token not in name_tokens:
            name_tokens[name_token] = vertex.NameToken(name_token)
        recipe_vertex.add_name_token(name_tokens[name_token])
    return recipe_vertex


class RecipeTree:
    """
    A tree data structure which represents recipes by how they can be classified in terms of categories, ingredients,
    and any words in their name. This is how the hierarchy looks:

    Depth Zero - Every recipe in the dataset, no filters
    Depth One - Recipes get filtered by the ingredients they contain, meaning at this level, if we have an "onion"
    ingredient, that node in the second layer will contain a mapping to ONLY recipes with onions
    Depth Two - Recipes get filtered by the categories they fall within
    Depth Three - Recipes get filtered by their name_tokens, which is what words they contain in their name

    No filters -> Filtered by ingredient -> Filtered by categories -> Filtered by name_tokens

    How this works in practice is that if someone wants to find a dairy-free recipe of some kind of yogurt with almonds
    in it, the tree first recognizes the user wants "almonds", and filters down. Then, it recognizes that it has to be
    "dairy free" and filters down even further. Finally, it recognizes that it has to be a "yogurt", meaning yogurt
    is in the name, and filters down. At that point, you have a dictionary mapping of every recipe which satisifies the
    given requirements

    Instance Attributes:
        - recipes: a mapping of every recipe UID to the recipe object it represents
        - filters: a mapping of the string name of every filter which is of the self.current_filter to the RecipeTree
        corresponding to that filtration
        - current_filter: a string representing what kind of filter occurs in self.filters, None if at a leaf

    Representation Invariants:
        - self.current_filter is None or self.current_filter in {INGREDIENTS, CATEGORIES, NAME_TOKENS}
    """

    recipes: dict[int, vertex.Recipe]
    filters: dict[str, RecipeTree]
    current_filter: str | None
    _max_recipe_name_length: int

    def __init__(self, current_filter: str | None):
        self.recipes = {}
        self.filters = {}
        self.current_filter = current_filter
        self._max_recipe_name_length = 0

    def add_vertex(self, recipe: vertex.Recipe) -> None:
        """
        Adds the vertex to the following recipe tree if it is not already in by first
        adding the vertex to the current layer, then adding it to the next layer depending
        on the condition of the current filter.
        """

        # Handle the case when the recipe is already in the tree
        if recipe.get_id() in self.recipes:
            return

        # Add the recipe to the tree and update the max recipe name length if the recipe has a longer name
        self.recipes[recipe.get_id()] = recipe
        self._max_recipe_name_length = max(
            self._max_recipe_name_length,
            len(recipe.get_name())
        )

        # If no more filtration can occur, return (this is the base case)
        if self.current_filter is None:
            return

        # Add the recipe according to the current filter, and move on to the next filter
        if self.current_filter == INGREDIENTS:
            self._add_to_children(recipe.get_ingredients(), CATEGORIES, recipe)

        elif self.current_filter == CATEGORIES:
            self._add_to_children(recipe.get_categories(), NAME_TOKENS, recipe)

        elif self.current_filter == NAME_TOKENS:
            self._add_to_children(recipe.get_name_tokens(), None, recipe)

    def _add_to_children(self, items: set, next_filter: str | None, recipe: vertex.Recipe):
        """Takes the recipe and recursively fully adds the recipe to every filter it is in"""
        for item in items:
            name = item.get_name()
            # If the filter is already found in filters, meaning other recipes have been filtered in the same way,
            # otherwise, create the filter, then recursively add the vertex
            if name not in self.filters:
                self.filters[name] = RecipeTree(next_filter)
            self.filters[name].add_vertex(recipe)

    def __contains__(self, uid: int) -> bool:
        return uid in self.recipes


    def sort_by_name(self) -> list[vertex.Recipe]:
        recipe_list = self.recipes.values()
        return sorted(recipe_list, key=lambda recipe: len(recipe.get_name()))

    def sort_by_ingredient_count(self) -> list[vertex.Recipe]:
        recipe_list = self.recipes.values()
        return sorted(recipe_list, key=lambda recipe: len(recipe.get_ingredients()))

    def search_by_name(self, name: str | None = None) -> list[vertex.Recipe]:
        """
        Return a list of recipes whose names partially match the given query.

        The search is case-insensitive and supports partial matching:
        - The input string is split into tokens
        - Each token is matched against name_tokens in the tree using prefix matching
        - Only recipes that match ALL tokens are returned

        Parameters:
            - name: the search query string

        Returns:
            - a list of Recipe objects whose names match the query
            - returns an empty list if name is None or no matches are found
        """
        if name is None:
            return []

        cleaned_name = name.lower().strip()
        name_tokens = cleaned_name.split()
        token_recipe_sets = []
        for token in name_tokens:
            matched_recipes = set()
            for candidate in self.filters:
                if candidate.startswith(token):
                    matched_recipes.update(self.filters[candidate].recipes.values())
            token_recipe_sets.append(matched_recipes)
        if not token_recipe_sets:
            return []
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

        if name is None:
            candidates = self.recipes.values()
        else:
            candidates = self.search_by_name(name)

        results = []
        for recipe in candidates:
            ingredient_names = {ingredient.get_name() for ingredient in recipe.get_ingredients()}
            category_names = {category.get_name() for category in recipe.get_categories()}
            if ingredients_set.issubset(ingredient_names) and categories_set.issubset(category_names):
                results.append(recipe)
        return results

    #to be implemented gang
    def find_recommendations(self, ingredients: list[str], categories: list[str],
                             name_tokens: list[str], allergies: list[str]) -> list[vertex.Recipe]:
        """Return a list of the top 3 recipes that best match the given user preferences.

        This method uses the tree structure to efficiently narrow down candidates by
        traversing ingredient subtrees and skipping any subtrees corresponding to allergens.
        A secondary allergy check is then performed on each candidate recipe directly,
        since a recipe may still contain an allergen ingredient via a different subtree path.

        After filtering, recipes are scored based on how well they match the provided
        criteria, and the top 3 recipes by score are returned.

        Matches contribute to the score as follows:
            - Each matching ingredient contributes 2 points
            - Each matching category contributes 3 points
            - Each matching name token contributes 1 point

        Parameters:
            - ingredients: a list of ingredient names to match against
            - categories: a list of category names to match against
            - name_tokens: a list of name tokens to match against
            - allergies: a list of ingredient names to exclude recipes by

        Returns:
            - a list of up to 3 Recipe objects with the highest scores
            - returns an empty list if no recipes match or all are excluded by allergies
        """

        ingredients_lower = {i.lower() for i in ingredients}
        categories_lower = {c.lower() for c in categories}
        name_tokens_lower = {t.lower() for t in name_tokens}
        allergies_lower = {a.lower() for a in allergies}

        # Use tree to get candidates — traverse ingredient subtrees skipping allergens
        candidates = set()
        for tok_name, tok_subtree in self.filters.items():
            for ing_name, ing_subtree in tok_subtree.filters.items():
                if ing_name.lower() not in allergies_lower:
                    candidates.update(ing_subtree.recipes.values())

        # Secondary allergy check on the recipe itself (a recipe could still
        # contain an allergen ingredient via a different subtree path)
        safe_candidates = set()
        for r in candidates:
            recipe_ingredients = {i.get_name().lower() for i in r.get_ingredients()}
            if not allergies_lower & recipe_ingredients:
                safe_candidates.add(r)

        # Score by most matches
        scores = []
        for r in safe_candidates:
            recipe_ingredients = {i.get_name().lower() for i in r.get_ingredients()}
            recipe_categories = {c.get_name().lower() for c in r.get_categories()}
            recipe_name_tokens = {t.get_name().lower() for t in r.get_name_tokens()}

            ingredient_score = len(ingredients_lower & recipe_ingredients) * 2
            category_score = len(categories_lower & recipe_categories) * 3
            name_score = len(name_tokens_lower & recipe_name_tokens) * 1

            total = ingredient_score + category_score + name_score

            if total > 0:
                scores.append((total, r))

        scores.sort(reverse=True, key=lambda x: x[0])
        return [r for _, r in scores[:3]]
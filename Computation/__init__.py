
from Data.recipe_graph import RecipeGraph
from Data.recipe_tree import RecipeTree
from Data.vertex import Recipe
from Data.recipe_tree import NAME_TOKENS

class RecommendationFinder:
    """ A tree based entity that recommends a recipe based on user's preferences.
     Instance Attributes:
        - recipes : the recipe tree that this entity uses to make recommendations.
     """
    recipes : RecipeTree

    def __init__(self, recipes : RecipeTree)-> None:
        """Initialize a new RecommendationFinder."""
        self.recipes = recipes

    def find_recommendations(self,ingredients: list[str],categories: list[str],name_tokens: list[str]) -> list[Recipe]:
        """Return a list of the top 3 recipes that best match the given user preferences.

        Recipes are scored based on how well they match the provided criteria.
        Matches contribute to the score as follows:
            - Each matching ingredient contributes 2 points
            - Each matching category contributes 3 points
            - Each matching name token contributes 1 point

        The method returns the 3 recipes with the highest total scores."""

class AlternativeComputer:
    """A graph based entity that provides an alternative recipe based on a given recipe.

    Instance Attributes:
        - recipes : the recipe graph that this entity uses to computer alternative recipes."""
    recipes : RecipeGraph

    def __init__(self, recipes : RecipeGraph) -> None:
        """Initialize a new AlternativeComputer."""
        self.recipes = recipes

    def findSimilarRecipe(recipe: int, ingredients: list[str],categories: list[[str]],name_tokens:list[str]) -> list[Recipe]:
        """"finds a similar recipe based on the given recipe and ingredients."""

    def findPairedRecipe(recipe: int, ingredients:list[str],categories: list[str], name_tokens: list[str]) -> list[Recipe]:
        """"finds a paired recipe based on the given recipe and ingredients."""



#THIS SHIT IS ALSO DONE ( I COPIED NEW IMPLEMENTATION FROM RECIPE GRAPH SO THE PARAMETERS DON'T WORK HERE!)
class RecipeFinder:
    """" A class for finding recipes from a recipe tree.
    This class provides functionality to search recipes either by name
    (supporting partial matches) or by applying attribute-based filters
    such as ingredients, categories, or other recipe properties.

    Instance Attributes:
        - recipes : a recipe tree
    """
    def __init__(self, recipes)-> None:
        self.recipes = recipes

    #so FUCK my BAKA CHUNGUS LIFE
    def searchByName(self, name: str) -> list[Recipe]:
        """Return all recipes whose name contains the given string."""
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

    def searchByFilters(self, ingredients: list[str], categories: list[str],name: str = None) -> list[Recipe]:
        """ Returns a list of recipes matching the given name and ingredients."""
        # Step 1: Determine candidate recipes
        if name is None:
            candidates = self.recipes.values()
        else:
            candidates = self.searchByName(name)
        # Step 2:  Filter candidates based on ingredients and categories
        results = []
        for recipe in candidates:
            recipe_ingredient_names = {ingredient.name for ingredient in recipe.ingredients}
            recipe_category_names = {category.name for category in recipe.categories}
            if ingredients.issubset(recipe_ingredient_names) and categories.issubset(recipe_category_names):
                results.append(recipe)
        return results


#THIS SHIT IS DONE
class Sorter:
    """A utility class for sorting lists of recipes."""
    def sort_by_name(self, recipes: list[Recipe]) -> list[Recipe]:
        """Return recipes sorted alphabetically by name."""
        return sorted(recipes, key=lambda r: r.name)

    def sort_by_ingredient_count(self, recipes: list[Recipe]) -> list[Recipe]:
        """Return recipes sorted by number of ingredients."""
        return sorted(recipes, key=lambda r: len(r.ingredients))

    def sort(self, recipes: list[Recipe], key: str) -> list[Recipe]:
        """Sort recipes based on a given key.
        Valid keys:
            - 'name'
            - 'ingredients'
        """
        if key == "name":
            return self.sort_by_name(recipes)
        elif key == "ingredients":
            return self.sort_by_ingredient_count(recipes)
        else:
            return recipes
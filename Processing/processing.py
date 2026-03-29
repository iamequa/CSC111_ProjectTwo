import pygame

import GUI.screen_displays as gui
from Data.recipe_tree import RecipeTree
from Data.recipe_graph import RecipeGraph
from Data.vertex import Recipe

ERROR_MESSAGE = "Either you have not pressed submit or we have found no recipes, sorry!"

def list_to_str(lst: list[str]) -> str:
    return ", ".join(lst)

class MainMenuProcessor:
    """Handles logic for the main menu screen.
    Instance Attributes:
        - organizer:
        - search_screen:
        - algorithm_screen:
        - main_screen:
    """
    organizer: gui.ScreenOrganizer
    search_screen: gui.Screen
    algorithm_screen: gui.Screen
    main_screen: gui.Screen

    def __init__(self, organizer: gui.ScreenOrganizer, search_screen: gui.Screen, algorithm_screen: gui.Screen,
                 main_screen: gui.Screen) -> None:
        self.organizer = organizer
        self.search_screen = search_screen
        self.algorithm_screen = algorithm_screen
        self.main_screen = main_screen

    def go_to_search(self) -> None:
        self.organizer.switch_screens(self.search_screen)

    def go_to_survey(self) -> None:
        self.organizer.switch_screens(self.algorithm_screen)

    def exit_app(self) -> None:
        from pygame import quit
        quit()
        exit()


class AlgorithmProcessor:
    """The processor for the algorithm Screen in app.py
    Instance Attributes:
        - organizer:
        - algorithm_screen:
        - main_screen:
    Private Instance Attributes (Note: you dont have to make it private if u dont agree but I added here in case):
        - _current_recipes:
        - _current_index:
        - _data:
        """
    organizer: gui.ScreenOrganizer
    algorithm_screen: gui.Screen
    main_screen: gui.Screen
    data: RecipeGraph
    _current_recipes: list[Recipe]
    _current_index: int

    def __init__(self, organizer: gui.ScreenOrganizer, algorithm_screen: gui.Screen, main_screen: gui.Screen,
                 data: RecipeGraph) -> None:

        self.organizer = organizer
        self.algorithm_screen = algorithm_screen
        self.main_screen = main_screen
        self.data = data
        self.current_recipes = []
        self.current_index = 0

    def go_to_main_menu(self) -> None:
        self.algorithm_screen.refresh_screen()
        self.organizer.switch_screens(self.main_screen)
        self.current_recipes, self.current_index = [], 0

    def give_recommendation(self) -> None:
        inputs = self.algorithm_screen.get_textbox_inputs()
        dietary, ingredients, allergies, recipe_name = inputs[0], inputs[1], inputs[2], inputs[3]

        self.algorithm_screen.refresh_screen()
        if len(inputs[0]) == len(inputs[1]) == len(inputs[2]) == 0:
            self._display_error("Please enter at least one filter.")
            return
        self.algorithm_screen.refresh_screen()
        self.current_index = 0

        if not recipe_name:
            self.current_recipes = self.data.find_recommendations(dietary, ingredients, allergies)
        else:
            recipe_name = recipe_name[0].lower().strip()
            if recipe_name not in self.data.recipe_name_to_id:
                self._display_error("Recipe not found.")
                return
            recipe_id = self.data.recipe_name_to_id[recipe_name]
            self.current_recipes = self.data.compute_alternative_recipe(dietary, ingredients, allergies, recipe_id)
        self.print_alternatives()

    def print_alternatives(self) -> None:
        if self.algorithm_screen.text is None:
            self.algorithm_screen.text = []

        if not self.current_recipes:
            self._display_error("No alternatives found.")
            return

        self.make_alternatives()

    def _display_error(self, error: str) -> None:
        if self.algorithm_screen.text is None:
            self.algorithm_screen.text = []

        error_text = gui.Text(
            error,
            pygame.Rect(0, 0, 550, 500),
            (50, 550),
            30
        )
        self.algorithm_screen.text.append(error_text)

    def go_right(self) -> None:
        self.algorithm_screen.refresh_screen()
        if self.current_recipes == [] and self.current_index == 0:
            self._display_error(ERROR_MESSAGE)
        elif len(self.current_recipes) - 1 <= self.current_index:
            self.make_alternatives()
        else:
            self.current_index += 1
            self.make_alternatives()

    def go_left(self) -> None:
        self.algorithm_screen.refresh_screen()
        if self.current_recipes == [] and self.current_index == 0:
            self._display_error(ERROR_MESSAGE)
        elif self.current_index <= 0:
            self.make_alternatives()
        else:
            self.current_index -= 1
            self.make_alternatives()

    def make_alternatives(self) -> None:  # change the name
        y = 520
        current_recipe = self.current_recipes[self.current_index]
        recipe_name, recipe_ingredients, recipe_categories = (current_recipe.get_name(),
                                                              current_recipe.get_ingredients(),
                                                              current_recipe.get_categories())
        recipe_ingredients = [ingredient.get_name() for ingredient in recipe_ingredients]
        recipe_categories = [category.get_name() for category in recipe_categories]

        current_recipe_text = gui.Text(recipe_name +
                                       "\nIngredients: " + list_to_str(recipe_ingredients) +
                                       "\nCategories: " + list_to_str(recipe_categories),
                                       pygame.Rect(0, 0, 550, 500)
                                       , (50, y), 30)
        self.algorithm_screen.text.append(current_recipe_text)


class SearchProcessor:
    """The processor for the search Screen in app.py
    Instance Attributes:
        - organizer: the ScreenOrganizer in app.py
        - search_screen: the search Screen in app.py
        - main_screen: the main Screen in app.py
    Private Instance Attributes:
        - _data: the RecipeTree with all the recipes
        - _current_recipes: a list of Recipes returned from searching
        - _current_index: the current index of _current_recipes the user is looking at
    """
    organizer: gui.ScreenOrganizer
    search_screen: gui.Screen
    main_screen: gui.Screen
    _data: RecipeTree
    _current_recipes: list[Recipe]
    _current_index: int

    def __init__(self, organizer: gui.ScreenOrganizer, search_screen: gui.Screen, main_screen: gui.Screen,
                 data: RecipeTree) -> None:
        self.organizer = organizer
        self.search_screen = search_screen
        self.main_screen = main_screen
        self._data = data
        self._current_recipes = []
        self._current_index = 0

    def go_to_main_menu(self) -> None:
        """Changes the current screen in organizer to the main menu."""
        self.search_screen.refresh_screen()
        self.organizer.switch_screens(self.main_screen)
        self._current_recipes, self._current_index = [], 0

    def _display_error(self, error: str) -> None:
        """Prints error message on search screen"""
        if self.search_screen.text is None:
            self.search_screen.text = []

        error_text = gui.Text(
            error,
            pygame.Rect(0, 0, 400, 500),
            (50, 200),
            25
        )
        self.search_screen.text.append(error_text)

    def search(self) -> None:
        """Searches for results based off user's entries and prints them on screen"""
        inputs = self.search_screen.get_textbox_inputs()
        ingr_filter, cat_filter, recipe_filter = inputs[0], inputs[1], inputs[2]

        if not recipe_filter:
            recipe_filter = ''
        else:
            recipe_filter = recipe_filter[0]

        self.search_screen.refresh_screen()

        results = self._data.search_by_filters(ingr_filter, cat_filter, recipe_filter)
        self._current_recipes = results
        self._current_index = 0
        self.print_search_results(results)

    def go_right(self) -> None:
        """Displays recipe to the right of current recipes based off user's search results"""
        self.search_screen.refresh_screen()
        if self._current_recipes == [] and self._current_index == 0:
            self._display_error(ERROR_MESSAGE)
        elif len(self._current_recipes) - 1 <= self._current_index:
            self.show_alternatives()
        else:
            self._current_index += 1
            self.show_alternatives()

    def go_left(self) -> None:
        """Displays recipe to the left of current recipes based off user's search results"""
        self.search_screen.refresh_screen()
        if self._current_recipes == [] and self._current_index == 0:
            self._display_error(ERROR_MESSAGE)
        elif self._current_index <= 0:
            self.show_alternatives()
        else:
            self._current_index -= 1
            self.show_alternatives()

    def print_search_results(self, search_results: list[Recipe]) -> None:
        """Prints all the search results based off search_results."""
        if self.search_screen.text is None:
            self.search_screen.text = []

        if not search_results:
            self._display_error("No recipes found.")
            return
        self.show_alternatives()

    def show_alternatives(self) -> None:  # change the name
        """Takes recipe alternative at current index and prints it on screen."""
        y = 200
        current_recipe = self._current_recipes[self._current_index]
        recipe_name, recipe_ingredients, recipe_categories = (current_recipe.get_name(),
                                                              current_recipe.get_ingredients(),
                                                              current_recipe.get_categories())
        recipe_ingredients = [ingredient.get_name() for ingredient in recipe_ingredients]
        recipe_categories = [category.get_name() for category in recipe_categories]

        current_recipe_text = gui.Text(recipe_name +
                                            "\nIngredients: " + list_to_str(recipe_ingredients) +
                                            "\nCategories: " + list_to_str(recipe_categories),
                                            pygame.Rect(0, 0, 550, 300)
                                            ,(50, y), 20)
        self.search_screen.text.append(current_recipe_text)

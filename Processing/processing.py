import pygame

import GUI.screen_displays as gui
from Data.recipe_tree import RecipeTree
from Data.recipe_graph import RecipeGraph
from Data.vertex import Recipe


def list_to_str(lst: list[str]) -> str:
    text = ", ".join(lst)

    max_len = 50
    lines = []
    current_line = ""

    for word in text.split(" "):
        # +1 for the space
        if len(current_line) + len(word) + 1 <= max_len:
            if current_line:
                current_line += " "
            current_line += word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return "\n".join(lines)


class MainMenuProcessor:
    """Handles logic for the main menu screen."""
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
    organizer: gui.ScreenOrganizer
    algorithm_screen: gui.Screen
    main_screen: gui.Screen
    data: RecipeGraph
    current_recipes: list[Recipe]
    current_index: int

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
            pygame.Rect(0, 0, 0, 0),
            (50, 550),
            25
        )
        self.algorithm_screen.text.append(error_text)

    def go_right(self) -> None:
        self.algorithm_screen.refresh_screen()
        if self.current_recipes == [] and self.current_index == 0:
            self._display_error("Either you have not pressed submit or we \nhave found no recipes, sorry!")
        elif len(self.current_recipes) - 1 <= self.current_index:
            self.make_alternatives()
        else:
            self.current_index += 1
            self.make_alternatives()

    def go_left(self) -> None:
        self.algorithm_screen.refresh_screen()
        if self.current_recipes == [] and self.current_index == 0:
            self._display_error("Either you have not pressed submit or we \nhave found no recipes, sorry!")
        elif self.current_index <= 0:
            self.make_alternatives()
        else:
            self.current_index -= 1
            self.make_alternatives()

    def make_alternatives(self) -> None:
        y = 520
        current_recipe = self.current_recipes[self.current_index]
        recipe_name, recipe_ingredients, recipe_categories = (current_recipe.get_name(),
                                                              current_recipe.get_ingredients(),
                                                              current_recipe.get_categories())
        recipe_ingredients = [ingredient.get_name() for ingredient in recipe_ingredients]
        recipe_categories = [category.get_name() for category in recipe_categories]

        current_recipe_name_text = gui.Text(recipe_name, pygame.Rect(0, 0, 0, 0), (50, y), 20)
        self.algorithm_screen.text.append(current_recipe_name_text)

        current_recipe_ingredients_text = gui.Text("Ingredients: " + list_to_str(recipe_ingredients),
                                                   pygame.Rect(0, 0, 0, 0), (50, y + 60), 20)
        self.algorithm_screen.text.append(current_recipe_ingredients_text)

        current_recipe_categories_text = gui.Text("Categories: " + list_to_str(recipe_categories),
                                                  pygame.Rect(0, 0, 0, 0), (50, y + 180), 20)
        self.algorithm_screen.text.append(current_recipe_categories_text)

class SearchProcessor:
    organizer: gui.ScreenOrganizer
    search_screen: gui.Screen
    main_screen: gui.Screen
    data: RecipeTree

    def __init__(self, organizer: gui.ScreenOrganizer, search_screen: gui.Screen, main_screen: gui.Screen,
                 data: RecipeTree) -> None:
        self.organizer = organizer
        self.search_screen = search_screen
        self.main_screen = main_screen
        self.data = data

    def go_to_main_menu(self) -> None:
        self.search_screen.refresh_screen()
        self.organizer.switch_screens(self.main_screen)

    def search(self) -> None:
        inputs = self.search_screen.get_textbox_inputs()

        name = inputs[0].lower().strip()
        ingredients = process_varchar_list(inputs[1])
        categories = process_varchar_list(inputs[2])

        self.search_screen.refresh_screen()

        results = self.data.search_by_filters(ingredients, categories, name)
        self.print_search_results(results)

    def print_search_results(self, search_results: list[Recipe]) -> None:
        if self.search_screen.text is None:
            self.search_screen.text = []

        if not search_results:
            no_results = gui.Text(
                "No recipes found.",
                pygame.Rect(0, 0, 0, 0),
                (50, 200),
                25
            )
            self.search_screen.text.append(no_results)
            return

        y = 200
        for recipe in search_results[:15]:
            text_obj = gui.Text(
                recipe.get_name(),
                pygame.Rect(0, 0, 0, 0),
                (50, y),
                25
            )
            self.search_screen.text.append(text_obj)
            y += 35

import pygame

import GUI.screen_displays as gui
from Data.recipe_tree import RecipeTree
from Data.recipe_graph import RecipeGraph
from Data.file_reader import process_varchar_list
from Data.vertex import Recipe


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

    def __init__(self, organizer: gui.ScreenOrganizer, algorithm_screen: gui.Screen, main_screen: gui.Screen,
                 data: RecipeGraph) -> None:

        self.organizer = organizer
        self.algorithm_screen = algorithm_screen
        self.main_screen = main_screen
        self.data = data

    def go_to_main_menu(self) -> None:
        self.algorithm_screen.refresh_screen()
        self.organizer.switch_screens(self.main_screen)

    def give_recommendation(self) -> None:
        self.algorithm_screen.refresh_screen()
        inputs = self.algorithm_screen.get_textbox_inputs()
        dietary = process_varchar_list(inputs[0])
        ingredients = process_varchar_list(inputs[1])
        allergies = process_varchar_list(inputs[2])
        recipe_name = inputs[3].lower()
        if recipe_name not in self.data.recipe_name_to_id:
            self._display_error("Recipe not found.")
            return
        recipe_id = self.data.recipe_name_to_id[recipe_name]
        alternatives = self.data.compute_alternative_recipe(dietary, ingredients, allergies, recipe_id)
        self.print_alternatives(alternatives)

    def print_alternatives(self, alternatives: list[Recipe]) -> None:
        if self.algorithm_screen.text is None:
            self.algorithm_screen.text = []

        if not alternatives:
            self._display_error("No alternatives found.")
            return

        y = 820
        for recipe in alternatives[:5]:
            text_obj = gui.Text(
                recipe.get_name(),
                pygame.Rect(0, 0, 0, 0),
                (50, y),
                25
            )
            self.algorithm_screen.text.append(text_obj)
            y += 35

    def _display_error(self, error: str) -> None:
        if self.algorithm_screen.text is None:
            self.algorithm_screen.text = []

        error_text = gui.Text(
            error,
            pygame.Rect(0, 0, 0, 0),
            (50, 820),
            25
        )
        self.algorithm_screen.text.append(error_text)


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

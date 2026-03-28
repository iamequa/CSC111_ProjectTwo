import assignments.CSC111_ProjectTwo.GUI.screen_displays as gui
from assignments.CSC111_ProjectTwo.Data.recipe_tree import RecipeTree
from assignments.CSC111_ProjectTwo.Data.recipe_graph import RecipeGraph
from assignments.CSC111_ProjectTwo.Data.file_reader import process_varchar_list
from assignments.CSC111_ProjectTwo.Data.vertex import Recipe


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
        self.organizer.switch_screens(self.main_screen)

    def give_recommendation(self) -> None:
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


    def _display_error(self, error: str) -> None:


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
        self.organizer.switch_screens(self.main_screen)

    def search(self) -> None:
        inputs = self.search_screen.get_textbox_inputs()
        name = inputs[0].lower()
        ingredients = process_varchar_list(inputs[1])
        categories = process_varchar_list(inputs[2])
        results = self.data.search_by_filters(ingredients, categories, name)
        self.print_search_results(results)

    def print_search_results(self, search_results: list[Recipe]) -> None:

"""CSC111 Project 2: The Ultimate Recipe Index - App

===============================

This Python module contains the area where the app is instanitated and used.
"""

import sys
import pygame

import GUI.screen_displays as screen_displays
import Processing.processing as processing
import Data.file_reader as file_reader
from Data import vertex
from Data.recipe_graph import RecipeGraph
from Data.recipe_tree import NAME_TOKENS, RecipeTree
from Processing.app_constants import *


def build_recipe_structures(recipes_path: str, is_recipes_csv: bool,
                            pairs_path: str, is_pairs_csv: bool) -> tuple[RecipeGraph, RecipeTree]:
    """
    Build both the RecipeGraph and RecipeTree in one pass over the recipe dataset.
    """
    recipes = file_reader.read_recipes_data(recipes_path, is_recipes_csv)
    recipe_pairs = file_reader.read_pairs_data(pairs_path, is_pairs_csv)

    graph = RecipeGraph()
    tree = RecipeTree(NAME_TOKENS)

    seen_categories: dict[str, vertex.Category] = {}
    seen_ingredients: dict[str, vertex.Ingredient] = {}
    seen_name_tokens: dict[str, vertex.NameToken] = {}

    for recipe in recipes:
        recipe_vertex = make_recipe_vertex_shared(
            recipe,
            seen_categories,
            seen_ingredients,
            seen_name_tokens
        )

        # add recipe to tree
        tree.add_vertex(recipe_vertex)

        # add recipe to graph
        graph.add_vertex(recipe_vertex)

        # add shared attributes to graph
        for ingredient in recipe_vertex.get_ingredients():
            graph.add_vertex(ingredient)

        for category in recipe_vertex.get_categories():
            graph.add_vertex(category)

    for pair in recipe_pairs:
        graph.add_recipe_pair(pair[BASE_INDEX], pair[TARGET_INDEX], pair[CATEGORIES_INDEX])

    return graph, tree


def make_recipe_vertex_shared(
        recipe: list,
        categories: dict[str, vertex.Category],
        ingredients: dict[str, vertex.Ingredient],
        name_tokens: dict[str, vertex.NameToken]
) -> vertex.Recipe:
    """
    Build one Recipe vertex with shared Category, Ingredient, and NameToken vertices.
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


class App:
    """
    Represents the main area where our app is created and ran.

    Instance Attributes:
        - screen: the screen display and dimensions
        - current_screen: the manager for what screen we are currently on
        - recipe_tree: a tree data structure representation of recipes
        - recipe_graph: a graph data structure representation of recipes
        - running: whether this app is currently running or not
    """
    screen: pygame.Surface
    current_screen: screen_displays.ScreenOrganizer
    recipe_tree: RecipeTree
    recipe_graph: RecipeGraph
    running: bool

    def __init__(self) -> None:
        self.recipe_graph, self.recipe_tree = build_recipe_structures(RECIPES_CSV_PATH, IS_RECIPE_CSV,
                                                                      PAIRS_CSV_PATH, IS_PAIRS_CSV)
        pygame.init()
        pygame.display.set_caption(CAPTION)

        self.screen = pygame.display.set_mode((X_DIMENSIONS, Y_DIMENSIONS))
        self.running = True
        self._setup()

    def _setup(self) -> None:
        """Sets up the entire app."""
        main_menu_screen, mm_buttons = self._setup_main_screen()
        survey_screen, ss_buttons = self._setup_survey_screen()
        search_screen, si_buttons = self._setup_search_screen()
        self._setup_buttons_and_processors(main_menu_screen, survey_screen, search_screen, mm_buttons, ss_buttons,
                                           si_buttons)

    def _setup_main_screen(self) -> tuple[screen_displays.Screen, list[screen_displays.Button]]:
        """Sets up main screen and return the list of buttons in main menu screen"""
        mm1_rect = pygame.Rect(MM1_RECT_X, MM1_RECT_Y, MM1_RECT_WIDTH, MM1_RECT_HEIGHT)
        main_menu_survey_button = screen_displays.Button(
            mm1_rect, MM1_BUTTON_TEXT, BUTTON_COLOR,
            top_left_coordinates=MM1_BUTTON_TOP_LEFT
        )

        mm2_rect = pygame.Rect(MM2_RECT_X, MM2_RECT_Y, MM2_RECT_WIDTH, MM2_RECT_HEIGHT)
        main_menu_search_button = screen_displays.Button(
            mm2_rect, MM2_BUTTON_TEXT, BUTTON_COLOR,
            top_left_coordinates=MM2_BUTTON_TOP_LEFT
        )

        mm3_rect = pygame.Rect(MM3_RECT_X, MM3_RECT_Y, MM3_RECT_WIDTH, MM3_RECT_HEIGHT)
        main_menu_quit_button = screen_displays.Button(mm3_rect, MM3_BUTTON_TEXT, BUTTON_COLOR,
                                                       top_left_coordinates=MM3_BUTTON_TOP_LEFT)
        main_text_format1 = pygame.Rect(
            MM_TEXT1_RECT_X, MM_TEXT1_RECT_Y,
            MM_TEXT1_RECT_WIDTH, MM_TEXT1_RECT_HEIGHT
        )
        main_text_format2 = pygame.Rect(
            MM_TEXT2_RECT_X, MM_TEXT2_RECT_Y,
            MM_TEXT2_RECT_WIDTH, MM_TEXT2_RECT_HEIGHT
        )

        mm_text1 = screen_displays.Text(
            TITLE, main_text_format1, MM_TEXT1_TOP_LEFT, TITLE_FONT
        )
        mm_text2 = screen_displays.Text(
            CREDITS, main_text_format2, MM_TEXT2_TOP_LEFT, CAPTION_FONT
        )
        buttons = [main_menu_survey_button, main_menu_search_button, main_menu_quit_button]
        text = [mm_text1, mm_text2]
        screen = screen_displays.Screen(buttons, MAIN_MENU_IMAGE_FILE_PATH, self.screen, text=text)
        return (screen, buttons)

    def _setup_survey_screen(self) -> tuple[screen_displays.Screen, list[screen_displays.Button]]:
        """Sets up survey screen features and return the screen and list of buttons"""
        ss1_rect = pygame.Rect(SS1_RECT_X, SS1_RECT_Y, SS1_RECT_WIDTH, SS1_RECT_HEIGHT)
        survey_menu_button = screen_displays.Button(
            ss1_rect, SS1_BUTTON_TEXT, BUTTON_COLOR,
            top_left_coordinates=SS1_BUTTON_TOP_LEFT
        )

        ss2_rect = pygame.Rect(SS2_RECT_X, SS2_RECT_Y, SS2_RECT_WIDTH, SS2_RECT_HEIGHT)
        survey_submit_button = screen_displays.Button(
            ss2_rect, SS2_BUTTON_TEXT, SUBMIT_COLOR,
            top_left_coordinates=SS2_BUTTON_TOP_LEFT
        )

        ss3_rect = pygame.Rect(SS3_RECT_X, SS3_RECT_Y, SS3_RECT_WIDTH, SS3_RECT_HEIGHT)
        survey_next_button = screen_displays.Button(
            ss3_rect, SS3_BUTTON_TEXT, SUBMIT_COLOR,
            top_left_coordinates=SS3_BUTTON_TOP_LEFT
        )

        ss4_rect = pygame.Rect(SS4_RECT_X, SS4_RECT_Y, SS4_RECT_WIDTH, SS4_RECT_HEIGHT)
        survey_screen_prev_button = screen_displays.Button(
            ss4_rect, SS4_BUTTON_TEXT, SUBMIT_COLOR,
            top_left_coordinates=SS4_BUTTON_TOP_LEFT
        )
        survey_text1_rect = pygame.Rect(SS_TEXT1_RECT_X, SS_TEXT1_RECT_Y, SS_TEXT1_RECT_WIDTH, SS_TEXT1_RECT_HEIGHT)
        survey_text2_rect = pygame.Rect(SS_TEXT2_RECT_X, SS_TEXT2_RECT_Y, SS_TEXT2_RECT_WIDTH, SS_TEXT2_RECT_HEIGHT)
        survey_text3_rect = pygame.Rect(SS_TEXT3_RECT_X, SS_TEXT3_RECT_Y, SS_TEXT3_RECT_WIDTH, SS_TEXT3_RECT_HEIGHT)
        survey_text4_rect = pygame.Rect(SS_TEXT4_RECT_X, SS_TEXT4_RECT_Y, SS_TEXT4_RECT_W, SS_TEXT4_RECT_H)

        survey_text1 = screen_displays.Text(SS_Q1_TEXT, survey_text1_rect, SS_TEXT1_TOP_LEFT, FONT_SIZE)
        survey_text2 = screen_displays.Text(SS_Q2_TEXT, survey_text2_rect, SS_TEXT2_TOP_LEFT, FONT_SIZE)
        survey_text3 = screen_displays.Text(SS_Q3_TEXT, survey_text3_rect, SS_TEXT3_TOP_LEFT, FONT_SIZE)
        survey_text4 = screen_displays.Text(SS_Q4_TEXT, survey_text4_rect, SS_TEXT4_TOP_LEFT, FONT_SIZE)

        survey_textbox1_rect = pygame.Rect(SS_TB1_RECT_X, SS_TB1_RECT_Y, SS_TB1_RECT_W, SS_TB1_RECT_H)
        survey_textbox2_rect = pygame.Rect(SS_TB2_RECT_X, SS_TB2_RECT_Y, SS_TB2_RECT_W, SS_TB2_RECT_H)
        survey_textbox3_rect = pygame.Rect(SS_TB3_RECT_X, SS_TB3_RECT_Y, SS_TB3_RECT_W, SS_TB3_RECT_H)
        survey_textbox4_rect = pygame.Rect(SS_TB4_RECT_X, SS_TB4_RECT_Y, SS_TB4_RECT_W, SS_TB4_RECT_H)

        survey_textbox1 = screen_displays.TextBox(survey_textbox1_rect, SS_TB1_TOP_LEFT, SS_TB1_LIMIT)
        survey_textbox2 = screen_displays.TextBox(survey_textbox2_rect, SS_TB2_TOP_LEFT, SS_TB2_LIMIT)
        survey_textbox3 = screen_displays.TextBox(survey_textbox3_rect, SS_TB3_TOP_LEFT, SS_TB3_LIMIT)
        survey_textbox4 = screen_displays.TextBox(survey_textbox4_rect, SS_TB4_TOP_LEFT, SS_TB4_LIMIT)

        buttons = [survey_menu_button, survey_submit_button, survey_next_button, survey_screen_prev_button]
        textboxes = [survey_textbox1, survey_textbox2, survey_textbox3, survey_textbox4]
        text = [survey_text1, survey_text2, survey_text3, survey_text4]
        screen = screen_displays.Screen(buttons, SURVEY_IMAGE_FILE_PATH, self.screen,
                                        textboxes=textboxes,
                                        text=text
                                        )
        return (screen, buttons)

    def _setup_search_screen(self) -> tuple[screen_displays.Screen, list[screen_displays.Button]]:
        """Sets up search screen features and return the screen and list of buttons"""
        si1_rect = pygame.Rect(SI1_RECT_X, SI1_RECT_Y, SI1_RECT_WIDTH, SI1_RECT_HEIGHT)
        search_menu_button = screen_displays.Button(
            si1_rect, SI1_BUTTON_TEXT, BUTTON_COLOR,
            top_left_coordinates=SI1_BUTTON_TOP_LEFT
        )

        si2_rect = pygame.Rect(SI2_RECT_X, SI2_RECT_Y, SI2_RECT_WIDTH, SI2_RECT_HEIGHT)
        search_submit_button = screen_displays.Button(si2_rect, SI2_BUTTON_TEXT, SUBMIT_COLOR,
                                                      top_left_coordinates=SI2_BUTTON_TOP_LEFT)

        si3_rect = pygame.Rect(SI3_RECT_X, SI3_RECT_Y, SI3_RECT_WIDTH, SI3_RECT_HEIGHT)
        search_next_button = screen_displays.Button(
            si3_rect, SI3_BUTTON_TEXT, SUBMIT_COLOR,
            top_left_coordinates=SI3_BUTTON_TOP_LEFT
        )

        si4_rect = pygame.Rect(SI4_RECT_X, SI4_RECT_Y, SI4_RECT_WIDTH, SI4_RECT_HEIGHT)
        search_prev_button = screen_displays.Button(
            si4_rect, SI4_BUTTON_TEXT, SUBMIT_COLOR,
            top_left_coordinates=SI4_BUTTON_TOP_LEFT
        )

        search_text1_rect = pygame.Rect(SI_TEXT1_RECT_X, SI_TEXT1_RECT_Y, SI_TEXT1_RECT_WIDTH, SI_TEXT1_RECT_HEIGHT)
        search_text2_rect = pygame.Rect(SI_TEXT2_RECT_X, SI_TEXT2_RECT_Y, SI_TEXT2_RECT_WIDTH, SI_TEXT2_RECT_HEIGHT)
        search_text3_rect = pygame.Rect(SI_TEXT3_RECT_X, SI_TEXT3_RECT_Y, SI_TEXT3_RECT_WIDTH, SI_TEXT3_RECT_HEIGHT)

        search_text1 = screen_displays.Text(SI_FILTER1_TEXT, search_text1_rect, SI_TEXT1_TOP_LEFT, FONT_SIZE)
        search_text2 = screen_displays.Text(SI_FILTER2_TEXT, search_text2_rect, SI_TEXT2_TOP_LEFT, FONT_SIZE)
        search_text3 = screen_displays.Text(SI_FILTER3_TEXT, search_text3_rect, SI_TEXT3_TOP_LEFT, FONT_SIZE)

        search_textbox1_rect = pygame.Rect(SI_TB1_RECT_X, SI_TB1_RECT_Y, SI_TB1_RECT_WIDTH, SI_TB1_RECT_HEIGHT)
        search_textbox2_rect = pygame.Rect(SI_TB2_RECT_X, SI_TB2_RECT_Y, SI_TB2_RECT_WIDTH, SI_TB2_RECT_HEIGHT)
        search_textbox3_rect = pygame.Rect(SI_TB3_RECT_X, SI_TB3_RECT_Y, SI_TB3_RECT_WIDTH, SI_TB3_RECT_HEIGHT)

        search_textbox1 = screen_displays.TextBox(search_textbox1_rect, SI_TB1_TOP_LEFT, SI_TB1_LIMIT)
        search_textbox2 = screen_displays.TextBox(search_textbox2_rect, SI_TB2_TOP_LEFT, SI_TB2_LIMIT)
        search_textbox3 = screen_displays.TextBox(search_textbox3_rect, SI_TB3_TOP_LEFT, SI_TB3_LIMIT)

        buttons = [search_menu_button, search_submit_button, search_next_button, search_prev_button]
        text = [search_text1, search_text2, search_text3]
        textboxes = [search_textbox1, search_textbox2, search_textbox3]
        screen = screen_displays.Screen(buttons, SEARCH_IMAGE_FILE_PATH, self.screen,
                                        textboxes=textboxes,
                                        text=text
                                        )
        return (screen, buttons)

    def _setup_buttons_and_processors(self, main_menu_screen: screen_displays.Screen,
                                      survey_screen: screen_displays.Screen,
                                      search_screen: screen_displays.Screen,
                                      mm_buttons: list,
                                      ss_buttons: list,
                                      si_buttons: list) -> None:
        """Sets up the processors and button actions.
           Preconditions:
            - the button order is in the correct order for the screens (so exit button does exit action, etc)
            - there are the exact same number of buttons as actions per screen
        """
        self.current_screen = screen_displays.ScreenOrganizer(main_menu_screen)
        main_menu_processor = processing.MainMenuProcessor(self.current_screen, search_screen, survey_screen,
                                                           main_menu_screen)
        survey_screen_processor = processing.SurveyProcessor(self.current_screen, survey_screen, main_menu_screen,
                                                             self.recipe_graph)

        search_screen_processor = processing.SearchProcessor(self.current_screen, search_screen, main_menu_screen,
                                                             self.recipe_tree)

        mm_buttons[0].action = main_menu_processor.go_to_survey
        mm_buttons[1].action = main_menu_processor.go_to_search
        mm_buttons[2].action = main_menu_processor.exit_app

        ss_buttons[0].action = survey_screen_processor.go_to_main_menu
        ss_buttons[1].action = survey_screen_processor.give_recommendation
        ss_buttons[2].action = survey_screen_processor.go_right
        ss_buttons[3].action = survey_screen_processor.go_left

        si_buttons[0].action = search_screen_processor.go_to_main_menu
        si_buttons[1].action = search_screen_processor.search
        si_buttons[2].action = search_screen_processor.go_right
        si_buttons[3].action = search_screen_processor.go_left

    def run(self) -> None:
        """The main area where the app runs"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                self.current_screen.curr_screen.update_all_buttons(event)
                self.current_screen.curr_screen.update_all_textboxes(event)

            self.current_screen.curr_screen.draw_screen()

        pygame.quit()
        sys.exit()

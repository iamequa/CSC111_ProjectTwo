import sys
import pygame

import GUI.screen_displays as screen_displays
import Processing.processing as processing
import Data.file_reader as file_reader
from Data import vertex
from Data.recipe_graph import RecipeGraph
from Data.recipe_tree import NAME_TOKENS,RecipeTree
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
        self._setup_ui()
        self._setup_processors()

    def _setup_ui(self) -> None:
        # -------------------- BUTTONS --------------------

        # Main menu
        mm1_rect = pygame.Rect(
            MM1_TEXT_RECT_X_COORDINATES,
            MM1_TEXT_RECT_Y_COORDINATES,
            MM1_TEXT_RECT_X_DIMENSIONS,
            MM1_TEXT_RECT_Y_DIMENSIONS
        )
        self.mm1_button = screen_displays.Button(
            mm1_rect, MM1_BUTTON_TEXT, BUTTON_COLOR,
            top_left_coordinates=MM1_BUTTON_TOP_LEFT_COORDINATES
        )

        mm2_rect = pygame.Rect(
            MM2_TEXT_RECT_X_COORDINATES,
            MM2_TEXT_RECT_Y_COORDINATES,
            MM2_TEXT_RECT_X_DIMENSIONS,
            MM2_TEXT_RECT_Y_DIMENSIONS
        )
        self.mm2_button = screen_displays.Button(
            mm2_rect, MM2_BUTTON_TEXT, BUTTON_COLOR,
            top_left_coordinates=MM2_BUTTON_TOP_LEFT_COORDINATES
        )

        mm3_rect = pygame.Rect(
            MM3_TEXT_RECT_X_COORDINATES,
            MM3_TEXT_RECT_Y_COORDINATES,
            MM3_TEXT_RECT_X_DIMENSIONS,
            MM3_TEXT_RECT_Y_DIMENSIONS
        )
        self.mm3_button = screen_displays.Button(
            mm3_rect, MM3_BUTTON_TEXT, BUTTON_COLOR,
            top_left_coordinates=MM3_BUTTON_TOP_LEFT_COORDINATES
        )

        # Algorithm
        as1_rect = pygame.Rect(
            AS1_TEXT_RECT_X_COORDINATES,
            AS1_TEXT_RECT_Y_COORDINATES,
            AS1_TEXT_RECT_X_DIMENSIONS,
            AS1_TEXT_RECT_Y_DIMENSIONS
        )
        self.as1_button = screen_displays.Button(
            as1_rect, AS1_BUTTON_TEXT, BUTTON_COLOR,
            top_left_coordinates=AS1_BUTTON_TOP_LEFT_COORDINATES
        )

        as2_rect = pygame.Rect(
            AS2_TEXT_RECT_X_COORDINATES,
            AS2_TEXT_RECT_Y_COORDINATES,
            AS2_TEXT_RECT_X_DIMENSIONS,
            AS2_TEXT_RECT_Y_DIMENSIONS
        )
        self.as2_button = screen_displays.Button(
            as2_rect, AS2_BUTTON_TEXT, SUBMIT_COLOR,
            top_left_coordinates=AS2_BUTTON_TOP_LEFT_COORDINATES
        )

        as3_rect = pygame.Rect(
            AS3_TEXT_RECT_X_COORDINATES,
            AS3_TEXT_RECT_Y_COORDINATES,
            AS3_TEXT_RECT_X_DIMENSIONS,
            AS3_TEXT_RECT_Y_DIMENSIONS
        )
        self.as3_button = screen_displays.Button(
            as3_rect, AS3_BUTTON_TEXT, SUBMIT_COLOR,
            top_left_coordinates=AS3_BUTTON_TOP_LEFT_COORDINATES
        )

        as4_rect = pygame.Rect(
            AS4_TEXT_RECT_X_COORDINATES,
            AS4_TEXT_RECT_Y_COORDINATES,
            AS4_TEXT_RECT_X_DIMENSIONS,
            AS4_TEXT_RECT_Y_DIMENSIONS
        )
        self.as4_button = screen_displays.Button(
            as4_rect, AS4_BUTTON_TEXT, SUBMIT_COLOR,
            top_left_coordinates=AS4_BUTTON_TOP_LEFT_COORDINATES
        )

        # Search
        si1_rect = pygame.Rect(
            SI1_TEXT_RECT_X_COORDINATES,
            SI1_TEXT_RECT_Y_COORDINATES,
            SI1_TEXT_RECT_X_DIMENSIONS,
            SI1_TEXT_RECT_Y_DIMENSIONS
        )
        self.si1_button = screen_displays.Button(
            si1_rect, SI1_BUTTON_TEXT, BUTTON_COLOR,
            top_left_coordinates=SI1_BUTTON_TOP_LEFT_COORDINATES
        )

        si2_rect = pygame.Rect(
            SI2_TEXT_RECT_X_COORDINATES,
            SI2_TEXT_RECT_Y_COORDINATES,
            SI2_TEXT_RECT_X_DIMENSIONS,
            SI2_TEXT_RECT_Y_DIMENSIONS
        )
        self.si2_button = screen_displays.Button(
            si2_rect, SI2_BUTTON_TEXT, SUBMIT_COLOR,
            top_left_coordinates=SI2_BUTTON_TOP_LEFT_COORDINATES
        )

        si3_rect = pygame.Rect(
            SI3_TEXT_RECT_X_COORDINATES,
            SI3_TEXT_RECT_Y_COORDINATES,
            SI3_TEXT_RECT_X_DIMENSIONS,
            SI3_TEXT_RECT_Y_DIMENSIONS
        )
        self.si3_button = screen_displays.Button(
            si3_rect, SI3_BUTTON_TEXT, SUBMIT_COLOR,
            top_left_coordinates=SI3_BUTTON_TOP_LEFT_COORDINATES
        )

        si4_rect = pygame.Rect(
            SI4_TEXT_RECT_X_COORDINATES,
            SI4_TEXT_RECT_Y_COORDINATES,
            SI4_TEXT_RECT_X_DIMENSIONS,
            SI4_TEXT_RECT_Y_DIMENSIONS
        )
        self.si4_button = screen_displays.Button(
            si4_rect, SI4_BUTTON_TEXT, SUBMIT_COLOR,
            top_left_coordinates=SI4_BUTTON_TOP_LEFT_COORDINATES
        )

        main_menu_screen_buttons = [self.mm1_button, self.mm2_button, self.mm3_button]
        algorithm_screen_buttons = [self.as1_button, self.as2_button, self.as3_button, self.as4_button]
        search_screen_buttons = [self.si1_button, self.si2_button, self.si3_button, self.si4_button]

        main_text_format1 = pygame.Rect(
            MM_TEXT1_RECT_X, MM_TEXT1_RECT_Y,
            MM_TEXT1_RECT_W, MM_TEXT1_RECT_H
        )
        main_text_format2 = pygame.Rect(
            MM_TEXT2_RECT_X, MM_TEXT2_RECT_Y,
            MM_TEXT2_RECT_W, MM_TEXT2_RECT_H
        )

        mm_text1 = screen_displays.Text(
            TITLE, main_text_format1, MM_TEXT1_TOP_LEFT, TITLE_FONT
        )
        mm_text2 = screen_displays.Text(
            CREDITS, main_text_format2, MM_TEXT2_TOP_LEFT, CAPTION_FONT
        )

        main_menu_screen_text = [mm_text1, mm_text2]

        AS_text_format1 = pygame.Rect(
            AS_TEXT1_RECT_X, AS_TEXT1_RECT_Y,
            AS_TEXT1_RECT_W, AS_TEXT1_RECT_H
        )
        AS_text_format2 = pygame.Rect(
            AS_TEXT2_RECT_X, AS_TEXT2_RECT_Y,
            AS_TEXT2_RECT_W, AS_TEXT2_RECT_H
        )
        AS_text_format3 = pygame.Rect(
            AS_TEXT3_RECT_X, AS_TEXT3_RECT_Y,
            AS_TEXT3_RECT_W, AS_TEXT3_RECT_H
        )
        AS_text_format4 = pygame.Rect(
            AS_TEXT4_RECT_X, AS_TEXT4_RECT_Y,
            AS_TEXT4_RECT_W, AS_TEXT4_RECT_H
        )

        AS_text1 = screen_displays.Text(AS_Q1_TEXT, AS_text_format1, AS_TEXT1_TOP_LEFT, FONT_SIZE)
        AS_text2 = screen_displays.Text(AS_Q2_TEXT, AS_text_format2, AS_TEXT2_TOP_LEFT, FONT_SIZE)
        AS_text3 = screen_displays.Text(AS_Q3_TEXT, AS_text_format3, AS_TEXT3_TOP_LEFT, FONT_SIZE)
        AS_text4 = screen_displays.Text(AS_Q4_TEXT, AS_text_format4, AS_TEXT4_TOP_LEFT, FONT_SIZE)

        algorithm_screen_text = [AS_text1, AS_text2, AS_text3, AS_text4]

        SI_text_format1 = pygame.Rect(
            SI_TEXT1_RECT_X, SI_TEXT1_RECT_Y,
            SI_TEXT1_RECT_W, SI_TEXT1_RECT_H
        )
        SI_text_format2 = pygame.Rect(
            SI_TEXT2_RECT_X, SI_TEXT2_RECT_Y,
            SI_TEXT2_RECT_W, SI_TEXT2_RECT_H
        )
        SI_text_format3 = pygame.Rect(
            SI_TEXT3_RECT_X, SI_TEXT3_RECT_Y,
            SI_TEXT3_RECT_W, SI_TEXT3_RECT_H
        )

        SI_text1 = screen_displays.Text(SI_FILTER1_TEXT, SI_text_format1, SI_TEXT1_TOP_LEFT, FONT_SIZE)
        SI_text2 = screen_displays.Text(SI_FILTER2_TEXT, SI_text_format2, SI_TEXT2_TOP_LEFT, FONT_SIZE)
        SI_text3 = screen_displays.Text(SI_FILTER3_TEXT, SI_text_format3, SI_TEXT3_TOP_LEFT, FONT_SIZE)

        search_screen_text = [SI_text1, SI_text2, SI_text3]

        # -------------------- TEXTBOXES --------------------

        AS_textbox_format1 = pygame.Rect(AS_TB1_RECT_X, AS_TB1_RECT_Y, AS_TB1_RECT_W, AS_TB1_RECT_H)
        AS_textbox_format2 = pygame.Rect(AS_TB2_RECT_X, AS_TB2_RECT_Y, AS_TB2_RECT_W, AS_TB2_RECT_H)
        AS_textbox_format3 = pygame.Rect(AS_TB3_RECT_X, AS_TB3_RECT_Y, AS_TB3_RECT_W, AS_TB3_RECT_H)
        AS_textbox_format4 = pygame.Rect(AS_TB4_RECT_X, AS_TB4_RECT_Y, AS_TB4_RECT_W, AS_TB4_RECT_H)

        self.AS_textbox_q1 = screen_displays.TextBox(AS_textbox_format1, AS_TB1_TOP_LEFT, AS_TB1_LIMIT)
        self.AS_textbox_q2 = screen_displays.TextBox(AS_textbox_format2, AS_TB2_TOP_LEFT, AS_TB2_LIMIT)
        self.AS_textbox_q3 = screen_displays.TextBox(AS_textbox_format3, AS_TB3_TOP_LEFT, AS_TB3_LIMIT)
        self.AS_textbox_q4 = screen_displays.TextBox(AS_textbox_format4, AS_TB4_TOP_LEFT, AS_TB4_LIMIT)

        algorithm_screen_textboxes = [
            self.AS_textbox_q1, self.AS_textbox_q2,
            self.AS_textbox_q3, self.AS_textbox_q4
        ]

        SI_textbox_format1 = pygame.Rect(SI_TB1_RECT_X, SI_TB1_RECT_Y, SI_TB1_RECT_W, SI_TB1_RECT_H)
        SI_textbox_format2 = pygame.Rect(SI_TB2_RECT_X, SI_TB2_RECT_Y, SI_TB2_RECT_W, SI_TB2_RECT_H)
        SI_textbox_format3 = pygame.Rect(SI_TB3_RECT_X, SI_TB3_RECT_Y, SI_TB3_RECT_W, SI_TB3_RECT_H)

        self.SI_textbox_q1 = screen_displays.TextBox(SI_textbox_format1, SI_TB1_TOP_LEFT, SI_TB1_LIMIT)
        self.SI_textbox_q2 = screen_displays.TextBox(SI_textbox_format2, SI_TB2_TOP_LEFT, SI_TB2_LIMIT)
        self.SI_textbox_q3 = screen_displays.TextBox(SI_textbox_format3, SI_TB3_TOP_LEFT, SI_TB3_LIMIT)

        search_screen_textboxes = [
            self.SI_textbox_q1,
            self.SI_textbox_q2,
            self.SI_textbox_q3
        ]

        # -------------------- SCREENS --------------------

        self.main_menu_screen = screen_displays.Screen(
            main_menu_screen_buttons,
            MAIN_MENU_IMAGE_FILE_PATH,
            self.screen,
            text=main_menu_screen_text
        )

        self.algorithm_screen = screen_displays.Screen(
            algorithm_screen_buttons,
            ALGORITHM_IMAGE_FILE_PATH,
            self.screen,
            textboxes=algorithm_screen_textboxes,
            text=algorithm_screen_text
        )

        self.search_screen = screen_displays.Screen(
            search_screen_buttons,
            SEARCH_IMAGE_FILE_PATH,
            self.screen,
            textboxes=search_screen_textboxes,
            text=search_screen_text
        )

        self.current_screen = screen_displays.ScreenOrganizer(self.main_menu_screen)

    def _setup_processors(self) -> None:
        self.main_menu_processor = processing.MainMenuProcessor(
            self.current_screen,
            self.search_screen,
            self.algorithm_screen,
            self.main_menu_screen
        )

        self.algorithm_screen_processor = processing.AlgorithmProcessor(
            self.current_screen,
            self.algorithm_screen,
            self.main_menu_screen,
            self.recipe_graph
        )

        self.search_screen_processor = processing.SearchProcessor(
            self.current_screen,
            self.search_screen,
            self.main_menu_screen,
            self.recipe_tree
        )

        # Assign button actions
        self.mm1_button.action = self.main_menu_processor.go_to_survey
        self.mm2_button.action = self.main_menu_processor.go_to_search
        self.mm3_button.action = self.main_menu_processor.exit_app

        self.as1_button.action = self.algorithm_screen_processor.go_to_main_menu
        self.as2_button.action = self.algorithm_screen_processor.give_recommendation
        self.as3_button.action = self.algorithm_screen_processor.go_right
        self.as4_button.action = self.algorithm_screen_processor.go_left

        self.si1_button.action = self.search_screen_processor.go_to_main_menu
        self.si2_button.action = self.search_screen_processor.search
        self.si3_button.action = self.search_screen_processor.go_right
        self.si4_button.action = self.search_screen_processor.go_left

    def run(self) -> None:
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

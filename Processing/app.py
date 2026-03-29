import sys
import pygame

import GUI.screen_displays as screen_displays
import Processing.processing as processing
import Data.file_reader as file_reader
from Data import vertex
from Data.recipe_graph import BASE_INDEX, CATEGORIES_INDEX, INGREDIENTS_INDEX, NAME_INDEX, NAME_TOKENS_INDEX, \
    RecipeGraph, STEPS_INDEX, \
    TARGET_INDEX, \
    UID_INDEX
from Data.recipe_tree import NAME_TOKENS, RecipeTree

RECIPES_CSV_PATH = "Data/Datasets/recipes.csv"
IS_RECIPE_CSV = True
PAIRS_CSV_PATH = "Data/Datasets/pairs.csv"
IS_PAIRS_CSV = True

BUTTON_COLOR = (148, 124, 92)
SUBMIT_COLOR = (138, 154, 91)

CAPTION = 'The Ultimate Recipe Index >:)'
X_DIMENSIONS, Y_DIMENSIONS = 1000, 800

MAIN_MENU_IMAGE_FILE_PATH = "GUI/design_features/backgrounds/title.png"
ALGORITHM_IMAGE_FILE_PATH = "GUI/design_features/backgrounds/background.png"
SEARCH_IMAGE_FILE_PATH = "GUI/design_features/backgrounds/background.png"

TITLE_FONT = 50
CAPTION_FONT = 20
FONT_SIZE = 25

TITLE = 'THE ULTIMATE RECIPE INDEX!!!'
CREDITS = 'By Arwa, Ema, Mostafa, and Noon!!'


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
        mm1_rect = pygame.Rect(500, 500, 150, 45)
        self.mm1_button = screen_displays.Button(
            mm1_rect, "Survey", BUTTON_COLOR, None, (400, 590)
        )

        mm2_rect = pygame.Rect(500, 600, 150, 45)
        self.mm2_button = screen_displays.Button(
            mm2_rect, "Search", BUTTON_COLOR, None, (400, 690)
        )

        # Algorithm
        as1_rect = pygame.Rect(50, 50, 160, 45)
        self.as1_button = screen_displays.Button(
            as1_rect, "Return to Menu", BUTTON_COLOR, None, (0, 0)
        )

        as2_rect = pygame.Rect(100, 100, 150, 45)
        self.as2_button = screen_displays.Button(
            as2_rect, "Submit", SUBMIT_COLOR, None, (700, 700)
        )

        # Search
        si1_rect = pygame.Rect(50, 50, 160, 45)
        self.si1_button = screen_displays.Button(
            si1_rect, "Return to Menu", BUTTON_COLOR, None, (0, 0)
        )

        si2_rect = pygame.Rect(100, 100, 150, 45)
        self.si2_button = screen_displays.Button(
            si2_rect, "Submit", SUBMIT_COLOR, None, (700, 600)
        )

        main_menu_screen_buttons = [self.mm1_button, self.mm2_button]
        algorithm_screen_buttons = [self.as1_button, self.as2_button]
        search_screen_buttons = [self.si1_button, self.si2_button]

        # -------------------- TEXT --------------------

        main_text_format1 = pygame.Rect(500, 500, 450, 60)
        main_text_format2 = pygame.Rect(500, 500, 450, 60)

        mm_text1 = screen_displays.Text(
            TITLE, main_text_format1, (200, 75), TITLE_FONT
        )
        mm_text2 = screen_displays.Text(
            CREDITS, main_text_format2, (250, 150), CAPTION_FONT
        )

        main_menu_screen_text = [mm_text1, mm_text2]

        text_format1 = pygame.Rect(500, 500, 450, 60)
        text_format2 = pygame.Rect(500, 500, 450, 60)
        text_format3 = pygame.Rect(500, 500, 450, 60)
        text_format4 = pygame.Rect(500, 500, 450, 60)

        question1 = '1. List Dietary Restrictions (Max 5). Enter 1 category at a time.'
        question2 = '2. List ingredients you want to use (Max 5). Enter 1 ingredient at a time.'
        question3 = '3. List any allergies (Max 5). Enter 1 ingredient to at a time.'
        question4 = '(Optional) List one type of recipe you want to make.'

        text1 = screen_displays.Text(question1, text_format1, (50, 50), FONT_SIZE)
        text2 = screen_displays.Text(question2, text_format2, (50, 170), FONT_SIZE)
        text3 = screen_displays.Text(question3, text_format3, (50, 290), FONT_SIZE)
        text4 = screen_displays.Text(question4, text_format4, (50, 410), FONT_SIZE)

        algorithm_screen_text = [text1, text2, text3, text4]

        # -------------------- TEXTBOXES --------------------

        textbox_format1 = pygame.Rect(500, 500, 450, 40)
        textbox_format2 = pygame.Rect(500, 500, 450, 40)
        textbox_format3 = pygame.Rect(500, 500, 450, 40)
        textbox_format4 = pygame.Rect(500, 500, 450, 40)

        self.textbox_q1 = screen_displays.TextBox(textbox_format1, (50, 100), 5)
        self.textbox_q2 = screen_displays.TextBox(textbox_format2, (50, 220), 5)
        self.textbox_q3 = screen_displays.TextBox(textbox_format3, (50, 340), 5)
        self.textbox_q4 = screen_displays.TextBox(textbox_format4, (50, 460), 1)

        algorithm_screen_textboxes = [
            self.textbox_q1, self.textbox_q2, self.textbox_q3, self.textbox_q4
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
            self.screen
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
            self.recipe_graph  # replace with RecipeGraph later
        )

        self.search_screen_processor = processing.SearchProcessor(
            self.current_screen,
            self.search_screen,
            self.main_menu_screen,
            self.recipe_tree  # replace with RecipeTree later
        )

        # Assign button actions
        self.mm1_button.action = self.main_menu_processor.go_to_survey
        self.mm2_button.action = self.main_menu_processor.go_to_search

        self.as1_button.action = self.algorithm_screen_processor.go_to_main_menu
        self.as2_button.action = self.algorithm_screen_processor.give_recommendation

        self.si1_button.action = self.search_screen_processor.go_to_main_menu
        self.si2_button.action = self.search_screen_processor.search

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

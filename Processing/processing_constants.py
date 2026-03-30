"""CSC111 Project 2: The Ultimate Recipe Index - Processing Constants

===============================

This Python module contains constants for the processing class in our recipe index app.
"""

# -------------------- STRINGS --------------------

ERROR_MESSAGE = "Either you have not pressed submit or we have found no recipes, sorry!"
NO_FILTER_ERROR = "Please enter at least one filter."
RECIPE_NOT_FOUND_ERROR = "Recipe not found."
NO_ALTERNATIVES_ERROR = "No alternatives found."
NO_RECIPES_FOUND_ERROR = "No recipes found."

INGREDIENTS_LABEL = "\nIngredients: "
CATEGORIES_LABEL = "\nCategories: "

# -------------------- TEXT FORMATTING --------------------

NEWLINE = "\n"
EMPTY_STR = ""

# -------------------- ALGORITHM SCREEN DISPLAY --------------------

AS_ERROR_RECT_X = 0
AS_ERROR_RECT_Y = 0
AS_ERROR_RECT_W = 550
AS_ERROR_RECT_H = 500
AS_ERROR_TOP_LEFT = (50, 550)
AS_ERROR_FONT_SIZE = 30

AS_RECIPE_RECT_X = 0
AS_RECIPE_RECT_Y = 0
AS_RECIPE_RECT_W = 550
AS_RECIPE_RECT_H = 500
AS_RECIPE_TOP_LEFT = (50, 520)
AS_RECIPE_FONT_SIZE = 20

# -------------------- SEARCH SCREEN DISPLAY --------------------

SI_ERROR_RECT_X = 0
SI_ERROR_RECT_Y = 0
SI_ERROR_RECT_W = 400
SI_ERROR_RECT_H = 500
SI_ERROR_TOP_LEFT = (50, 200)
SI_ERROR_FONT_SIZE = 25

SI_RECIPE_RECT_X = 0
SI_RECIPE_RECT_Y = 0
SI_RECIPE_RECT_W = 550
SI_RECIPE_RECT_H = 300
SI_RECIPE_TOP_LEFT_X = 50
SI_RECIPE_TOP_LEFT_Y = 200
SI_RECIPE_FONT_SIZE = 20

# -------------------- DEFAULT VALUES --------------------

START_INDEX = 0

# -------------------- ALGORITHM INPUT INDICES --------------------

AS_DIETARY_INDEX = 0
AS_INGREDIENTS_INDEX = 1
AS_ALLERGIES_INDEX = 2
AS_RECIPE_NAME_INDEX = 3

# -------------------- SEARCH INPUT INDICES --------------------

SI_INGREDIENTS_INDEX = 0
SI_CATEGORIES_INDEX = 1
SI_RECIPE_NAME_INDEX = 2
SI_RECIPE_FIRST_INPUT_INDEX = 0

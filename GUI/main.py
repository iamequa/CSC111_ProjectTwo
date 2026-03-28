import pygame
import sys
import screen_displays

pygame.init()
pygame.display.set_caption('The Ultimate Recipe Index >:)')
# INITILIAZERS (Filepath) AND CONSTANTS
screen = pygame.display.set_mode((1000, 1000))
main_menu_image_file_path = "design_features/backgrounds/title.png"
algorithm_image_file_path = "design_features/backgrounds/background.png"
search_image_file_path = "design_features/backgrounds/background.png"
BUTTON_COLOR = (148, 124, 92)
SUBMIT_COLOR = (138, 154, 91)
TITLE_FONT = 50
CAPTION_FONT = 20
FONT_SIZE = 30
TITLE = 'THE ULTIMATE RECIPE INDEX!!!'
CREDITS = 'By Arwa, Ema, Mostafa, and Noon!!'
# ------------------------------------- BUTTONS (SORTED BY SCREEN) --------------------------------------------------
# MAIN MENU BUTTONS
MM1_rect = pygame.Rect(500, 500, 200, 60)
MM1_button = screen_displays.Button(MM1_rect, "Survey", BUTTON_COLOR,
                                    lambda: screen_displays.proceed_to_algorithm(algorithm_screen, current_screen),
                                    (400, 640))
MM2_rect = pygame.Rect(500, 600, 200, 60)
MM2_button = screen_displays.Button(MM2_rect, "Search", BUTTON_COLOR,
                                    lambda: screen_displays.proceed_to_graph(search_image_screen,
                                                                             current_screen), (400, 740))

# ALGORITHM SCREEN BUTTONS
AS1_rect = pygame.Rect(50, 50, 200, 60)
AS1_button = screen_displays.Button(AS1_rect, "Return to Menu", BUTTON_COLOR,
                                    lambda: screen_displays.proceed_to_menu(main_menu_screen, current_screen),
                                    (0, 0))
AS2_rect = pygame.Rect(100, 100, 200, 60)
AS2_button = screen_displays.Button(AS2_rect, "Submit", SUBMIT_COLOR,
                                    lambda: screen_displays.store_all_answers(textbox_q1, textbox_q2,
                                                                              textbox_q3, textbox_q4,
                                                                              current_screen.curr_screen),
                                    (700, 700))

# SEARCH IMAGE SCREEN BUTTONS
SI1_rect = pygame.Rect(50, 50, 200, 60)
SI1_button = screen_displays.Button(SI1_rect, "Return to Menu", BUTTON_COLOR,
                                    lambda: screen_displays.proceed_to_menu(main_menu_screen, current_screen),
                                    (0, 0))
# ALL SCREEN BUTTONS
main_menu_screen_buttons = [MM1_button, MM2_button]
algorithm_screen_buttons = [AS1_button, AS2_button]
search_image_screen_buttons = [SI1_button]

# ------------------------------------------- ALL TEXT (SORTED BY SCREEN) ---------------------------------------------
# MAIN MENU TEXT
main_text_format1 = pygame.Rect(500, 500, 450, 60)
main_text_format2 = pygame.Rect(500, 500, 450, 60)
MM_text1 = screen_displays.Text(TITLE, main_text_format1, (200, 75), TITLE_FONT)
MM_text2 = screen_displays.Text(CREDITS, main_text_format2, (250, 150), CAPTION_FONT)

# ALGORITHM SCREEN TEXT
text_format1 = pygame.Rect(500, 500, 450, 60)
text_format2 = pygame.Rect(500, 500, 450, 60)
text_format3 = pygame.Rect(500, 500, 450, 60)
text_format4 = pygame.Rect(500, 500, 450, 60)
question1 = '1. List Dietary Restrictions (Max 5). Enter 1 ingredient at a time.'
question2 = '2. List ingredients you want to use (Max 5). Enter 1 ingredient at a time.'
question3 = '3. List any allergies (Max 5). Enter 1 allergy at a time.'
question4 = '(Optional) List one type of recipe you want to make.'
text1 = screen_displays.Text(question1, text_format1, (50, 100), FONT_SIZE)
text2 = screen_displays.Text(question2, text_format2, (50, 300), FONT_SIZE)
text3 = screen_displays.Text(question3, text_format3, (50, 500), FONT_SIZE)
text4 = screen_displays.Text(question4, text_format4, (50, 700), FONT_SIZE)

# SCREEN TEXTS
main_menu_screen_text = [MM_text1, MM_text2]
algorithm_screen_text = [text1, text2, text3, text4]

# ----------------------------------- TEXTBOXES (SORTED BY SCREEN) ---------------------------------------------
# ALGORITHM TEXTBOXES
textbox_format1 = pygame.Rect(500, 500, 450, 60)
textbox_format2 = pygame.Rect(500, 500, 450, 60)
textbox_format3 = pygame.Rect(500, 500, 450, 60)
textbox_format4 = pygame.Rect(500, 500, 450, 60)
textbox_q1 = screen_displays.TextBox(textbox_format1, (50, 150), 5)
textbox_q2 = screen_displays.TextBox(textbox_format2, (50, 350), 5)
textbox_q3 = screen_displays.TextBox(textbox_format3, (50, 550), 5)
textbox_q4 = screen_displays.TextBox(textbox_format4, (50, 750), 1)

# SCREEN TEXTBOXES
algorithm_screen_textboxes = [textbox_q1, textbox_q2, textbox_q3, textbox_q4]

# -------------------------------------- SCREENS -----------------------------------------------------------
main_menu_screen = screen_displays.Screen(main_menu_screen_buttons, main_menu_image_file_path, screen,
                                          text=main_menu_screen_text)
algorithm_screen = screen_displays.Screen(algorithm_screen_buttons, algorithm_image_file_path, screen,
                                          algorithm_screen_textboxes, algorithm_screen_text)
search_image_screen = screen_displays.Screen(search_image_screen_buttons, search_image_file_path, screen)
current_screen = screen_displays.ScreenOrganizer(main_menu_screen)


running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        current_screen.curr_screen.update_all_buttons(event)
        current_screen.curr_screen.update_all_textboxes(event)
    current_screen.curr_screen.draw_screen()
    pygame.display.flip()

pygame.quit()
sys.exit()

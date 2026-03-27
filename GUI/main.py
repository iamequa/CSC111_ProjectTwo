import pygame
import sys
import screen_displays

pygame.init()
# INITILIAZERS (File Path)
screen = pygame.display.set_mode((1000, 1000))
main_menu_image_file_path = "images/white.jpg"
algorithm_image_file_path = "images/white.jpg"
search_image_file_path = "images/blue.jpeg"
text_not_done = False
BUTTON_COLOR = (148, 124, 92)
SUBMIT_COLOR = (138, 154, 91)
# SCREENS
main_menu_screen = screen_displays.Screen([], main_menu_image_file_path, screen)
algorithm_screen = screen_displays.Screen([], algorithm_image_file_path, screen)
search_image_screen = screen_displays.Screen([], search_image_file_path, screen)
current_screen = screen_displays.ScreenOrganizer(main_menu_screen)

# Main menu buttons
MM1_rect = pygame.Rect(500, 500, 200, 60)

MM1_button = screen_displays.Button(MM1_rect, "Survey", BUTTON_COLOR,
                                    lambda: screen_displays.proceed_to_algorithm(algorithm_screen, current_screen),
                                    (400, 540))
MM2_rect = pygame.Rect(500, 600, 200, 60)
MM2_button = screen_displays.Button(MM2_rect, "Search", BUTTON_COLOR,
                                    lambda: screen_displays.proceed_to_graph(search_image_screen,
                                                                             current_screen), (400, 640))
# Algorithm Screen buttons
AS1_rect = pygame.Rect(50, 50, 200, 60)
AS1_button = screen_displays.Button(AS1_rect, "Return to Menu", BUTTON_COLOR,
                                    lambda: screen_displays.proceed_to_menu(main_menu_screen, current_screen),
                                    (0, 0))
AS2_rect = pygame.Rect(100, 100, 200, 60)
AS2_button = screen_displays.Button(AS2_rect, "Submit", SUBMIT_COLOR,
                                    lambda: screen_displays.store_all_answers(textbox_q1, textbox_q2,
                                                                              textbox_q3, textbox_q4),
                                    (700, 700))
# Search Image Screen buttons
SI1_rect = pygame.Rect(50, 50, 200, 60)
SI1_button = screen_displays.Button(SI1_rect, "Return to Menu", BUTTON_COLOR,
                                    lambda: screen_displays.proceed_to_menu(main_menu_screen, current_screen),
                                    (0, 0))
# Updating screen buttons
main_menu_screen.buttons = [MM1_button, MM2_button]
algorithm_screen.buttons = [AS1_button, AS2_button]
search_image_screen.buttons = [SI1_button]

# Text for the algorithm screen
text_format2 = None

# Textboxes for algorithm screen
textbox_format1 = pygame.Rect(500, 500, 450, 60)
textbox_format2 = pygame.Rect(500, 500, 450, 60)
textbox_format3 = pygame.Rect(500, 500, 450, 60)
textbox_format4 = pygame.Rect(500, 500, 450, 60)
textbox_q1 = screen_displays.TextBox(textbox_format1, (50, 150), 5)
textbox_q2 = screen_displays.TextBox(textbox_format2, (50, 350), 5)
textbox_q3 = screen_displays.TextBox(textbox_format3, (50, 550), 5)
textbox_q4 = screen_displays.TextBox(textbox_format3, (50, 750), 5)
algorithm_screen.textboxes = [textbox_q1, textbox_q2, textbox_q3, textbox_q4]

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

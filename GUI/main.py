import pygame
import sys
import screen_displays

pygame.init()
# INITILIAZERS (File Path)
screen = pygame.display.set_mode((1000, 1000))
main_menu_image_file_path = "images/white.jpg"
algorithm_image_file_path = "images/white.jpg"
search_image_file_path = "images/blue.jpeg"

# SCREENS
main_menu_screen = screen_displays.Screen([], main_menu_image_file_path, screen)
algorithm_screen = screen_displays.Screen([], algorithm_image_file_path, screen)
search_image_screen = screen_displays.Screen([], search_image_file_path, screen)
current_screen = screen_displays.ScreenOrganizer(main_menu_screen)

# Main menu buttons
pa_rect = pygame.Rect(500, 500, 200, 60)
pa_color = (148, 124, 92)
pa_button = screen_displays.Button(pa_rect, "Survey", pa_color,
                                   lambda: screen_displays.proceed_to_algorithm(algorithm_screen, current_screen),
                                   (400, 540))
si_rect = pygame.Rect(500, 600, 200, 60)
si_color = (148, 124, 92)
si_button = screen_displays.Button(si_rect, "Search", pa_color,
                                   lambda: screen_displays.proceed_to_graph(search_image_screen,
                                                                            current_screen), (400, 640))
# Algorithm Screen buttons
mm_rect = pygame.Rect(50, 50, 200, 60)
mm_color = (148, 124, 92)
mm_button = screen_displays.Button(mm_rect, "Return to Menu", pa_color,
                                   lambda: screen_displays.proceed_to_menu(main_menu_screen, current_screen),
                                   (0, 0))
# Updating screen buttons
main_menu_screen.buttons = [pa_button, si_button]
algorithm_screen.buttons = [mm_button]
search_image_screen.buttons = [mm_button]

# Textboxes for search screen
textbox_format = pygame.Rect(50, 50, 400, 60)
algorithm_screen.textboxes = [screen_displays.TextBox(textbox_format, (50,250))]


running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if current_screen.curr_screen == algorithm_screen:
            algorithm_screen.draw_screen()
            current_screen.curr_screen.update_all_textboxes(event)
        if current_screen.curr_screen.screen == search_image_screen:
            search_image_screen.draw_screen()
        if current_screen.curr_screen.screen == main_menu_screen:
            main_menu_screen.draw_screen()
        current_screen.curr_screen.update_all_buttons(event)
    current_screen.curr_screen.draw_screen()
    pygame.display.flip()

pygame.quit()
sys.exit()

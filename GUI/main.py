import pygame
import sys
import screen_displays

pygame.init()
# INITILIAZERS (File Path)
screen = pygame.display.set_mode((1000, 1000))
main_menu_image_file_path = "images/white.jpg"
algorithm_image_file_path = "images/white.jpg"
search_image_file_path = "images/blue.jpeg"

#SCREENS
main_menu_screen = screen_displays.Screen([], main_menu_image_file_path, screen)
algorithm_screen = screen_displays.Screen([], algorithm_image_file_path, screen)
search_image_screen = screen_displays.Screen([], search_image_file_path, screen)
current_screen = screen_displays.ScreenOrganizer(main_menu_screen)
# Main menu buttons
pa_rect = pygame.Rect(500, 500, 100, 60)
pa_color = (148, 124, 92)
pa_button = screen_displays.Button(pa_rect, "Survey", pa_color,
                                   lambda: screen_displays.proceed_to_algorithm(algorithm_screen, current_screen))
si_rect = pygame.Rect(500, 700, 100, 60)
si_color = (148, 124, 92)
si_button = screen_displays.Button(pa_rect, "Survey", pa_color,
                                   lambda: screen_displays.proceed_to_graph(search_image_screen, current_screen))

# Main menu screen
main_menu_screen.buttons = [pa_button, si_button]
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        current_screen.screen.update_all_buttons(event)
    current_screen.screen.draw_screen()

    pygame.display.flip()
pygame.quit()
sys.exit()

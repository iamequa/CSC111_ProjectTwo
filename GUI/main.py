import pygame
import sys
import screen_displays

pygame.init()
# INITILIAZERS (File Path)
main_menu_image_file_path = "images/bakery_placeholder.webp"
algorithm_image_file_path = ""
search_image_file_path = ""

# Main meny buttons
pa_rect = pygame.Rect(500, 399, 100, 60)
pa_color = (148, 124, 92)
pa_button = screen_displays.Button(pa_rect, "Survey", pa_color,
                                   screen_displays.proceed_to_algorithm())

si_rect = pygame.Rect(500, 399, 100, 60)

# Main menu screen
main_menu_screen = screen_displays.Screen([pa_button], main_menu_image_file_path)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    pygame.display.flip()
pygame.quit()
sys.exit()

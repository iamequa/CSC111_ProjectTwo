import pygame
from typing import Any, Callable


class Button:
    """Represents the buttons in Python.

    Instance Attributes:
        - rect: size of the button
        - font: the font used for the button
        - color: the color of a button using the RGB color scheme
        - action: the action button needs to perform
        - clicked: determines if person clicked button or not
    """
    rect: pygame.Rect
    text: str
    color: tuple[int, int, int]
    action: Callable[..., None]

    def __init__(self, width: int, length: int, x_coord: int, y_coord: int, text: str, color: tuple[int, int, int],
                 action: Callable[..., None]):
        self.rect = pygame.Rect(x_coord, y_coord, width, length, border_radius=15)
        self.font = pygame.font.SysFont("candara", 12)
        self.text = text
        self.color = color
        self.action = action

    def draw_button(self, surface: pygame.Surface) -> None:
        """Draws the given button on given surface.
        """
        BLACK = (0, 0, 0)
        pygame.draw.rect(surface, self.color, self.rect)
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def perform_event(self, event: pygame.event.Event) -> None:
        """Checks over if event was a click, if click collided with button surface area then perform action
        """
        if self.is_clicked(event):
            self.action()

    def is_clicked(self, event: pygame.event.Event) -> bool:
        """ Returns whether the given event is the user clicking the button.
        """
        mouse_position = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(mouse_position):
                return True
        return False


def proceed_to_graph():
    print("this is to go to data screen")


def rules():
    print("this is for the rules screen")


def proceed_to_algorithm():
    print("this is for the algorithm survey screen")


class Screen:
    """A class that represents a singular screen in Python

    Instance Attributes:
    - screen: this is the actual surface of the pygame window
    - buttons: a list of Buttons that are present on the screen
    - WIDTH: width of the screen
    - HEIGHT: height of the screen
    """

    screen: pygame.Surface
    WIDTH: int
    HEIGHT: int
    buttons: list[Button]
    image_filepath: str

    def __init__(self, buttons: list[Button], image_filepath: str):
        self.WIDTH = 1000
        self.HEIGHT = 1000
        self.buttons = buttons
        self.image_filepath = image_filepath

    def update_all_buttons(self, event: pygame.event.Event) -> None:
        """Checks if all buttons are clicked in self."""
        for button in self.buttons:
            if button.is_clicked(event):
                button.perform_event(event)

    def draw_screen(self) -> None:
        """Draws the screen in pygame with buttons.
        """
        pygame.init()
        pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.image.load(self.image_filepath)
        pygame.transform.scale(self.screen, (self.WIDTH, self.HEIGHT))
        for button in self.buttons:
            button.draw_button(self.screen)
        pygame.display.flip()


class ScreenOrganizer:
    """Manages the current Screen on pygame and updates according to button"""
    curr_screen: Screen

    def __init__(self, screen: Screen = None):
        if screen is None:
            self.screen = None  # set to default screen
        else:
            self.screen = screen

    def switch_screens(self, new_screen: Screen) -> None:
        """Swaps the screen with new_screen and makes it curr_screen"""
        self.curr_screen = new_screen
        self.curr_screen.draw_screen()

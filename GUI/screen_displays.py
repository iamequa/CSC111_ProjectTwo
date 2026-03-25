import pygame
from typing import Any, Callable
from Computation import __init__

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
    top_left_coordinates: tuple[int, int]

    def __init__(self, rect: pygame.Rect, text: str, color: tuple[int, int, int],
                 action: Callable[..., None], top_left_coordinates: tuple[int, int]):
        self.rect = rect
        self.font = pygame.font.SysFont("candara", 30)
        self.text = text
        self.color = color
        self.action = action
        self.top_left_coordinates = top_left_coordinates

    def draw_button(self, surface: pygame.Surface) -> None:
        """Draws the given button on given surface.
        """
        BLACK = (0, 0, 0)
        self.rect.topleft = self.top_left_coordinates
        pygame.draw.rect(surface, self.color, self.rect, border_radius=13)
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def perform_event(self, event: pygame.event.Event) -> None:
        """Checks over if event was a click, if click collided with button surface area then perform action
        """
        print("action performed")
        self.action()

    def is_clicked(self, event: pygame.event.Event) -> bool:
        """ Returns whether the given event is the user clicking the button.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                print("clicked")
                return True
        return False


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

    def __init__(self, buttons: list[Button], image_filepath: str, screen: pygame.Surface):
        self.screen = screen
        self.WIDTH = 1000
        self.HEIGHT = 1000
        self.buttons = buttons
        self.image_filepath = image_filepath
        self.image = pygame.image.load(self.image_filepath)
        self.image = pygame.transform.scale(self.image, (self.WIDTH, self.HEIGHT))

    def update_all_buttons(self, event: pygame.event.Event) -> None:
        """Checks if all buttons are clicked in self."""
        for button in self.buttons:
            if button.is_clicked(event):
                button.perform_event(event)

    def draw_screen(self) -> None:
        """Draws the screen in pygame with buttons.
        """
        self.screen.blit(self.image, (0, 0))
        for button in self.buttons:
            button.draw_button(self.screen)
        pygame.display.flip()


class ScreenOrganizer:
    """Manages the current Screen on pygame and updates according to button"""
    curr_screen: Screen

    def __init__(self, screen: Screen):
        # set to default screen
        self.curr_screen = screen

    def switch_screens(self, new_screen: Screen) -> None:
        """Swaps the screen with new_screen and makes it curr_screen"""
        self.curr_screen = new_screen

class TextBox:
    """A class that represents the textbox values a user inputs."""


def proceed_to_graph(search_screen: Screen, current_screen: ScreenOrganizer) -> None:
    """Switches from current screen to search screen
    """
    current_screen.switch_screens(search_screen)


def proceed_to_algorithm(algorithm_screen: Screen, current_screen: ScreenOrganizer) -> None:
    """Switches from current screen to algorithm screen
    """
    current_screen.switch_screens(algorithm_screen)


def proceed_to_menu(main_screen: Screen, current_screen: ScreenOrganizer) -> None:
    """Switches the screen back to the main screen"""
    current_screen.switch_screens(main_screen)

class SearchBar():
    """
    A class that handles the computations of the search bar and the reuqired events.
    Instance Attributes:
    - search_bar_image: The filepath of graphic associated with the search bar
    - search_bar_textbox: The textbox associated with the search bar
    """
    image: str
    textbox: TextBox
    screen: pygame.Surface

    def __init__(self, image: str, textbox: TextBox, screen: Screen):
        self.image = image
        self.textbox = textbox
        self.screen = screen.screen

    def draw_search_bar(self, coordinates: tuple) -> None:
        """
        Draws a search bar on the coordinates given
        """
        search_bar_graphic = pygame.image.load(self.image)
        self.screen.blit(search_bar_graphic, coordinates)
        self.screen.blit








def return_results(input: str) -> list[str]:
        """
        Returns the results of the search
        """
        data = RecipeFinder(#what tree should be placed here?)
        return data.SearchByName(input)



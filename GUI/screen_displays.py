from __future__ import annotations
import pygame
from typing import Callable, Optional
from Data import vertex
import pygame_gui


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

    def perform_event(self) -> None:
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


class Screen:  # pls add all the private attributes later as a reminder to myself
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
    textboxes: Optional[list[TextBox]] = None

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
                button.perform_event()

    def update_all_textboxes(self, event: pygame.event.Event):
        """Updates every textbox with a working textbook
        """
        if self.textboxes is not None:
            for textbox in self.textboxes:
                textbox.handle_textbox_input(event)

    def draw_screen(self) -> None:
        """Draws the screen in pygame with buttons.
        """
        self.screen.blit(self.image, (0, 0))
        for button in self.buttons:
            button.draw_button(self.screen)
        if self.textboxes is not None:
            for textbox in self.textboxes:
                textbox.draw_textbox(self.screen)
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
    rect: pygame.Rect
    text_inputted: str
    color: tuple[int, int, int]
    top_left_coordinates: tuple[int, int]
    _font: pygame.font.Font

    def __init__(self, rect: pygame.Rect, top_left_coordinates: tuple[int, int]):
        BLACK = (0, 0, 0)
        self.rect = rect
        self.top_left_coordinates = top_left_coordinates
        self.rect.topleft = top_left_coordinates
        self.color = BLACK
        self.font = pygame.font.SysFont("candara", 30)
        self.text_inputted = ''
        self.text_active = False

    def draw_textbox(self, surface: pygame.Surface):
        """ Draws a textbox for user"""
        BLACK = (0, 0, 0)
        text_surf = self.font.render(self.text_inputted, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_textbox_input(self, event: pygame.event.Event) -> None:
        """Takes care of the textbox stuff"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                print('set to true')
                self.text_active = True
            else:
                print('set to false')
                self.text_active = False
        if event.type == pygame.KEYDOWN and self.text_active:
            if event.key == pygame.K_RETURN:
                self.text_active = False
                self._return_text_input()
                self.clear_textbox()
            elif event.key == pygame.K_SPACE:
                self.text_inputted += ' '
            elif event.key == pygame.K_BACKSPACE:
                self.text_inputted = self.text_inputted[:-1]
            else:
                self.text_inputted += event.unicode



    # def can_type(self, text_not_done: bool, event: pygame.event.Event) -> bool:
    #     """Returns if user can still type"""
    #     if not text_not_done:
    #         print(event.pos)
    #         if event.type == pygame.MOUSEBUTTONDOWN:
    #             if self.rect.collidepoint(event.pos):
    #                 print('set to true')
    #                 text_not_done = True
    #     else:
    #         if event.type == pygame.KEYDOWN and text_not_done:
    #             if event.type == pygame.K_RETURN:
    #                 print('set to false')
    #                 text_not_done = False
    #     return text_not_done
    #
    # def handle_textbox_input(self, event: pygame.event.Event, text_not_done: bool) -> None:
    #     """Helper function that will keep track of what the user types and stops inputting once enter key pressed
    #     """
    #     text_not_done = self.can_type(text_not_done, event)
    #     if event.type == pygame.KEYDOWN and text_not_done:
    #         if event.type == pygame.K_BACKSPACE:
    #             self.text_inputted = self.text_inputted[:-1]
    #         elif event.type == pygame.K_SPACE:
    #             self.text_inputted += ' '
    #         elif event.type == pygame.KEYDOWN:
    #             self.text_inputted += event.unicode
    #     if not text_not_done:
    #         self._return_text_input()
    #         self.clear_textbox()
    #
    def _return_text_input(self):
        """Returns what the user inputted in textbox."""
        return self.text_inputted

    def clear_textbox(self):
        """Clears the textbox"""
        self.text_inputted = ''


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


class SearchEngine():
    """
    A class that handles the computations of the search bar and the reuqired events.
    Instance Attributes:
    - image: The filepath of graphic associated with the search bar
    - textbox: The textbox associated with the search bar
    - screen: The screen the SearchEngine operates on
    """
    image: str
    textbox: TextBox
    screen: pygame.Surface

    def __init__(self, image: str,  screen: Screen):
        self.image = image
        self.screen = screen.screen

# not necessarily needed for the class to finish
    def draw_search_bar(self, coordinates: tuple[int, int], textbox_rect: pygame.Rect) -> None:
        """
        Draws a search bar on the coordinates given
        """
        search_bar_graphic = pygame.image.load(self.image)
        self.screen.blit(search_bar_graphic, coordinates)
        self.textbox = TextBox(textbox_rect, coordinates)
        self.textbox.draw_textbox(self.screen)
        print('search bar generated!')

    # TODO: figure out how to scroll and add buttons iteratively fron the return results funtion
    def draw_results_section(self, coordinates: tuple, section_graphic: str) -> None:
        """
        Draws the results section of the search engine.
        """
        section_graphic = pygame.image.load(section_graphic)
        self.screen.blit(section_graphic, coordinates)
        # draw results section
        pygame.display.flip()
        print('results graphics generated')




class ResultsSection():
    """
    A scrollable container that contains links to the recipes that are reccomended by a search/
    """
    rect: pygame.Rect
    manager: pygame_gui.UIManager
    screen: pygame.Surface
    buttons: list[Button]

    def __init__(self, rect: pygame.Rect, manager: pygame_gui.UIManager, screen: pygame.Surface):
        self.screen = screen
        self.manager = manager
        self.container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=rect,
            manager=manager
        )
        self.buttons: list[Button] = []

    def draw_container(self, recipes: list[Recipe]) -> None:
        """
        Draws the container for the results section
        """
        self.buttons = []
        self.buttons = return_results(recipes)

    def return_results(self, recipes: list[Recipe]) -> list[
        Button]:
        """
        Returns the results of the search as a list of buttons
        """
        list_of_buttons = []
        for recipe in recipes:
            # how to update each button attribute?
            button = Button()
            list_of_buttons.append(button)
        return list_of_buttons


class RecipePage(Screen):
    """
    A page associated with each recipe.
    """

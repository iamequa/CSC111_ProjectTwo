from __future__ import annotations
import pygame
from typing import Callable, Optional

from assignments.CSC111_ProjectTwo.Processing.processing import SurveyProcessor


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
        self.action()

    def is_clicked(self, event: pygame.event.Event) -> bool:
        """ Returns whether the given event is the user clicking the button.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
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
    text: Optional[list[Text]] = None

    def __init__(self, buttons: list[Button], image_filepath: str, screen: pygame.Surface,
                 textboxes: Optional[list[TextBox]] = None, text: Optional[list[Text]] = None):
        self.screen = screen
        self.WIDTH = 1000
        self.HEIGHT = 1000
        self.buttons = buttons
        self.image_filepath = image_filepath
        self.image = pygame.image.load(self.image_filepath)
        self.image = pygame.transform.scale(self.image, (self.WIDTH, self.HEIGHT))
        self.textboxes = textboxes
        self.text = text

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
        if self.text is not None:
            for text in self.text:
                text.draw_text(self.screen)
        pygame.display.flip()


class ScreenOrganizer:
    """Manages the current Screen on pygame and updates according to button"""
    curr_screen: Screen

    def __init__(self, screen: Screen):
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
    _processor: SurveyProcessor
    limit: int

    def __init__(self, rect: pygame.Rect, top_left_coordinates: tuple[int, int], limit: int):
        BLACK = (0, 0, 0)
        self.rect = rect
        self.top_left_coordinates = top_left_coordinates
        self.rect.topleft = top_left_coordinates
        self.color = BLACK
        self.font = pygame.font.SysFont("candara", 30)
        self.text_inputted = ''
        self.text_active = False
        self._processor = SurveyProcessor(limit)
        self.enabled = True

    def draw_textbox(self, surface: pygame.Surface):
        """ Draws a textbox for user"""
        BLACK = (0, 0, 0)
        BEIGE = (245, 245, 220)
        text_surf = self.font.render(self.text_inputted, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        pygame.draw.rect(surface, BEIGE, self.rect, 60)
        surface.blit(text_surf, text_rect)

    def handle_textbox_input(self, event: pygame.event.Event) -> None:
        """Takes care of the textbox stuff"""
        MAX_LENGTH = 40
        if self.enabled:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.text_active = True
                else:
                    self.text_active = False
            if event.type == pygame.KEYDOWN and self.text_active:
                if event.key == pygame.K_RETURN:
                    self.text_active = False
                    process = self._processor.process_final_answer(self.text_inputted)
                    if process is not None:
                        self.enabled = False
                    self.clear_textbox()
                elif event.key == pygame.K_SPACE and len(self.text_inputted) < MAX_LENGTH:
                    self.text_inputted += ' '
                elif event.key == pygame.K_BACKSPACE:
                    self.text_inputted = self.text_inputted[:-1]
                else:
                    if len(self.text_inputted) < MAX_LENGTH:
                        self.text_inputted += event.unicode

    def clear_textbox(self) -> None:
        """Clears the textbox"""
        self.text_inputted = ''


class Text:
    """This class represents text on the screen"""
    text: str
    rect: pygame.rect.Rect
    coordinates: tuple[int,int]
    _font: pygame.font.Font

    def __init__(self, text: str, rect: pygame.rect.Rect, coordinates: tuple[int,int]):
        self.rect = rect
        self._font = pygame.font.SysFont("candara", 30)
        self.text = text
        self.rect.topleft = coordinates

    def draw_text(self, surface: pygame.Surface):
        """Draws the text onto the screen"""
        BLACK = (0, 0, 0)
        text_surf = self._font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


def proceed_to_graph(search_screen: Screen, current_screen: ScreenOrganizer) -> None:
    """Switches from current screen to search screen. """
    current_screen.switch_screens(search_screen)


def proceed_to_algorithm(algorithm_screen: Screen, current_screen: ScreenOrganizer) -> None:
    """Switches from current screen to algorithm screen."""
    current_screen.switch_screens(algorithm_screen)


def proceed_to_menu(main_screen: Screen, current_screen: ScreenOrganizer) -> None:
    """Switches the screen back to the main screen"""
    current_screen.switch_screens(main_screen)


def store_all_answers(textbox1: TextBox, textbox2: TextBox, textbox3: TextBox, textbox4: TextBox) -> list | None:
    """Takes all the values stored in each textbox and delivers it.
        Preconditions:
        - textbox1 is the dietary restrictions textbox
        - textbox2 is the ingredients to use textbox
        - textbox3 is the allergies textbox
        - textbox4 is the recommendation textbox
     """
    count = 0
    list_of_inputs = [textbox1.text_inputted, textbox2.text_inputted, textbox3.text_inputted, textbox4.text_inputted]
    for val in list_of_inputs:
        if val.strip().lower() == '':
            count += 1
    if count == 4:
        return None
    else:
        return list_of_inputs




from __future__ import annotations
import pygame
from typing import Callable, Optional

FONT_PATH = "GUI/design_features/font/ShadowsIntoLightTwo-Regular.ttf"


class Button:
    """Represents the buttons in GUI.

    Instance Attributes:
        - rect: size of the button
        - text: the text displayed on button
        - color: the color of a button using the RGB color scheme
        - action: the action button needs to perform
        - top_left_coordinates: the top left coordinates of the button
    Private Instance Attributes:
        - _font: the font used for the button
        - _FONT_COLOR: color of the font
        - _FONT_SIZE
    """
    rect: pygame.Rect
    text: str
    color: tuple[int, int, int]
    action: Optional[Callable[..., None]] = None
    top_left_coordinates: tuple[int, int]
    _FONT_COLOR: tuple[int, int, int]
    _FONT_SIZE: int

    def __init__(self, rect: pygame.Rect, text: str, color: tuple[int, int, int],
                 action: Callable[..., None] | None, top_left_coordinates: tuple[int, int]):
        self.rect = rect
        self._FONT_SIZE = 25
        self._FONT_COLOR = (0, 0, 0)
        self._font = pygame.font.Font(FONT_PATH, self._FONT_SIZE)
        self.text = text
        self.color = color
        self.action = action
        self.top_left_coordinates = top_left_coordinates

    def draw_button(self, surface: pygame.Surface) -> None:
        """Draws Button on given surface."""

        self.rect.topleft = self.top_left_coordinates
        pygame.draw.rect(surface, self.color, self.rect, border_radius=13)
        text_surf = self._font.render(self.text, True, self._FONT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def perform_event(self) -> None:
        """Calls on the buttons action to perform its duty."""
        self.action()

    def is_clicked(self, event: pygame.event.Event) -> bool:
        """ Returns whether the given event is the user clicking the button."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class Screen:
    """A class that represents a singular screen in pygame

       Instance Attributes:
           - screen: the surface the Screen draws on
           - WIDTH: width of the Screen
           - HEIGHT: height of the Screen
           - buttons: list of all Buttons displayed on Screen
           - textboxes: list of all Textboxes displayed on Screen (optional)
           - text: list of all Text displayed on Screen (optional)
       Private Instance Attributes:
           - _image: the image displayed on Screen
           - _default_text: the initial number of Text objects on screen
       """

    screen: pygame.Surface
    WIDTH: int
    HEIGHT: int
    buttons: list[Button]
    image_filepath: str
    textboxes: Optional[list[TextBox]] = None
    text: Optional[list[Text]] = None
    _image: pygame.Surface
    _default_text: int

    def __init__(self, buttons: list[Button], image_filepath: str, screen: pygame.Surface,
                 textboxes: Optional[list[TextBox]] = None, text: Optional[list[Text]] = None):
        self.screen = screen
        self.WIDTH = 1000
        self.HEIGHT = 1000
        self.buttons = buttons
        self.image_filepath = image_filepath
        self._image = pygame.image.load(self.image_filepath)
        self._image = pygame.transform.scale(self._image, (self.WIDTH, self.HEIGHT))
        self.textboxes = textboxes
        self.text = text
        if self.text is not None:
            self._default_text = len(self.text)
        else:
            self._default_text = 0

    def update_all_buttons(self, event: pygame.event.Event) -> None:
        """Checks if any buttons in self were clicked in given event and updates them if clicked."""
        for button in self.buttons:
            if button.is_clicked(event):
                button.perform_event()

    def update_all_textboxes(self, event: pygame.event.Event) -> None:
        """Updates every textbox with given event."""
        if self.textboxes is not None:
            for textbox in self.textboxes:
                textbox.handle_textbox_input(event)

    def draw_screen(self) -> None:
        """Draws the screen in pygame with all features (Text, Textbox, Button if any are present)."""
        self.screen.blit(self._image, (0, 0))
        for button in self.buttons:
            button.draw_button(self.screen)
        if self.textboxes is not None:
            for textbox in self.textboxes:
                textbox.draw_textbox(self.screen)
        if self.text is not None:
            for text in self.text:
                text.draw_text(self.screen)
        pygame.display.flip()

    def refresh_screen(self) -> None:
        """Completely resets screen to initial state. If any text was added to screen, it removes it."""
        for textbox in self.textboxes:
            textbox.refresh_textbox()
        if self.text is not None:
            print(self._default_text)
            for _ in range(len(self.text) - self._default_text):
                text = self.text.pop()
                text.remove_text()

    def get_textbox_inputs(self) -> list[list[str]]:
        """Returns all the text inputted in Textbox"""
        return [textbox.all_text_inputted for textbox in self.textboxes]


class ScreenOrganizer:
    """Manages the current Screen on pygame.
    Instance Attributes:
        - curr_screen: The current screen drawn on pygame.
    """
    curr_screen: Screen

    def __init__(self, screen: Screen):
        self.curr_screen = screen

    def switch_screens(self, new_screen: Screen) -> None:
        """Swaps the screen with new_screen and makes it curr_screen"""
        self.curr_screen = new_screen


class TextBox:
    """A class that represents textboxes on pygame.
     Instance Attributes:
         - rect: the area the of the textbox
         - text_inputted: the text entered by user
         - top_left_coordinates: the top left coordinates of TextBox
         - processor: a TextBoxProcessor that processes the user's entry and stores it
         - limit: maximum number of entries for TextBox
         - all_text_inputted: list of all the entries inputted by user
     Private Instance Attributes:
         - _enabled: bool representing if TextBox is enabled or not
         - _text_active: bool representing if TextBox is active or not
         - _FONT_COLOR: constant representing color of the font
         - _FONT_SIZE: constant representing the size of the font
         - _FONT: the font of the text in Textbox
         - _TEXTBOX_COLOR: constant representing color of TextBox
         - _TEXTBOX_WIDTH: constant representing the width of TextBox
     """
    rect: pygame.Rect
    text_inputted: str
    top_left_coordinates: tuple[int, int]
    limit: int
    _enabled: bool
    _text_active: bool
    _FONT_COLOR: tuple[int, int, int]
    _FONT_SIZE: int
    _FONT: pygame.font.Font
    _TEXTBOX_COLOR: tuple[int, int, int]
    _TEXTBOX_WIDTH: int
    all_text_inputted: list[str]

    def __init__(self, rect: pygame.Rect, top_left_coordinates: tuple[int, int], limit: int):
        self.rect = rect
        self.top_left_coordinates = top_left_coordinates
        self.rect.topleft = top_left_coordinates
        self.limit = limit
        self._FONT_SIZE = 20
        self._FONT_COLOR = (0, 0, 0)
        self._TEXTBOX_COLOR = (245, 245, 220)
        self._TEXTBOX_WIDTH = 45
        self._FONT = pygame.font.Font(FONT_PATH, self._FONT_SIZE)
        self.text_inputted = ''
        self._text_active = False
        self.all_text_inputted = []
        self._enabled = True

    def draw_textbox(self, surface: pygame.Surface) -> None:
        """Draws textbox on given surface."""
        text_surf = self._FONT.render(self.text_inputted, True, self._FONT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        pygame.draw.rect(surface, self._TEXTBOX_COLOR, self.rect, self._TEXTBOX_WIDTH)
        surface.blit(text_surf, text_rect)

    def handle_textbox_input(self, event: pygame.event.Event) -> None:
        """Updates TextBox if enabled and handles given event. Updates textbox if valid entry and does not exceed max
        length, otherwise does nothing."""
        MAX_LENGTH = 40
        if self._enabled:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self._text_active = True
                else:
                    self._text_active = False
            if event.type == pygame.KEYDOWN and self._text_active:
                if event.key == pygame.K_RETURN:
                    self._text_active = False
                    process = self.process_final_answer(self.text_inputted)
                    if process is not None:
                        self._enabled = False
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

    def refresh_textbox(self) -> None:
        """Refreshes and re-enables textbox."""
        self.refresh_answers()
        self.clear_textbox()
        self._enabled = True

    def process_final_answer(self, text_inputted: str):
        """Updates final answer """
        if len(self.all_text_inputted) < self.limit:
            print('if reached')
            self.all_text_inputted.append(text_inputted.lower().strip())
            if len(self.all_text_inputted) == self.limit:
                return 'Limit Reached'
        return None

    def refresh_answers(self):
        """Resets the user's inputted answers."""
        self.all_text_inputted = []


class Text:
    """This class represents text in pygame
    Instance Attributes:
        - text: the text to display
        - rect: the area of where text is displayed
        - top_left_coordinates: the top left coordinates of Text
        - size: the font size of the text
    Private Instance Attributes:
        - _FONT: the font of the text
        - _FONT_COLOR: constant that represents the color of the font
    """
    text: str
    rect: pygame.rect.Rect
    top_left_coordinates: tuple[int, int]
    size: int
    _FONT: pygame.font.Font
    _FONT_COLOR: tuple[int, int, int]

    def __init__(self, text: str, rect: pygame.rect.Rect, top_left_coordinates: tuple[int, int], size: int):
        self.rect = rect
        self._FONT = pygame.font.Font(FONT_PATH, size)
        self._FONT_COLOR = (0, 0, 0)
        self.text = text
        self.rect.topleft = top_left_coordinates

    def draw_text(self, surface: pygame.Surface) -> None:
        """Draws Text onto given surface, also wraps text around if it goes past rectangle."""
        text_surf = self._FONT.render(self.text, True, self._FONT_COLOR)
        text_rect = text_surf.get_rect(topleft=self.rect.topleft)
        surface.blit(text_surf, text_rect)

    def remove_text(self) -> None:
        """Removes text off-screen."""
        self.text = ''

"""CSC111 Project 2: The Ultimate Recipe Index - Screen Displays

===============================

This Python module contains code for the GUI elements in our recipe index application.
"""

from __future__ import annotations

from typing import Callable, Optional
import pygame
from Processing.app_constants import BUTTON_BORDER_RADIUS, BUTTON_FONT_COLOR, BUTTON_FONT_SIZE, DEFAULT_TEXT_COLOR, \
    ELLIPSIS_TEXT, EMPTY_TEXT, \
    FONT_PATH, LIMIT_REACHED_MESSAGE, NEWLINE_CHARACTER, SPACE_CHARACTER, TEXTBOX_BORDER_WIDTH, \
    TEXTBOX_COLOR, \
    TEXTBOX_FONT_COLOR, \
    TEXTBOX_FONT_SIZE, \
    TEXTBOX_MAX_LENGTH, \
    TOP_LEFT_CORNER_COORDINATES, X_DIMENSIONS, \
    Y_DIMENSIONS


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
    """
    rect: pygame.Rect
    text: str
    color: tuple[int, int, int]
    action: Optional[Callable[..., None]] = None
    top_left_coordinates: tuple[int, int]
    _font: pygame.font.Font

    def __init__(self, rect: pygame.Rect, text: str, color: tuple[int, int, int],
                 top_left_coordinates: tuple[int, int], action: Optional[Callable[..., None]] = None) -> None:
        self.rect = rect
        self._font = pygame.font.Font(FONT_PATH, BUTTON_FONT_SIZE)
        self.text = text
        self.color = color
        if action:
            self.action = action
        self.top_left_coordinates = top_left_coordinates

    def draw_button(self, surface: pygame.Surface) -> None:
        """Draws Button on given surface."""

        self.rect.topleft = self.top_left_coordinates
        pygame.draw.rect(surface, self.color, self.rect, border_radius=BUTTON_BORDER_RADIUS)
        text_surf = self._font.render(self.text, True, BUTTON_FONT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def perform_event(self) -> None:
        """Calls on the buttons action to perform its duty."""
        if self.action is not None:
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
           - width: width of the Screen
           - height: height of the Screen
           - buttons: list of all Buttons displayed on Screen
           - textboxes: list of all Textboxes displayed on Screen (optional)
           - text: list of all Text displayed on Screen (optional)
       Private Instance Attributes:
           - _image: the image displayed on Screen
           - _default_text: the initial number of Text objects on screen
       """

    surface: pygame.Surface
    width: int
    height: int
    buttons: list[Button]
    image_filepath: str
    textboxes: Optional[list[TextBox]] = None
    text: Optional[list[Text]] = None
    _image: pygame.Surface
    _default_text: int

    def __init__(self, buttons: list[Button], image_filepath: str, surface: pygame.Surface,
                 textboxes: Optional[list[TextBox]] = None, text: Optional[list[Text]] = None) -> None:
        self.surface = surface
        self.buttons = buttons
        self.image_filepath = image_filepath
        self._image = pygame.image.load(self.image_filepath)
        self._image = pygame.transform.scale(self._image, (X_DIMENSIONS, Y_DIMENSIONS))
        self.textboxes = textboxes
        self.text = text
        if self.text:
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
        if self.textboxes:
            for textbox in self.textboxes:
                textbox.handle_textbox_input(event)

    def draw_screen(self) -> None:
        """Draws the screen in pygame with all features (Text, Textbox, Button if any are present)."""
        self.surface.blit(self._image, TOP_LEFT_CORNER_COORDINATES)
        for button in self.buttons:
            button.draw_button(self.surface)
        if self.textboxes:
            for textbox in self.textboxes:
                textbox.draw_textbox(self.surface)
        if self.text:
            for text in self.text:
                text.draw_text(self.surface)
        pygame.display.flip()

    def refresh_screen(self) -> None:
        """Completely resets screen to initial state. If any text was added to screen, it removes it."""
        if self.textboxes:
            for textbox in self.textboxes:
                textbox.refresh_textbox()
        if self.text is not None:
            for _ in range(len(self.text) - self._default_text):
                text = self.text.pop()
                text.remove_text()

    def get_textbox_inputs(self) -> list[list[str]]:
        """Returns all the text inputted in Textbox"""
        if self.textboxes is None:
            return []
        return [textbox.all_text_inputted for textbox in self.textboxes]


class ScreenOrganizer:
    """Manages the current Screen on pygame.
    Instance Attributes:
        - curr_screen: The current screen drawn on pygame.
    """
    curr_screen: Screen

    def __init__(self, screen: Screen) -> None:
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
         - _font: the font of the text in Textbox
     """
    rect: pygame.Rect
    text_inputted: str
    top_left_coordinates: tuple[int, int]
    limit: int
    _enabled: bool
    _text_active: bool
    _font: pygame.font.Font
    all_text_inputted: list[str]

    def __init__(self, rect: pygame.Rect, top_left_coordinates: tuple[int, int], limit: int) -> None:
        self.rect = rect
        self.top_left_coordinates = top_left_coordinates
        self.rect.topleft = top_left_coordinates
        self.limit = limit
        self._font = pygame.font.Font(FONT_PATH, TEXTBOX_FONT_SIZE)
        self.text_inputted = EMPTY_TEXT
        self._text_active = False
        self.all_text_inputted = []
        self._enabled = True

    def draw_textbox(self, surface: pygame.Surface) -> None:
        """Draws textbox on given surface."""
        text_surf = self._font.render(self.text_inputted, True, TEXTBOX_FONT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        pygame.draw.rect(surface, TEXTBOX_COLOR, self.rect, TEXTBOX_BORDER_WIDTH)
        surface.blit(text_surf, text_rect)

    def handle_textbox_input(self, event: pygame.event.Event) -> None:
        """Update this textbox based on the given event."""
        if not self._enabled:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self._text_active = self.rect.collidepoint(event.pos)
            return

        if event.type != pygame.KEYDOWN or not self._text_active:
            return

        if event.key == pygame.K_RETURN:
            self._text_active = False
            process = self.process_final_answer(self.text_inputted)
            if process is not None:
                self._enabled = False
            self.clear_textbox()
            return

        if event.key == pygame.K_BACKSPACE:
            self.text_inputted = self.text_inputted[:-1]
            return

        if len(self.text_inputted) >= TEXTBOX_MAX_LENGTH:
            return

        if event.key == pygame.K_SPACE:
            self.text_inputted += SPACE_CHARACTER
        else:
            self.text_inputted += event.unicode

    def clear_textbox(self) -> None:
        """Clears the textbox"""
        self.text_inputted = EMPTY_TEXT

    def refresh_textbox(self) -> None:
        """Refreshes and re-enables textbox."""
        self.refresh_answers()
        self.clear_textbox()
        self._enabled = True

    def process_final_answer(self, text_inputted: str) -> str | None:
        """Updates final answer """
        if len(self.all_text_inputted) < self.limit:
            self.all_text_inputted.append(text_inputted.lower().strip())
            if len(self.all_text_inputted) == self.limit:
                return LIMIT_REACHED_MESSAGE
        return None

    def refresh_answers(self) -> None:
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
    display_text: str
    rect: pygame.rect.Rect
    top_left_coordinates: tuple[int, int]
    size: int
    _font: pygame.font.Font

    def __init__(self, text: str, rect: pygame.rect.Rect, top_left_coordinates: tuple[int, int], size: int) -> None:
        self.rect = rect
        self._font = pygame.font.Font(FONT_PATH, size)
        self.display_text = text
        self.rect.topleft = top_left_coordinates

    def draw_text(self, surface: pygame.Surface) -> None:
        """Draw multiline text with wrapping and ellipsis if too tall."""
        x, y = self.rect.topleft
        max_width = self.rect.width if self.rect.width > 0 else None
        max_height = self.rect.height if self.rect.height > 0 else None

        line_height = self._font.get_height()
        current_y = y

        for line in self.display_text.split(NEWLINE_CHARACTER):
            current_y = self._draw_wrapped_line(
                surface, line, x, y, current_y, line_height, max_width, max_height
            )
            if current_y is None:
                return

    def _draw_wrapped_line(self, surface: pygame.Surface, line: str, x: int, start_y: int, current_y: int,
                           line_height: int, max_width: int | None, max_height: int | None) -> int | None:
        """Draw one logical line of text, wrapping if needed. Return new y, or None if cut off."""
        words = line.split(SPACE_CHARACTER)
        current_line = EMPTY_TEXT

        for word in words:
            test_line = self._join_word(current_line, word)

            if self._fits_width(test_line, max_width):
                current_line = test_line
            else:
                if not self._has_height_space(current_y, start_y, line_height, max_height):
                    self._draw_ellipsis(surface, x, current_y)
                    return None

                self._blit_line(surface, current_line, x, current_y)
                current_y += line_height
                current_line = word

        if current_line:
            if not self._has_height_space(current_y, start_y, line_height, max_height):
                self._draw_ellipsis(surface, x, current_y)
                return None

            self._blit_line(surface, current_line, x, current_y)
            current_y += line_height

        return current_y

    @staticmethod
    def _join_word(current_line: str, word: str) -> str:
        """Return current_line with word appended properly."""
        return current_line + (SPACE_CHARACTER if current_line else EMPTY_TEXT) + word

    def _fits_width(self, text: str, max_width: int | None) -> bool:
        """Return whether the given text fits within max_width."""
        if max_width is None:
            return True
        text_surf = self._font.render(text, True, DEFAULT_TEXT_COLOR)
        return text_surf.get_width() <= max_width

    @staticmethod
    def _has_height_space(current_y: int, start_y: int, line_height: int, max_height: int | None) -> bool:
        """Return whether another line can be drawn within the height limit."""
        return max_height is None or current_y + line_height <= start_y + max_height

    def _blit_line(self, surface: pygame.Surface, text: str, x: int, y: int) -> None:
        """Render and draw one line of text."""
        text_surf = self._font.render(text, True, DEFAULT_TEXT_COLOR)
        surface.blit(text_surf, (x, y))

    def _draw_ellipsis(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Draws '...' at the cutoff point."""
        ellipsis_text = self._font.render(ELLIPSIS_TEXT, True, DEFAULT_TEXT_COLOR)
        surface.blit(ellipsis_text, (x, y))

    def remove_text(self) -> None:
        """Removes text off-screen."""
        self.display_text = EMPTY_TEXT

from abc import ABC, abstractmethod


class Palette(ABC):

    def __init__(self, background_color):
        self._background_color = background_color

    def get_window_stylesheet(self):
        return f"""background-color:{self._background_color};"""

    @abstractmethod
    def get_progress_bar_stylesheet(self):
        return NotImplementedError()

    @abstractmethod
    def get_tab_widget_stylesheet(self):
        return NotImplementedError()

    @abstractmethod
    def _stylesheet(self):
        return NotImplementedError()

# FIXME: implementation steps:
#   - finish creating abstract methods for this class, they correspond to the stylessheet constants in
#       palette.pallete.py
#   - if there are any stylesheets that do not change based on light/dark modes, impelement the methods here
#   - implement all abstract methods in the light mode and dark mode palette subclasses
#   - great, now we have a palette base class and a light and dark mode child classes
#   - create a switch ui element in application.py. Switch defaults to dark more, if flipped, you swap the
#       self.palette: Palette form a DarkModePalette to a LightModePalette
#   - then you reset the stylesheets of all the components in application.py
#   - implement injection - each class used by the config members needs accept a : Palette type as a parameter.
#   - the caller of these classes needs to pass its reference to the palette down
#   - on mode toggle, you may have to reset the self.components by calling the constructor again, this will
#       get them to pass the new palette down the chain.
#   - then we can delete the palette/palette.py file that we have been using for static constants

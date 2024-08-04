from StockBench.gui.palette.base.palette import Palette


class DarkModePalette(Palette):
    BACKGROUND_COLOR = "#202124"

    def __init__(self):
        super().__init__(self.BACKGROUND_COLOR)



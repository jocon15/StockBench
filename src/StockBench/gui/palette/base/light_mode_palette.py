from StockBench.gui.palette.base.palette import Palette


class LightModePalette(Palette):
    BACKGROUND_COLOR = "#fff"

    def __init__(self):
        super().__init__(self.BACKGROUND_COLOR)



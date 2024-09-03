import os


class Palette:
    """Data class for storing shared style items.

    Inheritance allows subclasses of a base class to abstract shared style code to the base class. But in unrelated
    classes with shared style code, inheritance cannot be done. Palette as a static class allows unrelated
    classes to share common style code.
    """
    # ============================= Icons ========================================
    CANDLE_ICON = os.path.join('resources', 'images', 'candle.ico')

    # ============================= Stylesheets ==================================

    WINDOW_STYLESHEET = """background-color:#202124;"""

    PROGRESS_BAR_STYLESHEET = """
            QProgressBar{
                border-radius: 2px;
            }

            QProgressBar::chunk{
                border-radius: 2px;
                background-color: #7532a8;
            }"""

    TAB_WIDGET_STYLESHEET = """
            QTabWidget::pane{
                background-color: #202124;
                border: 0;
            }
            QTabBar::tab:selected {
                color: #ffffff;
                background-color: #42444a;
            }
            QTabBar::tab:!selected {
                color: #ffffff;
                background-color: #323338;
            }"""

    INPUT_LABEL_STYLESHEET = """color: #FFF;"""

    INPUT_BOX_STYLESHEET = """background-color: #303134;color:#FFF;border-width:0px;border-radius:10px;
            height:25px;"""

    TEXT_BOX_STYLESHEET = """background-color: #303134;color:#FFF;border-width:0px;border-radius:10px;height:25px;
            text-indent:3px;"""

    COMBOBOX_STYLESHEET = """background-color: #303134;color:#FFF;border-width:0px;border-radius:10px;height:25px;
            text-indent:3px;"""

    RADIO_BTN_STYLESHEET = """color: #fff; margin-left: 15px;"""

    LINE_EDIT_STYLESHEET = """background-color:#303134;color:#FFF;border-width:0px;border-radius:10px;height:25px;
            text-indent:5px;"""

    SIDEBAR_HEADER_STYLESHEET = """max-height:45px; color:#FFF;font-size:20px;font-weight:bold;"""

    SIDEBAR_OUTPUT_BOX_STYLESHEET = """color: #fff; background-color: #303136; border-radius: 8px;border: 
    0px; padding: 5px;max-height: 300px;"""

    SECONDARY_BTN = """
                QPushButton
                {
                    color: #FFF;
                    background-color: #303134;
                    border-width:0px;
                    border-radius:10px;
                    height:25px;
                }
                QPushButton:hover
                {
                    background-color: #3f4145;
                }
    """

    TOGGLE_BTN_ENABLED_STYLESHEET = """
                QPushButton
                {
                    background-color:#04ba5f;
                    margin-left:auto;
                    margin-right:auto;
                    width:40%;
                    height:25px;
                    border-radius:10px;
                }
                QPushButton:hover
                {
                    background-color: #4ab577;
                }
                """

    TOGGLE_BTN_DISABLED_STYLESHEET = """
                QPushButton
                {
                    background-color: #303134;
                    margin-left: auto;
                    margin-right:auto;
                    width: 40%;
                    height:25px;
                    border-radius: 10px;
                }
                QPushButton:hover
                {
                    background-color: #3f4145;
                }
                """

    RUN_BTN_STYLESHEET = """
                QPushButton
                {
                    background-color: #04ba5f;
                    color: #FFF;
                    border-radius: 10px;
                }
                QPushButton:hover
                {
                    background-color: #4ab577;
                }
                """

    ERROR_LABEL_STYLESHEET = """color:#dc143c;"""

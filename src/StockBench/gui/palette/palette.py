import os


class Palette:
    """Data class for storing shared style items.

    Inheritance allows subclasses of a base class to abstract shared style code to the base class. But in unrelated
    classes with shared style code, inheritance cannot be done. Palette as a static class allows unrelated
    classes to share common style code.
    """
    # ============================= Icons ========================================
    CANDLE_ICON_FILEPATH = os.path.join('resources', 'images', 'candle.ico')

    # ============================= Stylesheets ==================================

    WINDOW_STYLESHEET = """background-color:#202124;"""

    PROGRESS_BAR_STYLESHEET = """
        QProgressBar{
            border-radius: 2px;
        }

        QProgressBar::chunk{
            border-radius: 2px;
            background-color: #7532a8;
        }
    """

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
        }
    """

    HINT_LABEL_STYLESHEET = """color: #707070; font-size:12px;"""

    INPUT_LABEL_STYLESHEET = """
        color: #FFF;
        font-size: 13px;
    """

    FILEPATH_BOX_STYLESHEET = """
        color: #8c8c8c;
        background-color: #303134;
        border-width: 0px;
        border-radius: 10px;
        padding: 5px;
        text-indent: 4px;
    """

    INPUT_BOX_STYLESHEET = """
        color: #FFF;
        background-color: #303134;
        border-width: 0px;
        border-radius: 10px;
        padding: 5px;
        text-indent: 4px;
    """

    TEXT_BOX_STYLESHEET = """
        background-color: #303134;
        color: #FFF;
        border-width: 0px;
        border-radius: 10px;
        height: 25px;
        text-indent: 4px;
    """

    COMBOBOX_STYLESHEET = """
        color:#FFF;
        background-color: #303134;
        font-size: 15px;
        border-width: 0px;
        border-radius: 10px;
        padding-left: 5px;
        height: 30px;
    """

    RADIO_BTN_STYLESHEET = """
        color: #fff; 
        margin-left: 15px;
        font-size: 15px;
        
    """

    LINE_EDIT_STYLESHEET = """
        color: #FFF;
        background-color:#303134;
        font-size: 15px;
        border-width: 0px;
        border-radius: 10px;
        padding-left: 5px;
        height: 30px;
    """

    STRATEGY_TEXT_EDIT_STYLESHEET = """
        color: #fff;
        background-color: #303134;
        font-size: 15px;
        border-radius: 12px;
        padding: 5px;
    """

    STATUS_STYLESHEET = """
        border-radius: 5px;
        padding: 3px;
        background-color: #303134;
        color: #fff
    """

    SIDEBAR_HEADER_STYLESHEET = """
        color:#FFF;
        max-height:45px;
        font-size:20px;
        font-weight:bold;
    """

    SIDEBAR_OUTPUT_BOX_STYLESHEET = """
        color: #fff;
        background-color: #303136;
        border-radius: 8px;
        border: 0px; 
        padding: 5px;
    """

    STRATEGY_STUDIO_BTN = """
        QPushButton
        {
            color: #FFF;
            background-color: #303134;
            font-size: 14px;
            border-width: 0px;
            border-radius: 10px;
            height: 25px;
            width: 200px;
            margin-left: 10px;
        }
        QPushButton:hover
        {
            background-color: #3f4145;
        }
    """

    SECONDARY_BTN = """
        QPushButton
        {
            color: #FFF;
            background-color: #303134;
            font-size: 14px;
            border-width: 0px;
            border-radius: 10px;
            height: 25px;
        }
        QPushButton:hover
        {
            background-color: #3f4145;
        }
    """

    TOGGLE_BTN_ENABLED_STYLESHEET = """
        QPushButton
        {
            background-color: #04ba5f;
            margin-left: auto;
            margin-right: auto;
            border-radius: 10px;
            font-size: 15px;
            width: 40%;
            height: 25px;
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
            margin-right: auto;
            border-radius: 10px;
            font-size: 15px;
            width: 40%;
            height: 25px;
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

    ERROR_LABEL_STYLESHEET = """
        color: #dc143c;
        font-size: 15px;
    """

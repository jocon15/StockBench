import os

from PyQt6.QtWidgets import QLabel, QLineEdit
from PyQt6.QtCore import Qt

from StockBench.gui.config.tabs.base.config_tab import ConfigTab, MessageBoxCaptureException, CaptureConfigErrors
from StockBench.gui.palette.palette import Palette
from StockBench.gui.results.folder.folder_results_window import FolderResultsWindow
from StockBench.gui.config.components.cached_folder_selector import CachedFolderSelector


class FolderConfigTab(ConfigTab):
    FOLDER_CACHE_KEY = 'cached_folderpath'

    def __init__(self):
        super().__init__()
        # add shared_components to the layout
        label = QLabel()
        label.setText('Folder:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.folder_selection = CachedFolderSelector()
        self.folder_selection.setStyleSheet(Palette.SECONDARY_BTN)
        self.layout.addWidget(self.folder_selection)

        self.layout.addWidget(self.simulation_length_label)

        self.layout.addWidget(self.simulation_length_cbox)

        label = QLabel()
        label.setText('Simulation Symbols:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.symbol_tbox = QLineEdit()
        self.symbol_tbox.setText("MSFT, AAPL")
        self.symbol_tbox.setStyleSheet(Palette.LINE_EDIT_STYLESHEET)
        self.layout.addWidget(self.symbol_tbox)

        self.layout.addWidget(self.initial_balance_label)

        self.layout.addWidget(self.initial_balance_tbox)

        self.layout.addWidget(self.logging_label)

        self.layout.addWidget(self.logging_btn)

        self.layout.addWidget(self.unique_chart_save_label)

        self.layout.addWidget(self.unique_chart_save_btn)

        self.layout.addWidget(self.run_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.layout.addWidget(self.error_message_box)

        self.setLayout(self.layout)

    @CaptureConfigErrors
    def on_run_btn_clicked(self, clicked_signal: bool):
        """On-click function for the run button.

        Args:
            clicked_signal: DO NOT REMOVE - Unused boolean param that PyQt clicked.connect() function sends when a
            decorator is connected.

        Decorator:
            The CaptureErrors decorator allows custom exceptions to be caught and logged to the error message box
            instead of crashing. It also allows us to functionalize the filepath validation without the need for
            try blocks or return values.
        """
        # extract the folder path from the input
        folderpath = self.folder_selection.folderpath_box.text()

        # gather other data from UI shared_components
        raw_simulation_symbols = self.symbol_tbox.text().split(',')
        simulation_symbols = []
        for symbol in raw_simulation_symbols:
            simulation_symbols.append(symbol.upper().strip())
        simulation_balance = float(self.initial_balance_tbox.text())

        if simulation_balance <= 0:
            raise MessageBoxCaptureException('Initial account balance must be a positive number!')

        strategies = []
        for filename in os.listdir(folderpath):
            filepath = os.path.join(folderpath, filename)
            strategy = self.load_strategy(filepath, self.FOLDER_CACHE_KEY, folderpath)
            strategies.append(strategy)

        # create a new simulations results window
        self.simulation_result_window = FolderResultsWindow(
            strategies,
            simulation_symbols,
            simulation_balance,
            self.simulation_logging,
            self.simulation_reporting,
            self.simulation_unique_chart_saving,
            None)

        # all error checks have passed, can now clear the error message box
        self.error_message_box.setText('')

        # begin the simulation and progress checking timer
        self.simulation_result_window.begin()

        self.simulation_result_window.showMaximized()

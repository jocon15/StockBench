import os
from typing import Callable

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

from StockBench.controllers.stockbench_controller import StockBenchController
from StockBench.gui.config.tabs.base.config_tab import ConfigTab, MessageBoxCaptureException, CaptureConfigErrors
from StockBench.gui.config.tabs.folder.components.grid_config_frame import GridConfigFrame
from StockBench.gui.palette.palette import Palette
from StockBench.gui.results.folder.folder_results_window import FolderResultsWindow
from StockBench.gui.config.components.cached_folder_selector import CachedFolderSelector
from StockBench.models.constants.general_constants import SECONDS_1_YEAR


class FolderConfigTab(ConfigTab):
    FOLDER_CACHE_KEY = 'cached_folderpath'

    def __init__(self, update_geometry: Callable, stockbench_controller: StockBenchController):
        super().__init__(update_geometry, stockbench_controller)
        label = QLabel()
        label.setText('Folder:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.folder_selection = CachedFolderSelector()
        self.folder_selection.setStyleSheet(Palette.SECONDARY_BTN)
        self.layout.addWidget(self.folder_selection)

        self.simulation_length = SECONDS_1_YEAR
        self.grid_config_frame = GridConfigFrame(self.on_simulation_length_cbox_index_changed,
                                                 self.on_logging_btn_clicked, self.on_chart_saving_btn_clicked)
        self.layout.addWidget(self.grid_config_frame)

        self.layout.addWidget(self.run_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.layout.addStretch()

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
        folderpath = self.folder_selection.folderpath_box.text()

        raw_simulation_symbols = self.grid_config_frame.left_frame.symbol_tbox.text().split(',')
        simulation_symbols = []
        for symbol in raw_simulation_symbols:
            simulation_symbols.append(symbol.upper().strip())
        simulation_balance = float(self.grid_config_frame.left_frame.initial_balance_tbox.text())

        if simulation_balance <= 0:
            raise MessageBoxCaptureException('Initial account balance must be a positive number!')

        strategies = []
        for filename in os.listdir(folderpath):
            filepath = os.path.join(folderpath, filename)
            strategy = self._load_strategy(filepath, self.FOLDER_CACHE_KEY, folderpath)
            strategies.append(strategy)

        self.simulation_result_window = FolderResultsWindow(
            self._stockbench_controller,
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

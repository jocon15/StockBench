from typing import Callable

from PyQt6.QtWidgets import QLabel, QPushButton
from PyQt6.QtCore import Qt

from StockBench.controllers.stockbench_controller import StockBenchController
from StockBench.gui.config.tabs.base.config_tab import ConfigTab, MessageBoxCaptureException, CaptureConfigErrors
from StockBench.gui.config.tabs.compare.components.grid_config_frame import GridConfigFrame
from StockBench.gui.results.compare.compare_results_window import CompareResultsWindow
from StockBench.gui.palette.palette import Palette
from StockBench.gui.config.components.strategy_selection import StrategySelection
from StockBench.models.constants.general_constants import SECONDS_1_YEAR


class CompareConfigTab(ConfigTab):
    STRATEGY_1_CACHE_KEY = 'cached_h2h_strategy_1_filepath'

    STRATEGY_2_CACHE_KEY = 'cached_h2h_strategy_2_filepath'

    def __init__(self, update_geometry: Callable, stockbench_controller: StockBenchController):
        super().__init__(update_geometry, stockbench_controller)
        label = QLabel()
        label.setText('Strategy 1:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.strategy_1_selection_box = StrategySelection(self.STRATEGY_1_CACHE_KEY)
        self.layout.addWidget(self.strategy_1_selection_box)

        self.strategy_1_studio_btn = QPushButton()
        self.strategy_1_studio_btn.setText('Strategy Studio')
        self.strategy_1_studio_btn.clicked.connect(lambda: self.on_strategy_studio_btn_clicked(  # noqa
                                                   self.strategy_1_selection_box.filepath_box.text()))
        self.strategy_1_studio_btn.setStyleSheet(Palette.STRATEGY_STUDIO_BTN)
        self.layout.addWidget(self.strategy_1_studio_btn, alignment=Qt.AlignmentFlag.AlignRight)

        label = QLabel()
        label.setText('Strategy 2:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.strategy_2_selection_box = StrategySelection(self.STRATEGY_2_CACHE_KEY)
        self.layout.addWidget(self.strategy_2_selection_box)

        self.strategy_2_studio_btn = QPushButton()
        self.strategy_2_studio_btn.setText('Strategy Studio')
        self.strategy_2_studio_btn.clicked.connect(lambda: self.on_strategy_studio_btn_clicked(  # noqa
                                                   self.strategy_2_selection_box.filepath_box.text()))
        self.strategy_2_studio_btn.setStyleSheet(Palette.STRATEGY_STUDIO_BTN)
        self.layout.addWidget(self.strategy_2_studio_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.simulation_length = SECONDS_1_YEAR
        self.grid_config_frame = GridConfigFrame(self.on_simulation_length_cbox_index_changed,
                                                 self.on_logging_btn_clicked, self.on_reporting_btn_clicked,
                                                 self.on_chart_saving_btn_clicked, self.data_and_charts_btn_selected,
                                                 self.data_only_btn_selected)
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
        # load the strategy from the JSON file into a strategy python dict
        strategy1 = self.load_strategy(self.strategy_1_selection_box.filepath_box.text(), self.STRATEGY_1_CACHE_KEY)
        strategy2 = self.load_strategy(self.strategy_2_selection_box.filepath_box.text(), self.STRATEGY_2_CACHE_KEY)

        # gather other data from UI shared_components
        raw_simulation_symbols = self.grid_config_frame.left_frame.symbol_tbox.text().split(',')
        simulation_symbols = []
        for symbol in raw_simulation_symbols:
            simulation_symbols.append(symbol.upper().strip())
        simulation_balance = float(self.grid_config_frame.left_frame.initial_balance_tbox.text())

        if simulation_balance <= 0:
            raise MessageBoxCaptureException('Initial account balance must be a positive number!')

        # reminder: h2h will store the references of these simulations, so we do not need to attribute them with self
        # also, h2h will call the begin functions

        self.head_to_head_window = CompareResultsWindow(
            self._stockbench_controller,
            simulation_symbols,
            strategy1,
            strategy2,
            self.simulation_logging,
            self.simulation_reporting,
            simulation_balance,
            self.results_depth
        )

        self.head_to_head_window.showMaximized()

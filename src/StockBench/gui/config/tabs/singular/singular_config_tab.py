from PyQt6.QtWidgets import QLabel, QPushButton
from PyQt6.QtCore import Qt

from StockBench.controllers.stockbench_controller import StockBenchController
from StockBench.gui.config.tabs.base.config_tab import ConfigTab, MessageBoxCaptureException, CaptureConfigErrors
from StockBench.gui.config.tabs.singular.components.grid_config_frame import GridConfigFrame
from StockBench.gui.results.singular.singular_results_window import SingularResultsWindow
from StockBench.gui.palette.palette import Palette
from StockBench.gui.config.components.strategy_selection import StrategySelection
from StockBench.models.constants.general_constants import SECONDS_1_YEAR


class SingularConfigTab(ConfigTab):
    def __init__(self, stockbench_controller: StockBenchController):
        super().__init__(stockbench_controller)

        self.show_volume = True

        label = QLabel()
        label.setText('Strategy:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.strategy_selection_box = StrategySelection()
        self.layout.addWidget(self.strategy_selection_box)

        self.strategy_studio_btn = QPushButton()
        self.strategy_studio_btn.setText('Strategy Studio')
        self.strategy_studio_btn.clicked.connect(lambda: self.on_strategy_studio_btn_clicked(  # noqa
                                                 self.strategy_selection_box.filepath_box.text()))
        self.strategy_studio_btn.setStyleSheet(Palette.STRATEGY_STUDIO_BTN)
        self.layout.addWidget(self.strategy_studio_btn)

        self.simulation_length = SECONDS_1_YEAR
        self.grid_config_frame = GridConfigFrame(self.on_simulation_length_cbox_index_changed,
                                                 self.on_logging_btn_clicked, self.on_reporting_btn_clicked,
                                                 self.on_show_volume_btn_clicked,
                                                 self.on_chart_saving_btn_clicked, self.data_and_charts_btn_selected,
                                                 self.data_only_btn_selected)
        self.layout.addWidget(self.grid_config_frame)

        self.layout.addWidget(self.run_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.layout.addStretch()

        self.setLayout(self.layout)

    def on_show_volume_btn_clicked(self, button: QPushButton):
        if button.isChecked():
            self.show_volume = True
            button.setText(self.ON)
            button.setStyleSheet(Palette.TOGGLE_BTN_ENABLED_STYLESHEET)
        else:
            self.show_volume = False
            button.setText(self.OFF)
            button.setStyleSheet(Palette.TOGGLE_BTN_DISABLED_STYLESHEET)

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
        strategy = self.load_strategy(self.strategy_selection_box.filepath_box.text())

        # gather other data from UI shared_components
        simulation_symbol = self.grid_config_frame.left_frame.symbol_tbox.text().upper().strip()
        simulation_balance = float(self.grid_config_frame.left_frame.initial_balance_tbox.text())

        if simulation_balance <= 0:
            raise MessageBoxCaptureException('Initial account balance must be a positive number!')

        self.simulation_result_window = SingularResultsWindow(
            self._stockbench_controller,
            simulation_symbol,
            strategy,
            simulation_balance,
            self.simulation_logging,
            self.simulation_reporting,
            self.simulation_unique_chart_saving,
            self.show_volume,
            self.results_depth)

        # all error checks have passed, can now clear the error message box
        self.error_message_box.setText('')

        # begin the simulation and progress checking timer
        self.simulation_result_window.begin()

        self.simulation_result_window.showMaximized()

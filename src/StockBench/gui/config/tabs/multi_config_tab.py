from PyQt6.QtWidgets import QLabel, QPushButton, QLineEdit
from PyQt6.QtCore import Qt

from StockBench.gui.config.tabs.base.config_tab import ConfigTab, MessageBoxCaptureException, CaptureConfigErrors
from StockBench.gui.results.multi.multi_results_window import MultiResultsWindow
from StockBench.gui.palette.palette import Palette
from StockBench.gui.config.components.strategy_selection import StrategySelection


class MultiConfigTab(ConfigTab):
    def __init__(self):
        super().__init__()
        # add shared_components to the layout
        label = QLabel()
        label.setText('Strategy:')
        label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        self.layout.addWidget(label)

        self.strategy_selection_box = StrategySelection()
        self.strategy_selection_box.setStyleSheet(Palette.INPUT_BOX_STYLESHEET)
        self.layout.addWidget(self.strategy_selection_box)

        self.strategy_studio_btn = QPushButton()
        self.strategy_studio_btn.setText('Strategy Studio')
        self.strategy_studio_btn.clicked.connect(lambda: self.on_strategy_studio_btn_clicked(  # noqa
                                                 self.strategy_selection_box.filepath_box.text()))
        self.strategy_studio_btn.setStyleSheet(Palette.SECONDARY_BTN)
        self.layout.addWidget(self.strategy_studio_btn)

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

        self.layout.addWidget(self.reporting_label)

        self.layout.addWidget(self.reporting_btn)

        self.layout.addWidget(self.unique_chart_save_label)

        self.layout.addWidget(self.unique_chart_save_btn)

        self.layout.addWidget(self.results_depth_label)

        self.layout.addWidget(self.data_and_charts_radio_btn)

        self.layout.addWidget(self.data_only_radio_btn)

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
        # load the strategy from the JSON file into a strategy python dict
        strategy = self.load_strategy(self.strategy_selection_box.filepath_box.text())

        # gather other data from UI shared_components
        raw_simulation_symbols = self.symbol_tbox.text().split(',')
        simulation_symbols = []
        for symbol in raw_simulation_symbols:
            simulation_symbols.append(symbol.upper().strip())
        simulation_balance = float(self.initial_balance_tbox.text())

        if simulation_balance <= 0:
            raise MessageBoxCaptureException('Initial account balance must be a positive number!')

        self.simulation_result_window = MultiResultsWindow(
            simulation_symbols,
            strategy,
            simulation_balance,
            self.simulation_logging,
            self.simulation_reporting,
            self.simulation_unique_chart_saving,
            self.results_depth)

        # all error checks have passed, can now clear the error message box
        self.error_message_box.setText('')

        # begin the simulation and progress checking timer
        self.simulation_result_window.begin()

        self.simulation_result_window.showMaximized()

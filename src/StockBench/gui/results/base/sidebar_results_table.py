from PyQt6.QtWidgets import QFrame
from StockBench.gui.palette.palette import Palette
from abc import abstractmethod
from PyQt6.QtWidgets import QLabel, QGridLayout


class SidebarResultsTable(QFrame):
    """Superclass for a results table frame."""
    TABLE_STYLESHEET = """background-color: #303136; border-radius:8px;"""

    RESULT_VALUE_STYLESHEET = """color: #fff;"""

    def __init__(self):
        super().__init__()
        self.layout = QGridLayout()

        self.spacer = QFrame()
        self.spacer.setFrameShape(QFrame.Shape.HLine)  # Set the shape to a horizontal line
        self.spacer.setFrameShadow(QFrame.Shadow.Sunken)  # Give it a 3D sunken effect

        # ========================= Shared Metadata ================================
        self.strategy_label = QLabel()
        self.strategy_label.setText('Strategy')
        self.strategy_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # strategy data label
        self.strategy_data_label = QLabel()
        self.strategy_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        # trade-able days label
        self.trade_able_days_label = QLabel()
        self.trade_able_days_label.setText('Length')
        self.trade_able_days_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # trade-able days data label
        self.trade_able_days_data_label = QLabel()
        self.trade_able_days_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        self.elapsed_time_label = QLabel()
        self.elapsed_time_label.setText('Elapsed Time')
        self.elapsed_time_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # elapsed time data label
        self.elapsed_time_data_label = QLabel()
        self.elapsed_time_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        # ========================= Shared Results ================================
        self.trades_made_label = QLabel()
        self.trades_made_label.setText('Trades Made')
        self.trades_made_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # trades made data label
        self.trades_made_data_label = QLabel()
        self.trades_made_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        self.average_trade_duration_label = QLabel()
        self.average_trade_duration_label.setText('Average Trade Duration')
        self.average_trade_duration_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # trades made data label
        self.average_trade_duration_data_label = QLabel()
        self.average_trade_duration_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        self.effectiveness_label = QLabel()
        self.effectiveness_label.setText('Effectiveness')
        self.effectiveness_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # effectiveness data label
        self.effectiveness_data_label = QLabel()
        self.effectiveness_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        self.total_pl_label = QLabel()
        self.total_pl_label.setText('Total PL')
        self.total_pl_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # total P/L data label
        self.total_pl_data_label = QLabel()
        self.total_pl_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        self.average_pl_label = QLabel()
        self.average_pl_label.setText('Average PL')
        self.average_pl_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # average P/L data label
        self.average_pl_data_label = QLabel()
        self.average_pl_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        self.median_pl_label = QLabel()
        self.median_pl_label.setText('Median PL')
        self.median_pl_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # median data label
        self.median_pl_data_label = QLabel()
        self.median_pl_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        self.stddev_pl_label = QLabel()
        self.stddev_pl_label.setText('Stddev PL')
        self.stddev_pl_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # stddev data label
        self.stddev_pl_data_label = QLabel()
        self.stddev_pl_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        self.average_plpc_label = QLabel()
        self.average_plpc_label.setText('Average PLPC')
        self.average_plpc_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # average P/L data label
        self.average_plpc_data_label = QLabel()
        self.average_plpc_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        self.median_plpc_label = QLabel()
        self.median_plpc_label.setText('Median PLPC')
        self.median_plpc_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # median data label
        self.median_plpc_data_label = QLabel()
        self.median_plpc_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        self.stddev_plpc_label = QLabel()
        self.stddev_plpc_label.setText('Stddev PLPC')
        self.stddev_plpc_label.setStyleSheet(Palette.INPUT_LABEL_STYLESHEET)
        # stddev data label
        self.stddev_plpc_data_label = QLabel()
        self.stddev_plpc_data_label.setStyleSheet(self.RESULT_VALUE_STYLESHEET)

        self.setStyleSheet(self.TABLE_STYLESHEET)

    @abstractmethod
    def render_data(self, simulation_results: dict):
        raise NotImplementedError('You must define an implementation for render_data()!')

import os
import json

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtWidgets import QFileDialog
from StockBench.gui.palette.palette import Palette


class StrategySelection(QWidget):
    CACHE_FILE_FILEPATH = 'cache.json'

    DEFAULT_CACHE_KEY = 'cached_strategy_filepath'

    def __init__(self, cache_key=None):
        super().__init__()

        self.layout = QHBoxLayout()

        self.filepath_box = QLabel()
        self.filepath_box.setStyleSheet(Palette.INPUT_BOX_STYLESHEET)
        self.layout.addWidget(self.filepath_box)
        self.apply_cached_strategy_filepath(cache_key)

        self.select_file_btn = QPushButton()
        self.select_file_btn.setText('Select File')
        self.select_file_btn.clicked.connect(self.on_select_file_btn_clicked)  # noqa
        self.select_file_btn.setStyleSheet(Palette.SECONDARY_BTN)
        self.layout.addWidget(self.select_file_btn)

        self.setLayout(self.layout)

    def apply_cached_strategy_filepath(self, cache_key=None):
        if os.path.exists(self.CACHE_FILE_FILEPATH):
            with open(self.CACHE_FILE_FILEPATH, 'r') as file:
                data = json.load(file)

            # swap the key to the passed key if one was entered (used when using h2h cached keys)
            key = self.DEFAULT_CACHE_KEY
            if cache_key:
                key = cache_key

            if key in data.keys():
                self.filepath_box.setText(data[key])

    def on_select_file_btn_clicked(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dlg.setNameFilter("JSON (*.json)")
        if dlg.exec():
            filenames = dlg.selectedFiles()
            self.filepath_box.setText(filenames[0])

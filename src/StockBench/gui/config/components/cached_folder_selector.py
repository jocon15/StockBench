import os
import json
from typing import Callable

from StockBench.gui.palette.palette import Palette
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog
from StockBench.caching.file_cache import CACHE_FILE_FILEPATH


class CachedFolderSelector(QWidget):
    DEFAULT_CACHE_KEY = 'cached_folderpath'

    def __init__(self, update_cache: Callable):
        super().__init__()
        self.update_cache = update_cache

        self.layout = QHBoxLayout()

        self.folderpath_box = QLabel()
        self.folderpath_box.setStyleSheet(Palette.FILEPATH_BOX_STYLESHEET)
        self.layout.addWidget(self.folderpath_box)
        self.apply_cached_folderpath()

        self.select_folder_btn = QPushButton()
        self.select_folder_btn.setText('Select Folder')
        self.select_folder_btn.clicked.connect(self.on_select_folder_btn_clicked)  # noqa
        self.select_folder_btn.setStyleSheet(Palette.SECONDARY_BTN)
        self.select_folder_btn.setFixedWidth(90)
        self.layout.addWidget(self.select_folder_btn)

        self.setLayout(self.layout)

    def apply_cached_folderpath(self):
        if os.path.exists(CACHE_FILE_FILEPATH):
            with open(CACHE_FILE_FILEPATH, 'r') as file:
                data = json.load(file)

            if self.DEFAULT_CACHE_KEY in data.keys():
                self.folderpath_box.setText(data[self.DEFAULT_CACHE_KEY])

    def on_select_folder_btn_clicked(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        dlg.setNameFilter("JSON (*.json)")
        if dlg.exec():
            filenames = dlg.selectedFiles()
            # QFileDialog does not have an easy way of limiting selection to 1 file - only the first file is selected
            self.folderpath_box.setText(filenames[0])
            self.update_cache(filenames[0], cache_key=self.DEFAULT_CACHE_KEY)

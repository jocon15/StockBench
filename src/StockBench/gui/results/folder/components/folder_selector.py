from StockBench.gui.palette.palette import Palette
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog


class FolderSelector(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()

        self.folderpath_box = QLabel()
        self.folderpath_box.setStyleSheet(Palette.TEXT_BOX_STYLESHEET)
        self.layout.addWidget(self.folderpath_box)

        self.select_folder_btn = QPushButton()
        self.select_folder_btn.setText('Select Folder')
        self.select_folder_btn.clicked.connect(self.on_select_folder_btn_clicked)  # noqa
        self.select_folder_btn.setStyleSheet(Palette.SECONDARY_BTN)
        self.layout.addWidget(self.select_folder_btn)

        self.setLayout(self.layout)

    def on_select_folder_btn_clicked(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        dlg.setNameFilter("JSON (*.json)")
        if dlg.exec():
            filenames = dlg.selectedFiles()
            self.folderpath_box.setText(filenames[0])

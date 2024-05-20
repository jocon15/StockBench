import os
import json
from PyQt6 import QtGui
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QFileDialog

TEMPLATE_JSON = {"buy": {}, "sell": {}}


class StrategyStudioWindow(QWidget):
    window_stylesheet = """background-color: #202124;"""
    strategy_text_edit_stylesheet = """background-color: #303134;color: #fff"""
    status_stylesheet = """background-color: #303134;color: #fff"""

    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath

        # header
        self.setWindowIcon(QtGui.QIcon(os.path.join('resources', 'images', 'candle.ico')))
        self.setWindowTitle('Strategy Studio (beta)')

        # layout type
        self.layout = QVBoxLayout()

        # add objects to the layout
        self.status = QLabel()
        self.status.setStyleSheet(self.status_stylesheet)
        self.layout.addWidget(self.status)
        self.save_buttons = SaveButtons()
        self.save_buttons.save_btn.clicked.connect(self.on_save_btn_clicked)  # noqa
        self.save_buttons.save_as_btn.clicked.connect(self.on_save_as_btn_clicked)  # noqa
        self.layout.addWidget(self.save_buttons)
        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet(self.strategy_text_edit_stylesheet)
        self.setStyleSheet(self.window_stylesheet)
        self.layout.addWidget(self.text_edit)

        self.setGeometry(600, 100, 400, 600)

        # load the strategy from the file
        self.load_filepath_into_editor()

        # apply the layout
        self.setLayout(self.layout)

    def load_filepath_into_editor(self):
        # if a filepath was injected, try loading it, else, show the template
        if self.filepath is not None and self.filepath != '':
            # load the strategy from the file
            with open(self.filepath, 'r') as file:
                json_data = json.load(file)

            # set the strategy text to the editor widget
            self.text_edit.setText(json.dumps(json_data, indent=4))

            self.__set_status(f'You are editing: {self.filepath}')
        else:
            # set the strategy text to the editor widget
            self.text_edit.setText(json.dumps(TEMPLATE_JSON, indent=4))

            self.__set_status('You are creating a new strategy')

    def on_save_btn_clicked(self):
        if self.filepath is not None and self.filepath != '':
            # write the json to the filepath
            self.__save_json_file(self.filepath)
        else:
            # this file has not been saved yet and needs to use save_as instead
            self.on_save_as_btn_clicked()

    def on_save_as_btn_clicked(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "", "JSON (*.json)")
        if fileName is not None and fileName != '':
            # only save the file if the user picked a location
            self.__save_json_file(fileName)

    def __set_status(self, msg):
        self.status.setText(f'Status: {msg}')

    def __save_json_file(self, filepath):
        with open(filepath, 'w+') as file:
            json.dump(json.loads(self.text_edit.toPlainText()), file, indent=4)


class SaveButtons(QWidget):
    btn_stylesheet = """background-color: #303134;color:#FFF;border-width:0px;border-radius:10px;
        height:25px;"""

    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()

        self.save_btn = QPushButton()
        self.save_btn.setText('Save')
        self.save_btn.setStyleSheet(self.btn_stylesheet)
        self.layout.addWidget(self.save_btn)
        self.save_as_btn = QPushButton()
        self.save_as_btn.setText('Save as')
        self.save_as_btn.setStyleSheet(self.btn_stylesheet)
        self.layout.addWidget(self.save_as_btn)

        # buttons get connected by the window

        self.setLayout(self.layout)
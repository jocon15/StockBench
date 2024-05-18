import json

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton


class StrategyEditorWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.layout.addWidget(self.text_edit)
        self.done_btn = QPushButton()
        self.done_btn.setText('Done')
        self.done_btn.clicked.connect(self.done_btn_clicked)  # noqa
        self.layout.addWidget(self.done_btn)

        self.setGeometry(1000, 10, 1000, 1000)

        # load the strategy from the file
        with open('test.json', 'r') as file:
            json_data = json.load(file)

        # set the strategy text to the editor widget
        self.text_edit.setText(json.dumps(json_data, indent=4))

        self.setLayout(self.layout)

    def done_btn_clicked(self):
        pass

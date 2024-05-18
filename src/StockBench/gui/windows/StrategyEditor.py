import json

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton

TEMPLATE_JSON = {
    "buy": {

    },
    "sell": {

    }
}


class StrategyEditorWindow(QWidget):
    def __init__(self, filepath):
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
        self.load_filepath_into_editor(filepath)

        self.setLayout(self.layout)

    def load_filepath_into_editor(self, filepath):
        # if a filepath was injected, try loading it, else, show the template
        if filepath is not None and filepath != '':
            # load the strategy from the file
            with open('test.json', 'r') as file:
                json_data = json.load(file)

            # set the strategy text to the editor widget
            self.text_edit.setText(json.dumps(json_data, indent=4))
        else:
            # set the strategy text to the editor widget
            self.text_edit.setText(json.dumps(TEMPLATE_JSON, indent=4))

    def done_btn_clicked(self):
        pass

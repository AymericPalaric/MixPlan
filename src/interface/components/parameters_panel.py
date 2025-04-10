from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit

class ParametersPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Paramètres généraux
        self.layout.addWidget(QLabel("Paramètres"))
        self.param_input = QLineEdit()
        self.param_input.setPlaceholderText("Paramètre générique")
        self.layout.addWidget(self.param_input)
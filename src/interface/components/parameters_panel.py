from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton

class ParametersPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Paramètres des composants"))

        self.component_inputs = {}
        for i in range(1, 4):
            self.layout.addWidget(QLabel(f"Composant {i}"))
            
            min_input = QLineEdit()
            min_input.setPlaceholderText(f"Valeur min Composant {i}")
            self.layout.addWidget(min_input)
            
            max_input = QLineEdit()
            max_input.setPlaceholderText(f"Valeur max Composant {i}")
            self.layout.addWidget(max_input)
            
            self.component_inputs[f"component_{i}_min"] = min_input
            self.component_inputs[f"component_{i}_max"] = max_input

        self.update_button = QPushButton("Mettre à jour")
        self.layout.addWidget(self.update_button)

        if parent:
            self.update_button.clicked.connect(parent.update_graph_and_scores)

    def get_parameters(self):
        parameters = {}
        for i in range(1, 4):
            try:
                min_val = float(self.component_inputs[f"component_{i}_min"].text())
                max_val = float(self.component_inputs[f"component_{i}_max"].text())
                parameters[f"component_{i}"] = {"min": min_val, "max": max_val}
            except ValueError:
                parameters[f"component_{i}"] = {"min": None, "max": None}
        return parameters
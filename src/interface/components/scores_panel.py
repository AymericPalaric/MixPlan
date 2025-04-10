from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QLineEdit

class ScoresPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Liste des scores
        self.scores_list = QListWidget()
        self.layout.addWidget(QLabel("Scores"))
        self.layout.addWidget(self.scores_list)

        # Champs pour ajouter un point
        self.layout.addWidget(QLabel("Ajouter un point :"))
        self.x_input = QLineEdit()
        self.x_input.setPlaceholderText("X")
        self.layout.addWidget(self.x_input)

        self.y_input = QLineEdit()
        self.y_input.setPlaceholderText("Y")
        self.layout.addWidget(self.y_input)

        self.score_input = QLineEdit()
        self.score_input.setPlaceholderText("Score")
        self.layout.addWidget(self.score_input)

        # Bouton pour ajouter un point
        self.add_button = QPushButton("Ajouter")
        self.layout.addWidget(self.add_button)

        # Bouton pour interpoler
        self.interpolate_button = QPushButton("Interpoler")
        self.layout.addWidget(self.interpolate_button)

    def get_point_data(self):
        """Récupère les données des champs pour ajouter un point."""
        try:
            x = float(self.x_input.text())
            y = float(self.y_input.text())
            score = float(self.score_input.text())
            return x, y, score
        except ValueError:
            return None
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from functools import partial
from src.algo.interpolator import *
from src.interface.utils.logger import gui_logger

# Dictionnaire des interpolateurs disponibles
INTERPOLATORS = {
    # "LinearND": LinearNDInterpolator,
    # "Delaunay": DelaunayInterpolator,
    "RBF": RBFInterpolator,
    "Quadratic": QuadraticInterpolator,
    "Linear": LinearInterpolator,
}

class ScoresPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Tableau de points (X, Y, Z, Score)
        self.points_table = QTableWidget()
        self.points_table.setColumnCount(4)
        self.points_table.setHorizontalHeaderLabels(["X", "Y", "Z", "Score"])
        self.points_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.points_table.setEditTriggers(QTableWidget.AllEditTriggers)
        self.layout.addWidget(self.points_table)

        # Champs pour ajouter un point
        self.layout.addWidget(QLabel("Ajouter un point :"))

        point_layout = QHBoxLayout()
        self.x_input = QLineEdit()
        self.x_input.setPlaceholderText("X")
        point_layout.addWidget(self.x_input)

        self.y_input = QLineEdit()
        self.y_input.setPlaceholderText("Y")
        point_layout.addWidget(self.y_input)

        self.z_input = QLineEdit()
        self.z_input.setPlaceholderText("Z")
        point_layout.addWidget(self.z_input)

        self.score_input = QLineEdit()
        self.score_input.setPlaceholderText("Score")
        point_layout.addWidget(self.score_input)
        self.layout.addLayout(point_layout)

        # Bouton pour ajouter un point
        self.add_button = QPushButton("Ajouter")
        self.layout.addWidget(self.add_button)
        self.score_input.returnPressed.connect(self.add_button.click)

        # Menu déroulant pour sélectionner l'interpolateur
        self.layout.addWidget(QLabel("Choisir un interpolateur :"))
        self.interpolator_selector = QComboBox()
        self.interpolator_selector.addItems(INTERPOLATORS.keys())
        self.layout.addWidget(self.interpolator_selector)

        # Bouton pour lancer l'interpolation
        self.interpolate_button = QPushButton("Interpoler")
        self.layout.addWidget(self.interpolate_button)

        # Interpolateur actuellement sélectionné (par défaut)
        self.interpolator = INTERPOLATORS[self.interpolator_selector.currentText()]

        # Connexion du menu déroulant à la mise à jour
        self.interpolator_selector.currentTextChanged.connect(self.update_interpolator)

    def get_point_data(self):
        """Récupère les données des champs pour ajouter un point."""
        try:
            x = float(self.x_input.text())
            y = float(self.y_input.text())
            z = float(self.z_input.text())
            score = float(self.score_input.text())
            return x, y, z, score
        except ValueError:
            return None

    def update_points_table(self, point_data):
        """Ajoute un point dans le tableau."""
        row_position = self.points_table.rowCount()
        self.points_table.insertRow(row_position)
        for i, value in enumerate(point_data):
            item = QTableWidgetItem(str(value))
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            # round to 3 decimal places
            item.setData(Qt.EditRole, round(value, 3))
            self.points_table.setItem(row_position, i, item)

    def clear_inputs(self):
        """Efface les champs d'entrée."""
        self.x_input.clear()
        self.y_input.clear()
        self.z_input.clear()
        self.score_input.clear()

    def clear_scores_table(self):
        self.points_table.setRowCount(0)

    def clear(self):
        """Efface les champs d'entrée et la liste des scores."""
        self.clear_inputs()
        self.clear_scores_list()

    def update_interpolator(self):
        """Met à jour l'interpolateur sélectionné."""
        selected_name = self.interpolator_selector.currentText()
        self.interpolator = INTERPOLATORS[selected_name]
        gui_logger.log(f"Interpolateur sélectionné : {selected_name}")
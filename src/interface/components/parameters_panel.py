from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from PyQt5.QtCore import Qt

from src.interface.utils.points_lists import *

POINTS_LISTS = {
    "SimplexCentroid": SimplexCentroid(),
    "ScheffeNetwork": ScheffeNetwork(),
}

class ParametersPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Paramètres des composants"))

        self.component_inputs = {}
        self.component_names = {}
        self.names = []

        for i in range(1, 4):
            self.layout.addSpacing(50)
            # Champ pour le nom
            name_input = QLineEdit()
            name_input.setPlaceholderText(f"Nom du composant {i}")
            self.layout.addWidget(name_input)
            self.component_names[f"component_{i}_name"] = name_input

            self.names.append(QLabel(f"Composant {i}"))
            self.layout.addWidget(self.names[-1])
            # Champs min/max
            min_input = QLineEdit()
            min_input.setPlaceholderText(f"Valeur min composant {i}")
            self.layout.addWidget(min_input)

            max_input = QLineEdit()
            max_input.setPlaceholderText(f"Valeur max composant {i}")
            self.layout.addWidget(max_input)

            self.component_inputs[f"component_{i}_min"] = min_input
            self.component_inputs[f"component_{i}_max"] = max_input

        self.update_button = QPushButton("Mettre à jour")
        self.layout.addWidget(self.update_button)

        if parent:
            self.update_button.clicked.connect(parent.update_graph_and_scores)
        
        self.layout.addSpacing(100)
        # Menu déroulant pour choisir la liste de points initiaux
        self.layout.addWidget(QLabel("Sélectionner une configuration de plan d'expérience :"))
        self.initial_points_selector = QComboBox()
        self.initial_points_selector.addItems(POINTS_LISTS.keys())
        self.layout.addWidget(self.initial_points_selector)

        self.plan_order = QLineEdit()
        self.plan_order.setPlaceholderText("Ordre de la configuration")
        self.layout.addWidget(self.plan_order)

        self.launch_plan_button = QPushButton("Initialiser le plan")
        self.layout.addWidget(self.launch_plan_button)


    def get_parameters(self):
        parameters = {}
        for i in range(1, 4):
            try:
                min_val = float(self.component_inputs[f"component_{i}_min"].text())
                max_val = float(self.component_inputs[f"component_{i}_max"].text())
            except ValueError:
                min_val, max_val = 0, 100

            name = self.component_names[f"component_{i}_name"].text()
            if not name:
                name = f"Composant {i}"
            self.names[i-1].setText(name)
            self.names[i-1].setToolTip(name)

            # Changement des placeholders
            self.component_names[f"component_{i}_name"].setPlaceholderText(name)
            self.component_inputs[f"component_{i}_min"].setPlaceholderText(f"Valeur min {name}")
            self.component_inputs[f"component_{i}_max"].setPlaceholderText(f"Valeur max {name}")

            # Ajout des paramètres dans le dictionnaire
            parameters[f"component_{i}"] = {
                "min": min_val,
                "max": max_val,
                "name": name,
            }
        return parameters


    def launch_initial_plan(self):
        """Lance la configuration de plan d'expérience."""
        selected_plan = self.initial_points_selector.currentText()
        order = self.plan_order.text()
        if selected_plan and order:
            try:
                order = int(order)
                if order < 1:
                    raise ValueError("L'ordre doit être supérieur à 0")
            except ValueError:
                print("Erreur : L'ordre doit être un entier positif.")
                return

            # Récupérer la classe de points correspondante
            points_class = POINTS_LISTS[selected_plan]
            points = points_class[3,order].get_points()
            print(f"Points initiaux pour {selected_plan} (ordre {order}) : {points}")
        
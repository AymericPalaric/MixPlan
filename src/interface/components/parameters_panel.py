from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QHBoxLayout, QTextEdit
from PyQt5.QtCore import Qt, QTimer

from src.algo.points_lists import *
from src.interface.utils.logger import gui_logger
from src.interface.utils.console import SmartConsole

POINTS_LISTS = {
    "SimplexCentroid": SimplexCentroid(),
    "ScheffeNetwork": ScheffeNetwork(),
    "SimplexCentroidGrowth": SimplexCentroidGrowth(),
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

            self.names.append(QLabel(f"Contraintes pour Composant {i}"))
            self.layout.addWidget(self.names[-1])

            # Champs min/max (collés horizontalement)
            min_max_layout = QHBoxLayout()
            # min_max_layout.setAlignment(Qt.AlignLeft)
            min_max_layout.setSpacing(10)
            min_input = QLineEdit()
            min_input.setPlaceholderText(f"Valeur min composant {i}")
            min_max_layout.addWidget(min_input)
            min_max_layout.addStretch(1)

            max_input = QLineEdit()
            max_input.setPlaceholderText(f"Valeur max composant {i}")
            min_max_layout.addWidget(max_input)
            min_max_layout.addStretch(1)
            self.layout.addLayout(min_max_layout)

            self.component_inputs[f"component_{i}_min"] = min_input
            self.component_inputs[f"component_{i}_max"] = max_input

        self.update_button = QPushButton("Mettre à jour")
        self.layout.addWidget(self.update_button)

        if parent:
            self.update_button.clicked.connect(parent.update_graph_and_scores)
        
        self.layout.addSpacing(70)
        # Menu déroulant pour choisir la liste de points initiaux
        self.layout.addWidget(QLabel("Sélectionner une configuration de plan d'expérience :"))
        plan_type_order = QHBoxLayout()
        self.initial_points_selector = QComboBox()
        self.initial_points_selector.addItems(POINTS_LISTS.keys())
        plan_type_order.addWidget(self.initial_points_selector)

        self.plan_order = QLineEdit()
        self.plan_order.setPlaceholderText("Ordre de la configuration")
        plan_type_order.addWidget(self.plan_order)
        self.layout.addLayout(plan_type_order)

        # On selector switch, change enabled state of order input
        self.initial_points_selector.currentTextChanged.connect(self.enable_plan_order)

        self.launch_plan_button = QPushButton("Initialiser le plan")
        self.layout.addWidget(self.launch_plan_button)

        # Ajout d’un champ console pour les logs
        self.console = SmartConsole()
        # self.console.setFixedHeight(150)  # ajustable selon ton besoin
        self.console.setStyleSheet("background-color: #1e1e1e; color: white; font-family: Consolas;")
        self.layout.addWidget(QLabel("Console :"))
        self.layout.addWidget(self.console)

        gui_logger.log_signal.connect(self.log)


    def get_parameters(self):
        parameters = {}
        for i in range(1, 4):
            try:
                min_val = float(self.component_inputs[f"component_{i}_min"].text())
            except ValueError:
                min_val = None
            try:
                max_val = float(self.component_inputs[f"component_{i}_max"].text())
            except ValueError:
                max_val = None

            name = self.component_names[f"component_{i}_name"].text()
            if not name:
                name = f"Composant {i}"
            self.names[i-1].setText(f"Contraintes pour {name}")
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
                gui_logger.log("L'ordre doit être un entier positif.", level="error")
                return

            # Récupérer la classe de points correspondante
            points_class = POINTS_LISTS[selected_plan]
            points = points_class[3,order].get_points()
            gui_logger.log(f"Points initiaux pour {selected_plan} (ordre {order}) : {points}")
    
    def log(self, message, level="INFO"):
        level = level.upper()
        color = {
            "ERROR": "red",
            "WARNING": "orange",
            "INFO": "white",
            "USER_ACTION": "yellow",  # pour clignotement
        }.get(level, "white")

        # Ajout avec style
        formatted = f'<span style="color:{color}">{message}</span>'
        self.console.append(formatted)

        # Effet clignotant pour USER_ACTION
        if level == "USER_ACTION":
            self.blink_text(message)

    def blink_text(self, msg):
        def toggle_visibility():
            if self.console.toPlainText().endswith(msg):
                # remove the last line (the blinking message)
                cursor = self.console.textCursor()
                cursor.movePosition(cursor.End, cursor.MoveAnchor)
                cursor.select(cursor.BlockUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()
                self.console.setTextCursor(cursor)
            else:
                self.console.append(f'<span style="color:yellow">{msg}</span>')

        # Faire clignoter 3 fois
        timer = QTimer(self)
        timer.setInterval(300)
        count = {"value": 0}

        def update():
            toggle_visibility()
            count["value"] += 1
            if count["value"] >= 10:
                timer.stop()

        timer.timeout.connect(update)
        timer.start()
    
    def enable_plan_order(self, text):
        """Active ou désactive le champ d'ordre selon la sélection de la configuration."""
        if text:
            self.plan_order.setEnabled(POINTS_LISTS[text].order)
        else:
            self.plan_order.setEnabled(True)
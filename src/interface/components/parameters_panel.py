from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QHBoxLayout, QTextEdit, QGroupBox
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
        label = QLabel("Paramètres des composants")
        label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.layout.addWidget(label)

        self.component_inputs = {}
        self.component_names = {}
        self.names = []

        for i in range(1, 4):
            group_box = QGroupBox(f"Composant {i}")
            group_box.setStyleSheet("QGroupBox { font-style: italic; }")
            group_layout = QVBoxLayout()
            group_box.setLayout(group_layout)

            # Champ pour le nom
            name_input = QLineEdit()
            name_input.setPlaceholderText(f"Nom du composant {i}")
            group_layout.addWidget(name_input)
            self.component_names[f"component_{i}_name"] = name_input

            self.names.append(QLabel(f"Contraintes pour Composant {i}"))
            group_layout.addWidget(self.names[-1])

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
            group_layout.addLayout(min_max_layout)

            self.layout.addWidget(group_box)

            self.component_inputs[f"component_{i}_min"] = min_input
            self.component_inputs[f"component_{i}_max"] = max_input

        total_mass = QLineEdit()
        total_mass.setPlaceholderText("Masse totale du mélange (g)")
        self.layout.addWidget(total_mass)
        self.component_inputs["total_mass"] = total_mass
        self.update_button = QPushButton("Mettre à jour")
        self.layout.addWidget(self.update_button)

        if parent:
            self.update_button.clicked.connect(parent.update_graph_and_scores)
        
        self.layout.addSpacing(10)
        experience_gbox = QGroupBox("Plan d'expérience")
        experience_layout = QVBoxLayout()
        experience_gbox.setLayout(experience_layout)
        experience_gbox.setStyleSheet("QGroupBox { font-weight: bold; }")
        # Menu déroulant pour choisir la liste de points initiaux
        plan_type_order = QHBoxLayout()
        self.initial_points_selector = QComboBox()
        self.initial_points_selector.addItems(POINTS_LISTS.keys())
        plan_type_order.addWidget(self.initial_points_selector)

        self.plan_order = QLineEdit()
        self.plan_order.setPlaceholderText("Ordre de la configuration")
        plan_type_order.addWidget(self.plan_order)
        experience_layout.addLayout(plan_type_order)

        # On selector switch, change enabled state of order input
        self.initial_points_selector.currentTextChanged.connect(self.enable_plan_order)

        buttons_layout = QHBoxLayout()
        self.launch_plan_button = QPushButton("Initialiser le plan d'expérience")
        self.reset_plan_button = QPushButton("Réinitialiser plan d'expérience")
        buttons_layout.addWidget(self.launch_plan_button)
        buttons_layout.addWidget(self.reset_plan_button)
        experience_layout.addLayout(buttons_layout)
        if parent:
            self.reset_plan_button.clicked.connect(parent.reset_experiment_plan)
        self.layout.addWidget(experience_gbox)

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
                name = f"Comp{i}"
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
        parameters["total_mass"] = self.component_inputs["total_mass"].text()
        # Vérification de la masse totale
        try:
            total_mass_txt = parameters["total_mass"]
            total_mass = float(total_mass_txt)
            if total_mass <= 0:
                raise ValueError("La masse totale doit être supérieure à 0")
        except ValueError:
            if total_mass_txt == "":
                total_mass = None
            else:
                gui_logger.log("La masse totale doit être un nombre positif.", level="error")
                total_mass = None
            parameters["total_mass"] = total_mass
        return parameters


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
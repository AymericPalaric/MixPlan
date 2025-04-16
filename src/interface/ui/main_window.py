from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSplitter
from PyQt5.QtCore import Qt
import numpy as np
from src.algo.points_lists import TypeIIIPlan
from src.interface.components.parameters_panel import ParametersPanel, POINTS_LISTS
from src.interface.components.ternary_graph import TernaryGraph
from src.interface.components.scores_panel import ScoresPanel
from src.interface.utils.logger import gui_logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Outil de Graphe Ternaire")

        # Création des composants
        self.parameters_panel = ParametersPanel(parent=self)
        self.ternary_graph = TernaryGraph()
        self.scores_panel = ScoresPanel()

        # Connexions
        self.scores_panel.add_button.clicked.connect(self.add_point_to_graph)
        self.scores_panel.points_table.cellChanged.connect(self.edit_point_in_graph)
        self.scores_panel.interpolate_button.clicked.connect(self.interpolate_graph)
        self.ternary_graph.enable_click_callback(self.update_score_inputs_from_graph_click)
        self.parameters_panel.launch_plan_button.clicked.connect(self.launch_plan)
        # Mise en page avec QSplitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.parameters_panel)
        splitter.addWidget(self.ternary_graph)
        splitter.addWidget(self.scores_panel)

        # Définir les proportions initiales
        splitter.setStretchFactor(0, 2)  # Panneau des paramètres : 1 part
        splitter.setStretchFactor(1, 3)  # Graphe ternaire : 2 parts (50 %)
        splitter.setStretchFactor(2, 1)  # Panneau des scores : 1 part

        # Définir le widget central
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(splitter)
        self.setCentralWidget(central_widget)

        # Lancer en plein écran
        self.showMaximized()

        self.ignore_table_changes = False
        self.polygon = None

    def add_point_to_graph(self):
        """Ajoute un point au graphe depuis le ScoresPanel."""
        point_data = self.scores_panel.get_point_data()
        if point_data:
            x, y, z, score = point_data
            self.ternary_graph.add_point(x, y, z, score)
            self.scores_panel.update_points_table((x, y, z, score))
            self.scores_panel.x_input.clear()
            self.scores_panel.y_input.clear()
            self.scores_panel.z_input.clear()
            self.scores_panel.score_input.clear()
            gui_logger.log("Point ajouté :", point_data)
    
    def edit_point_in_graph(self, row):
        """Modifie un point déjà affiché sur le graphe suite à l'édition du tableau."""
        if self.ignore_table_changes:
            return

        try:
            x = float(self.scores_panel.points_table.item(row, 0).text())
            y = float(self.scores_panel.points_table.item(row, 1).text())
            z = float(self.scores_panel.points_table.item(row, 2).text())
            score = float(self.scores_panel.points_table.item(row, 3).text())
            self.ternary_graph.update_point(row, x, y, z, score)
            gui_logger.log(f"Point modifié (ligne {row}) -> ({x}, {y}, {z}) score {score}")
        except ValueError as e:
            gui_logger.log("Erreur lors de la modification du point :", e, level="warning")
        except AttributeError as e:
            pass

    def interpolate_graph(self):
        """Effectue une interpolation sur le graphe."""
        interpolated_scores = self.ternary_graph.interpolate(self.scores_panel.interpolator)
        if interpolated_scores is not None:
            gui_logger.log("Interpolation effectuée.")

    def update_graph_and_scores(self):
        """Met à jour le graphe ternaire et le panneau des scores en fonction des paramètres."""
        parameters = self.parameters_panel.get_parameters()
        gui_logger.log("Mise à jour avec les paramètres :", parameters)
        polygon = self.ternary_graph.update_with_parameters(parameters)
        self.update_hull(polygon)
    
    def update_score_inputs_from_graph_click(self, a, b, c):
        """Met à jour les champs du ScoresPanel avec les coordonnées ternaires du clic."""
        self.scores_panel.x_input.setText(f"{a:.3f}")
        self.scores_panel.y_input.setText(f"{b:.3f}")
        self.scores_panel.z_input.setText(f"{c:.3f}")
        self.scores_panel.score_input.setFocus()
    

    def launch_plan(self):
        """Lance le plan d'expérience sélectionné."""
        selected_plan = self.parameters_panel.initial_points_selector.currentText()
        order = self.parameters_panel.plan_order.text()
        parameters = self.parameters_panel.get_parameters()
        min_values = [parameters[f"component_{i}"]["min"] or 0 for i in range(1, 4)]
        max_values = [parameters[f"component_{i}"]["max"] or 100 for i in range(1, 4)]
        real_max_values = [min(max_values[i], 100 - min_values[(i+1)%3] - min_values[(i+2)%3]) for i in range(3)]
        real_min_values = min_values # [min_values[i] + max_values[(i+1)%3] + max_values[(i+2)%3] for i in range(3)]
        try:
            order = int(order) if selected_plan != "Type III" else order
        except ValueError:
            if POINTS_LISTS[selected_plan].order:
                gui_logger.log("Ordre de configuration invalide", level="warning")
                return

        order = int(order) if order.isdigit() else 0
        # update points coordinates with min and max values
        points = [
            [
                (real_min_values[i] + (real_max_values[i] - real_min_values[i]) * p[i])/100 for i in range(3)
            ]
            for p in POINTS_LISTS[selected_plan][3, order]
        ] if selected_plan != "Type III" else POINTS_LISTS[selected_plan][3, order]
        points_data = [
            (points[i][0], points[i][1], points[i][2], 0) for i in range(len(points))
        ]
        if selected_plan == "Type III":
            X = np.array(points)
            gui_logger.log("Score de l'algorithm de Fedorov (D-Optimality) :", np.linalg.det(X.T @ X))
        self.ternary_graph.set_initial_points(points)
        self.scores_panel.clear_scores_table()
        for point in points_data:
            self.scores_panel.update_points_table(point)
        gui_logger.log(f"Lancement du plan d'expérience : {selected_plan} avec ordre {order}")
        gui_logger.log("N'oubliez pas de modifier les scores dans le tableau !", level="user_action")

    def update_hull(self, polygon):
        self.polygon = polygon
        # Si plus de 3 sommets, changer la liste de initial_points_selector du param_panel
        if len(polygon) > 3:
            POINTS_LISTS["Type III"] = TypeIIIPlan(polygon)
            self.parameters_panel.initial_points_selector.clear()
            self.parameters_panel.initial_points_selector.addItems(["Type III",])
            self.parameters_panel.initial_points_selector.setCurrentText("Type III")
            self.parameters_panel.plan_order.setEnabled(False)
            self.parameters_panel.plan_order.clear()
        else:
            # Revenir à la liste de points par défaut : remover Type III
            if "Type III" in POINTS_LISTS:
                del POINTS_LISTS["Type III"]
            self.parameters_panel.plan_order.setEnabled(True)
            self.parameters_panel.initial_points_selector.clear()
            self.parameters_panel.initial_points_selector.addItems(POINTS_LISTS.keys())
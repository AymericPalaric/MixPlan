from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from src.interface.components.parameters_panel import ParametersPanel
from src.interface.components.ternary_graph import TernaryGraph
from src.interface.components.scores_panel import ScoresPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Outil de Graphe Ternaire")

        # Création des composants
        self.parameters_panel = ParametersPanel()
        self.ternary_graph = TernaryGraph()
        self.scores_panel = ScoresPanel()

        # Connexions
        self.scores_panel.add_button.clicked.connect(self.add_point_to_graph)
        self.scores_panel.interpolate_button.clicked.connect(self.interpolate_graph)

        # Mise en page
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.parameters_panel)
        layout.addWidget(self.ternary_graph)
        layout.addWidget(self.scores_panel)
        self.setCentralWidget(central_widget)

    def add_point_to_graph(self):
        """Ajoute un point au graphe depuis le ScoresPanel."""
        point_data = self.scores_panel.get_point_data()
        if point_data:
            x, y, score = point_data
            self.ternary_graph.add_point(x, y, score)
            self.scores_panel.scores_list.addItem(f"Point ({x}, {y}) - Score: {score}")

    def interpolate_graph(self):
        """Effectue une interpolation sur le graphe."""
        interpolated_scores = self.ternary_graph.interpolate()
        if interpolated_scores is not None:
            print("Interpolation effectuée.")
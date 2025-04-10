from PyQt5.QtWidgets import QWidget, QVBoxLayout
import ternary
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from scipy.interpolate import LinearNDInterpolator

class TernaryGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Création de la figure matplotlib pour le graphe ternaire
        self.figure, self.tax = ternary.figure(scale=100)
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Initialisation des données
        self.points = []  # Liste des points ajoutés (ternary coordinates)
        self.scores = []  # Liste des scores associés

        # Configuration initiale du graphe
        self.initialize_graph()

    def initialize_graph(self):
        """Initialise le graphe ternaire."""
        self.figure.clear()
        self.tax.boundary(linewidth=2.0)
        self.tax.gridlines(color="black", multiple=20)
        self.tax.gridlines(color="blue", multiple=10, linewidth=0.5)

        # Définir les labels des axes
        fontsize = 15
        self.tax.left_axis_label("Composant 1", fontsize=fontsize)
        self.tax.right_axis_label("Composant 2", fontsize=fontsize)
        self.tax.bottom_axis_label("Composant 3", fontsize=fontsize)

        # Supprimer les ticks par défaut de Matplotlib
        self.tax.clear_matplotlib_ticks()
        self.canvas.draw()

    def add_point(self, a, b, c, score):
        """Ajoute un point au graphe avec un score associé."""
        if not np.isclose(a + b + c, 1.0):
            raise ValueError("Les proportions doivent totaliser 1.0")
        self.points.append((a, b, c))
        self.scores.append(score)
        self.update_graph()

    def update_graph(self):
        """Met à jour l'affichage du graphe."""
        self.initialize_graph()

        # Ajouter les points au graphe
        if self.points:
            scaled_points = [(p[0] * 100, p[1] * 100, p[2] * 100) for p in self.points]
            self.tax.scatter(scaled_points, marker='o', color='red', label="Points")

        self.canvas.draw()

    def interpolate(self):
        """Effectue une interpolation sur les points existants."""
        if len(self.points) < 3:
            return None  # Pas assez de points pour interpoler

        # Convertir les coordonnées ternaires en coordonnées cartésiennes
        def ternary_to_cartesian(t):
            total = sum(t)
            if total == 0:
                return (0, 0)
            x = 0.5 * (2 * t[1] + t[2]) / total
            y = (np.sqrt(3) / 2) * t[2] / total
            return (x, y)

        points_cartesian = np.array([ternary_to_cartesian(p) for p in self.points])
        scores = np.array(self.scores)

        # Créer l'interpolateur
        interpolator = LinearNDInterpolator(points_cartesian, scores)

        # Définir la fonction de heatmap
        def heatmap_function(p):
            cart = np.array([ternary_to_cartesian(p)])
            score = interpolator(cart)
            return float(score) if not np.isnan(score) else 0

        # Appliquer la heatmap au graphe
        self.tax.heatmapf(heatmap_function, boundary=True, style="triangular")
        self.canvas.draw()
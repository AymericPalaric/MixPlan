from PyQt5.QtWidgets import QWidget, QVBoxLayout
import ternary
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from scipy.interpolate import LinearNDInterpolator
from matplotlib.figure import Figure

class TernaryGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Créer une figure matplotlib standard
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Initialisation des données
        self.points = []  # Liste des points ajoutés (ternary coordinates)
        self.scores = []  # Liste des scores associés
        self.parameters = None  # Stockage des paramètres min/max/nom
        self.R2_score = None  # Stockage du score R2

        # Configuration initiale du graphe
        self.initialize_graph()
    
    def set_initial_points(self, points):
        """Définir les points initiaux pour le graphe."""
        self.points = points
        self.scores = [0] * len(points)
        self.update_graph()

    def initialize_graph(self):
        """Initialise le graphe ternaire."""
        # Supprimer les axes matplotlib
        for ax in self.figure.axes:
            self.figure.delaxes(ax)
        self.ax = self.figure.add_subplot(111)
        self.tax = ternary.TernaryAxesSubplot(ax=self.ax, scale=100)

        # Configuration du triangle
        self.tax.boundary(linewidth=2.0)
        self.tax.gridlines(color="blue", multiple=10, linewidth=0.5)

        # Définir les labels des axes
        fontsize = 15
        if self.parameters is not None:
            # Utiliser les noms des composants si disponibles
            self.tax.left_axis_label(f'{self.parameters["component_3"]["name"]} (%)', fontsize=fontsize)
            self.tax.right_axis_label(f'{self.parameters["component_2"]["name"]} (%)', fontsize=fontsize)
            self.tax.bottom_axis_label(f'{self.parameters["component_1"]["name"]} (%)', fontsize=fontsize)
        else:
            # Noms par défaut
            self.tax.left_axis_label("Composant 3", fontsize=fontsize)
            self.tax.right_axis_label("Composant 2", fontsize=fontsize)
            self.tax.bottom_axis_label("Composant 1", fontsize=fontsize)

        self.tax.ticks(axis='lbr', linewidth=1, multiple=10)

        # Supprimer les ticks de matplotlib
        self.tax.clear_matplotlib_ticks()

        if self.R2_score is not None:
            self.tax.set_title(f"R²: {self.R2_score:.2f}", fontsize=fontsize)

        # Redessiner
        self.canvas.draw()

    def add_point(self, a, b, c, score):
        """Ajoute un point au graphe avec un score associé."""
        if not np.isclose(a + b + c, 1.0, atol=1e-2):
            raise ValueError("Les proportions doivent totaliser 1.0")
        self.points.append((a, b, c))
        self.scores.append(score)
        self.update_graph()

    def update_graph(self, hm=False):
        """Met à jour l'affichage du graphe."""
        self.initialize_graph()
        if hm:
            self.tax.heatmapf(hm, boundary=True, style="triangular")

        # Ajouter les points au graphe
        if self.points:
            scaled_points = [(p[0] * 100, p[1] * 100, p[2] * 100) for p in self.points]
            self.tax.scatter(scaled_points, marker='o', color='red', label="Points")
        self.canvas.draw()

    def interpolate(self, interpolator_cls):
        """Effectue une interpolation sur les points existants."""
        points = np.array(self.points)
        scores = np.array(self.scores)
        if len(self.points) < interpolator_cls.min_num_points:
            print("Pas assez de points pour interpoler")
            return None

        # Créer l'interpolateur
        interpolator = interpolator_cls(points, scores)
        self.R2_score = interpolator.R2_score()

        # Définir la fonction de heatmap
        def heatmap_function(p):
            score = interpolator(np.array(p))
            return float(score) if not np.isnan(score) else 0

        # Appliquer la heatmap au graphe
        self.update_graph(hm=heatmap_function)
        self.canvas.draw()

    def update_with_parameters(self, parameters):
        """
        Met à jour le graphe en fonction des paramètres min/max pour chaque composant.
        :param parameters: Dictionnaire contenant les valeurs min et max pour chaque composant.
        """
        self.parameters = parameters

        # Vérifier que les paramètres sont valides
        for component, values in parameters.items():
            if values["min"] is None or values["max"] is None:
                print(f"Paramètres invalides pour {component}: {values}")
                return

        # Réafficher les points existants
        self.update_graph()
    

    def update_point(self, row, a, b, c, score):
        """Met à jour un point existant dans le graphe."""
        if row < 0 or row >= len(self.points):
            raise IndexError("Index de ligne invalide")
        self.points[row] = (a, b, c)
        self.scores[row] = score
        self.update_graph()
    
    def enable_click_callback(self, callback):
        """Active le clic sur le graphe et appelle le callback avec les coordonnées ternaires."""
        def on_click(event):
            if event.inaxes is None:
                return

            x, y = event.xdata, event.ydata
            x /= self.tax.get_scale()
            y /= self.tax.get_scale()
            a, b, c = self.cartesian_to_ternary(x, y)
            if a is not None:
                callback(a, b, c)

        self.canvas.mpl_connect("button_press_event", on_click)

    def cartesian_to_ternary(self, x, y):
        """Convertit des coordonnées cartésiennes en coordonnées ternaires (a, b, c)."""
        if x is None or y is None:
            return None, None, None

        # Inverse de la transformation utilisée dans ternary_to_cartesian
        t = y / (np.sqrt(3) / 2)  # c
        b = (x - 0.5 * t) / 1.0  # b (approximation)
        a = 1.0 - b - t  # a
        if a < 0 or b < 0 or t < 0 or a + b + t > 1.01:
            return None, None, None

        return b, t, a
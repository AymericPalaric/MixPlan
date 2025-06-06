from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox
import ternary
from ternary.helpers import project_point
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from scipy.spatial import ConvexHull
from matplotlib.figure import Figure
from src.interface.utils.logger import gui_logger

class TernaryGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent_ = parent

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Créer une figure matplotlib standard
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self._is_panning = False
        self._pan_start = None

        self.canvas.mpl_connect("button_press_event", self.on_mouse_press)
        self.canvas.mpl_connect("button_release_event", self.on_mouse_release)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas.mpl_connect("scroll_event", self.on_scroll)
        self.layout.addWidget(self.canvas)

        # Initialisation des données
        self.points = []  # Liste des points ajoutés (ternary coordinates)
        self.scores = []  # Liste des scores associés
        self.parameters = None  # Stockage des paramètres min/max/nom
        self.R2_score = None  # Stockage du score R2
        self.constraint_mask = None  # Stockage de la heatmap des contraintes
        self.polygon = None  # Stockage de l'enveloppe convexe pour les contraintes

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

            # TODO :Prendre en compte les contraintes min/max :
            # -> Dessiner les lignes de contraintes pour chaque composant, dessinant ainsi un triangle intérieur
            for i in range(1, 4):
                min_val = self.parameters[f"component_{i}"]["min"]
                max_val = self.parameters[f"component_{i}"]["max"]
                if min_val is not None:
                    p1 = [None, None, None]
                    p2 = [None, None, None]
                    p1[i-1] = min_val
                    p1[i%3] = 0
                    p1[(i+1)%3] = 100 - min_val
                    p2[i-1] = min_val
                    p2[i%3] = 100 - min_val
                    p2[(i+1)%3] = 0
                    self.tax.line(p1, p2, color='red', linewidth=2, linestyle='--')
                if max_val is not None:
                    p1 = [None, None, None]
                    p2 = [None, None, None]
                    p1[i-1] = max_val
                    p1[i%3] = 0
                    p1[(i+1)%3] = 100 - max_val
                    p2[i-1] = max_val
                    p2[i%3] = 100 - max_val
                    p2[(i+1)%3] = 0
                    self.tax.line(p1, p2, color='red', linewidth=2, linestyle='--')
            # Griser les zones hors contraintes
            self.draw_constraints_overlay()
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
            # Ajouter les numéros à côté de chaque point
            for idx, pt in enumerate(scaled_points):
                # Décaler légèrement le texte pour qu'il ne soit pas sur le point
                offset = (2, 2, -4)  # Décalage arbitraire, à ajuster si besoin
                label_pos = tuple(pt[i] + offset[i] for i in range(3))
                self.tax.annotate(str(idx + 1), pt, fontsize=12, ha='left', va='bottom', color='black')
        self.canvas.draw()

    def interpolate(self, interpolator_cls):
        """Effectue une interpolation sur les points existants."""
        points = np.array(self.points)
        scores = np.array(self.scores)
        if len(self.points) < interpolator_cls.min_num_points:
            gui_logger.log("Pas assez de points pour interpoler", level="warning")
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
        self.constraint_mask = self.generate_constraint_mask()
        self.update_graph()
        return self.polygon
    

    def update_point(self, row, a, b, c, score):
        """Met à jour un point existant dans le graphe."""
        if row < 0:
            gui_logger.log(f"Index de ligne invalide : {row}", level="error")
            return
        if row >= len(self.points):
            gui_logger.log(f"Detection d'un nouveau point : {row}")
            self.points.append((a, b, c))
            self.scores.append(score)
        else:
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

    def ternary_to_cartesian(self, points):
        """
        Convertit une liste de points ternaires (a, b, c) en cartésien pour matplotlib.
        """
        from ternary.helpers import project_point
        return [project_point(p) for p in points]

    def generate_constraint_mask(self, resolution=2):
        """
        Génère un masque des zones hors contraintes en heatmap (valeurs 0 ou 1).
        """
        if self.parameters is None:
            return None

        func = self.constraint_mask_function()
        scale = 100
        d = resolution

        # Générer les triplets possibles
        data = {}
        for i in range(scale + 1):
            for j in range(scale + 1 - i):
                k = scale - i - j
                a, b, c = i / scale, j / scale, k / scale
                data[(i, j, k)] = func((a, b, c))

        return data

    def constraint_mask_function(self):
        """
        Crée une fonction qui retourne 1 pour les zones en dehors des contraintes, 0 sinon.
        Utilisée pour griser les zones invalides.
        """
        if self.parameters is None:
            return lambda p: 0  # Pas de contrainte

        def is_outside(p):
            a, b, c = p
            for i, comp in enumerate(['component_1', 'component_2', 'component_3']):
                val = [a, b, c][i]
                min_val = self.parameters[comp]["min"]
                max_val = self.parameters[comp]["max"]
                if (min_val is not None and val * 100 < min_val) or (max_val is not None and val * 100 > max_val):
                    return 1
            return 0

        return is_outside


    def draw_constraints_overlay(self):
        """
        Grise les zones hors contraintes en dessinant un masque via matplotlib.
        """
        if self.parameters is None:
            return

        constraints = self.parameters

        def get_bound(c, which):
            return constraints[c][which] if constraints[c][which] is not None else (0 if which == "min" else 100)

        min1 = get_bound("component_1", "min")
        max1 = get_bound("component_1", "max")
        min2 = get_bound("component_2", "min")
        max2 = get_bound("component_2", "max")
        min3 = get_bound("component_3", "min")
        max3 = get_bound("component_3", "max")

        valid = []
        max1 = int(max1) or 100
        max2 = int(max2) or 100
        max3 = int(max3) or 100
        min1 = int(min1) or 0
        min2 = int(min2) or 0
        min3 = int(min3) or 0
        for a in range(min1, max1 + 1, 2):
            for b in range(min2, max2 + 1, 2):
                c = 100 - a - b
                if min3 <= c <= max3 and a >= 0 and b >= 0 and c >= 0:
                    valid.append((a, b, c))

        if not valid:
            return

        pts_2d = np.array([[p[0], p[1]] for p in valid])
        try:
            hull = ConvexHull(pts_2d)
            polygon = [valid[i] for i in hull.vertices]
            self.polygon = polygon
        except:
            polygon = valid

        outer_triangle = [(0, 0, 100), (0, 100, 0), (100, 0, 0)]
        outer_cart = self.ternary_to_cartesian(outer_triangle)
        valid_cart = self.ternary_to_cartesian(polygon)

        # Dessiner le masque
        self.ax.fill(*zip(*outer_cart), color='lightgrey', alpha=0.4, zorder=0)
        self.ax.fill(*zip(*valid_cart), color='white', alpha=1.0, zorder=1)
    

    def on_scroll(self, event):
        base_scale = 1.2
        ax = self.ax

        # Zoom in
        if event.button == 'up':
            scale_factor = 1 / base_scale
        # Zoom out
        elif event.button == 'down':
            scale_factor = base_scale
        else:
            scale_factor = 1

        # Get current x and y limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        # Get mouse position in axis coordinates
        xdata = event.xdata
        ydata = event.ydata

        if xdata is None or ydata is None:
            return

        new_xlim = [
            xdata - (xdata - xlim[0]) * scale_factor,
            xdata + (xlim[1] - xdata) * scale_factor
        ]
        new_ylim = [
            ydata - (ydata - ylim[0]) * scale_factor,
            ydata + (ylim[1] - ydata) * scale_factor
        ]

        ax.set_xlim(new_xlim)
        ax.set_ylim(new_ylim)
        self.canvas.draw_idle()

    def on_mouse_press(self, event):
        if event.button == 3:  # clic droit
            # Tentative de suppression de point si clic sur un point
            index = self.find_closest_point_index(event.xdata, event.ydata)
            if index is not None:
                self.confirm_delete_point(index)
            else:
                # Sinon, activer le pan
                self._is_panning = True
                self._pan_start = (event.xdata, event.ydata)
    
    def delete_point(self, index):
        self.points.pop(index)
        self.scores.pop(index)
        self.update_graph()

    def confirm_delete_point(self, index):
        result = QMessageBox.question(
            self,
            "Supprimer ce point",
            f"Voulez-vous vraiment supprimer le point {index + 1} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if result == QMessageBox.Yes:
            # Optionnel : notifie le parent
            if hasattr(self.parent_, "on_point_deleted"):
                self.parent_.on_point_deleted(index)

    def on_mouse_release(self, event):
        if event.button == 3:
            self._is_panning = False
            self._pan_start = None

    def on_mouse_move(self, event):
        if not self._is_panning or event.xdata is None or event.ydata is None:
            return

        dx = self._pan_start[0] - event.xdata
        dy = self._pan_start[1] - event.ydata

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        self.ax.set_xlim(xlim[0] + dx, xlim[1] + dx)
        self.ax.set_ylim(ylim[0] + dy, ylim[1] + dy)
        self.canvas.draw_idle()

        self._pan_start = (event.xdata, event.ydata)
    
    def find_closest_point_index(self, x, y):
        if not self.points:
            return None

        # Conversion des points ternaires en coordonnées cartésiennes pour comparaison
        cart_points = self.ternary_to_cartesian([(a * 100, b * 100, c * 100) for a, b, c in self.points])
        distances = [np.hypot(x - xp, y - yp) for xp, yp in cart_points]
        min_dist = min(distances)
        if min_dist < 3:  # Seuil de proximité en pixels
            return distances.index(min_dist)
        return None
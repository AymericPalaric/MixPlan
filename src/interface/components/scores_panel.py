from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QHBoxLayout,
    QGroupBox, QFileDialog, QMenu, QAction
)
from PyQt5.QtCore import Qt
from functools import partial
from src.algo.interpolator import *
from src.interface.utils.logger import gui_logger
import csv
from datetime import datetime

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

        self.total_mass = None

        # Tableau de points (X, Y, Z, Score)
        self.points_table = QTableWidget()
        self.points_table.setColumnCount(4)
        self.points_table.setHorizontalHeaderLabels(["Comp1 (%)", "Comp2 (%)", "Comp3 (%)", "Score"])
        self.points_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.points_table.setEditTriggers(QTableWidget.AllEditTriggers)
        self.layout.addWidget(self.points_table)


        # Boutons pour importer et exporter les points
        self.import_export_layout = QHBoxLayout()
        self.layout.addLayout(self.import_export_layout)
        self.import_button = QPushButton("Importer")
        self.import_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.import_button.setToolTip("Importer un fichier de points.")
        self.import_export_layout.addWidget(self.import_button)
        self.export_button = QPushButton("Exporter")
        self.export_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.export_button.setToolTip("Exporter les points vers un fichier.")
        self.import_export_layout.addWidget(self.export_button)
        self.import_button.clicked.connect(self.import_points)
        self.export_button.clicked.connect(self.export_points)
        self.export_button.setEnabled(False)

        # Bouton pour afficher un popup qui donne les masses (à partir des pourcentages dans le tableau)
        self.show_masses_button = QPushButton("Afficher les masses")
        self.show_masses_button.setStyleSheet("QPushButton { font-weight: bold; }")
        self.layout.addWidget(self.show_masses_button)
        self.show_masses_button.clicked.connect(self.show_masses_popup)
        self.show_masses_button.setEnabled(False)
        self.show_masses_button.setToolTip("Rentrer une masse totale dans le panneau de gauche pour activer ce bouton.")

        # Champs pour ajouter un point
        addpoint_gbox = QGroupBox("Ajouter un point")
        addpoint_gbox.setStyleSheet("QGroupBox { font-weight: bold; font-style: italic; }")
        addpoint_layout = QVBoxLayout()
        addpoint_gbox.setLayout(addpoint_layout)
        self.layout.addWidget(addpoint_gbox)

        point_layout = QHBoxLayout()
        self.x_input = QLineEdit()
        self.x_input.setPlaceholderText("Comp1 (%)")
        point_layout.addWidget(self.x_input)

        self.y_input = QLineEdit()
        self.y_input.setPlaceholderText("Comp2 (%)")
        point_layout.addWidget(self.y_input)

        self.z_input = QLineEdit()
        self.z_input.setPlaceholderText("Comp3 (%)")
        point_layout.addWidget(self.z_input)

        self.score_input = QLineEdit()
        self.score_input.setPlaceholderText("Score")
        point_layout.addWidget(self.score_input)
        addpoint_layout.addLayout(point_layout)

        # Bouton pour ajouter un point
        self.add_button = QPushButton("Ajouter")
        addpoint_layout.addWidget(self.add_button)
        self.score_input.returnPressed.connect(self.add_button.click)

        # Menu déroulant pour sélectionner l'interpolateur
        interpolator_gbox = QGroupBox("Sélectionner un interpolateur")
        interpolator_gbox.setStyleSheet("QGroupBox { font-weight: bold; font-style: italic; }")
        interpolator_layout = QVBoxLayout()
        interpolator_gbox.setLayout(interpolator_layout)
        self.layout.addWidget(interpolator_gbox)
        self.interpolator_selector = QComboBox()
        self.interpolator_selector.addItems(INTERPOLATORS.keys())
        interpolator_layout.addWidget(self.interpolator_selector)

        # Bouton pour lancer l'interpolation
        self.interpolate_button = QPushButton("Interpoler")
        interpolator_layout.addWidget(self.interpolate_button)

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
            score = float(self.score_input.text()) if self.score_input.text() else 0.0
            return x, y, z, score
        except ValueError:
            return None

    def update_points_table(self, point_data):
        """Ajoute un point dans le tableau."""
        self.export_button.setEnabled(True)
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
        self.clear_scores_table()

    def update_interpolator(self):
        """Met à jour l'interpolateur sélectionné."""
        selected_name = self.interpolator_selector.currentText()
        self.interpolator = INTERPOLATORS[selected_name]
        gui_logger.log(f"Interpolateur sélectionné : {selected_name}")

    def update_with_parameters(self, parameters):
        """Met à jour le tableau avec les paramètres."""
        # self.clear_scores_table()
        inputs = [self.x_input, self.y_input, self.z_input]
        for i in range(1, 4):
            name = parameters[f"component_{i}"]["name"] + " (%)"
            if not name:
                name = f"Comp{i} (%)"
            self.points_table.setHorizontalHeaderItem(i-1, QTableWidgetItem(name))
            inputs[i-1].setPlaceholderText(name)
        
        self.total_mass = parameters["total_mass"]
        if self.total_mass:
            self.show_masses_button.setEnabled(True)
            self.show_masses_button.setToolTip("Afficher les masses calculées à partir des pourcentages.")
        else:
            self.show_masses_button.setEnabled(False)
            self.show_masses_button.setToolTip("Rentrer une masse totale dans le panneau de gauche pour activer ce bouton.")
    

    def show_masses_popup(self):
        """Affiche un popup avec les masses calculées à partir des pourcentages."""
        if self.total_mass is None:
            gui_logger.log("Aucune masse totale spécifiée.", level="error")
            return

        if not hasattr(self, 'mass_popup') or self.mass_popup is None or not self.mass_popup.isVisible():
            self.mass_popup = MassPopup(self)
        self.mass_popup.show()
        self.mass_popup.raise_()
        self.mass_popup.activateWindow()

    def export_points(self):
        """Exporte les points vers un fichier csv."""
        options = QFileDialog.Options()
        default_path = f"essai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les points", default_path, "CSV Files (*.csv);;All Files (*)", options=options
        )
        if not file_path:
            return  # L'utilisateur a annulé

        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Écrire les en-têtes
                headers = [self.points_table.horizontalHeaderItem(i).text() for i in range(4)]
                writer.writerow(headers)

                # Écrire les données
                for row in range(self.points_table.rowCount()):
                    row_data = [
                        self.points_table.item(row, col).text()
                        if self.points_table.item(row, col) else ""
                        for col in range(4)
                    ]
                    writer.writerow(row_data)

            QMessageBox.information(self, "Succès", "Les points ont été exportés avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur s'est produite lors de l'exportation : {e}")
            gui_logger.log(f"Erreur lors de l'exportation des points : {e}", level="error")
    
    def import_points(self):
        """Importe les points depuis un fichier csv."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importer les points", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if not file_path:
            return
        
        try:
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader)  # Lire les en-têtes
                if len(headers) != 4:
                    raise ValueError("Le fichier doit contenir exactement 4 colonnes.")

                self.clear_scores_table()
                for row in reader:
                    if len(row) != 4:
                        continue  # Ignorer les lignes incorrectes
                    try:
                        point_data = [float(value) for value in row]
                        self.update_points_table(point_data)
                    except ValueError:
                        continue  # Ignorer les lignes avec des valeurs non numériques

            QMessageBox.information(self, "Succès", "Les points ont été importés avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur s'est produite lors de l'importation : {e}")
            gui_logger.log(f"Erreur lors de l'importation des points : {e}", level="error")

    def delete_point(self, row):
        self.points_table.removeRow(row)
        if self.points_table.rowCount() == 0:
            self.export_button.setEnabled(False)
            self.show_masses_button.setEnabled(False)

class MassPopup(QWidget):
    def __init__(self, parent: ScoresPanel = None):
        super().__init__(parent)
        self.parent_scores_panel = parent
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("Masse des points")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Tableau des masses
        self.masses_list = QTableWidget()
        self.masses_list.setColumnCount(3)
        
        column_names = [self.parent_scores_panel.points_table.horizontalHeaderItem(i).text().replace("%", "g") for i in range(3)]
        self.masses_list.setHorizontalHeaderLabels(column_names)

        # ➔ Options pour rendre le tableau copiable mais pas éditable
        self.masses_list.setEditTriggers(QTableWidget.NoEditTriggers)
        self.masses_list.setSelectionBehavior(QTableWidget.SelectItems)
        self.masses_list.setSelectionMode(QTableWidget.ExtendedSelection)
        self.masses_list.setStyleSheet("""
            QTableWidget {
                selection-background-color: #0078D7;
                selection-color: white;
            }
        """)
        
        self.layout.addWidget(self.masses_list)

        # Remplir les données
        self.populate_masses_table()

        # Bouton fermer
        self.close_button = QPushButton("Fermer")
        self.close_button.clicked.connect(self.close)
        self.layout.addWidget(self.close_button)

        self.adjustSize()

    def populate_masses_table(self):
        """Remplit le tableau avec les masses calculées à partir des pourcentages."""
        self.masses_list.setRowCount(0)
        for i in range(self.parent_scores_panel.points_table.rowCount()):
            row_position = self.masses_list.rowCount()
            self.masses_list.insertRow(row_position)
            for j in range(3):
                percentage_item = self.parent_scores_panel.points_table.item(i, j)
                if percentage_item is None:
                    continue
                try:
                    percentage = float(percentage_item.text())
                except (ValueError, AttributeError):
                    percentage = 0.0

                mass = percentage * float(self.parent_scores_panel.total_mass)
                item = QTableWidgetItem(str(round(mass, 3)))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Lecture seule mais copiable
                self.masses_list.setItem(row_position, j, item)

        self.masses_list.resizeColumnsToContents()
        self.masses_list.resizeRowsToContents()
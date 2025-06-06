# MixPlan

MixPlan est une application graphique interactive pour la conception, la visualisation et l’analyse de plans d’expériences de mélanges ternaires. Elle permet de générer des plans de mélange, de saisir des scores expérimentaux, d’interpoler les résultats et de visualiser les contraintes et les résultats sur un graphe ternaire.

## Fonctionnalités

- **Définition des composants** : Saisie des noms, contraintes minimales et maximales, et masse totale du mélange.
- **Génération de plans d’expériences** :
  - Simplex Centroid
  - Réseau de Scheffé (Simplex Lattice)
  - Simplex Centroid Growth
  - Type III (D-optimalité via l’algorithme de Fedorov)
- **Ajout et édition de points** : Ajout manuel ou import/export de points (CSV), édition directe dans un tableau.
- **Calcul et affichage des scores** : Saisie des scores, calcul de masses à partir des pourcentages et de la masse totale.
- **Interpolation** : Interpolation linéaire, quadratique, RBF, etc., avec affichage du R².
- **Visualisation graphique** :
  - Graphe ternaire interactif (zoom, pan, clic pour ajouter un point)
  - Affichage des contraintes sous forme de zones grisées
  - Affichage des points expérimentaux et des surfaces interpolées
- **Console intégrée** : Affichage des logs et des actions utilisateur.

## Installation

### Prérequis

- Python 3.10+
- [pip](https://pip.pypa.io/en/stable/)
- (Optionnel) Environnement virtuel recommandé

### Dépendances

Les dépendances sont listées dans [requirements.txt](requirements.txt) :

- python-ternary
- numpy
- scipy
- PyQt5
- pyqtgraph
- scikit-learn

Installation :

```sh
pip install -r requirements.txt
```

### Lancement
Pour lancer l'application, exécutez le script principal :

```sh
python main.py
```

## Structure du projet
Le projet est structuré comme suit :

```
MixPlan/
│
├── main.py                      # Point d'entrée principal de l'application
├── requirements.txt             # Dépendances Python
├── README.md                    # Ce fichier
├── MixPlanApp.spec              # Spécification PyInstaller pour la génération de l'exécutable
├── tools/
│   └── build.sh                 # Script de build pour générer l'exécutable
│
└── src/
    ├── algo/
    │   ├── interpolator.py      # Interpolateurs (RBF, linéaire, quadratique, etc.)
    │   └── points_lists.py      # Génération des plans de points (Simplex, Scheffé, etc.)
    ├── interface/
    │   ├── components/
    │   │   ├── parameters_panel.py  # Panneau de saisie des paramètres
    │   │   ├── scores_panel.py      # Tableau des points et scores
    │   │   └── ternary_graph.py     # Widget de graphe ternaire interactif
    │   ├── ui/
    │   │   ├── main_window.py       # Fenêtre principale (logique)
    │   │   └── main_window.ui       # Fichier Qt Designer (layout)
    │   └── utils/
    │       ├── logger.py            # Logger pour la console GUI
    │       ├── console.py           # Widget console
    │       └── data_processing.py   # Fonctions de conversion et calculs
    └── __init__.py                  # Fichier d'initialisation du package
```

## Utilisation
1. **Définir les composants** : Renseignez les noms, contraintes min/max et la masse totale dans le panneau de gauche.
2. **Choisir un plan d’expérience** : Sélectionnez le type de plan et l’ordre, puis cliquez sur « Initialiser le plan d’expérience ».
3. **Saisir les scores** : Ajoutez ou éditez les scores dans le tableau ou importez-les depuis un fichier CSV.
4. **Visualiser et interpoler** : Sélectionnez un interpolateur et cliquez sur « Interpoler » pour afficher la surface d’interpolation sur le graphe ternaire.
5. **Exporter les résultats** : Exportez les points et scores au format CSV.

## Génération de l'exécutable
Pour générer un exécutable Windows :

```sh
cd tools
bash build.sh
```
L'exécutable sera disponible dans le dossier tools/MixPlanApp.exe.

## Auteurs
- Aymeric Palaric

## Licence
Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

**Remarque** : MixPlan est conçu pour l’expérimentation et l’optimisation de mélanges à 3 composants, avec une interface graphique intuitive et des outils avancés d’analyse de plans d’expériences.
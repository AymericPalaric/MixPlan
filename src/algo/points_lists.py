from itertools import combinations_with_replacement, combinations
import numpy as np
from src.interface.utils.data_processing import cartesian_to_ternary, ternary_to_cartesian

__all__ = [
    "SimplexCentroid",
    "ScheffeNetwork",
    "TypeIIIPlan",
    ]

class SimplexCentroid:
    """
    A class to represent a simplex centroid mixture design.

    A (k, m) simplex centroid plan consists of:
        - all mixtures of 1 to k components in equal proportions,
        - repeated according to the degree m,
        - totaling k * m + 1 points.
    """

    def __getitem__(self, config):
        """
        Generate the simplex centroid design.

        Parameters:
            config (tuple): (k, m)
                - k: number of components
                - m: degree of the model to approximate

        Returns:
            List[Tuple[float, ...]]: list of points (each point is a tuple of k proportions)
        """
        k, m = config
        assert m < k, "Degree m must be less than number of components k"
        if m < 1 or k < 1:
            raise ValueError("k and m must be >= 1")

        points = []

        # For each degree d from 1 to m
        for d in range(1, m + 1):
            # Generate all combinations of d components (no repetition in indices)
            for combo in combinations(range(k), d):
                # Create a proportion vector for this combination
                p = [0.0] * k
                for idx in combo:
                    p[idx] = 1.0 / d
                # Repeat this configuration m times (as in standard centroid design)
                points.append(tuple(p))

        # Add the centroid point: all components equal
        centroid = tuple([1.0 / k] * k)
        points.append(centroid)

        return points


class ScheffeNetwork:
    """
    Generate a simplex lattice (Scheffé network) design.

    A (k, m) network corresponds to all combinations of (k) components
    whose proportions are multiples of 1/m and sum to 1.

    The resulting design has C(m + k - 1, m) points.
    """

    def __getitem__(self, config):
        """
        Parameters:
            config (tuple): (k, m)
                - k: number of components (factors)
                - m: number of subdivisions of the simplex (m+1 levels)

        Returns:
            List[Tuple[float, ...]]: list of points in the mixture space
        """
        k, m = config
        if k < 1 or m < 1:
            raise ValueError("k and m must be >= 1")

        # Generate all integer partitions of m into k non-negative integers
        # such that sum(p) == m
        grid_points = []
        for parts in combinations_with_replacement(range(k), m):
            counts = [0] * k
            for i in parts:
                counts[i] += 1
            point = tuple(c / m for c in counts)
            grid_points.append(point)

        return grid_points


class TypeIIIPlan:
    def __init__(self, polygon):
        self.polygon = [tuple([x/100, y/100, z/100]) for (x, y, z) in polygon]
        self.points = self.generate_points()
    
    def generate_points(self):
        # Generate points based on the polygon :
        # - Sommets du polyèdre
        # - Milieux des arêtes et des faces
        # - Centre du polyèdre
        points = []
        # Sommets
        points.extend(self.polygon)
        # Milieux des arêtes
        # Milieux des arêtes
        edges = [(self.polygon[i], self.polygon[(i + 1) % len(self.polygon)]) for i in range(len(self.polygon))]
        for edge in edges:
            edge_mid_point = tuple((edge[0][l] + edge[1][l]) / 2 for l in range(len(edge[0])))
            points.append(edge_mid_point)
        
        # Milieux des faces (for 3D)
        if len(self.polygon[0]) == 4:
            for i in range(len(self.polygon)):
                for j in range(i + 1, len(self.polygon)):
                    for k in range(j + 1, len(self.polygon)):
                        face_mid_point = tuple((self.polygon[i][l] + self.polygon[j][l] + self.polygon[k][l]) / 3 for l in range(len(self.polygon[i])))
                        points.append(face_mid_point)
        # Centre du polyèdre
        center = tuple(sum(coord) / len(self.polygon) for coord in zip(*self.polygon))
        points.append(center)
        return points

    def fedorov_exchange(self, candidates, n_points, max_iter=100):
        """
        Implémente l'algorithme d'échange de Fedorov pour sélectionner un plan D-optimal.
        
        :param candidates: ndarray, ensemble des points candidats
        :param model_func: fonction, génère la matrice de régression à partir des points
        :param n_points: int, nombre de points à sélectionner
        :param max_iter: int, nombre maximal d'itérations
        :return: ndarray, sous-ensemble D-optimal de points
        """
        import random

        # Initialisation aléatoire du design
        indices = list(range(len(candidates)))
        candidates = np.array(candidates)
        current_indices = random.sample(indices, n_points)
        current_design = candidates[current_indices]
        current_X = current_design
        current_det = np.linalg.det(current_X.T @ current_X)

        improved = True
        iter_count = 0

        while improved and iter_count < max_iter:
            improved = False
            iter_count += 1
            for i in range(n_points):
                for j in set(indices) - set(current_indices):
                    # Essayer d'échanger le point i avec le point j
                    new_indices = current_indices.copy()
                    new_indices[i] = j
                    new_design = candidates[new_indices]
                    new_X = new_design
                    try:
                        new_det = np.linalg.det(new_X.T @ new_X)
                    except np.linalg.LinAlgError:
                        continue  # matrice singulière, passer
                    if new_det > current_det:
                        # Accepter l'échange
                        current_indices = new_indices
                        current_det = new_det
                        improved = True
                        break  # sortir de la boucle interne
                if improved:
                    break  # sortir de la boucle externe
        
        return current_indices

    def __getitem__(self, config):
        # Return the generated points for the given hull
        return [self.points[i] for i in self.fedorov_exchange(self.points, 5)]


if __name__ == "__main__":
    # Example usage
    # design = SimplexCentroid()
    design = ScheffeNetwork()
    points = design[(3, 1)]  # 3 components, degree 2
    for point in points:
        print(point)
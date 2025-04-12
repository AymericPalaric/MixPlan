from itertools import combinations_with_replacement, combinations
import numpy as np

__all__ = [
    "SimplexCentroid",
    "ScheffeNetwork",
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


if __name__ == "__main__":
    # Example usage
    # design = SimplexCentroid()
    design = ScheffeNetwork()
    points = design[(3, 1)]  # 3 components, degree 2
    for point in points:
        print(point)
import numpy as np
from scipy.interpolate import (
    LinearNDInterpolator,
    RBFInterpolator as RBF,
)
from scipy.spatial import Delaunay
from sklearn.metrics import r2_score
from functools import partial

__all__ = [
    "RBFInterpolator",
    "LinearNDInterpolator",
    "DelaunayInterpolator",
    "LinearInterpolator",
    "QuadraticInterpolator",
]


class Interpolator:
    min_num_points = None
    max_num_points = None
    def __init__(self, points: np.ndarray, scores: np.ndarray):
        self.points = points
        self.scores = scores
        assert len(points) == len(scores), "Points and scores must have the same length"
        assert len(points) > 0, "Points and scores must not be empty"
    
    def update(self, points, scores):
        self.points = np.array(points)
        self.scores = np.array(scores)
        self.recompute()
    
    def append(self, points, scores):
        self.update(np.concatenate(self.points, np.array(points)), np.concatenate(self.scores, np.array(scores)))
    
    def recompute(self,):
        raise NotImplementedError()

    def __call__(self, *args, **kwds):
        raise NotImplementedError()


class RBFInterpolator(Interpolator):
    min_num_points = 3
    max_num_points = None
    def __init__(self, points: np.ndarray, scores, lazy_init=False, **kwargs):
        super().__init__(points, scores)
        # init the partial interpolator (all kwargs but no point nor score)
        self.interpolator = partial(RBF, **kwargs)
        self.lazy_init = lazy_init
        if not lazy_init:
            self.recompute()
    
    @staticmethod
    def ternary_to_cartesian(t_points):
        """
        Convert ternary coordinates to cartesian coordinates.
        Vectorized version for efficiency.
        """
        total = np.sum(t_points, axis=1, keepdims=True)
        # Avoid division by zero if total is 0
        total[total == 0] = 1e-10
        x = 0.5 * (2 * t_points[:, 1][..., None]+ t_points[:, 2][..., None]) / total
        y = (np.sqrt(3) / 2) * t_points[:, 2][..., None] / total
        return np.column_stack((x, y))


    def recompute(self,):
        # Convert ternary coordinates to cartesian
        cartesian_points = self.ternary_to_cartesian(self.points)
        # Create the RBF interpolator
        self.interpolator = self.interpolator(cartesian_points, self.scores)
        self.lazy_init = False

    def R2_score(self,):
        # Compute the R2 score of the interpolation
        cartesian_points = self.ternary_to_cartesian(self.points)
        return r2_score(self.scores, self.interpolator(cartesian_points))
    
    def __call__(self, p):
        if self.lazy_init:
            self.recompute()
        # Convert ternary coordinates to cartesian
        cartesian_point = self.ternary_to_cartesian(p[None])
        # Compute the interpolated value
        return float(self.interpolator(cartesian_point))
    

class LinearNDInterpolator(Interpolator):
    min_num_points = 3
    max_num_points = None
    def __init__(self, points: np.ndarray, scores: np.ndarray):
        super().__init__(points, scores)
        self.recompute()
    
    def recompute(self,):
        # Create the LinearNDInterpolator
        self.interpolator = LinearNDInterpolator(self.points, self.scores)
    
    def __call__(self, p):
        # Compute the interpolated value
        return float(self.interpolator(p))


class DelaunayInterpolator(Interpolator):
    min_num_points = 3
    max_num_points = None
    def __init__(self, points: np.ndarray, scores: np.ndarray):
        super().__init__(points, scores)
        self.recompute()
    
    def recompute(self,):
        # Create the Delaunay triangulation
        self.triangulation = Delaunay(self.points)
        # Create the LinearNDInterpolator
        self.interpolator = LinearNDInterpolator(self.triangulation, self.scores)
    
    def R2_score(self,):
        # Compute the R2 score of the interpolation
        return self.interpolator.R2_score()
    
    def __call__(self, p):
        # Compute the interpolated value
        return float(self.interpolator(p))


class LinearInterpolator(Interpolator):
    """
    Classic linear interpolation via matrix inversion.
    """
    min_num_points = 3
    max_num_points = 3
    def __init__(self, points: np.ndarray, scores: np.ndarray):
        super().__init__(points, scores)
        self.recompute()
    
    def recompute(self,):
        points = self.points[:3].T
        scores = self.scores[:3]
        # Compute the coefficients of the linear interpolation
        self.coeffs = np.dot(scores, np.linalg.inv(points))
    

    def R2_score(self,):
        # Compute the R2 score of the interpolation
        predicted_scores = np.dot(self.coeffs, self.points.T)
        return r2_score(self.scores, predicted_scores)
    
    def __call__(self, p):
        # Compute the interpolated value
        point = np.array(p).T
        score = np.dot(self.coeffs, point)
        return score


class QuadraticInterpolator(Interpolator):
    """
    Quadratic interpolation via matrix inversion.
    """
    min_num_points = 7
    max_num_points = 7
    def __init__(self, points: np.ndarray, scores: np.ndarray):
        super().__init__(points, scores)
        self.recompute()
    
    @staticmethod
    def ternary_to_quadratic(t_points):
        """
        Convert ternary coordinates to quadratic coordinates.
        Vectorized version for efficiency.
        """
        return np.column_stack((
            t_points[:, 0],
            t_points[:, 1],
            t_points[:, 2],
            t_points[:, 0] * t_points[:, 1],
            t_points[:, 0] * t_points[:, 2],
            t_points[:, 1] * t_points[:, 2],
            np.prod(t_points, axis=1),
        ))
    
    def recompute(self,):
        # Quadratic interpolation : Y = c*A
        # with A = (X1, X2, X3, X1*X2, X1*X3, X2*X3, X1*X2*X3)
        points = self.points[:7]
        # Convert ternary coordinates to quadratic coordinates
        A = self.ternary_to_quadratic(points)
        # Convert the scores to a column vector
        scores = np.array(self.scores[:7]).T
        # Compute the coefficients of the quadratic interpolation
        self.coeffs = np.dot(scores, np.linalg.inv(A))

    def R2_score(self,):
        # Compute the R2 score of the interpolation
        # Convert the points to quadratic coordinates
        A = self.ternary_to_quadratic(self.points)
        # Compute the predicted scores
        predicted_scores = np.dot(self.coeffs, A.T)
        # Compute the R2 score
        return r2_score(self.scores, predicted_scores)

    def __call__(self, p):
        # Compute the interpolated value
        point = self.ternary_to_quadratic(np.array(p)[None]).T
        score = np.dot(self.coeffs, point)
        return score
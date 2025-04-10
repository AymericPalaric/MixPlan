import numpy as np
from scipy.interpolate import LinearNDInterpolator, RBFInterpolator as RBF

class Interpolator:
    def __init__(self, points, scores):
        self.points = np.array(points)
        self.scores = np.array(scores)
    
    def update(self, points, scores):
        self.points = np.array(points)
        self.scores = np.array(scores)
        self.recompute()
    
    def append(self, points, scores):
        self.update(np.concatenate(self.points, np.array(points)), np.concatenate(self.scores, np.array(scores)))
    
    def recompute(self,):
        raise NotImplementedError()


class RBFInterpolator(Interpolator):
    def __init__(self, points, scores, **kwargs):
        super().__init__(points, scores)

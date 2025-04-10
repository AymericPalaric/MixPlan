import numpy as np

def ternary_to_cartesian(t_points):
    total = np.sum(t_points, axis=1, keepdims=True)
    total[total == 0] = 1e-10
    x = 0.5 * (2 * t_points[:, 1] + t_points[:, 2]) / total
    y = (np.sqrt(3) / 2) * t_points[:, 2] / total
    return np.column_stack((x, y))

def cartesian_to_ternary(c_points):
    x, y = c_points[:, 0], c_points[:, 1]
    total = x + y
    total[total == 0] = 1e-10
    t1 = (2 * y) / total
    t2 = (2 * (total - x - y)) / total
    t3 = 1 - t1 - t2
    return np.column_stack((t1, t2, t3))

def calculate_scores(points, weights):
    return np.dot(points, weights)  # Example: weighted sum of points
import ternary
from scipy.interpolate import LinearNDInterpolator, RBFInterpolator
import numpy as np

def XPs_from_bounds(bounds1, bounds2, bounds3):
    # Les sommets du triangle
    Xs = np.array([bounds1[1], bounds1[0], bounds1[0], (bounds1[1] + bounds1[0]) / 2, (bounds1[1] + bounds1[0]) / 2, bounds1[0], (bounds1[1] + 2 * bounds1[0]) / 3])
    Ys = np.array([bounds2[0], bounds2[1], bounds2[0], (bounds2[1] + bounds2[0]) / 2, bounds2[0], (bounds2[1] + bounds2[0]) / 2, (bounds2[1] + 2 * bounds2[0]) / 3])
    Zs = np.array([bounds3[0], bounds3[0], bounds3[1], bounds3[0], (bounds3[1] + bounds3[0]) / 2, (bounds3[1] + bounds3[0]) / 2, (bounds3[1] + 2 * bounds3[0]) / 3])

    return Xs, Ys, Zs

def get_scores(Xs, Ys, Zs):
    scores = []
    for i, (x,y,z) in enumerate(zip(Xs, Ys, Zs)):
        scores.append(float(input(f"Score for XP {i+1} (Comp1={x}, Comp2={y}, Comp3={z}) : ")))
    return np.array(scores)

def interpol_from_xps(Xs, Ys, Zs, scores):
    # Convert ternary coordinates to cartesian
    def ternary_to_cartesian(t):
        total = sum(t)
        # Avoid division by zero if total is 0
        if total == 0:
            return (0, 0)
        x = 0.5 * (2 * t[1] + t[2]) / total
        y = (np.sqrt(3) / 2) * t[2] / total
        return (x, y)

    # Prepare data for RBF
    points_ternary = list(zip(Xs, Ys, Zs))
    points_cartesian = np.array([ternary_to_cartesian(p) for p in points_ternary])
    scores = np.array(scores)

    # Create the RBF interpolator
    # rbf = RBFInterpolator(points_cartesian, scores, kernel='multiquadric', epsilon=1)
    rbf = LinearNDInterpolator(points_cartesian, scores)

    # Define the heatmap function used by ternary.heatmapf
    def f(p):
        # cart = np.array([ternary_to_cartesian(p)])
        # return float(rbf(cart))
        # Convert ternary coordinates to cartesian
        cart = np.array([ternary_to_cartesian(p)])
        # Get the interpolated value
        score = rbf(cart)
        # If the score is NaN, return 0
        if np.isnan(score):
            return 0
        # Return the score
        return float(score)

    return f

## Boundary and Gridlines
scale = 100
figure, tax = ternary.figure(scale=scale)

# Draw Boundary and Gridlines
tax.boundary(linewidth=2.0)
tax.gridlines(color="black", multiple=20)
tax.gridlines(color="blue", multiple=10, linewidth=0.5)

# Set Axis labels and Title
fontsize = 20
tax.set_title("Simplex Boundary and Gridlines", fontsize=fontsize)
tax.left_axis_label("Comp1", fontsize=fontsize)
tax.right_axis_label("Comp2", fontsize=fontsize)
tax.bottom_axis_label("Comp3", fontsize=fontsize)

# Set ticks
tax.ticks(axis='lbr', linewidth=1)

# Remove default Matplotlib Axes
tax.clear_matplotlib_ticks()

# Convert ternary coordinates to the scale of the plot
# Xs, Ys, Zs = XPs_from_bounds((0, 100), (0, 100), (0, 100))
Xs = np.array([0.8, 0.1, 0.1, 1/3, 0.1, 0.45, 0.45])*scale
Ys = np.array([0.1, 0.8, 0.1, 1/3, 0.45, 0.45, 0.1])*scale
Zs = np.array([0.1, 0.1, 0.8, 1/3, 0.45, 0.1, 0.45])*scale
scores = [13, 72, 54, 90, 62, 16, 69]
points = list(zip(Xs, Ys, Zs))

# Example scores
# print(points)
# scores = [0, 0, 0, 1, 1, 1, 3]
heatmap_function = interpol_from_xps(Xs, Ys, Zs, scores)
tax.heatmapf(heatmap_function, boundary=True, style="triangular")
tax.scatter(points, marker='o', color='red', label="Experience Points")

# Show the plot
ternary.plt.show()
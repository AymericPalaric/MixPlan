import ternary
from scipy.spatial import Delaunay
import numpy as np

def XPs_from_bounds(bounds1, bounds2, bounds3):
    # Les sommets du triangle
    Xs = np.array([bounds1[1], bounds1[0], bounds1[0], (bounds1[1] + bounds1[0]) / 2, (bounds1[1] + bounds1[0]) / 2, bounds1[0], (bounds1[1] + 2 * bounds1[0]) / 3])
    Ys = np.array([bounds2[0], bounds2[1], bounds2[0], (bounds2[1] + bounds2[0]) / 2, bounds2[0], (bounds2[1] + bounds2[0]) / 2, (bounds2[1] + 2 * bounds2[0]) / 3])
    Zs = np.array([bounds3[0], bounds3[0], bounds3[1], bounds3[0], (bounds3[1] + bounds3[0]) / 2, (bounds3[1] + bounds3[0]) / 2, (bounds3[1] + 2 * bounds3[0]) / 3])

    return Xs, Ys, Zs

def interpol_from_xps(Xs, Ys, Zs, scores):
    # Convert ternary coordinates to 2D Cartesian coordinates
    points = np.array([Xs[-3:], Ys[-3:], Zs[-3:]]).T
    scores = np.array(scores[-3:])
    coeffs = np.dot(scores, np.linalg.inv(points))

    def f(p):
        point = np.array(p).T
        score = np.dot(coeffs, point)
        return score

    return f

Xs, Ys, Zs = XPs_from_bounds((0, 100), (0, 100), (0, 100))

## Boundary and Gridlines
scale = 100
figure, tax = ternary.figure(scale=scale)

# Draw Boundary and Gridlines
tax.boundary(linewidth=2.0)
tax.gridlines(color="black", multiple=5)
tax.gridlines(color="blue", multiple=1, linewidth=0.5)

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
points = list(zip(Xs, Ys, Zs))

# Example scores
print(points)
scores = [0, 0, 0, 1, 1, 1, 3]
heatmap_function = interpol_from_xps(Xs, Ys, Zs, scores)
tax.heatmapf(heatmap_function, boundary=True, style="triangular")
tax.scatter(points, marker='o', color='red', label="Experience Points")

# Show the plot
ternary.plt.show()

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

# --------------------------------------------------------------------
# 1. Load the data
# --------------------------------------------------------------------
# File columns (assuming a header):
#  rank   a     b     c     period
#   0     1     2     3       4

data = np.loadtxt("ti_0.1_0.22_0.2_5.0_25.0", skiprows=1)

x = data[:, 1]  # a
y = data[:, 3]  # c
z = data[:, 4]  # period

# --------------------------------------------------------------------
# 2. Clamp or remap z-values so:
#    - z=0 stays 0
#    - z=1..10 remains the same
#    - z>10 becomes 11 (we'll color that white)
# --------------------------------------------------------------------
z_clamped = np.where(z > 10, 11, z)

# --------------------------------------------------------------------
# 3. Define discrete colors and boundaries
# --------------------------------------------------------------------
# We have 12 discrete bins:
#   bin 0  -> period=0      (black)
#   bin 1  -> period=1      (some color)
#   ...
#   bin 10 -> period=10     (some color)
#   bin 11 -> period>10     (white)

# List of 12 colors (index 0..11):
colors = [
    "black",    # 0  => period=0
    "tab:blue", # 1
    "tab:orange", 
    "tab:green", 
    "tab:red", 
    "tab:purple", 
    "tab:brown", 
    "tab:pink", 
    "tab:gray", 
    "tab:olive", 
    "tab:cyan",  # 10
    "white"      # 11 => period>10
]
cmap = ListedColormap(colors)

# Define boundaries so each integer maps to its own color bin:
#   -0.5 < z <  0.5 => color[0]
#    0.5 < z <  1.5 => color[1]
#    ...
#    9.5 < z < 10.5 => color[10]
#   10.5 < z        => color[11]
boundaries = np.arange(-0.5, 12.5, 1.0)  # -0.5, 0.5, 1.5, ..., 11.5
norm = BoundaryNorm(boundaries, len(colors))

# --------------------------------------------------------------------
# 4. Plot
# --------------------------------------------------------------------
plt.figure(figsize=(10, 8), dpi=300)
plt.tripcolor(x, y, z_clamped, cmap=cmap, norm=norm, shading='flat')

# Create discrete colorbar
cbar = plt.colorbar(ticks=np.arange(0, 12))
# Manually label the ticks: 0..10 + '>10'
cbar.ax.set_yticklabels(
    ['0','1','2','3','4','5','6','7','8','9','10','>10']
)
cbar.set_label('Period')

plt.xlabel(r'$\alpha$')
plt.ylabel(r'$\gamma$')
plt.tight_layout()
plt.savefig('heatmap.png', dpi=300, bbox_inches='tight')
plt.show()

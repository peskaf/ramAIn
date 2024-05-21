import numpy as np
import matplotlib
from matplotlib import cm

N_COLORS = 10

# NOTE: colormap names have to exist in matplotlib library
COLORMAPS = {
            "viridis": [(68.0, 1.0, 84.0), (72.0, 40.0, 120.0), (62.0, 73.0, 137.0), (49.0, 104.0, 142.0), (38.0, 130.0, 142.0), (31.0, 158.0, 137.0), (53.0, 183.0, 121.0), (110.0, 206.0, 88.0), (181.0, 222.0, 43.0), (253.0, 231.0, 37.0), ],
            "hot": [(11.0, 0.0, 0.0), (85.0, 0.0, 0.0), (159.0, 0.0, 0.0), (234.0, 0.0, 0.0), (255.0, 53.0, 0.0), (255.0, 128.0, 0.0), (255.0, 202.0, 0.0), (255.0, 255.0, 32.0), (255.0, 255.0, 143.0), (255.0, 255.0, 255.0), ],
            "jet": [(0.0, 0.0, 128.0), (0.0, 0.0, 255.0), (0.0, 99.0, 255.0), (0.0, 212.0, 255.0), (78.0, 255.0, 169.0), (169.0, 255.0, 78.0), (255.0, 230.0, 0.0), (255.0, 125.0, 0.0), (255.0, 20.0, 0.0), (128.0, 0.0, 0.0), ],
            "cividis": [(0.0, 34.0, 78.0), (18.0, 53.0, 112.0), (59.0, 73.0, 108.0), (87.0, 93.0, 109.0), (112.0, 113.0, 115.0), (138.0, 134.0, 120.0), (165.0, 156.0, 116.0), (195.0, 179.0, 105.0), (225.0, 204.0, 85.0), (254.0, 232.0, 56.0), ]
        }

# colors for scatterings onto corresponding `COLORMAPS`, chosen to be contrast
SCATTER_COLORMAPS = {
    "viridis": [(255.0, 0.0, 0.0)],
    "hot": [(0.0, 255.0, 0.0)],
    "jet": [(255.0, 255.0, 255.0)],
    "cividis": [(255.0, 0.0, 0.0)]
}

def get_colors(colormap_name: str, n_colors: int, hex: bool = False):
    """
    A function to generate `n_colors` from matplotlib `colormap_name` colormap.
    Output is in hex if `hex` is true, rgb otherwise.

    Note that colors are print on stdout as the output expected to be stored directly
    in the source code because of library dependancy.
    """

    print('"' + colormap_name + '": ', end="")
    cmap = cm.get_cmap(colormap_name, n_colors)
    print("[", end="")
    for i in range(cmap.N):
        rgba = cmap(i)
        rgb = rgba[:3]
        if hex:
            print(matplotlib.colors.rgb2hex(rgba))
        else:
            print(tuple(np.round(np.asarray(rgb)*255)), end=", ")
    print("]")

# main function for colormaps generation
if __name__ == "__main__":
    n_colors = 10
    get_colors("viridis", n_colors)
    get_colors("hot", n_colors)
    get_colors("jet", n_colors)
    get_colors("cividis", n_colors)
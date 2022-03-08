
VIRIDIS_COLOR_MAP = [(68.0, 1.0, 84.0), (64.0, 67.0, 135.0), (41.0, 120.0, 142.0), (34.0, 167.0, 132.0), (121.0, 209.0, 81.0), (253.0, 231.0, 36.0)]
HOT_COLOR_MAP = [(11.0, 0.0, 0.0), (144.0, 0.0, 0.0), (255.0, 23.0, 0.0), (255.0, 157.0, 0.0), (255.0, 255.0, 54.0), (255.0, 255.0, 255.0)]
GRAY_COLOR_MAP = [(0.0, 0.0, 0.0), (51.0, 51.0, 51.0), (102.0, 102.0, 102.0), (153.0, 153.0, 153.0), (204.0, 204.0, 204.0), (255.0, 255.0, 255.0)]
CIVIDIS_COLOR_MAP = [(0.0, 34.0, 78.0), (53.0, 69.0, 108.0), (102.0, 105.0, 112.0), (148.0, 142.0, 119.0), (200.0, 184.0, 102.0), (254.0, 232.0, 56.0)]
# here curr cmap, ...

# UTILS

def get_colors(): # get colors from cmap
    import matplotlib
    from matplotlib import cm

    cmap = cm.get_cmap('cividis', 6)

    for i in range(cmap.N):
        rgba = cmap(i)
        print(matplotlib.colors.rgb2hex(rgba))
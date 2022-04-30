from PySide6.QtWidgets import QFrame, QLabel, QGridLayout, QRadioButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, Qt, QSettings

import pyqtgraph as pg
import numpy as np

COLORMAPS = {
            "viridis": [(68.0, 1.0, 84.0), (72.0, 40.0, 120.0), (62.0, 73.0, 137.0), (49.0, 104.0, 142.0), (38.0, 130.0, 142.0), (31.0, 158.0, 137.0), (53.0, 183.0, 121.0), (110.0, 206.0, 88.0), (181.0, 222.0, 43.0), (253.0, 231.0, 37.0), ],
            "hot": [(11.0, 0.0, 0.0), (85.0, 0.0, 0.0), (159.0, 0.0, 0.0), (234.0, 0.0, 0.0), (255.0, 53.0, 0.0), (255.0, 128.0, 0.0), (255.0, 202.0, 0.0), (255.0, 255.0, 32.0), (255.0, 255.0, 143.0), (255.0, 255.0, 255.0), ],
            "jet": [(0.0, 0.0, 128.0), (0.0, 0.0, 255.0), (0.0, 99.0, 255.0), (0.0, 212.0, 255.0), (78.0, 255.0, 169.0), (169.0, 255.0, 78.0), (255.0, 230.0, 0.0), (255.0, 125.0, 0.0), (255.0, 20.0, 0.0), (128.0, 0.0, 0.0), ],
            "cividis": [(0.0, 34.0, 78.0), (18.0, 53.0, 112.0), (59.0, 73.0, 108.0), (87.0, 93.0, 109.0), (112.0, 113.0, 115.0), (138.0, 134.0, 120.0), (165.0, 156.0, 116.0), (195.0, 179.0, 105.0), (225.0, 204.0, 85.0), (254.0, 232.0, 56.0), ]
        }

SCATTER_COLORMAPS = {
    "viridis": [(255.0, 0.0, 0.0)],
    "hot": [(0.0, 255.0, 0.0)],
    "jet": [(255.0, 255.0, 255.0)],
    "cividis": [(255.0, 0.0, 0.0)]
}

class Settings(QFrame):
    cmap_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.icon = QIcon("icons/settings.svg")
        self.settings = QSettings()

        n_colors = 10
        cmap_data = np.tile(np.linspace(0, 1, num=n_colors), (2,1)).T

        cmap_pics = []

        for colormap in COLORMAPS.values():
            cmap_pic = pg.ImageView()
            cmap_pic.ui.histogram.hide()
            cmap_pic.ui.roiBtn.hide()
            cmap_pic.ui.menuBtn.hide()

            cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, len(colormap)), color=colormap)
            cmap_pic.setColorMap(cmap)

            cmap_pic.setImage(cmap_data, autoRange=False)

            cmap_pic.getView().setMouseEnabled(False, False)
            cmap_pic.getView().setDefaultPadding(0)
            cmap_pic.getView().setAspectLocked(True)
            cmap_pic.setFixedSize(150, 30)

            cmap_pics.append(cmap_pic)

        self.viridis = QRadioButton("Viridis")
        self.viridis.toggled.connect(self.emit_cmap_changed)
        self.hot = QRadioButton("Hot")
        self.hot.toggled.connect(self.emit_cmap_changed)
        self.jet = QRadioButton("Jet")
        self.jet.toggled.connect(self.emit_cmap_changed)
        self.cividis = QRadioButton("Cividis")
        self.cividis.toggled.connect(self.emit_cmap_changed)

        try:
            cmap = str(self.settings.value("spectral_map/cmap"))
            getattr(self, cmap).setChecked(True)
        except:
            # default
            self.viridis.setChecked(True)


        layout = QGridLayout()
        layout.addWidget(QLabel("Spectral Map - Colormap"), 0, 0)
        layout.addWidget(self.viridis, 1, 0)
        layout.addWidget(self.hot, 2, 0)
        layout.addWidget(self.jet, 3, 0)
        layout.addWidget(self.cividis, 4, 0)

        layout.addWidget(cmap_pics[0], 1, 1)
        layout.addWidget(cmap_pics[1], 2, 1)
        layout.addWidget(cmap_pics[2], 3, 1)
        layout.addWidget(cmap_pics[3], 4, 1)
        layout.setAlignment(Qt.AlignTop)
        layout.setRowStretch(layout.rowCount(), 1)
        layout.setColumnStretch(layout.columnCount(), 1)

        self.setLayout(layout)
        
    def emit_cmap_changed(self):
        sender = self.sender()
        if sender.isChecked():
            self.settings.setValue("spectral_map/cmap", sender.text().lower())
     
    def get_string_name(self):
        return "Settings"

# UTILS

# get colors from cmap
def get_colors(colormap_name: str, clrs_cnt: int, hex: bool=False):
    import matplotlib
    from matplotlib import cm
    import numpy as np

    print(colormap_name.upper() + "_COLOR_MAP = ", end="")
    cmap = cm.get_cmap(colormap_name, clrs_cnt)
    print("[", end="")
    for i in range(cmap.N):
        rgba = cmap(i)
        rgb = rgba[:3]
        if hex:
            print(matplotlib.colors.rgb2hex(rgba))
        else:
            print(tuple(np.round(np.asarray(rgb)*255)), end=", ")
    print("]")


if __name__ == "__main__":
    n_colors = 10
    get_colors("viridis", n_colors)
    get_colors("hot", n_colors)
    get_colors("jet", n_colors)
    get_colors("cividis", n_colors)
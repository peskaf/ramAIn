from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QGridLayout,
    QRadioButton,
    QButtonGroup,
    QWidget,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSettings

from utils import colors

import pyqtgraph as pg
import numpy as np


class Settings(QFrame):
    """
    A widget providinf interface for user settings update.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for settings adjusting widget.

        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.icon = QIcon("src/resources/icons/settings.svg")
        self.settings = QSettings()

        n_colors = colors.N_COLORS

        # data for cmap visualization
        cmap_data = np.tile(np.linspace(0, 1, num=n_colors), (2, 1)).T

        cmap_pics = []

        # create visuaizations of the colormaps
        for colormap in colors.COLORMAPS.values():
            cmap_pic = pg.ImageView(self)
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

        # button group for exclusive cmaps selection
        self.group = QButtonGroup()
        self.group.setExclusive(True)

        self.viridis = QRadioButton("Viridis")
        self.viridis.toggled.connect(self.change_cmap)
        self.group.addButton(self.viridis)

        self.hot = QRadioButton("Hot")
        self.hot.toggled.connect(self.change_cmap)
        self.group.addButton(self.hot)

        self.jet = QRadioButton("Jet")
        self.jet.toggled.connect(self.change_cmap)
        self.group.addButton(self.jet)

        self.cividis = QRadioButton("Cividis")
        self.cividis.toggled.connect(self.change_cmap)
        self.group.addButton(self.cividis)

        # set init cmap based on settings
        try:
            cmap = str(self.settings.value("spectral_map/cmap", "viridis"))
            getattr(self, cmap).setChecked(True)
        except:
            # default
            self.viridis.setChecked(True)

        layout = QGridLayout(self)
        layout.addWidget(QLabel("Spectral Map - Colormap"), 0, 0)

        layout.addWidget(self.viridis, 1, 0)
        layout.addWidget(cmap_pics[0], 1, 1)

        layout.addWidget(self.hot, 2, 0)
        layout.addWidget(cmap_pics[1], 2, 1)

        layout.addWidget(self.jet, 3, 0)
        layout.addWidget(cmap_pics[2], 3, 1)

        layout.addWidget(self.cividis, 4, 0)
        layout.addWidget(cmap_pics[3], 4, 1)

        layout.setAlignment(Qt.AlignTop)

        # add stretch for better alignment
        layout.setRowStretch(layout.rowCount(), 1)
        layout.setColumnStretch(layout.columnCount(), 1)

        self.setLayout(layout)

    def change_cmap(self) -> None:
        """
        A function to change currently selected cmap in the widget and in the settings.
        """

        sender = self.sender()
        if sender.isChecked():
            self.settings.setValue("spectral_map/cmap", sender.text().lower())

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Settings"

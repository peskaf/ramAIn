from pydoc import Doc
from PySide6.QtGui import QColor, QWheelEvent
from PySide6.QtWidgets import QFrame, QHBoxLayout, QWidget, QLineEdit, QGraphicsSceneWheelEvent
from PySide6.QtCore import Qt, QPoint, QSettings

import pyqtgraph as pg
import numpy as np

from widgets.settings import COLORMAPS

class ScrollablePlotWidget(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def wheelEvent(self,event):
        self.parent.wheelEvent(event)

    def mousePressEvent(self, QMouseEvent):
        pass

    def mouseReleaseEvent(self, QMouseEvent):
        pass

class Component(QFrame):
    def __init__(self, x, y, map, parent=None):
        super().__init__(parent)

        self.settings = QSettings()

        self.setMinimumHeight(175)
        self.setMaximumHeight(400)

        self.x_data = x
        self.y_data = y
        self.map_data = map
        
        self.component_map = pg.ImageView(parent)
        self.component_map.ui.histogram.hide()
        self.component_map.ui.roiBtn.hide()
        self.component_map.ui.menuBtn.hide()

        bg_color = (240,240,240)
        color_map = COLORMAPS[str(self.settings.value("spectral_map/cmap"))]
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, len(color_map)), color=color_map)

        self.component_map.setColorMap(cmap)
        self.component_map.setImage(self.map_data, autoRange=False)
        self.component_map.getView().setMouseEnabled(False, False)
        self.component_map.getView().setDefaultPadding(0)
        self.component_map.getView().setAspectLocked(True, ratio=None)
        self.component_map.getView().setBackgroundColor(QColor(240,240,240))
        self.component_map.setMinimumWidth(175)
        self.component_map.setMaximumWidth(250)

        self.component_plot = ScrollablePlotWidget(parent)
        self.component_plot.setBackground(bg_color)
        plot_pen = pg.mkPen(color="#266867", width=1.5)
        self.line = self.component_plot.plot(self.x_data, self.y_data, pen=plot_pen)

        # TODO: solve labels
        """
        styles = { "font-family" : "montserrat", "color" : "#1A4645", "font-size": "14px" }
        self.component_plot.getPlotItem().setLabel("top", f"x = {0000.00}, y = {000.00}", **styles)
        self.component_plot.getPlotItem().setLabel("left", "Intensity (a.u.)", **styles)
        self.component_plot.getPlotItem().setLabel("bottom", "Raman shift (1/cm)", **styles) # jednotky ?
        """

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.component_map)
        layout.addWidget(self.component_plot)
        self.setLayout(layout)
        
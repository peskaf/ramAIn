from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QWidget
from PySide6.QtCore import Qt, QEvent

from ramain.utils import colors
from ramain.utils.settings import SETTINGS

import pyqtgraph as pg
import numpy as np


class ScrollablePlotWidget(pg.PlotWidget):
    """
    Subclass of `pg.PlotWidget` that overrides `wheelEvent` and `mouse(Press/Release)Event`
    so that user scrolls the parent widget when scrolling on the plot.
    Widget performs no action on mouse press/release.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        The constructor for scrollable plot widget.

        Parameters:
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__()

        self.parent = parent

    def wheelEvent(self, event: QEvent):
        """
        A function that overrides `pg.PlotWidget`'s `wheelEvent` so that parent widget is scrolled.

        Parameters:
            event (QEvent): Scrolling event.
        """

        self.parent.wheelEvent(event)

    def mousePressEvent(self, QMouseEvent: QEvent):
        """
        A function that overrides `pg.PlotWidget`'s `mousePressEvent` so that it does nothing.

        Parameters:
            event (QEvent): Mouse press event.
        """

        pass

    def mouseReleaseEvent(self, QMouseEvent: QEvent):
        """
        A function that overrides `pg.PlotWidget`'s `mouseReleaseEvent` so that it does nothing.

        Parameters:
            event (QEvent): Mouse release event.
        """

        pass


class Component(QFrame):
    """
    A widget representing one Raman component. It displays a spectral map and a single spectral plot.
    """

    def __init__(
        self, x: np.ndarray, y: np.ndarray, map: np.ndarray, parent: QWidget = None
    ) -> None:
        super().__init__(parent)

        # limit size of one component
        self.setMinimumHeight(175)
        self.setMaximumHeight(400)

        self.x_data = x
        self.y_data = y
        self.map_data = map

        # NOTE: scrolling over spectral map does nothing at all as wheelEvent works
        #       different for `pg.ImageView`
        self.component_map = pg.ImageView(parent)

        # hide controll buttons
        self.component_map.ui.histogram.hide()
        self.component_map.ui.roiBtn.hide()
        self.component_map.ui.menuBtn.hide()

        # set colors
        bg_color = (240, 240, 240)
        color_map = colors.COLORMAPS[str(SETTINGS.value("spectral_map/cmap"))]
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, len(color_map)), color=color_map)

        # component map properties
        self.component_map.setColorMap(cmap)
        self.component_map.setImage(self.map_data, autoRange=False)
        self.component_map.getView().setMouseEnabled(False, False)
        self.component_map.getView().setDefaultPadding(0)
        self.component_map.getView().setAspectLocked(True, ratio=None)
        self.component_map.getView().setBackgroundColor(QColor(240, 240, 240))
        self.component_map.setMinimumWidth(175)
        self.component_map.setMaximumWidth(250)

        # spectral plot is the scrollable one
        self.component_plot = ScrollablePlotWidget(parent)
        self.component_plot.setBackground(bg_color)
        plot_pen = pg.mkPen(color="#266867", width=1.5)
        self.line = self.component_plot.plot(self.x_data, self.y_data, pen=plot_pen)

        # make final layout
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.component_map)
        layout.addWidget(self.component_plot)
        self.setLayout(layout)

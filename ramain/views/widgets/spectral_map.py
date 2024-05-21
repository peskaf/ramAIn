from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QWidget
from PySide6.QtCore import QRectF, QPoint

from ramain.views.widgets.plot_mode import PlotMode
from ramain.views.widgets.adjustable_handles_roi import AdjustableHandlesROI

from ramain.utils import colors
from ramain.utils.settings import SETTINGS

import pyqtgraph as pg
import numpy as np


class SpectralMapGraph(QFrame):
    """
    A widget for spectral map visualization.
    """

    def __init__(self, data: np.ndarray, parent: QWidget = None) -> None:
        """
        The constructor for SpectralMap widget.

        Parameters:
            data (np.ndarray): Data that is to be displayed.
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.image_view = pg.ImageView()
        self.data = data

        # hide histogram and buttons (initially are visible)
        self.image_view.ui.histogram.hide()
        self.image_view.ui.roiBtn.hide()
        self.image_view.ui.menuBtn.hide()

        color_map = colors.COLORMAPS[str(SETTINGS.value("spectral_map/cmap"))]
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, len(color_map)), color=color_map)
        self.image_view.setColorMap(cmap)
        self.image_view.setImage(self.data, autoRange=False)
        self.image_view.getView().setDefaultPadding(0)
        self.image_view.getView().setBackgroundColor(QColor(240, 240, 240))

        # set limits for image manipulation (scrolling, moving)
        self._set_limits()

        # make crosshair on the spectral map
        self._make_crosshair()

        # init mode is view
        self.mode = PlotMode.DEFAULT

        self.ROI = None
        self.scatter = None

        layout = QHBoxLayout(self)
        layout.addWidget(self.image_view)

    def _make_crosshair(self) -> None:
        """
        A helper function to create crosshair on the plot.
        """

        # crosshair lines.
        self._crosshair_v = pg.InfiniteLine(angle=90, movable=False)
        self._crosshair_h = pg.InfiniteLine(angle=0, movable=False)

        self.image_view.addItem(self._crosshair_v, ignoreBounds=True)
        self.image_view.addItem(self._crosshair_h, ignoreBounds=True)

        self._crosshair_visible = True

        # update crosshair on mouse move
        self.mouse_movement_proxy = pg.SignalProxy(
            self.image_view.getView().scene().sigMouseMoved,
            rateLimit=60,
            slot=self.update_crosshair,
        )

    def update_crosshair(self, event: tuple[QPoint, None]) -> None:
        """
        A function to change crosshair's location on mouse movement.

        Parameters:
            event (tuple[QPoint, None]): Tuple with current mouse coordinates on the first index (auto generated format).
        """

        coordinates = event[0]
        self.mouse_point = self.image_view.getView().mapSceneToView(coordinates)

        self._crosshair_v.setPos(self.mouse_point.x())
        self._crosshair_h.setPos(self.mouse_point.y())

    def update_image(self, new_data: np.ndarray) -> None:
        """
        A function to update visualized data.

        Parameters:
            new_data (np.ndarray): New data to visualize.
        """

        color_map = colors.COLORMAPS[str(SETTINGS.value("spectral_map/cmap"))]
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, len(color_map)), color=color_map)
        self.image_view.setColorMap(cmap)

        self.data = new_data
        self.image_view.setImage(self.data)
        self._set_limits()
        # reset view zoom
        self.image_view.getView().enableAutoRange()

    def _set_limits(self) -> None:
        """
        A helper function for setting movement limits of the spectral map in the view.
        """

        img = self.image_view.getImageItem()
        offset = np.absolute(img.height() - img.width()) / 2

        if img.height() > img.width():
            self.image_view.getView().setLimits(
                xMin=-offset, xMax=img.height() - offset, yMin=0, yMax=img.height()
            )
        else:
            self.image_view.getView().setLimits(
                xMin=0, xMax=img.width(), yMin=-offset, yMax=img.width() - offset
            )

    def hide_crosshair(self) -> None:
        """
        A function to make crosshair invisible.

        Note that proxy signal is not blocked as mousepoint coordinates are needed
        for plots' changing.
        """
        if self._crosshair_visible:
            self._crosshair_v.hide()
            self._crosshair_h.hide()
            self._crosshair_visible = False

    def show_crosshair(self) -> None:
        """
        A function to make crosshair visible.
        """
        if not self._crosshair_visible:
            self._crosshair_v.show()
            self._crosshair_h.show()
            self._crosshair_visible = True

    def set_mode(self, new_mode: PlotMode) -> None:
        """
        A function to set new plot mode of the spectral map.

        Parameters:
            new_mode (PlotMode): Enum representing new plot mode.
        """

        if new_mode == PlotMode.CROPPING:
            self._set_cropping_mode()
        elif new_mode == PlotMode.COSMIC_RAY_REMOVAL:
            self._set_crr_mode()
        else:  # default
            self._set_view_mode()
            return

        self.mode = new_mode

    def _set_view_mode(self) -> None:
        """
        A function to perform actions demanded by `view` mode.
        """

        # hide selection region
        if self.ROI is not None:
            self.image_view.removeItem(self.ROI)
            self.ROI = None

        self.show_crosshair()
        self._remove_scatter()

    def _set_cropping_mode(self) -> None:
        """
        A function to perform actions demanded by `cropping` mode.
        """

        self.hide_crosshair()

        # remove ROI if it was not deleted so that new object is created (crucial for bounds and size setting)
        if self.ROI is not None:
            self.image_view.removeItem(self.ROI)
        self.add_selection_region()

        self._remove_scatter()

    def _set_crr_mode(self) -> None:
        """
        A function to perform actions demanded by `CRR` mode.
        """

        # hide selection region
        if self.ROI is not None:
            self.image_view.removeItem(self.ROI)
            self.ROI = None

        self.show_crosshair()
        self._remove_scatter()

    def add_selection_region(self) -> None:
        """
        A function to add new region for selection.
        """

        pen = pg.mkPen(color="#F58800", width=2)
        hoverPen = pg.mkPen(color="#F8BC24", width=2)

        self.ROI = AdjustableHandlesROI(
            pos=(0, 0),
            size=(
                self.image_view.getImageItem().width(),
                self.image_view.getImageItem().height(),
            ),
            maxBounds=QRectF(
                0,
                0,
                self.image_view.getImageItem().width(),
                self.image_view.getImageItem().height(),
            ),
            sideScalers=True,
            rotatable=False,
            pen=pen,
            hoverPen=hoverPen,
        )

        # rest of handles around the ROI
        self.ROI.addScaleHandle((1, 1), (0, 0))
        self.ROI.addScaleHandle((0, 0), (1, 1))
        self.ROI.addScaleHandle((0, 1), (1, 0))
        self.ROI.addScaleHandle((1, 0), (0, 1))
        self.ROI.addScaleHandle((0, 0.5), (1, 0.5))
        self.ROI.addScaleHandle((0.5, 0), (0.5, 1))

        self.image_view.addItem(self.ROI)

    def update_ROI(
        self, new_pos: tuple[float, float], new_size: tuple[float, float]
    ) -> None:
        """
        A function to update region's position and size according to passed parameters.

        Parameters:
            new_pos (tuple[float, float]): New position of the upper-left corner of the region.
            new_size (tuple[float, float]): New size of the region.
        """

        # new_pos validation
        if new_pos[0] < 0:
            new_pos = (0, new_pos[1])
        elif new_pos[0] > self.image_view.getImageItem().width():
            new_pos = (self.image_view.getImageItem().width(), new_pos[1])

        if new_pos[1] < 0:
            new_pos = (new_pos[0], 0)
        elif new_pos[1] > self.image_view.getImageItem().height():
            new_pos = (new_pos[0], self.image_view.getImageItem().height())

        # new_size validation
        if new_size[0] < 0:
            new_size = (0, new_size[1])
        elif new_size[0] > self.image_view.getImageItem().width():
            new_size = (self.image_view.getImageItem().width(), new_size[1])

        if new_size[1] < 0:
            new_size = (new_size[0], 0)
        elif new_size[1] > self.image_view.getImageItem().height():
            new_size = (new_size[0], self.image_view.getImageItem().height())

        self.ROI.setPos(new_pos)
        self.ROI.setSize(new_size)

    def scatter_spikes(self, positions: np.ndarray) -> None:
        """
        A function to scatter passed positions onto the spectral map.

        Parameters:
            positions (np.ndarray): Indices of the spikes in the array.
        """

        if self.scatter is not None:
            self.scatter.setData([])
        else:
            scatter_color = colors.SCATTER_COLORMAPS[
                str(SETTINGS.value("spectral_map/cmap"))
            ]
            scatter_brush = pg.mkBrush(*(scatter_color[0]), 255)
            self.scatter = pg.ScatterPlotItem(size=3, brush=scatter_brush)

        # data for x-axis; 0.5 for centering
        x_data = [float(i[0] + 0.5) for i in positions]

        # data for y-axis; 0.5 for centering
        y_data = [float(i[1] + 0.5) for i in positions]

        self.scatter.addPoints(x_data, y_data)
        self.image_view.addItem(self.scatter)

    def _remove_scatter(self) -> None:
        """
        A function to remove the scatter object from the view.
        """

        if self.scatter is not None:
            self.image_view.removeItem(self.scatter)
            self.scatter = None

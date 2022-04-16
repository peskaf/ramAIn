from PySide6.QtWidgets import QFrame, QHBoxLayout, QWidget
from PySide6.QtCore import QPoint

import pyqtgraph as pg
import numpy as np

from widgets.plot_mode import PlotMode

class SpectralPlot(QFrame):
    """
    A widget for visualizing spectral plot.

    Attributes: # TODO: prepsat sem vsechny atributy
    """

    def __init__(self, x: np.ndarray, y: np.ndarray, parent: QWidget = None) -> None:
        """
        The constructor for SpectralPlot widget.
  
        Parameters:
            x (np.ndarray): Values fo x axis.
            y (np.ndarray): Values for y axis.
            parent (QWidget): Parent widget of this widget. Default: None.
        """

        super().__init__(parent)

        self.x_data = x
        self.y_data = y

        self.plot_widget = pg.PlotWidget(self)

        bg_color = (240,240,240)
        self.plot_widget.setBackground(bg_color)

        # shading of the plot
        self.cm = pg.ColorMap(pos=np.linspace(0.0, 1.0, 2), color=[(38, 104, 103, 0), (38, 104, 103, 50)], mapping="diverging") # color same as for plot but in rgba with opacity going from 50 to 0
        brush = self.cm.getBrush(span=(np.min(self.y_data), np.max(self.y_data)))
        
        # axis styling
        axis_pen = pg.mkPen(color="#051821")
        axes = ["top", "left", "bottom"]
        for axis in axes:
            self.plot_widget.getPlotItem().getAxis(axis).setPen(axis_pen)
        self.plot_widget.getPlotItem().getAxis(axis).setTextPen(axis_pen)

        # plotting
        plot_pen = pg.mkPen(color="#266867", width=1.5)
        self.line = self.plot_widget.plot(self.x_data, self.y_data, pen=plot_pen, brush=brush, fillLevel=np.min(self.y_data))

        # labels setup
        styles = { "font-family" : "montserrat", "color" : "#1A4645", "font-size": "14px" }
        self.plot_widget.getPlotItem().setLabel("top", f"x = {0000.00}, y = {000.00}", **styles)
        self.plot_widget.getPlotItem().setLabel("left", "Intensity (a.u.)", **styles)
        self.plot_widget.getPlotItem().setLabel("bottom", "Raman shift (1/cm)", **styles) # jednotky ?

        # create crosshair object
        self._make_crosshair()

        self.mode = PlotMode.DEFAULT
        self.linear_region = None

        self.bg_pen = pg.mkPen(color="#F58800", width=2.5)
        self.background = None

        layout = QHBoxLayout(self)
        layout.addWidget(self.plot_widget)

    def _make_crosshair(self) -> None:
        """
        A helper function to create crosshair on the plot.
        """

        crosshair_pen = pg.mkPen(color="black")

        # crosshair with ust vertical line
        self.crosshair_v = pg.InfiniteLine(angle=90, movable=False, pen=crosshair_pen)

        self._crosshair_visible = True
        self.plot_widget.addItem(self.crosshair_v, ignoreBounds=True)

        # update crosshair on mouse movement
        self.mouse_movement_proxy = pg.SignalProxy(self.plot_widget.scene().sigMouseMoved, rateLimit=60, slot=self.update_crosshair)

    def update_data(self, new_x: np.ndarray, new_y: np.ndarray) -> None:
        """
        A function to update the plot with passed data.

        Parameters:
            new_x (np.ndarray): New values for x axis.
            new_y (np.ndarray): New values for y axis.
        """

        self.x_data, self.y_data  = new_x, new_y

        # update plot brush -> `y_data` has changed
        brush = self.cm.getBrush(span=(np.min(self.y_data), np.max(self.y_data)))

        # set new line
        self.line.setData(self.x_data, self.y_data, brush=brush, fillLevel=np.min(self.y_data))

        # if the plot is zoomed somehow, "remove" the zoom
        self.plot_widget.getPlotItem().autoRange() 

        # set new Y range in case the plot kept it from previous line
        self.plot_widget.getPlotItem().setYRange(min=np.min(self.y_data), max=np.max(self.y_data))
        

    def update_crosshair(self, event: tuple[QPoint, None]) -> None:
        """
        A function to change crosshair's location on mouse movement.

        Parameters:
            event (tuple[QPoint, None]): Tuple with current mouse coordinates on the first index (auto generated format).
        """

        coordinates = event[0]
        mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(coordinates)
        self.crosshair_v.setPos(mouse_point.x())

        # change current crosshair location label
        self.plot_widget.getPlotItem().setLabel("top", f"x = {mouse_point.x():.2f}, y = {self.y_data[np.argmin(np.abs(self.x_data - mouse_point.x()))]:.2f}")

    def hide_crosshair(self) -> None:
        """
        A function to make crosshair invisible.
        """

        self.crosshair_v.hide()
        self._crosshair_visible = False

        # block signal to prevent performance issues
        self.mouse_movement_proxy.blockSignal = True

    def show_crosshair(self) -> None:
        """
        A function to make crosshair visible.
        """
    
        self.crosshair_v.show()
        self._crosshair_visible = True

        self.mouse_movement_proxy.blockSignal = False

    def set_mode(self, new_mode: PlotMode) -> None:
        """
        A function to set current plotting mode.

        Parameters:
            new_mode (PlotMode): New mode enum.
        """

        if new_mode == PlotMode.CROPPING:
            self._set_cropping_mode()
        elif new_mode == PlotMode.COSMIC_RAY_REMOVAL:
            self._set_crr_mode()
        elif new_mode == PlotMode.BACKGROUND_REMOVAL:
            self._set_bg_removal_mode()
        else:
            self._set_view_mode() # default
            return

        self.mode = new_mode

    def _set_view_mode(self) -> None:
        """
        A function to perform actions demanded by `view` mode.
        """

        # hide region
        if self.linear_region is not None:
            self.hide_selection_region()

        # show crosshair
        if not self._crosshair_visible:
            self.show_crosshair()

        # hide background
        if self.background is not None:
            self.hide_background()

    def _set_cropping_mode(self) -> None:
        """
        A function to perform actions demanded by `cropping` mode.
        """

        # hide crosshair
        if self._crosshair_visible:
            self.hide_crosshair()
        
        # if region is present -> delete it and create again so that sizes and bounds fit
        if self.linear_region is not None:
            self.hide_selection_region()
        self.show_selection_region()

        # hide background
        if self.background is not None:
            self.hide_background()

    def _set_bg_removal_mode(self) -> None:
        """
        A function to perform actions demanded by `BGR` mode.
        """

        # hide region
        if self.linear_region is not None:
            self.hide_selection_region()

        # show crosshair
        if not self._crosshair_visible:
            self.show_crosshair()

        # hide background -> wait for new one to be passed to `plot_background` as it depends on the data
        if self.background is not None:
            self.hide_background()

    def _set_crr_mode(self) -> None:
        """
        A function to perform actions demanded by `CRR` mode.
        """

        # hide region
        if self.linear_region is not None:
            self.hide_selection_region()

        # show crosshair
        if not self._crosshair_visible:
            self.show_crosshair()

        # hide background
        if self.background is not None:
            self.hide_background()

    def show_selection_region(self) -> None:
        """
        A function to plot linear region onto the plot.
        """

        brush = pg.mkBrush(color=(38,104,103,50))
        hoverBrush = pg.mkBrush(color=(38,104,103,70))
        pen = pg.mkPen(color="#051821")
        hoverPen = pg.mkPen(color="#F58800")

        self.linear_region = pg.LinearRegionItem(
            values=[self.x_data[0], self.x_data[-1]], # min and max from x data (x data is sorted)
            bounds=[self.x_data[0], self.x_data[-1]],
            brush=brush,
            pen=pen,
            hoverBrush=hoverBrush,
            hoverPen=hoverPen)

        self.plot_widget.addItem(self.linear_region)
    
    def hide_selection_region(self) -> None:
        """
        A function to remove linear region.
        """

        self.plot_widget.removeItem(self.linear_region)
        self.linear_region = None

    def update_region(self, new_region: tuple[float, float]) -> None:
        """
        A function to update linear region according to passed region.

        Parameters:
            new_region (tuple[float, float]): New region end-points.
        """

        self.linear_region.setRegion(new_region)

    def plot_background(self, background: np.ndarray) -> None:
        #remove prev bg in case there is some
        if self.background is not None:
            self.hide_background()
        self.background = self.plot_widget.plot(self.x_data, background, pen=self.bg_pen)

    def hide_background(self) -> None:
        self.background.hide()
        self.background = None

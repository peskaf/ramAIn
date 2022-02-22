from PySide6.QtWidgets import QFrame, QHBoxLayout

import pyqtgraph as pg
import numpy as np

from widgets.plot_mode import PlotMode

class SpectralPlot(QFrame):
    def __init__(self, x, y, parent=None):
        super().__init__(parent)

        self.x_data = x
        self.y_data = y

        self.plot_widget = pg.PlotWidget(self)

        # STYLING
        self.plot_widget.setBackground((240,240,240))
        
        # to qss TODO: HOW?! # style for labels only
        styles = { "font-family" : "montserrat", "color" : "#1A4645", "font-size": "14px" }

        axis_pen = pg.mkPen(color="#051821")
        plot_pen = pg.mkPen(color="#266867", width=1.1)
        crosshair_pen = pg.mkPen(color="black")
        cm = pg.ColorMap(pos=np.linspace(0.0, 1.0, 2), color=[(38, 104, 103, 0), (38, 104, 103, 50)], mapping="diverging") # color same as for plot but in rgba with opacity going from 50 to 0
        brush = cm.getBrush(span=(np.min(self.y_data), np.max(self.y_data)))
        
        axes = ["top", "left", "bottom"]
        for axis in axes:
            self.plot_widget.getPlotItem().getAxis(axis).setPen(axis_pen)
        self.plot_widget.getPlotItem().getAxis(axis).setTextPen(axis_pen)

        # PLOTTING
        self.line = self.plot_widget.plot(self.x_data, self.y_data, pen=plot_pen, brush=brush, fillLevel=np.min(self.y_data))

        # LABELS
        self.plot_widget.getPlotItem().setLabel("top", f"x = {0000.00}, y = {000.00}", **styles)
        self.plot_widget.getPlotItem().setLabel("left", "Intensity (a.u.)", **styles)
        self.plot_widget.getPlotItem().setLabel("bottom", "Raman shift (1/cm)", **styles) # jednotky ?

        # CROSSHAIR
        self.crosshair_v = pg.InfiniteLine(angle=90, movable=False, pen=crosshair_pen)
        self.plot_widget.addItem(self.crosshair_v, ignoreBounds=True)
        self.mouse_movement_proxy = pg.SignalProxy(self.plot_widget.scene().sigMouseMoved, rateLimit=60, slot=self.update_crosshair)
        self._crosshair_visible = True

        # LAYOUT
        layout = QHBoxLayout(self)
        layout.addWidget(self.plot_widget)

        # SET INIT MODE - VIEW
        self.mode = PlotMode.VIEW

        # MISC
        self.linear_region = None


    def update_data(self, new_x, new_y):
        self.x_data, self.y_data  = new_x, new_y
        self.line.setData(self.x_data, self.y_data)
        self.plot_widget.getPlotItem().enableAutoRange()

    def update_crosshair(self, event):
        coordinates = event[0]
        mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(coordinates)
        self.crosshair_v.setPos(mouse_point.x())
        self.plot_widget.getPlotItem().setLabel("top", f"x = {mouse_point.x():.2f}, y = {self.y_data[np.argmin(np.abs(self.x_data - mouse_point.x()))]:.2f}")

    def hide_crosshair(self):
        self.crosshair_v.hide()
        self.mouse_movement_proxy.blockSignal = True
        self._crosshair_visible = False
    
    def show_crosshair(self):
        self.crosshair_v.show()
        self.mouse_movement_proxy.blockSignal = False
        self._crosshair_visible = True

    def set_mode(self, new_mode : PlotMode):
        if new_mode == self.mode: # no change
            return

        if new_mode == PlotMode.VIEW:
            self._set_view_mode()
        elif new_mode == PlotMode.CROPPING:
            self._set_cropping_mode()
        elif new_mode == PlotMode.COSMIC_RAY_REMOVAL:
            self._set_crr_mode()
        elif new_mode == PlotMode.BACKGROUND_REMOVAL:
            self._set_bg_removal_mode()
        else:
            # invalid mode -> do nothing
            return 

        self.mode = new_mode

    def _set_view_mode(self):
        if self.linear_region is not None:
            self.plot_widget.removeItem(self.linear_region)
            self.linear_region = None
        if not self._crosshair_visible:
            self.show_crosshair()

    def _set_cropping_mode(self):
        if self._crosshair_visible:
            self.hide_crosshair()
        if self.linear_region is None:
            self.add_selection_region()

    def _set_bg_removal_mode(self):
        self._set_view_mode()

    def _set_crr_mode(self):
        self._set_view_mode()

    def add_selection_region(self):
        # PENS AND BRUSHES
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
    
    def update_region(self, new_region):
        self.linear_region.setRegion(new_region)
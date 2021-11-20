from PySide6.QtCore import QSize
from PySide6.QtWidgets import QHBoxLayout, QWidget
import pyqtgraph as pg
import numpy as np
from data_processing import Data

class Plot(QWidget):
    def __init__(self, x, y):
        super().__init__()
        self.plot_widget = pg.PlotWidget(self)

        styles = {"color": "yellow", "font-size": "14px"}
        self.plot_widget.setLabel("left", "Intensity (a.u.)", **styles)
        self.plot_widget.setLabel("bottom", "Raman shift (1/cm)", **styles)
        self.plot_widget.plot(x, y)

        layout = QHBoxLayout(self)
        layout.addWidget(self.plot_widget)


class Picture(QWidget): # custom widget
    def __init__(self, data):
        super().__init__()
        
        self.image_view = pg.ImageView()

        # hide histogram and buttons -> but it may be useful
        self.image_view.ui.histogram.hide()
        self.image_view.ui.roiBtn.hide()
        self.image_view.ui.menuBtn.hide()
        # self.label = pg.LabelItem("NICE")
        # self.image_view.getView().addItem(self.label)

        # matplotlib's viridis colormap (6 colors)
        viridis = [(68.0, 1.0, 84.0), (64.0, 67.0, 135.0), (41.0, 120.0, 142.0), (34.0, 167.0, 132.0), (121.0, 209.0, 81.0), (253.0, 231.0, 36.0)]
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 6), color=viridis)
        self.image_view.setColorMap(cmap)

        self.image_view.setImage(data, autoRange=False)

        self.image_view.getView().setMouseEnabled(x=False, y=False) # fix image location
        self.image_view.getView().setDefaultPadding(0)

        # Add crosshair lines.
        self.crosshair_v = pg.InfiniteLine(angle=90, movable=False)
        self.crosshair_h = pg.InfiniteLine(angle=0, movable=False)
        self.image_view.addItem(self.crosshair_v, ignoreBounds=True)
        self.image_view.addItem(self.crosshair_h, ignoreBounds=True)

        self.mouse_movement_proxy = pg.SignalProxy(self.image_view.getView().scene().sigMouseMoved, rateLimit=60, slot=self.update_crosshair)
        # self.mouse_click_proxy = pg.SignalProxy(self.image_view.getView().scene().sigMouseClicked, rateLimit=60, slot=self.update_label)

        layout = QHBoxLayout(self)
        layout.addWidget(self.image_view)

    def update_crosshair(self, e):
        pos = e[0]
        self.mouse_point = self.image_view.getView().mapSceneToView(pos)
        self.crosshair_v.setPos(self.mouse_point.x())
        self.crosshair_h.setPos(self.mouse_point.y())

    """
    def update_label(self):
        self.label.setText(f"x={self.mouse_point.x():0.1f}, y={self.mouse_point.y():0.1f}")
    """

class PicPlot(QWidget): # combination of Picture and correspondings Plots
    def __init__(self, file_name):
        super().__init__()

        self.layout = QHBoxLayout(self)
        self.data = Data(file_name)
        self.plot = Plot(self.data.x_axis, self.data.data[0,0])
        self.pic = Picture(self.data.averages)

        # TODO: velikost inastavit podle velikosti okna nejspis
        self.plot.setFixedSize(QSize(500,500))
        self.pic.setFixedSize(QSize(500,500)) # self.pic.height(),self.pic.width() ??

        self.layout.addWidget(self.plot)
        self.layout.addWidget(self.pic)

        self.mouse_click_proxy = pg.SignalProxy(self.pic.image_view.getView().scene().sigMouseClicked, rateLimit=60, slot=self.replot)

    def replot(self):
        # TODO: exituje lepsi zpusob prekresleni grafu?
        self.plot.plot_widget.clear()
        print((int(np.floor(self.pic.mouse_point.x())),int(np.floor(self.pic.mouse_point.y()))))
        # TODO: posetrit aby se ignorovalo kliknuti na indexy ktere neexistuji
        self.plot.plot_widget.getPlotItem().plot(self.data.x_axis, self.data.data[int(np.floor(self.pic.mouse_point.x())),int(np.floor(self.pic.mouse_point.y()))])
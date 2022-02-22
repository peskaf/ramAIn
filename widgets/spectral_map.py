from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QHBoxLayout
from PySide6.QtCore import QRectF

import pyqtgraph as pg
import numpy as np

from widgets.plot_mode import PlotMode
from widgets.adjustable_handles_roi import AdjustableHandlesROI

class SpectralMap(QFrame):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.win = pg.GraphicsLayoutWidget()
        
        self.image_view = pg.ImageView()
        self.data = data

        # hide histogram and buttons
        self.image_view.ui.histogram.hide()
        self.image_view.ui.roiBtn.hide()
        self.image_view.ui.menuBtn.hide()

        # matplotlib's viridis colormap (6 colors)
        viridis = [(68.0, 1.0, 84.0), (64.0, 67.0, 135.0), (41.0, 120.0, 142.0), (34.0, 167.0, 132.0), (121.0, 209.0, 81.0), (253.0, 231.0, 36.0)]
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 6), color=viridis)
        self.image_view.setColorMap(cmap)

        self.image_view.setImage(self.data, autoRange=False)

        self.set_limits() # set limits for image manipulation (scrolling, moving)
        
        self.image_view.getView().setDefaultPadding(0)
        self.image_view.getView().setBackgroundColor(QColor(240,240,240))

        # Add crosshair lines.
        self.crosshair_v = pg.InfiniteLine(angle=90, movable=False)
        self.crosshair_h = pg.InfiniteLine(angle=0, movable=False)
        self.image_view.addItem(self.crosshair_v, ignoreBounds=True)
        self.image_view.addItem(self.crosshair_h, ignoreBounds=True)
        self._crosshair_visible = True

        self.mouse_movement_proxy = pg.SignalProxy(self.image_view.getView().scene().sigMouseMoved, rateLimit=60, slot=self.update_crosshair)

        layout = QHBoxLayout(self)
        layout.addWidget(self.image_view)

        # SET INIT MODE
        self.mode = PlotMode.VIEW

        # MISC
        self.ROI = None

    def update_crosshair(self, event):
        pos = event[0]
        self.mouse_point = self.image_view.getView().mapSceneToView(pos)

        self.crosshair_v.setPos(self.mouse_point.x())
        self.crosshair_h.setPos(self.mouse_point.y())

    def update_image(self, new_data):
        self.data = new_data
        self.image_view.setImage(self.data)
        self.set_limits()
        self.image_view.getView().enableAutoRange() # reset view zoom if zoomed

    def set_limits(self):
        img = self.image_view.getImageItem()
        offset = np.absolute(img.height()-img.width())/2

        if img.height() > img.width():
            self.image_view.getView().setLimits(xMin=-offset, xMax=img.height()-offset, yMin=0, yMax=img.height())
        else:
            self.image_view.getView().setLimits(xMin=0, xMax=img.width(), yMin=-offset, yMax=img.width()-offset)
    
    def hide_crosshair(self):
        # proxy signal not blocked here -> it is needed for x y mousepoint update
        self.crosshair_v.hide()
        self.crosshair_h.hide()
        self._crosshair_visible = False

    def show_crosshair(self):
        self.crosshair_v.show()
        self.crosshair_h.show()
        self._crosshair_visible = True

    def set_mode(self, new_mode : PlotMode):
        if new_mode == self.mode: # no change
            return

        if new_mode == PlotMode.VIEW:
            self._set_view_mode()
        elif new_mode == PlotMode.CROPPING:
            self._set_cropping_mode()
        else:
            # invalid mode -> do nothing
            return 

        self.mode = new_mode

    def _set_view_mode(self):
        if self.ROI is not None:
            self.image_view.removeItem(self.ROI)
            self.ROI = None
        if not self._crosshair_visible:
            self.show_crosshair()

    def _set_cropping_mode(self):
        if self._crosshair_visible:
            self.hide_crosshair()
        if self.ROI is None:
            self.add_selection_region()

    def add_selection_region(self):

        pen = pg.mkPen(color="#F58800", width=2)
        hoverPen = pg.mkPen(color="#F8BC24", width=2)

        self.ROI = AdjustableHandlesROI(
            pos=(0,0),
            size=(self.image_view.getImageItem().width(), self.image_view.getImageItem().height()),
            maxBounds=QRectF(0, 0, self.image_view.getImageItem().width(), self.image_view.getImageItem().height()),
            sideScalers=True,
            rotatable=False,
            pen=pen,
            hoverPen=hoverPen,
            # handle pen, handle hover pen, 
            )

        # rest of handles around the ROI
        self.ROI.addScaleHandle((1,1), (0,0))
        self.ROI.addScaleHandle((0,0), (1,1))
        self.ROI.addScaleHandle((0,1), (1,0))
        self.ROI.addScaleHandle((1,0), (0,1))
        self.ROI.addScaleHandle((0,0.5), (1,0.5))
        self.ROI.addScaleHandle((0.5,0), (0.5,1))
        
        self.image_view.addItem(self.ROI)
    
    def update_ROI(self, new_pos : tuple, new_size : tuple):
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
import pyqtgraph as pg

class AdjustableHandlesROI(pg.RectROI):
    def addHandle(self, *args, **kwargs):
        self.handleSize = 10
        super(AdjustableHandlesROI, self).addHandle(*args, **kwargs)
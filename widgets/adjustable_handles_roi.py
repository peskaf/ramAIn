import pyqtgraph as pg


class AdjustableHandlesROI(pg.RectROI):
    """
    A class subclassing `pg.RectROI` so that handles are bigger.

    Attributes:
        handleSize (int): Size of the handles.
    """

    def addHandle(self, *args, **kwargs):
        """
        Overrided function to add the handles to the ROI with desired `handleSize`.
        Note the camel style for compatibility.
        """

        self.handleSize = 10
        super(AdjustableHandlesROI, self).addHandle(*args, **kwargs)

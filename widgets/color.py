from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QFrame, QSizePolicy, QWidget

# OK
# placeholder widget from https://www.pythonguis.com/
class Color(QFrame):
    def __init__(self, color, parent: QWidget = None):
        super().__init__(parent)

        # name for styling in qss file
        self.setObjectName("color")

        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))

        self.setPalette(palette)
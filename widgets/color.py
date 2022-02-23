from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QFrame, QSizePolicy

# OK
# placeholder widget from https://www.pythonguis.com/
class Color(QFrame):
    def __init__(self, color):
        super(Color, self).__init__()

        # name for styling in qss file
        self.setObjectName("color")

        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))

        self.setPalette(palette)
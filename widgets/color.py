from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QFrame, QSizePolicy, QWidget


class Color(QFrame):
    """
    A placeholder widget from https://www.pythonguis.com/.
    It is a rectangle with only given color.
    """

    def __init__(self, color: str, parent: QWidget = None) -> None:
        super().__init__(parent)

        # name for styling in the qss file
        self.setObjectName("color")

        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # set color
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)
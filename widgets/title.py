from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt

class Title(QFrame):
    """
    A widget for application title (name).
    """

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        # name for qss styling
        self.setObjectName("title")

        layout = QHBoxLayout()

        # icon has to be set as a lable with no text but with pixmap
        icon = QLabel()
        icon.setPixmap(QPixmap("icons/RamAIn_logo_f8bc24.svg"))
    
        # enables resizing the icon to fit
        icon.setScaledContents(True)
        layout.addWidget(icon)

        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)

        self.setLayout(layout)

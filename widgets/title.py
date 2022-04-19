from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

# OK
class Title(QFrame):
    def __init__(self):
        super(Title, self).__init__()

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
from PySide6.QtGui import QIcon, QCursor
from PySide6.QtWidgets import QFrame, QPushButton
from PySide6.QtCore import Qt

# OK
class CollapseButton(QPushButton):
    def __init__(self, frame : QFrame, text=""):
        super(CollapseButton, self).__init__()

        # name for future styling in qss
        self.setObjectName("collapse_button")

        # frame to be collapsed/expanded on button click
        self.frame = frame

        # icons
        self.checked_icon = QIcon("icons/chevron_down.svg")
        self.unchecked_icon = QIcon("icons/chevron_right.svg")

        self.setIcon(self.checked_icon)

        self.setCheckable(True)
        self.setText(text)

        # cursor on button hover
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # connect function that is to be executed on btn click
        self.clicked.connect(self.collapse_layout)

    def collapse_layout(self):
        if self.isChecked():
            self.setIcon(self.unchecked_icon)
            self.frame.hide()
        else:
            self.setIcon(self.checked_icon)
            self.frame.show()
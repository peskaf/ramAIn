from PySide6.QtGui import QIcon, QCursor
from PySide6.QtWidgets import QFrame, QPushButton
from PySide6.QtCore import Qt

class CollapseButton(QPushButton):
    def __init__(self, to_collapse : QFrame, text="", parent=None):
        super().__init__(parent)

        self.to_collapse = to_collapse
        self.setObjectName("collapse_button")
        self.checked_icon = QIcon("icons/chevron_down.svg")
        self.unchecked_icon = QIcon("icons/chevron_right.svg")

        self.setCheckable(True)
        self.setIcon(self.checked_icon)
        self.setText(text)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        self.clicked.connect(self.collapse_layout)

    def collapse_layout(self):
        if self.isChecked():
            self.setIcon(self.unchecked_icon)
            self.to_collapse.hide()
        else:
            self.setIcon(self.checked_icon)
            self.to_collapse.show()
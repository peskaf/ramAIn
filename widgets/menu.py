from PySide6.QtGui import QIcon, QCursor
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt

# MENU
class Menu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("menu")

        icon = QIcon("icons/icon.svg")
        buttons = [
            QPushButton("   Manual Preprocessing", icon=icon), # spaces because of spacing between icon and text
            QPushButton("   Database", icon=icon),
            QPushButton("   Project", icon=icon),
            QPushButton("   Settings", icon=icon),
            QPushButton("   Raman", icon=icon)
        ]

        layout = QVBoxLayout()

        for button in buttons:
            # self.setObjectName("nazev") # pripadne pak pro routing tlacitek
            button.setCursor(QCursor(Qt.PointingHandCursor))
            layout.addWidget(button)


        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)
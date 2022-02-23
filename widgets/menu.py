from PySide6.QtGui import QIcon, QCursor
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt

# OK
class Menu(QFrame):
    def __init__(self):
        super(Menu, self).__init__()

        # set name for qss styling
        self.setObjectName("menu")

        # TODO: add relevant icons to the menu items
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

        # buttons should be aligned to the top of the layout
        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)
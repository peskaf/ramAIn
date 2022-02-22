from PySide6.QtWidgets import QFrame, QGridLayout, QLabel

class BackgroundRemoval(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QGridLayout()

        layout.addWidget(QLabel("TBD"), 0, 0)

        self.setLayout(layout)
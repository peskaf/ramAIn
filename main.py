from PySide6.QtGui import QIcon, QFontDatabase, QScreen, QCloseEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import QCoreApplication, QSettings

from widgets.menu import Menu
from widgets.header import Header

import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        QCoreApplication.setOrganizationName("RamAIn")
        QCoreApplication.setOrganizationDomain("ramain.cz")
        QCoreApplication.setApplicationName("RamAIn")

        self.setWindowTitle("  " + "RamAIn")
        self.setWindowIcon(QIcon("icons/RamAIn_logo_R_f8bc24.svg"))
        
        self.settings = QSettings()

        # how the whole app will look like
        layout = QVBoxLayout()
        layout.addWidget(Header(self))
        layout.addWidget(Menu(self))

        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        QFontDatabase.addApplicationFont("fonts/montserrat.ttf")

        with open("themes/light_style.qss") as f:
            self.setStyleSheet(f.read())
    
    def show(self):
        # centering has to be called after show -> overriding
        super().show()
        self.center()

    def center(self):
        center_point = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

if __name__ == "__main__":
    app = QApplication([])
    main = MainWindow()
    main.show()
    app.exec()
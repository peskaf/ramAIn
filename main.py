from PySide6.QtGui import QIcon, QFontDatabase, QScreen
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import QCoreApplication, QSettings

from widgets.menu import Menu
from widgets.header import Header

import os
import sys

basedir = os.path.dirname(__file__)

class MainWindow(QMainWindow):
    """
    The main widnow of the application.
    """

    def __init__(self) -> None:
        """
        The constructor of the main window of the application.
        """

        super().__init__()

        QCoreApplication.setOrganizationName("RamAIn")
        QCoreApplication.setOrganizationDomain("ramain.cz")
        QCoreApplication.setApplicationName("RamAIn")

        self.setWindowTitle("  " + "RamAIn")
        self.setWindowIcon(QIcon(os.path.join(basedir, "icons/RamAIn_logo_R_f8bc24.svg")))
        
        self.settings = QSettings()

        # how the whole app will look like
        layout = QVBoxLayout()
        layout.addWidget(Header(self))
        layout.addWidget(Menu(self))

        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        QFontDatabase.addApplicationFont(os.path.join(basedir, "fonts/montserrat.ttf"))
        
        stylesheet = "themes/light_style.qss"
        with open(os.path.join(basedir, stylesheet)) as f: # os.path.abspath(stylesheet)
            self.setStyleSheet(f.read())

    def show(self) -> None:
        """
        A functino to show the main window.
        """

        # centering has to be called after show -> overriding
        super().show()
        self.center()

    def center(self) -> None:
        """
        A function to center the window on the screen.
        """

        center_point = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

if __name__ == "__main__":
    app = QApplication([])
    main = MainWindow()
    main.show()
    app.exec()

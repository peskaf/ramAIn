from PySide6.QtGui import QIcon, QFontDatabase, QScreen
from PySide6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt

from widgets.menu import Menu
from widgets.header import Header
from widgets.manual_preprocessing import ManualPreprocessing

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("  " + "RamAIn")
        self.setWindowIcon(QIcon("icons/icon.svg"))
        
        # self.setWindowFlag(Qt.FramelessWindowHint) # hide windows frame

        # how the whole app will look like
        layout = QVBoxLayout()
        layout.addWidget(Header())

        layout2 = QHBoxLayout()
        layout2.addWidget(Menu())

        # sem pak widget layout kde jsou za sebou ta okna a poradi se meni pomoci tlacitek v menu
        layout2.addWidget(ManualPreprocessing())

        layout.addLayout(layout2)
    
        widget = QWidget()
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
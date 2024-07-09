import sys
from PySide6.QtWidgets import QApplication
from ramain.views.main_window import MainWindow


class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        self.setOrganizationName("RamAIn")
        self.setApplicationName("RamAIn")
        self.main_view = MainWindow()  # self.model, self.main_controller)
        self.main_view.show()


if __name__ == "__main__":
    app = App(sys.argv)
    sys.exit(app.exec())
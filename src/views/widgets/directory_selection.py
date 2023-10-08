from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QFileDialog
from PySide6.QtCore import QSettings
from typing import Union

import os


class DirectorySelection(QWidget):
    _settings: QSettings = QSettings()

    def __init__(
        self, registry_value: Union[str, None] = None, parent: QWidget = None
    ) -> None:
        super().__init__(parent)

        self.directory: Union[str, None] = os.getcwd()
        self.registry_value = registry_value
        if self.registry_value:
            self.directory = self._settings.value(self.registry_value, os.getcwd())

        self._check_directory_exists()

        self.change_dir_btn = QPushButton("Change Directory", parent=self)
        self.change_dir_btn.clicked.connect(self._change_directory)

        self.curr_dir = QLabel(str(self.directory), parent=self)

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.curr_dir, 0, 0)
        # NOTE: (0,1) is better -> folder name needs to be truncated somehow
        grid_layout.addWidget(self.change_dir_btn, 1, 0)

        self.setLayout(grid_layout)

    def _check_directory_exists(self) -> None:
        if not os.path.exists(self.directory):
            self.directory = os.getcwd()

    def _change_directory(self) -> None:
        self._check_directory_exists()

        temp_dir = QFileDialog.getExistingDirectory(
            self, "Select Directory", self.directory
        )

        # invalid selection
        if temp_dir is None or len(temp_dir) == 0:
            return

        if self.registry_value:
            self._settings.setValue(self.registry_value, temp_dir)

        self.directory = temp_dir
        self.curr_dir.setText(str(self.directory))

    def getCurrentDirectory(self) -> str:
        return self.directory

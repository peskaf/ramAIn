from PySide6.QtWidgets import QFrame, QVBoxLayout, QListWidgetItem, QMessageBox, QScrollArea, QSizePolicy, QPushButton, QFileDialog, QHBoxLayout, QProgressDialog, QWidget
from PySide6.QtCore import Qt, Signal, QSettings, QEventLoop, QCoreApplication
from PySide6.QtGui import QIcon, QPixmap

from widgets.files_view import FilesView
from widgets.collapse_button import CollapseButton
from widgets.decomposition_methods import DecompositionMethods
from widgets.component import Component

from data import Data

import os

class SpectraDecomposition(QFrame):
    update_progress = Signal()

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.icon = QIcon("icons/view.svg") #TODO: change

        self.settings = QSettings()

        # files
        self.files_view = FilesView(self)

        self.curr_folder = self.files_view.data_folder
        self.curr_file = None
        self.curr_data = None

        self.files_view.file_list.currentItemChanged.connect(self.update_file)
        self.files_view.folder_changed.connect(self.update_folder)

        # method selection + params
        self.methods = DecompositionMethods(self)

        # connect signals from the methods
        self.init_pca()
        self.init_nmf()

        # results visualization
        self.components_area = QScrollArea(self)
        self.components_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.components_frame = QFrame(self.components_area)
        self.components = QVBoxLayout()
        self.components_area.setWidgetResizable(True)

        self.components_frame.setLayout(self.components)
        self.components_frame.setMouseTracking(True)

        self.components_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.components_area.setWidgetResizable(True)

        self.components_area.setWidget(self.components_frame)

        # misc
        self.init_file_error_widget()
        self.file_error.hide()

        self.export_button = QPushButton("Export Components")
        self.export_button.clicked.connect(self.export_components)

        self.methods.setEnabled(False)
        self.export_button.setEnabled(False)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.export_button)
        buttons_layout.setAlignment(Qt.AlignLeft)

        layout = QVBoxLayout()
        layout.addWidget(CollapseButton(self.files_view, "Choose File", self))
        layout.addWidget(self.files_view)
        layout.addWidget(CollapseButton(self.methods, "Choose Method", self))
        layout.addWidget(self.methods)
        layout.addWidget(self.components_area)
        layout.addLayout(buttons_layout)
        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)

    def update_file(self, file: QListWidgetItem) -> None:
        """
        A function to update the file that is to be processed.

        Parameters:
            file (QListWidgetItem): File to be processed.
        """

        if file is None:
            return # do nothing if no file is provided
        else:
            temp_curr_file = file.text()

        try:
            self.curr_data = Data(os.path.join(self.curr_folder, temp_curr_file))
        except:
            self.file_error.show()
            return

        self.methods.reset()
        self.methods.setEnabled(True)

        self.curr_file = temp_curr_file

    def update_folder(self, new_folder_name: str) -> None:
        """
        A function to set `self.curr_folder` to `new_folder_name`.
        """

        self.curr_folder = new_folder_name

    def init_file_error_widget(self) -> None:
        """
        A function to create an error message box.
        """

        self.file_error = QMessageBox()
        self.file_error.setIconPixmap(QPixmap("icons/x-circle.svg"))
        self.file_error.setText("File has invalide structure and cannot be loaded.")
        self.file_error.setInformativeText("RamAIn currently supports only .mat files originally produced by WITec spectroscopes. Sorry :(")
        self.file_error.setWindowTitle("Invalid file structure")
        self.file_error.setWindowIcon(QIcon("icons/message.svg"))
        self.file_error.setStandardButtons(QMessageBox.Ok)

    def init_pca(self) -> None:
        """
        A function to connect PCAs apply button to `PCA_apply` function.
        """

        self.methods.PCA.apply_clicked.connect(self.PCA_apply)

    def init_nmf(self) -> None:
        """
        A function to connect NMFs apply button to `NMF_apply` function.
        """

        self.methods.NMF.apply_clicked.connect(self.NMF_apply)

    def PCA_apply(self) -> None:
        """
        A function to apply PCA on the data and to show the result.
        """

        n_comps = self.methods.PCA.get_params()[0]
        self.methods.setEnabled(False)
        self.export_button.setEnabled(False)
        self.curr_data.PCA(n_comps)
        self.methods.setEnabled(True)
        self.export_button.setEnabled(True)
        self.show_components()

    def NMF_apply(self) -> None:
        """
        A function to apply NMF on the data and to show the result.
        """

        n_comps = self.methods.NMF.get_params()[0]
        NMF_max_iter = 200
        # multiply max_iter by 2 as colver is being used while both transform and fit, both with max_iter = 200
        self.make_progress_bar(2*NMF_max_iter)
        self.curr_data.NMF(n_comps, self.update_progress)
        self.progress.setValue(2*NMF_max_iter)
        self.destroy_progress_bar()
        self.show_components()

    def show_components(self) -> None:
        """
        A function to display the components obtained by one of the methods.
        """

        # remove components if some are present
        self.remove_components()

        # show new components
        for component in self.curr_data.components:
            self.components.addWidget(Component(self.curr_data.x_axis, component["plot"], component["map"], parent=self.components_frame))
        
        self.export_button.setEnabled(True)

    def remove_components(self) -> None:
        """
        A function to remove all components in the components area.
        """

        # NOTE: reversed needed here as the items would shift to lower index and would be never deleted
        for i in reversed(range(self.components.count())): 
            self.components.takeAt(i).widget().deleteLater()

    def export_components(self) -> None:
        """
        A function to open file dialog for export file selection and export method call.
        """

        # do nothing if no components are generated yet
        if len(self.curr_data.components) == 0:
            return

        # formats supported by matplotlib
        supported_formats = ["png", "pdf", "ps", "eps", "svg"]

        # filter fot QFileDialog
        regex_formats = ["*." + ext for ext in supported_formats]
        filter = ';;'.join(regex_formats)

        data_folder = self.settings.value("export_dir", self.files_view.data_folder)
        if not os.path.exists(data_folder):
            data_folder = os.getcwd()

        file_name, extension = QFileDialog.getSaveFileName(self, "Components Export", data_folder, filter=filter)

        # user exited file selection dialog without any file selected
        if file_name is None or len(file_name) == 0:
            return

        # get only format string
        format = str.split(extension, '.')[1]

        self.curr_data.export_components(file_name, format)

    def update_file_list(self) -> None:
        """
        A function to silently update the file list without any signals being emitted.
        """

        if self.curr_file is not None:
            self.files_view.file_list.currentItemChanged.disconnect()
            # update file list so that new file is visible
            self.files_view.update_list()
            # set that required file is visually selected
            self.files_view.set_curr_file(self.curr_file)
            # connect again
            self.files_view.file_list.currentItemChanged.connect(self.update_file)

    def enable_widgets(self, enable: bool) -> None:
        """
        A function to enable/disable widgets in ManulPreprocessing instance.

        Parameters:
            enable (bool): Whether widgets should be enabled or disabled.
        """

        self.files_view.setEnabled(enable)
        self.methods.setEnabled(enable)
        self.export_button.setEnabled(enable)
        self.components_area.setEnabled(enable)


    def make_progress_bar(self, maximum: int) -> None:
        """
        A function to make a progress bar dialog with `maximum` steps.

        Parameters:
            maximum (int): A number of steps that has to be reached so that 100 % is displayed.
        """

        # disable widgets
        self.enable_widgets(False)

        self.progress = QProgressDialog("Progress", "...", 0, maximum)
        self.progress.setValue(0)
        self.progress.setCancelButton(None)

        # style for progress bar that is inside progress dialog must be set here for some reason
        self.progress.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid;
                border-radius: 5px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: rgb(248, 188, 36);
                width: 1px;
            }
            """
        )

        # hide borders, title and "X" in the top right corner
        self.progress.setWindowFlags(Qt.WindowTitleHint) # Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowTitleHint
        self.progress.setWindowIcon(QIcon("icons/message.svg"))

        self.progress.setWindowTitle("Work in progress")
        self.update_progress.connect(self.set_progress)

    def set_progress(self) -> None:
        """
        A functino to increment the progress in the progress bar.
        """

        # process other events in the file loop
        QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

        # increment
        val = self.progress.value()
        self.progress.setValue(val + 1)
    
    def destroy_progress_bar(self) -> None:
        """
        A function to destroy the progress bar dialog and to disconnect all its signals.
        """

        # enable widgets again
        self.enable_widgets(True)

        self.update_progress.disconnect()
        self.progress.deleteLater()

    def get_string_name(self) -> str:
        """
        A function to return name of this widget as a string.

        Returns:
            widget_name (str): Name of the widget so that it can be recognized by the user.
        """

        return "Spectra Decomposition"

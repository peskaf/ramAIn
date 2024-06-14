import os
from PySide6.QtCore import QSettings

SETTINGS = QSettings("RamAIn", "RamAIn")

# NOTE: should not be needed as we now have set organization and app name
if SETTINGS.value("spectral_map/cmap") is None:
    SETTINGS.setValue("spectral_map/cmap", "hot")

if SETTINGS.value("source_dir") is None:
    SETTINGS.setValue("source_dir", os.getcwd())

if SETTINGS.value("logs_dir") is None:
    SETTINGS.setValue("logs_dir", os.getcwd())

if SETTINGS.value("export_dir") is None:
    SETTINGS.setValue("export_dir", os.getcwd())

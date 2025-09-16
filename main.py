import sys
import os
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from modules.dashboard import Dashboard

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and PyInstaller.
    """
    try:
        # PyInstaller stores temporary files in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Normal execution
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Patch the uic.loadUi function to use resource_path automatically
from PyQt5 import uic
_original_loadUi = uic.loadUi
def loadUi(ui_file, baseinstance=None, **kwargs):
    ui_file = resource_path(ui_file)
    return _original_loadUi(ui_file, baseinstance, **kwargs)
uic.loadUi = loadUi

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Roboto", 11)
    app.setFont(font)

    dashboard = Dashboard()
    dashboard.show()

    sys.exit(app.exec_())

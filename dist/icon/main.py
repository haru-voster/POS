import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from modules.dashboard import Dashboard

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Roboto", 11)
    app.setFont(font)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())

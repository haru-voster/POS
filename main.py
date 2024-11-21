import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from modules.intro import Intro

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Roboto", 11)
    app.setFont(font)
    intro = Intro()
    sys.exit(app.exec_())

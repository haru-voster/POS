from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from modules.dashboard import Dashboard  # Import Dashboard class

class Intro(QMainWindow):
    def __init__(self):
        super(Intro, self).__init__()
        uic.loadUi('ui/intro.ui', self)  # Load the intro UI
        self.showMaximized()
        self.show()

        # Set up a timer to close the intro screen and open the dashboard after 3 seconds
        QTimer.singleShot(1000, self.show_dashboard)  # 3000 ms = 3 seconds

    def show_dashboard(self):
        # Initialize and show the Dashboard window
        self.dashboard = Dashboard()
        self.dashboard.show()
        self.close()  # Close the intro screen

import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QMainWindow
from PyQt5.QtGui import QIcon, QFont 


class window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("First PyQt5 App")
        self.setGeometry(700, 300, 500, 500)

        label = QLabel("Hi Ivan", self)
        label.setFont(QFont("Arial", 30))
        label.setGeometry(150, 50, 200, 50)
        label.setStyleSheet("color: blue;"
                            "background-color: yellow;"
                            "font-weight: bold;")


def main():
    app = QApplication(sys.argv)
    mainWindow = window()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
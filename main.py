import sys
from PyQt5.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QLabel, QVBoxLayout, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtGui import QPixmap
from main_menu import MainMenuWindow
import os



   

if __name__ == "__main__":
    from requirement_manager import RequirementManager
    app = QApplication(sys.argv)
    shared_manager = RequirementManager()
    menu = MainMenuWindow(shared_manager)
    menu.show()
    sys.exit(app.exec_())
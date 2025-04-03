import sys
from PyQt6.QtWidgets import QApplication
from TaskManager import TaskManager

def main():
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
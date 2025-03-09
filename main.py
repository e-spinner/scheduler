import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

from database import SchedulerStorage

# Initialize storage for scheduling logic
storage = SchedulerStorage()

def main():
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Load QML UI
    engine.load("main.qml")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

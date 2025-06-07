import sys
from PyQt6.QtWidgets import QApplication
# from views.login_window import LoginWindow
# from views.dashboardsample import Dashboard
from views.Minutes import MinutesApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MinutesApp()
    window.run()
    sys.exit(app.exec())
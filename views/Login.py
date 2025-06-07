from PyQt6 import QtWidgets, uic
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMessageBox
import sys, os, json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.insert(0, PROJECT_ROOT)

from controller.LogInController import Login
from views.DashboardView import Dashboard
# from views.dashboardsample import Dashboard


# Define where credentials should be stored
APP_NAME = "PaperSync"
USER_DATA_DIR = os.path.join(os.path.expanduser("~"), f".{APP_NAME}")

if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)

CREDENTIALS_FILE = os.path.join(USER_DATA_DIR, "credentials.json")

def resource_path(relative_path):
    """ For PyInstaller: Get absolute path to resource """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create a central widget first
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Load the UI into the central widget
        # uic.loadUi(os.path.join(BASE_DIR, "..", "ui", "login.ui"), central_widget)
        uic.loadUi(resource_path("ui/login.ui"), central_widget)

        # Set fixed size
        self.setFixedSize(900, 580)

        # Set logos - now access widgets through central_widget
        # central_widget.madLogo.setPixmap(QPixmap(os.path.join(BASE_DIR, "..", "asset", "images", "madridejosLogo.png")))
        # central_widget.madLogo.setScaledContents(True)
        # central_widget.cebuLogo.setPixmap(QPixmap(os.path.join(BASE_DIR, "..", "asset", "images", "provinceCebuLogo.png")))
        # central_widget.cebuLogo.setScaledContents(True)
        central_widget.madLogo.setPixmap(QPixmap(resource_path("asset/images/madridejosLogo.png")))
        central_widget.madLogo.setScaledContents(True)
        central_widget.cebuLogo.setPixmap(QPixmap(resource_path("asset/images/provinceCebuLogo.png")))
        central_widget.cebuLogo.setScaledContents(True)

        # Store references to widgets for easier access
        self.userInput = central_widget.userInput
        self.passInput = central_widget.passInput
        self.rememberChkBox = central_widget.rememberChkBox
        self.loginBtn = central_widget.loginBtn

        # Center the window
        self.center_window()

        # Connect signals
        self.loginBtn.clicked.connect(self.handle_login)

        # Load saved credentials if remembered
        self.load_credentials()

        # Initialize login controller
        self.login_controller = Login()


    def center_window(self):
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            int((screen.width() - size.width()) / 2),
            int((screen.height() - size.height()) / 2)
        )

    def load_credentials(self):
        if os.path.exists(CREDENTIALS_FILE):
            try:
                with open(CREDENTIALS_FILE, "r") as file:
                    data = json.load(file)
                    self.userInput.setText(data.get("username", ""))
                    self.passInput.setText(data.get("password", ""))
                    self.rememberChkBox.setChecked(True)
            except Exception as e:
                print(f"[ERROR] Could not load credentials: {e}")

    def save_credentials(self, username, password):
        try:
            with open(CREDENTIALS_FILE, "w") as file:
                json.dump({"username": username, "password": password}, file)
        except Exception as e:
            print(f"[ERROR] Could not save credentials: {e}")

    def clear_credentials(self):
        if os.path.exists(CREDENTIALS_FILE):
            try:
                os.remove(CREDENTIALS_FILE)
            except Exception as e:
                print(f"[ERROR] Could not delete credentials: {e}")

    def handle_login(self):
        username = self.userInput.text()
        password = self.passInput.text()
        remember = self.rememberChkBox.isChecked()

        try:
            is_authenticated = self.login_controller.authenticate(username, password)
            if is_authenticated:
                if remember:
                    self.save_credentials(username, password)
                else:
                    self.clear_credentials()

                self.dashboard = Dashboard(username)
                self.dashboard.show()
                self.close()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# if __name__ == "__main__":
#     # Allow relative import from root even if run from /views
#     sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#     app = QtWidgets.QApplication(sys.argv)
#     window = LoginWindow()
#     window.show()
#     sys.exit(app.exec())

# from PyQt6.QtWidgets import QMessageBox
# import sys
# import os
# from PyQt6 import uic



# class LogOut():
#     def __init__(self, current_window):
#         from views.login_window import LoginWindow
#         self.current_window = current_window
        
#     def show_message(self):
#         reply = QMessageBox.question(
#             self.current_window,
#             "Confirm Logout",
#             "Are you sure you want to log out?",
#             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
#         )
        
#         if reply == QMessageBox.StandardButton.Yes:
#             self.current_window.close()
            
#             #Load back to the login window
#             BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#             login_ui_path = os.path.join(BASE_DIR, "..", "ui", "login_window.ui")
#             login_window = uic.loadUI(login_ui_path)
#             login_window.setWindowTitle("Papersync - Login")
#             login_window.show()
            
#             self.login_window = login_window

# from PyQt6.QtWidgets import QMessageBox

# class LogOut:
#     def __init__(self, current_window):
#         self.current_window = current_window
#         self.login_window = None  # Hold a persistent reference

#     def show_message(self):
#         # Create the confirmation message box
#         reply = QMessageBox(self.current_window)
#         reply.setWindowTitle("Confirm Logout")
#         reply.setText("Are you sure you want to log out?")
#         reply.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

#         # Optional: your custom styles
#         reply.setStyleSheet("""
#             QMessageBox {
#                 background-color: #1b3652;
#                 color: white;
#             }
#             QMessageBox QPushButton {
#                 background-color: #2c3e50;
#                 color: white;
#                 border-radius: 5px;
#                 padding: 8px;
#             }
#             QMessageBox QPushButton:hover {
#                 background-color: #34495e;
#             }
#         """)

#         reply.exec()

#         if reply.clickedButton() == reply.button(QMessageBox.StandardButton.Yes):
#             self.open_login_window()  # Open login window before closing current
#             self.current_window.close()

#     def open_login_window(self):
#         from views.login_window import LoginWindow
#         self.login_window = LoginWindow()
#         self.login_window.show()

from PyQt6.QtWidgets import QMessageBox

class LogOut:
    def __init__(self, current_window):
        self.current_window = current_window

    def show_message(self):
        reply = QMessageBox(self.current_window)
        reply.setWindowTitle("Confirm Logout")
        reply.setText("Are you sure you want to log out?")
        reply.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        reply.setStyleSheet("""
            QMessageBox {
                background-color: #1b3652;
                color: white;
            }
            QMessageBox QPushButton {
                background-color: #2c3e50;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QMessageBox QPushButton:hover {
                background-color: #34495e;
            }
        """)

        user_response = reply.exec()

        if user_response == QMessageBox.StandardButton.Yes:
            self.restart_to_login()

    def restart_to_login(self):
        from views.Login import LoginWindow
        self.current_window.hide()  # Hide current window

        self.login_window = LoginWindow()
        self.login_window.show()

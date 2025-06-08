# #views/DashboardView.py

# from PyQt6 import uic
# from PyQt6.QtWidgets import QMainWindow, QMessageBox, QFileDialog
# from PyQt6.QtGui import QIcon, QPixmap
# from PyQt6.QtCore import QPropertyAnimation, QTimer, QTime, QDate
# import os
# import random


# BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# from database.connection import Database
# from controller.LogoutController import LogOut

# from views.proposeMeasuresample import ProposeMeasureApp
# from views.CommunicationDoc import CommunicationDocApp
# from views.OtherDocument import OtherDocumentApp
# from views.Minutes import MinutesApp

# from controller.TrashbinController import TrashbinController
# from controller.HistoryController import HistoryController


# class Dashboard(QMainWindow):
#     def __init__(self, username):  # Pass username when creating the Dashboard window
#         super().__init__()
#         self.username = username  
#         self.db = Database()
#         self.db.connect()
        
#         # Load UI
#         uic.loadUi(os.path.join(BASE_DIR, "..", "ui", "dashboard(5).ui"), self)
        
#         # ─── Set initial stacked page ──────────────────────────────────────
#         self.mainStack.setCurrentIndex(0)
        
#         #  Set title, icon, etc...
#         self.setWindowTitle("paperSync")
#         self.setGeometry(300, 200, 1000, 500)
#         self.setWindowIcon(QIcon(os.path.join(BASE_DIR, "..", "asset", "images", "madridejosLogo.png")))

#         self.logoLabel.setPixmap(QPixmap(os.path.join(BASE_DIR, "..", "asset", "images", "madridejosLogo.png")))
#         self.logoLabel.setScaledContents(True)

#         self.pfpLabel.setPixmap(QPixmap(os.path.join(BASE_DIR, "..", "asset", "images", "profilePic.png")))
#         self.pfpLabel.setScaledContents(True)
#         self.pfpLabel.setPixmap(QPixmap(os.path.join(BASE_DIR, "..", "asset", "images", "profilePic.png")))
#         self.pfpLabel.setScaledContents(True)
#         self.profileSquareLabel.setPixmap(QPixmap(os.path.join(BASE_DIR, "..", "asset", "images", "profilePicSquare.png")))
#         self.profileSquareLabel.setScaledContents(True)
#         self.ctuLogoLabel.setPixmap(QPixmap(os.path.join(BASE_DIR, "..", "asset", "images", "ctu_logo.png")))
#         self.ctuLogoLabel.setScaledContents(True)
        
#         self.icons = {
#             "menuBtn": "menu.svg",
#             "homeBtn": "home.svg",
#             "trashBtn": "trash-2.svg",
#             "historyBtn": "clock.svg",
#             "profileBtn": "user.svg",
#             "askHelpBtn": "help-circle.svg",
#             "logOutBtn": "log-out.svg",
#             "themeBtn": "colorTheme.png",
#             "addBtn": "plus.svg"
#         }

#         for btn_name, icon in self.icons.items():
#             btn = getattr(self, btn_name)
#             btn.setIcon(QIcon(os.path.join(BASE_DIR, "..", "asset", "icons", icon)))
            
            
#         self.EXPANDED, self.COLLAPSED = 200, 70
#         self.menuContainer.setMaximumWidth(self.COLLAPSED)
#         self.sidebar_expanded = False
        
#         def toggle_sidebar():
#             # global sidebar_expanded
#             anim = QPropertyAnimation(self.menuContainer, b"maximumWidth", self)
#             anim.setDuration(250)
#             if self.sidebar_expanded:
#                 anim.setStartValue(self.EXPANDED); anim.setEndValue(self.COLLAPSED)
#                 self.menuBtn.setIcon(QIcon(os.path.join(BASE_DIR, "..", "asset", "icons", "menu.svg")))
#             else:
#                 anim.setStartValue(self.COLLAPSED); anim.setEndValue(self.EXPANDED)
#                 self.menuBtn.setIcon(QIcon(os.path.join(BASE_DIR, "..", "asset", "icons", "arrow-left-circle.svg")))
#             anim.start()
#             self._sidebar_anim = anim
#             self.sidebar_expanded = not self.sidebar_expanded

    
#         #navigations
#         self.menuBtn.clicked.connect(toggle_sidebar)
        
#         self.homeBtn.clicked.connect(self.go_to_home_page)
        
#         self.trashBtn.clicked.connect(self.go_to_trash_page)
        
#         self.historyBtn.clicked.connect(self.go_to_history_page)

#         self.profileBtn.clicked.connect(self.go_to_profile_page)

#         self.askHelpBtn.clicked.connect(self.go_to_askhelp_page)

        
        
#         #open 4 tables
#         self.pmBtn.clicked.connect(self.open_propose_measure)
#         self.commDocbtn.clicked.connect(self.open_communication_doc)
#         self.minBtn.clicked.connect(self.open_minutes)
#         self.odBtn.clicked.connect(self.open_other_doc)
        
#         # Logout
#         self.logOutBtn.clicked.connect(self.log_out)

#         self.user_display(username)

        
#         self.trashbin_controller = TrashbinController(self, self.db, self.username)
#         self.history_controller = HistoryController(self, self.db, self.username)


#     # display user for welcome
#     def user_display(self, username):
#         db = Database()
#         db.connect()

#         first_name = db.get_user_first_name(username)

#         # Close the database connection
#         db.close()
#         if first_name:
#             greetings = [
#                 "Welcome back, {}!",
#                 "Hi there, {}!",
#                 "Good to see you, {}!",
#                 "Hello, {}!",
#                 "Greetings, {}!"
#             ]

#             selected_greeting = random.choice(greetings).format(first_name)

#             self.welcomeLabel.setText(selected_greeting)
#             self.usernameLabel.setText(first_name)
#         else:
#             # Handle the case when the first name is not found
#             self.welcomeLabel.setText("Welcome!")
#             self.usernameLabel.setText("User")
    
    
#     def go_to_home_page(self):
#         self.mainStack.setCurrentIndex(0)
    
#     # def go_to_trash_page(self):
#     #     self.mainStack.setCurrentIndex(1)

#     # def go_to_history_page(self):
#     #     self.mainStack.setCurrentIndex(2)

#     # In your DashboardView.py (add these methods to the Dashboard class)

#     def go_to_profile_page(self):
#         self.mainStack.setCurrentIndex(3)
#         self.load_profile_data()

#     def load_profile_data(self):
#         """Load user profile data into the profile page"""
#         self.profile_controller = ProfileController(self.username)
        
#         # Get profile data
#         profile_data = self.profile_controller.get_profile_data()
#         if profile_data:
#             firstname, lastname, birthdate, address, prof_pic, username = profile_data
            
#             # Set profile picture
#             profile_pic_path = self.profile_controller.get_profile_pic_path()
#             self.pfpLabel.setPixmap(QPixmap(profile_pic_path))
#             self.profileSquareLabel.setPixmap(QPixmap(profile_pic_path))
            
#             # Set current values in edit fields
#             self.lastNameInput.setText(lastname)
#             self.firstNameInput.setText(firstname)
#             if birthdate:
#                 self.birthdateInput.setDate(birthdate)
#             self.addressInput.setText(address if address else "")
            
#             # Set username display (read-only)
#             self.usernameDisplay.setText(username)
            
#             # Connect edit profile buttons
#             self.editProfileBtn.clicked.connect(lambda: self.profileStackedWidget.setCurrentIndex(1))
#             self.cancelBtn.clicked.connect(lambda: self.profileStackedWidget.setCurrentIndex(0))
#             self.saveBtn.clicked.connect(self.save_profile_changes)
#             self.choosePhotoBtn.clicked.connect(self.choose_profile_picture)
            
#             # Connect password change button if you have one
#             if hasattr(self, 'changePasswordBtn'):
#                 self.changePasswordBtn.clicked.connect(self.change_password)

#     def choose_profile_picture(self):
#         """Open file dialog to choose a new profile picture"""
#         file_dialog = QFileDialog()
#         file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg)")
#         if file_dialog.exec():
#             selected_files = file_dialog.selectedFiles()
#             if selected_files:
#                 self.photoPathLabel.setText(os.path.basename(selected_files[0]))
#                 self.new_profile_pic_path = selected_files[0]

#     def save_profile_changes(self):
#         """Save profile changes to database"""
#         firstname = self.firstNameInput.text()
#         lastname = self.lastNameInput.text()
#         birthdate = self.birthdateInput.date().toPyDate()
#         address = self.addressInput.text()
        
#         # Get profile pic path if a new one was selected
#         new_pic_path = getattr(self, 'new_profile_pic_path', None)
        
#         if self.profile_controller.update_profile(firstname, lastname, birthdate, address, new_pic_path):
#             QMessageBox.information(self, "Success", "Profile updated successfully!")
#             self.profileStackedWidget.setCurrentIndex(0)
#             self.load_profile_data()  # Refresh profile data
#         else:
#             QMessageBox.warning(self, "Error", "Failed to update profile.")

#     def change_password(self):
#         """Handle password change"""
#         current_pass = self.currentPassInput.text()
#         new_pass = self.newPassInput.text()
#         confirm_pass = self.confirmPassInput.text()
        
#         if new_pass != confirm_pass:
#             QMessageBox.warning(self, "Error", "New passwords don't match.")
#             return
        
#         if self.profile_controller.change_password(current_pass, new_pass):
#             QMessageBox.information(self, "Success", "Password changed successfully!")
#             # Clear password fields
#             self.currentPassInput.clear()
#             self.newPassInput.clear()
#             self.confirmPassInput.clear()
#         else:
#             QMessageBox.warning(self, "Error", "Failed to change password. Current password may be incorrect.")


    
#     # In DashboardView.py

#     def load_motivation_text(self):
#         """Load the current motivation text"""
#         text = self.profile_controller.get_motivation_text()
#         self.motivationInput.setPlainText(text)
        
#         # Connect save button if you have one
#         if hasattr(self, 'saveMotivationBtn'):
#             self.saveMotivationBtn.clicked.connect(self.save_motivation_text)

#     def save_motivation_text(self):
#         """Save the motivation text"""
#         text = self.motivationInput.toPlainText()
#         self.profile_controller.update_motivation_text(text)
#         QMessageBox.information(self, "Success", "Motivation text updated for everyone!")

#     def load_accomplishments(self):
#         """Load user accomplishments"""
#         accomplishments = self.profile_controller.get_accomplishments()
        
#         # Clear existing items
#         for i in reversed(range(self.accomplishmentsLayout.count())): 
#             self.accomplishmentsLayout.itemAt(i).widget().setParent(None)
        
#         # Add new items
#         for acc_id, text, is_completed in accomplishments:
#             item = CheckListItem()
#             item.line_edit.setText(text)
#             item.checkbox.setChecked(is_completed)
            
#             # Connect signals to save changes
#             item.line_edit.textChanged.connect(
#                 lambda text, acc_id=acc_id: self.update_accomplishment_text(acc_id, text))
#             item.checkbox.stateChanged.connect(
#                 lambda state, acc_id=acc_id: self.update_accomplishment_status(acc_id, state))
#             item.delete_button.clicked.connect(
#                 lambda _, acc_id=acc_id: self.delete_accomplishment(acc_id))
            
#             self.accomplishmentsLayout.addWidget(item)

#     def add_accomplishment_item(self):
#         """Add a new accomplishment item"""
#         item = CheckListItem()
#         item.line_edit.setPlaceholderText("Write accomplishment...")
        
#         # Connect the line edit's editingFinished signal to save the new item
#         item.line_edit.editingFinished.connect(
#             lambda: self.save_new_accomplishment(item))
        
#         self.accomplishmentsLayout.addWidget(item)

#     def save_new_accomplishment(self, item):
#         """Save a newly created accomplishment"""
#         text = item.line_edit.text()
#         if text:  # Only save if there's actual text
#             self.profile_controller.add_accomplishment(text)
#             self.load_accomplishments()  # Refresh the list

#     def update_accomplishment_text(self, acc_id, text):
#         """Update accomplishment text in database"""
#         self.profile_controller.update_accomplishment(acc_id, text, False)

#     def update_accomplishment_status(self, acc_id, state):
#         """Update accomplishment completion status in database"""
#         is_completed = state == 2  # Qt.Checked is 2
#         self.profile_controller.update_accomplishment(acc_id, None, is_completed)

#     def delete_accomplishment(self, acc_id):
#         """Delete an accomplishment from database"""
#         self.profile_controller.delete_accomplishment(acc_id)
#         self.load_accomplishments()  # Refresh the list



#     def go_to_askhelp_page(self):
#         self.mainStack.setCurrentIndex(4)

    
    
    
#     #trashbin_display
#     def go_to_trash_page(self):
#         self.mainStack.setCurrentIndex(1)
#         self.trashbin_controller.load_trash_data()
    
    
#     #history_display
#     def go_to_history_page(self):
#         self.mainStack.setCurrentIndex(2)
#         self.history_controller.load_history_data()
    
    
    
#     def open_propose_measure(self):
#         self.pm_window = ProposeMeasureApp(self.username)
#         self.pm_window.show()
#         self.hide()
    
#     def open_communication_doc(self):
#         self.cd_window = CommunicationDocApp(self.username)
#         self.cd_window.show()
#         self.hide()
    
#     def open_minutes(self):
#         self.minutes_window = MinutesApp(self.username)
#         self.minutes_window.show()
#         self.hide()
        
#     def open_other_doc(self):
#         self.od_window = OtherDocumentApp(self.username)
#         self.od_window.show()
#         self.hide() 
    
#     def log_out(self):
#         self.logout_handler = LogOut(self)
#         self.logout_handler.show_message()
        
# views/DashboardView.py
# views/DashboardView.py

from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLineEdit, QPushButton
from PyQt6.QtGui import QIcon, QPixmap, QCursor
from PyQt6.QtCore import QPropertyAnimation, QTimer, QTime, QDate, Qt, QSize
import os
import random
import sys
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.insert(0, PROJECT_ROOT)

from database.connection import Database
from controller.LogoutController import LogOut
from controller.ProfileController import ProfileController
from controller.TrashbinController import TrashbinController
from controller.HistoryController import HistoryController

from views.ProposeMeasure import ProposeMeasureApp
from views.CommunicationDoc import CommunicationDocApp
from views.OtherDocument import OtherDocumentApp
from views.Minutes import MinutesApp


def resource_path(*relative_paths):
    """ For PyInstaller: Get absolute path to resource """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, *relative_paths)



class ClickableFrame(QFrame):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)



# if getattr(sys, 'frozen', False):
#     # Running in packaged mode
#     BASE_DIR = sys._MEIPASS  # PyInstaller temp folder
# else:
#     # Running in dev mode
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    

class Dashboard(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username  
        self.db = Database()
        self.db.connect()
        
        
        
        # Load UI
        # uic.loadUi(os.path.join(BASE_DIR, "..", "ui", "dashboard.ui"), self)
        uic.loadUi(resource_path("ui/dashboard.ui"), self)

        # uic.loadUi(os.path.join(BASE_DIR, "ui", "dashboard.ui"), self)

        # ─── Set initial stacked page ──────────────────────────────────────
        self.mainStack.setCurrentIndex(0)
        
        # Set title, icon, etc...,
        self.setWindowTitle("paperSync")
        # self.showFullScreen() 
        # self.setGeometry(300, 200, 1000, 500)
        self.setWindowIcon(QIcon(resource_path("asset/images/madridejosLogo.png")))

        # Set images
        self.logoLabel.setPixmap(QPixmap(resource_path("asset/images/madridejosLogo.png")))
        self.logoLabel.setScaledContents(True)

        self.pfpLabel.setPixmap(QPixmap(resource_path("asset/images/profilePic.png")))
        self.pfpLabel.setScaledContents(True)
        self.profileSquareLabel.setPixmap(QPixmap(resource_path("asset/images/profilePicSquare.png")))
        self.profileSquareLabel.setScaledContents(True)
        self.ctuLogoLabel.setPixmap(QPixmap(resource_path("asset/images/ctu_logo.png")))
        self.ctuLogoLabel.setScaledContents(True)
        
        # Set icons
        self.icons = {
            "menuBtn": "menu.svg",
            "homeBtn": "home.svg",
            "trashBtn": "trash-2.svg",
            "historyBtn": "clock.svg",
            "profileBtn": "user.svg",
            "askHelpBtn": "help-circle.svg",
            "logOutBtn": "log-out.svg",
            "themeBtn": "colorTheme.png",
            "addBtn": "plus.svg"
        }

        for btn_name, icon in self.icons.items():
            btn = getattr(self, btn_name)
            btn.setIcon(QIcon(resource_path("asset/icons", icon)))
            
        # Sidebar animation setup
        self.EXPANDED, self.COLLAPSED = 200, 70
        self.menuContainer.setMaximumWidth(self.COLLAPSED)
        self.sidebar_expanded = False
        
        # Initialize controllers
        self.trashbin_controller = TrashbinController(self, self.db, self.username)
        self.history_controller = HistoryController(self, self.db, self.username)
        self.profile_controller = ProfileController(self.username, self)
        
        # Connect signals
        self.connect_signals()
        
        # Initialize user display
        self.user_display(username)
        
        
        self.pmFrameclick.mousePressEvent = self.pm_frame_click
        self.cdFrameclick.mousePressEvent = self.cd_frame_click
        self.minFrameclick.mousePressEvent = self.min_frame_click
        self.odFrameclick.mousePressEvent = self.od_frame_click

        
    def pm_frame_click(self, event):
        self.open_propose_measure()

    def cd_frame_click(self, event):
        self.open_communication_doc()

    def min_frame_click(self, event):
        self.open_minutes()

    def od_frame_click(self, event):
        self.open_other_doc()


    def connect_signals(self):
        """Connect all UI signals to their respective methods"""
        # Sidebar toggle
        self.menuBtn.clicked.connect(self.toggle_sidebar)
        
        # Navigation buttons
        self.homeBtn.clicked.connect(self.go_to_home_page)
        self.trashBtn.clicked.connect(self.go_to_trash_page)
        self.historyBtn.clicked.connect(self.go_to_history_page)
        self.profileBtn.clicked.connect(self.go_to_profile_page)
        self.askHelpBtn.clicked.connect(self.go_to_askhelp_page)
        
        # Document type buttons
        self.pmBtn.clicked.connect(self.open_propose_measure)
        self.commDocbtn.clicked.connect(self.open_communication_doc)
        self.minBtn.clicked.connect(self.open_minutes)
        self.odBtn.clicked.connect(self.open_other_doc)
        
        # Logout
        self.logOutBtn.clicked.connect(self.log_out)

    def toggle_sidebar(self):
        """Toggle sidebar expansion/collapse"""
        anim = QPropertyAnimation(self.menuContainer, b"maximumWidth")
        anim.setDuration(250)
        if self.sidebar_expanded:
            anim.setStartValue(self.EXPANDED)
            anim.setEndValue(self.COLLAPSED)
            self.menuBtn.setIcon(QIcon(resource_path("asset/icons/menu.svg")))
        else:
            anim.setStartValue(self.COLLAPSED)
            anim.setEndValue(self.EXPANDED)
            self.menuBtn.setIcon(QIcon(resource_path("asset/icons/arrow-left-circle.svg")))
        anim.start()
        self._sidebar_anim = anim
        self.sidebar_expanded = not self.sidebar_expanded

    # ─── NAVIGATION METHODS ────────────────────────────────────────────────
    def go_to_home_page(self):
        self.mainStack.setCurrentIndex(0)
    
    def go_to_trash_page(self):
        self.mainStack.setCurrentIndex(1)
        self.trashbin_controller.load_trash_data()
    
    def go_to_history_page(self):
        self.mainStack.setCurrentIndex(2)
        self.history_controller.load_history_data()
    
    def go_to_profile_page(self):
        self.mainStack.setCurrentIndex(3)
        # Refresh profile data when navigating to profile page
        self.profile_controller.load_profile_data()
        self.profile_controller.load_accomplishments()
        self.profile_controller.load_motivation_text()
    
    def go_to_askhelp_page(self):
        self.mainStack.setCurrentIndex(4)

    # ─── DOCUMENT WINDOW METHODS ─────────────────────────────────────────
    def open_propose_measure(self):
        self.pm_window = ProposeMeasureApp(self.username)
        self.pm_window.show()
        self.hide()
    
    def open_communication_doc(self):
        self.cd_window = CommunicationDocApp(self.username)
        self.cd_window.show()
        self.hide()
    
    def open_minutes(self):
        self.minutes_window = MinutesApp(self.username)
        self.minutes_window.show()
        self.hide()
        
    def open_other_doc(self):
        self.od_window = OtherDocumentApp(self.username)
        self.od_window.show()
        self.hide()

    # ─── USER METHODS ─────────────────────────────────────────────────────
    def user_display(self, username):
        """Display welcome message with user's first name"""
        db = Database()
        db.connect()

        first_name = db.get_user_first_name(username)

        # Close the database connection
        db.close()
        if first_name:
            greetings = [
                "Welcome back, {}!",
                "Hi there, {}!",
                "Good to see you, {}!",
                "Hello, {}!",
                "Greetings, {}!"
            ]

            selected_greeting = random.choice(greetings).format(first_name)

            self.welcomeLabel.setText(selected_greeting)
            self.usernameLabel.setText(first_name)
        else:
            # Handle the case when the first name is not found
            self.welcomeLabel.setText("Welcome!")
            self.usernameLabel.setText("User")

    def log_out(self):
        """Handle logout process"""
        self.logout_handler = LogOut(self)
        self.logout_handler.show_message()


class CheckListItem(QWidget):
    """Custom widget for accomplishment items"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.accomplishment_id = None  # Will be set when loading from db
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.checkbox = QCheckBox()
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Write accomplishment...")

        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon(resource_path("asset/icons/x(blue).svg")))
        self.delete_button.setIconSize(QSize(16, 16))
        self.delete_button.setFixedSize(30, 30)
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.clicked.connect(self.remove_self)

        layout.addWidget(self.checkbox)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.delete_button)

        self.setStyleSheet("""
            QCheckBox {
                spacing: 0px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QLineEdit {
                border: none;
                padding: 5px;
                font-size: 14px;
                background-color: transparent;
                color: #112335;
            }
            QWidget {
                background-color: #f0f4f8;
                border-radius: 8px;
                padding: 5px;
            }
        """)

    def remove_self(self):
        """Remove this item from the layout"""
        parent_layout = self.parent().layout()
        if parent_layout:
            parent_layout.removeWidget(self)
            self.deleteLater()

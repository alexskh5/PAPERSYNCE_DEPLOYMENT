# controller/ProfileController.py

import os
import sys
from datetime import datetime
from PyQt6 import uic
from PyQt6.QtWidgets import (QMainWindow, QMessageBox, QFileDialog, 
                            QWidget, QHBoxLayout, QCheckBox, QLineEdit, 
                            QPushButton, QVBoxLayout)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QPropertyAnimation, Qt, QSize, QTimer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.insert(0, PROJECT_ROOT)

from database.connection import Database

class ProfileController:
    def __init__(self, username, view):
        self.username = username
        self.view = view
        self.db = Database()
        self.db.connect()
        self.staff_id = self.db.get_staff_id(username)
        
        # Path setup
        self.UPLOADS_DIR = os.path.join(PROJECT_ROOT, "uploads")
        self.PROFILE_PICS_DIR = os.path.join(self.UPLOADS_DIR, "profile_pics")
        
        # Create directories if they don't exist
        os.makedirs(self.PROFILE_PICS_DIR, exist_ok=True)
        
        # Initialize profile data
        self.load_profile_data()
        self.view.profileStackedWidget.setCurrentIndex(0)
        self.load_accomplishments()
        self.load_motivation_text()
        
        # Connect signals
        self.connect_signals()
    
    def connect_signals(self):
        """Connect all UI signals to their respective methods"""
        # Profile edit buttons
        self.view.editProfileBtn.clicked.connect(self.edit_profile)
        self.view.cancelBtn.clicked.connect(self.cancel_edit)
        self.view.saveBtn.clicked.connect(self.save_profile)
        self.view.chooseProfileBtn.clicked.connect(self.choose_profile_photo)
        
        # Accomplishments
        self.view.addBtn.clicked.connect(self.add_accomplishment_item)
        
        # Motivation board
        self.view.motivationSaveBtn.clicked.connect(self.save_motivation_text)
    
    def load_profile_data(self):
        """Load user profile data from database"""
        cursor = self.db.get_cursor()
        try:
            cursor.execute(
                "SELECT STAFF_FIRSTNAME, STAFF_LASTNAME, STAFF_BIRTHDATE, STAFF_ADDRESS, STAFF_PROF_PIC "
                "FROM STAFF WHERE STAFF_ID = %s", 
                (self.staff_id,)
            )
            result = cursor.fetchone()
            
            if result:
                firstname, lastname, birthdate, address, prof_pic = result
                
                # Set profile data in view
                self.view.fnameInput.setText(firstname)
                self.view.lnameInput.setText(lastname)
                self.view.bdInput.setDate(birthdate)
                self.view.addInput.setText(address)
                
                # Display birthdate and address in the labels
                if birthdate:
                    self.view.bdayLabel.setText(birthdate.strftime("%B %d, %Y"))  # Format as "Month Day, Year"
                if address:
                    self.view.addressLabel.setText(address)
                
                # Load profile picture if exists
                if prof_pic:
                    self.load_profile_picture(prof_pic)
                
                # Set display name
                self.view.nameLabel.setText(f"{firstname} {lastname}")
                
        except Exception as e:
            print(f"Error loading profile data: {e}")
            QMessageBox.warning(self.view, "Error", "Failed to load profile data.")
        finally:
            cursor.close()
    
    def load_profile_picture(self, pic_path):
        """Load profile picture from path"""
        try:
            if os.path.exists(pic_path):
                pixmap = QPixmap(pic_path)
                # Set for both circular and square profile pics
                self.view.pfpLabel.setPixmap(pixmap.scaled(
                    self.view.pfpLabel.size(), 
                    aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                    transformMode=Qt.TransformationMode.SmoothTransformation
                ))
                self.view.profileSquareLabel.setPixmap(pixmap.scaled(
                    self.view.profileSquareLabel.size(),
                    aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                    transformMode=Qt.TransformationMode.SmoothTransformation
                ))
        except Exception as e:
            print(f"Error loading profile picture: {e}")
    
    def edit_profile(self):
        """Switch to edit profile view"""
        self.view.profileStackedWidget.setCurrentIndex(1)
        
        # Store original values for cancel
        self.original_values = {
            'firstname': self.view.fnameInput.text(),
            'lastname': self.view.lnameInput.text(),
            'birthdate': self.view.bdInput.date(),
            'address': self.view.addInput.text(),
            'current_password': '',
            'new_password': ''
        }
    
    def cancel_edit(self):
        """Cancel editing and revert to original values"""
        self.view.profileStackedWidget.setCurrentIndex(0)

        if hasattr(self, 'original_values'):
            self.view.fnameInput.setText(self.original_values['firstname'])
            self.view.lnameInput.setText(self.original_values['lastname'])
            self.view.bdInput.setDate(self.original_values['birthdate'])
            self.view.addInput.setText(self.original_values['address'])
        else:
            print("Warning: original_values not set. Edit mode may not have been triggered.")

        self.view.currpassInput.clear()
        self.view.newpassInput.clear()

    
    def save_profile(self):
        """Save profile changes to database"""
        # Get updated values
        firstname = self.view.fnameInput.text().strip()
        lastname = self.view.lnameInput.text().strip()
        birthdate = self.view.bdInput.date().toPyDate()
        address = self.view.addInput.text().strip()
        current_password = self.view.currpassInput.text().strip()
        new_password = self.view.newpassInput.text().strip()
        
        # Validate required fields
        if not firstname or not lastname:
            QMessageBox.warning(self.view, "Error", "First name and last name are required.")
            return
        
        # Handle password change if provided
        password_update = ""
        params = []
        if current_password and new_password:
            # Verify current password
            cursor = self.db.get_cursor()
            try:
                cursor.execute(
                    "SELECT STAFF_PASSWORD FROM STAFF WHERE STAFF_ID = %s",
                    (self.staff_id,))
                db_password = cursor.fetchone()[0]
                
                if db_password != current_password:  # In real app, use hashed passwords
                    QMessageBox.warning(self.view, "Error", "Current password is incorrect.")
                    return
                
                password_update = ", STAFF_PASSWORD = %s"
                params.append(new_password)
            except Exception as e:
                print(f"Error verifying password: {e}")
                QMessageBox.warning(self.view, "Error", "Failed to verify password.")
                return
            finally:
                cursor.close()
        
        # Handle profile photo if selected
        if hasattr(self, 'new_profile_pic_path'):
            profile_pic_path = self.new_profile_pic_path
            # Copy file to profile pics directory
            try:
                import shutil
                filename = f"profile_{self.staff_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                dest_path = os.path.join(self.PROFILE_PICS_DIR, filename)
                shutil.copy2(profile_pic_path, dest_path)
                profile_pic_path = dest_path
            except Exception as e:
                print(f"Error saving profile picture: {e}")
                profile_pic_path = None
        else:
            # Get existing profile pic path
            cursor = self.db.get_cursor()
            try:
                cursor.execute(
                    "SELECT STAFF_PROF_PIC FROM STAFF WHERE STAFF_ID = %s",
                    (self.staff_id,)
                )
                profile_pic_path = cursor.fetchone()[0]
            except Exception as e:
                print(f"Error getting current profile pic: {e}")
                profile_pic_path = None
            finally:
                cursor.close()
        
        # Update database
        cursor = self.db.get_cursor()
        try:
            query = f"""
                UPDATE STAFF SET 
                    STAFF_FIRSTNAME = %s,
                    STAFF_LASTNAME = %s,
                    STAFF_BIRTHDATE = %s,
                    STAFF_ADDRESS = %s
                    {', STAFF_PROF_PIC = %s' if profile_pic_path else ''}
                    {password_update}
                WHERE STAFF_ID = %s
            """
            
            params = [
                firstname,
                lastname,
                birthdate,
                address
            ]
            
            if profile_pic_path:
                params.append(profile_pic_path)
            
            if password_update:
                params.append(new_password)
            
            params.append(self.staff_id)
            
            cursor.execute(query, params)
            self.db.commit()
            
            # Update display name
            self.view.nameLabel.setText(f"{firstname} {lastname}")
            
            # Update birthdate and address labels
            self.view.bdayLabel.setText(birthdate.strftime("%B %d, %Y"))
            self.view.addressLabel.setText(address)
            
            # Reload profile picture if changed
            if hasattr(self, 'new_profile_pic_path'):
                self.load_profile_picture(profile_pic_path)
            
            QMessageBox.information(self.view, "Success", "Profile updated successfully.")
            self.view.profileStackedWidget.setCurrentIndex(0)
            
        except Exception as e:
            self.db.rollback()
            print(f"Error updating profile: {e}")
            QMessageBox.warning(self.view, "Error", "Failed to update profile.")
        finally:
            cursor.close()
            
    def choose_profile_photo(self):
        """Open file dialog to choose profile photo"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.new_profile_pic_path = selected_files[0]
                
                # Preview the selected image
                pixmap = QPixmap(self.new_profile_pic_path)
                self.view.profileSquareLabel.setPixmap(pixmap.scaled(
                    self.view.profileSquareLabel.size(),
                    aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                    transformMode=Qt.TransformationMode.SmoothTransformation
                ))
    
    def load_accomplishments(self):
        """Load user accomplishments from database"""
        cursor = self.db.get_cursor()
        try:
            cursor.execute(
                "SELECT accomplishment_id, accomplishment_text, is_completed "
                "FROM user_accomplishments "
                "WHERE staff_id = %s "
                "ORDER BY created_at DESC",
                (self.staff_id,)
            )

            accomplishments = cursor.fetchall()

            layout = self.view.accomplishmentsContainer.layout()
            if layout is None:
                layout = QVBoxLayout()
                self.view.accomplishmentsContainer.setLayout(layout)
            else:
                # Clear existing items
                for i in reversed(range(layout.count())):
                    item = layout.itemAt(i).widget()
                    if item:
                        item.setParent(None)

            # Add items from database
            for acc_id, text, is_completed in accomplishments:
                item = CheckListItem(self.view)
                item.line_edit.setText(text)
                item.checkbox.setChecked(is_completed)
                item.accomplishment_id = acc_id
                item.parent_controller = self
                layout.addWidget(item)

        except Exception as e:
            print(f"Error loading accomplishments: {e}")
        finally:
            cursor.close()

        
    def add_accomplishment_item(self):
        item = CheckListItem(self.view)
        item.parent_controller = self
        
        # Ensure accomplishmentsContainer has a layout
        layout = self.view.accomplishmentsContainer.layout()
        if layout is None:
            layout = QVBoxLayout()
            self.view.accomplishmentsContainer.setLayout(layout)
            
        layout.addWidget(item)
    
    def save_accomplishments(self):
        """Save all accomplishments to database"""
        cursor = self.db.get_cursor()
        try:
            # First delete all existing accomplishments for this user
            cursor.execute(
                "DELETE FROM user_accomplishments WHERE staff_id = %s",
                (self.staff_id,)
            )
            
            # Save all current items
            for i in range(self.view.accomplishmentsContainer.count()):
                item = self.view.accomplishmentsContainer.itemAt(i).widget()
                if isinstance(item, CheckListItem) and item.line_edit.text().strip():
                    cursor.execute(
                        "INSERT INTO user_accomplishments "
                        "(staff_id, accomplishment_text, is_completed) "
                        "VALUES (%s, %s, %s)",
                        (self.staff_id, item.line_edit.text().strip(), item.checkbox.isChecked())
                    )
            
            self.db.commit()
            QMessageBox.information(self.view, "Success", "Accomplishments saved successfully.")
            
        except Exception as e:
            self.db.rollback()
            print(f"Error saving accomplishments: {e}")
            QMessageBox.warning(self.view, "Error", "Failed to save accomplishments.")
        finally:
            cursor.close()
    
    def load_motivation_text(self):
        """Load motivation text from database"""
        cursor = self.db.get_cursor()
        try:
            cursor.execute(
                "SELECT motivation_text FROM motivation_board ORDER BY last_updated_at DESC LIMIT 1"
            )
            result = cursor.fetchone()
            
            if result:
                self.view.motivationInput.setPlainText(result[0])
            else:
                # Default text if no motivation exists
                self.view.motivationInput.setPlainText("Pay day is coming!")
                
        except Exception as e:
            print(f"Error loading motivation text: {e}")
        finally:
            cursor.close()
    
    def save_motivation_text(self):
        """Save motivation text to database"""
        text = self.view.motivationInput.toPlainText().strip()
        
        if not text:
            QMessageBox.warning(self.view, "Error", "Motivation text cannot be empty.")
            return
        
        cursor = self.db.get_cursor()
        try:
            cursor.execute(
                "INSERT INTO motivation_board (motivation_text, last_updated_by) "
                "VALUES (%s, %s)",
                (text, self.staff_id)
            )
            self.db.commit()
            QMessageBox.information(self.view, "Success", "Motivation text updated successfully.")
        except Exception as e:
            self.db.rollback()
            print(f"Error saving motivation text: {e}")
            QMessageBox.warning(self.view, "Error", "Failed to update motivation text.")
        finally:
            cursor.close()


class CheckListItem(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.accomplishment_id = None  # Will be set when loading from db
        self.parent_controller = None  # Will be set by parent controller
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.checkbox = QCheckBox()
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Write accomplishment...")

        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon(os.path.join(BASE_DIR, "..", "asset", "icons", "x(blue).svg")))
        self.delete_button.setIconSize(QSize(16, 16))
        self.delete_button.setFixedSize(30, 30)
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.clicked.connect(self.remove_self)

        layout.addWidget(self.checkbox)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.delete_button)

        # Set up auto-save functionality
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_to_db)
        
        self.line_edit.textChanged.connect(self.schedule_save)
        self.checkbox.stateChanged.connect(self.schedule_save)

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

    def schedule_save(self):
        """Schedule a save after a short delay"""
        self.save_timer.start(500)  # 500ms delay after typing stops

    def save_to_db(self):
        """Save this item to database"""
        if not self.parent_controller:
            return
            
        cursor = self.parent_controller.db.get_cursor()
        try:
            text = self.line_edit.text().strip()
            is_completed = self.checkbox.isChecked()
            
            if self.accomplishment_id:  # Update existing
                cursor.execute(
                    "UPDATE user_accomplishments SET "
                    "accomplishment_text = %s, is_completed = %s "
                    "WHERE accomplishment_id = %s",
                    (text, is_completed, self.accomplishment_id)
                )
            elif text:  # Insert new only if there's text
                cursor.execute(
                    "INSERT INTO user_accomplishments "
                    "(staff_id, accomplishment_text, is_completed) "
                    "VALUES (%s, %s, %s) RETURNING accomplishment_id",
                    (self.parent_controller.staff_id, text, is_completed)
                )
                self.accomplishment_id = cursor.fetchone()[0]
            
            self.parent_controller.db.commit()
        except Exception as e:
            print(f"Error saving accomplishment: {e}")
            self.parent_controller.db.rollback()
        finally:
            cursor.close()

    def remove_self(self):
        """Remove this item from the layout and database"""
        if self.accomplishment_id and self.parent_controller:
            cursor = self.parent_controller.db.get_cursor()
            try:
                cursor.execute(
                    "DELETE FROM user_accomplishments WHERE accomplishment_id = %s",
                    (self.accomplishment_id,)
                )
                self.parent_controller.db.commit()
            except Exception as e:
                print(f"Error deleting accomplishment: {e}")
                self.parent_controller.db.rollback()
            finally:
                cursor.close()
        
        parent_layout = self.parent().layout()
        if parent_layout:
            parent_layout.removeWidget(self)
            self.deleteLater()

#views/pm4.py

from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QAbstractScrollArea, QTableWidget, QHeaderView,
    QPushButton, QWidget, QHBoxLayout, QTableWidgetItem, QMenu,
    QVBoxLayout, QLineEdit, QLabel, QListWidget, QToolButton,
    QAbstractItemView, QListWidgetItem, QMessageBox, QFileDialog, QInputDialog, QMainWindow
)

from PyQt6.QtCore import Qt, QSize, QDate
from PyQt6.QtGui import QIcon, QAction, QFont
import sys, os, shutil, subprocess, platform, re



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.insert(0, PROJECT_ROOT)

from database.connection import Database
from controller.ProposeMeasureController import ProposeMeasureController

def resource_path(*relative_paths):
    """ For PyInstaller: Get absolute path to resource """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, *relative_paths)


class ProposeMeasureApp:
    def __init__(self, username):
        self.username = username
        
        self.db = Database()
        self.db.connect()
        self.staff_id = self.db.get_staff_id(username)



        self.window = uic.loadUi(resource_path("ui/ProposeMeasure.ui"), QMainWindow())
        self.window.setWindowIcon(QIcon(resource_path("asset/icons/app_logo.svg")))
    
        # Then setup uploads directory
        self.UPLOADS_DIR = r"\\192.168.1.100\uploads2"
        print(f"[INIT] Initial UPLOADS_DIR: {self.UPLOADS_DIR}")
        
        # Verify network share or fall back to local
        if not self.check_network_share():
            local_uploads = os.path.join(PROJECT_ROOT, "uploads")
            print(f"[INIT] Falling back to local storage: {local_uploads}")
            self.UPLOADS_DIR = local_uploads
            os.makedirs(self.UPLOADS_DIR, exist_ok=True)
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Network Storage Unavailable")
            msg.setInformativeText(
                f"Could not access network storage at:\n{self.UPLOADS_DIR}\n\n"
                f"Falling back to local storage at:\n{local_uploads}"
            )
            msg.setWindowTitle("Storage Warning")
            msg.exec()
        
        print(f"[INIT] Final UPLOADS_DIR: {self.UPLOADS_DIR}")
        print(f"[INIT] Directory exists: {os.path.exists(self.UPLOADS_DIR)}")
        if os.path.exists(self.UPLOADS_DIR):
            print(f"[INIT] Initial contents: {os.listdir(self.UPLOADS_DIR)}")
        
                
        # Local development path (default)
        #self.UPLOADS_DIR = os.path.join(PROJECT_ROOT, "uploads")
        # self.UPLOADS_DIR = r"C:\paperSync\uploads"
        
        # Uncomment this when deploying to client and NAS is mounted
        # self.UPLOADS_DIR = "/mnt/nas/uploads"  # For Linux
        # self.UPLOADS_DIR = "/Volumes/NASShare/uploads"  # For macOS


        #for flexible environtment
        # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        # PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

        # # Will use NAS path if UPLOADS_DIR env variable is set, else default to local
        # self.UPLOADS_DIR = os.getenv("UPLOADS_DIR", os.path.join(PROJECT_ROOT, "uploads"))

        if not os.path.exists(self.UPLOADS_DIR):
            os.makedirs(self.UPLOADS_DIR)
        sys.path.insert(0, PROJECT_ROOT)


        # self.app = QApplication(sys.argv)
        # self.window = uic.loadUi(os.path.join(BASE_DIR, "..", "ui", "proposeMeasuredups.ui"))
        # self.window = uic.loadUi(resource_path("ui/ProposeMeasure.ui"), QMainWindow())
        
        # self.window.setWindowFlags(Qt.WindowType.Window)  # enable minimize/maximize/close
        # self.window.resize(1200, 800)  # initial window size
        # self.window.setMinimumSize(800, 600)  # optional limit
        # self.window.show() 
        
        # self.window.setWindowIcon(QIcon(resource_path("asset/icons/app_logo.svg")))
        # self.window.showFullScreen() 
        # if parent_geometry:
        #     self.window.setGeometry(parent_geometry)
        # else:
        #     self.window.setGeometry(300, 200, 1000, 500)
        # print(f"Window size: {self.window.size()}")
        # print(f"Frame size: {self.window.frameSize()}")

        self.window.stackedWidget.setCurrentIndex(0)


        # --- to get today's date ---
        self.window.dateReceivedInput.setDate(QDate.currentDate())
        self.window.sessionDateInput.setDate(QDate.currentDate())
        self.window.seriesyearInput.setDate(QDate.currentDate())

        # Table setup   
        self.table: QTableWidget = self.window.proposeTableDetails


        self.controller = ProposeMeasureController(self.table, self.db, ui=self.window)
        self.controller.load_data_display()

        self.setup_ui()

    def setup_ui(self):
        self.load_condition_types()
        self.setup_table()
        self.setup_buttons()
        self.setup_sort_menu()
        self.set_icons()
        self.setup_attachments()
        self.setup_navigation()
        self.setup_search()
        self.window.setWindowTitle("Propose Measure")
        self.window.setGeometry(300, 200, 1000, 500)


    # --- to load condition types ---
    def load_condition_types(self):
        cursor = self.db.get_cursor()
        try:
            cursor.execute("SELECT cond_id, cond_name FROM condition_type ORDER BY cond_id")
            rows = cursor.fetchall()
            self.window.conditionInput.clear()
            self.window.editConditionInput.clear()


            self.window.conditionInput.addItem("Select here", None)
            self.window.editConditionInput.addItem("Select here", None)


            for cond_id, cond_name in rows:
                self.window.conditionInput.addItem(cond_name, cond_id)
                self.window.editConditionInput.addItem(cond_name, cond_id)

        except Exception as e:
            print(f"Error loading condition types: {e}")
            self.db.rollback()  # Rollback the transaction if there's an error

    # --- Table Setup ---
    def setup_table(self):
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        headerH = self.table.horizontalHeader()
        headerV = self.table.verticalHeader()
        headerV.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        
        
        # Set custom font
        font = QFont()
        font.setPointSize(14)  # Change 12 to any desired size
        self.table.setFont(font)

        # Optional: Adjust font for header
        header_font = QFont()
        header_font.setPointSize(18)  # Larger size for header
        header_font.setBold(True)

        for col in range(self.table.columnCount()):
            item = self.table.horizontalHeaderItem(col)
            if item:
                item.setFont(header_font)
        
        for col in range(self.table.columnCount()):
            headerH.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(True)
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.horizontalHeader().setFixedHeight(50)


    # --- Create Button Setup ---
    def handle_create_new(self):
        # Clear input fields
        self.window.titleInput.clear()
        self.window.receivedFromInput.clear()
        self.window.remarksInput.clear()
        self.window.attachFileInput.clear()
        self.window.lineEdit.clear()          # reso_number
        self.window.lineEdit_2.clear()        # ordi_number
        self.window.sessionDateInput.setDate(QDate.currentDate())
        self.window.dateReceivedInput.setDate(QDate.currentDate())
        self.window.authorInput.clear()
        self.window.scanInput.setCurrentIndex(0)
        self.window.furnishInput.setCurrentIndex(0)
        self.window.publicationInput.setCurrentIndex(0)
        self.window.postingInput.setCurrentIndex(0)
        self.window.conditionInput.setCurrentIndex(0)
        self.window.attachFileInput.setToolTip("")  # Clear tooltip

        self.window.stackedWidget.setCurrentIndex(1)

    # --- Mapping and Validation ---
    def map_form_data_to_db_keys(self, form_data):
        return {
            "propose_date_rcvd": form_data.get("date_rcvd"),
            "propose_title": form_data.get("title"),
            "propose_rcvd_from": form_data.get("rcvd_from"),
            "remarks": form_data.get("remarks"),
            "propose_attachfile": form_data.get("attachfile"),
            "propose_reso_number": form_data.get("reso_number"),
            "propose_ordi_number": form_data.get("ordi_number"),
            "series_yr": form_data.get("series_yr"),
            "propose_session_date": form_data.get("session_date"),
            "propose_author": form_data.get("author"),
            "propose_is_scan": form_data.get("is_scan"),
            "propose_is_furnish": form_data.get("is_furnish"),
            "propose_is_publication": form_data.get("is_publication"),
            "propose_is_posting": form_data.get("is_posting"),
            "cond_id": form_data.get("cond_id"),
            "created_by": form_data.get("created_by"),
            "updated_by": form_data.get("updated_by"),
        }

    def validate_input_numbers(self, reso_number, ordi_number):
        pattern = r'^[0-9]+[A-Za-z]*$'  # numbers followed optionally by letters, e.g. 101 or 101A
        if reso_number and not re.match(pattern, reso_number):
            QMessageBox.warning(None, "Invalid Input", "Resolution number must start with digits and optionally end with letters.")
            return False
        if ordi_number and not re.match(pattern, ordi_number):
            QMessageBox.warning(None, "Invalid Input", "Ordinance number must start with digits and optionally end with letters.")
            return False
        return True

    # --- Submit and Save Handlers ---
    def handle_submit(self):
        # Collect data from form inputs (creation)
        title = self.window.titleInput.text().strip()
        rcvd_from = self.window.receivedFromInput.text().strip()

        if not title or not rcvd_from:
            QMessageBox.warning(self.window, "Missing Information", "Please fill in Title and Received From fields.")
            self.window.stackedWidget.setCurrentIndex(1)
            return

        cond_data = self.window.conditionInput.currentData()
        form_data = {
            "date_rcvd": self.window.dateReceivedInput.date().toPyDate(),
            "title": title,
            "rcvd_from": rcvd_from,
            "remarks": self.window.remarksInput.toPlainText(),
            "attachfile": self.window.attachFileInput.toolTip(),  # tooltip holds the file paths string
            "reso_number": self.window.lineEdit.text().strip(),
            "ordi_number": self.window.lineEdit_2.text().strip(),
            "series_yr": self.window.seriesyearInput.date().toPyDate(),  # Returns datetime.date(2025, 1, 1,
            "session_date": self.window.sessionDateInput.date().toPyDate(),
            "author": self.window.authorInput.text().strip(),
            "is_scan": self.window.scanInput.currentText().strip().lower() == "yes",
            "is_furnish": self.window.furnishInput.currentText().strip().lower() == "yes",
            "is_publication": self.window.publicationInput.currentText().strip().lower() == "yes",
            "is_posting": self.window.postingInput.currentText().strip().lower() == "yes",
            "cond_id": int(cond_data) if cond_data is not None else None,
            "created_by": self.staff_id,
            "updated_by": self.staff_id,
            # "created_by": 1,
            # "updated_by": 1,
        }

        reso_number = form_data["reso_number"]
        ordi_number = form_data["ordi_number"]

        if not self.verify_attachments(form_data["attachfile"]):
            return
            
        # Validate format first
        if not self.validate_input_numbers(reso_number, ordi_number):
            return

        mapped_data = self.map_form_data_to_db_keys(form_data)
        propose_id = getattr(self.controller, 'editing_propose_id', None)

        # Check duplicates after format validation
        if not self.controller.validate_and_check_duplicates(reso_number, ordi_number, propose_id):
            return

        success = self.controller.save_to_database(mapped_data, propose_id=propose_id)

        if success:
            QMessageBox.information(self.window, "Success", "Propose Measure successfully saved.")
            print("Attach file path:", form_data["attachfile"])
            self.controller.load_data_display()
            self.window.stackedWidget.setCurrentIndex(0)
        else:
            # Remain on form view to fix the issue
            self.window.stackedWidget.setCurrentIndex(1)

    def save_form_data(self):
        # Collect data from form inputs (editing)
        selected_row = self.controller.editing_row
        if selected_row is None:
            QMessageBox.warning(self.window, "No Selection", "No row selected for editing.")
            return

        propose_id_item = self.controller.table.item(selected_row, 5)
        if not propose_id_item:
            QMessageBox.warning(self.window, "Error", "Could not determine the record ID.")
            return

        propose_id = int(propose_id_item.text())
        title = self.window.editTitleInput.text().strip()
        rcvd_from = self.window.editReceivedFromInput.text().strip()

        if not title or not rcvd_from:
            QMessageBox.warning(self.window, "Missing Information", "Please fill in Title and Received From fields.")
            self.window.stackedWidget.setCurrentIndex(2)
            return

        cond_data = self.window.editConditionInput.currentData()
        attachfile_tooltip = self.window.editAttachFileInput.toolTip()

        form_data = {
            "date_rcvd": self.window.editDateReceivedInput.date().toPyDate(),
            "title": title,
            "rcvd_from": rcvd_from,
            "remarks": self.window.editRemarksInput.toPlainText(),
            "attachfile": attachfile_tooltip,
            "reso_number": self.window.lineEdit_3.text().strip(),
            "ordi_number": self.window.lineEdit_4.text().strip(),
            "series_yr": self.window.editSeriesDateInput.date().toPyDate(),  # Returns datetime.date(2025, 1, 1)
            "session_date": self.window.editSessionDateInput.date().toPyDate(),
            "author": self.window.editAuthorInput.text().strip(),
            "is_scan": self.window.editScanInput.currentText().strip().lower() == "yes",
            "is_furnish": self.window.editFurnishInput.currentText().strip().lower() == "yes",
            "is_publication": self.window.editPublicationInput.currentText().strip().lower() == "yes",
            "is_posting": self.window.editPostingInput.currentText().strip().lower() == "yes",
            "cond_id": int(cond_data) if cond_data is not None else None,
            "updated_by": self.staff_id,
            # "updated_by": 1,
        }

        reso_number = form_data["reso_number"]
        ordi_number = form_data["ordi_number"]

        # Validate format first
        if not self.validate_input_numbers(reso_number, ordi_number):
            return

        mapped_data = self.map_form_data_to_db_keys(form_data)


        # Check duplicates after format validation
        if not self.controller.validate_and_check_duplicates(reso_number, ordi_number, propose_id):
            return

        success = self.controller.save_to_database(mapped_data, propose_id=propose_id)

        if success:
            QMessageBox.information(self.window, "Success", "Propose Measure updated successfully.")
            self.window.stackedWidget.setCurrentIndex(0)
            self.controller.load_data_display()
        else:
            self.window.stackedWidget.setCurrentIndex(2)  # Stay on edit form

    # --- Sorting Menu Setup ---
    def setup_sort_menu(self):
        sort_menu = QMenu(self.window)

        sort_labels = [
            "Show all",
            "---",  
            "First Reading", "Second Reading", "Third Reading",
            "On Hold", "Public Hearing", "Archived", "Approved", "Others",
            "---",  
            "Newest",
            "Oldest",
            "Title A - Z",
            "Title Z - A"
        ]

        for label in sort_labels:
            if label == "---":
                sort_menu.addSeparator()
                continue
            action = QAction(label, self.window)
            action.triggered.connect(lambda _, a=action: self.handle_sort_selection(a))
            sort_menu.addAction(action)

        tool_button: QToolButton = self.window.sortBtn

        def show_aligned_menu():
            btn_rect = tool_button.rect()
            pos = tool_button.mapToGlobal(btn_rect.bottomRight())
            pos.setX(pos.x() - sort_menu.sizeHint().width())
            pos.setY(pos.y() + 10)
            sort_menu.popup(pos)

        tool_button.clicked.connect(show_aligned_menu)
        tool_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        tool_button.setStyleSheet("QToolButton::menu-indicator { image: none; }")
        sort_menu.setStyleSheet("""
            QMenu {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                color: #112335;
            }
            QMenu::item:selected {
                background-color: #1b3652;
                color: white;
            }
        """)

    def handle_sort_selection(self, action):
        condition_text = action.text()
        if condition_text.lower() == "show all":
            self.controller.load_data_display()
        elif condition_text in ["Newest", "Oldest", "Title A - Z", "Title Z - A"]:
            self.controller.sort_data(condition_text)
        else:
            self.controller.filter_by_condition(condition_text)

    # --- Icon Setup ---
    def set_icons(self):
        icons = {
            "searchBtn": "search(blue).svg",
            "backBtn": "arrow-left-circle.svg",
            "attachFileBtn": "paperclip(black).svg",
            "editAttachFileBtn": "paperclip(black).svg",
            "sortBtn": "sort.svg",
            "removeAttachmentBtn": "remove.svg"
        }
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        for name, icon in icons.items():
            btn = getattr(self.window, name)
            btn.setIcon(QIcon(resource_path("asset/icons", icon)))

    # --- Attachment Handling ---
    def open_file(self, path):
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        except Exception as e:
            return str(e)
        return None

    def handle_attach_file(self, window, inputField):
        try:
            files, _ = QFileDialog.getOpenFileNames(window, "Select Files", "", "All Files (*)")
            if not files:
                return
    
            print(f"[DEBUG] Selected files: {files}")
            print(f"[DEBUG] Uploading to: {self.UPLOADS_DIR}")
    
            # Ensure uploads directory exists
            try:
                os.makedirs(self.UPLOADS_DIR, exist_ok=True)
                print(f"[DEBUG] Created directory if needed: {self.UPLOADS_DIR}")
            except Exception as e:
                QMessageBox.critical(window, "Error", 
                    f"Cannot create uploads directory:\n{str(e)}\n"
                    f"Path: {self.UPLOADS_DIR}")
                return
    
            current_files = inputField.toolTip().strip().split(";") if inputField.toolTip() else []
            new_files = []
    
            for file_path in files:
                try:
                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(self.UPLOADS_DIR, filename)
    
                    print(f"[DEBUG] Copying {file_path} to {dest_path}")
    
                    # Copy file (overwrite if exists)
                    shutil.copy2(file_path, dest_path)
                    
                    # Verify copy
                    if os.path.exists(dest_path):
                        new_files.append(filename)
                        print(f"[DEBUG] Successfully copied {filename}")
                    else:
                        error_msg = f"Failed to copy file: {filename}"
                        print(f"[ERROR] {error_msg}")
                        QMessageBox.warning(window, "Error", error_msg)
                except Exception as e:
                    error_msg = f"Error copying {filename}:\n{str(e)}"
                    print(f"[ERROR] {error_msg}")
                    QMessageBox.warning(window, "Error", error_msg)
                    
            # Force refresh the directory cache
            try:
                os.listdir(self.UPLOADS_DIR)
            except:
                pass
                
            if new_files:
                all_files = list(dict.fromkeys(current_files + new_files))
                inputField.setText(", ".join(os.path.basename(f) for f in all_files))
                inputField.setToolTip(";".join(all_files))
                print(f"[DEBUG] Updated attachment list: {all_files}")
        except Exception as e:
            error_msg = f"Unexpected error:\n{str(e)}"
            print(f"[ERROR] {error_msg}")
            QMessageBox.critical(window, "Error", error_msg)
            
    def open_attachments(self, window, inputField):
        filenames = inputField.toolTip().strip()
        if not filenames:
            QMessageBox.information(window, "No Attachments", "No files to open.")
            return
    
        print(f"[DEBUG] Current UPLOADS_DIR: {self.UPLOADS_DIR}")
        print(f"[DEBUG] Directory exists: {os.path.exists(self.UPLOADS_DIR)}")
        if os.path.exists(self.UPLOADS_DIR):
            print(f"[DEBUG] Directory contents: {os.listdir(self.UPLOADS_DIR)}")
    
        file_list = filenames.split(";")
        display_names = [os.path.basename(p) for p in file_list]
    
        selected_file, ok = QInputDialog.getItem(
            window,
            "Open Attachment",
            "Select a file to open:",
            display_names,
            editable=False
        )
    
        if ok and selected_file:
            index = display_names.index(selected_file)
            filename = file_list[index]
            full_path = os.path.join(self.UPLOADS_DIR, filename)
    
            print(f"[DEBUG] Trying to open file at: {full_path}")
            print(f"[DEBUG] File exists: {os.path.exists(full_path)}")
            
            if os.path.exists(full_path):
                try:
                    error = self.open_file(full_path)
                    if error:
                        QMessageBox.warning(window, "Error", 
                            f"Cannot open file:\n{error}\n"
                            f"Path: {full_path}")
                except Exception as e:
                    QMessageBox.warning(window, "Error", 
                        f"Unexpected error opening file:\n{str(e)}\n"
                        f"Path: {full_path}")
            else:
                QMessageBox.warning(window, "Not Found", 
                    f"File not found at:\n{full_path}\n"
                    f"Please verify the file exists in:\n{self.UPLOADS_DIR}")
                
    def verify_attachments(self, filenames_str):
        if not filenames_str or not filenames_str.strip():
            return True
    
        print(f"[DEBUG] Verifying attachments in: {self.UPLOADS_DIR}")
        try:
            missing_files = []
            existing_files = []
    
            for filename in filenames_str.split(";"):
                filename = filename.strip()
                if not filename:
                    continue
    
                full_path = os.path.join(self.UPLOADS_DIR, filename)
                found = False
    
                # Try up to 3 times with small delay
                for attempt in range(3):
                    if os.path.exists(full_path):
                        found = True
                        break
                    time.sleep(1)  # Wait before retrying
    
                if found:
                    existing_files.append(filename)
                else:
                    missing_files.append(filename)
    
            print(f"[DEBUG] Missing files: {missing_files}")
            print(f"[DEBUG] Existing files: {existing_files}")
    
            if missing_files:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText("Missing Files")
                msg.setInformativeText(
                    f"The following files could not be found:\n"
                    f"{', '.join(missing_files)}\n\n"
                    f"Current storage location:\n{self.UPLOADS_DIR}\n\n"
                    f"Please reattach them or check the storage location."
                )
                msg.setWindowTitle("Missing Files")
                msg.exec()
                return False
    
            return True
    
        except Exception as e:
            print(f"[ERROR] verify_attachments failed: {str(e)}")
            QMessageBox.warning(self.window, "Error", f"Could not verify attachments:\n{str(e)}")
            return False

    def check_uploads_dir(self):
        """Verify the uploads directory is accessible"""
        try:
            # First check if path exists
            if not os.path.exists(self.UPLOADS_DIR):
                return False
                
            # Try to create a test file
            test_file = os.path.join(self.UPLOADS_DIR, "test.tmp")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                return True
            except Exception as e:
                print(f"Error accessing uploads directory: {str(e)}")
                return False
        except Exception as e:
            print(f"Error checking uploads directory: {str(e)}")
            return False

    def check_uploads_dir_with_retry(self, retries=3, delay=2):
        """Check uploads directory with retries"""
        import time
        for attempt in range(retries):
            if self.check_uploads_dir():
                return True
            if attempt < retries - 1:
                time.sleep(delay)
        return False

    def check_network_share(self):
        """Check if network share is available and accessible"""
        if not self.UPLOADS_DIR.startswith(r"\\"):
            return True  # Not a network path
            
        print(f"[DEBUG] Checking network share: {self.UPLOADS_DIR}")
        
        try:
            # First check if path exists
            if not os.path.exists(self.UPLOADS_DIR):
                print(f"[DEBUG] Network path does not exist")
                return False
                
            # Try to list contents
            try:
                files = os.listdir(self.UPLOADS_DIR)
                print(f"[DEBUG] Network share accessible. Contains {len(files)} items")
                return True
            except Exception as e:
                print(f"[ERROR] Could not access network share: {str(e)}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Network share check failed: {str(e)}")
            return False
    
    def remove_attachment(self, window, inputField):
        paths = inputField.toolTip().strip()
        if not paths:
            QMessageBox.information(window, "No Attachments", "No files to remove.")
            return

        rel_paths = paths.split(";")
        display_names = [os.path.basename(p) for p in rel_paths]

        selected_file, ok = QInputDialog.getItem(
            window,
            "Remove Attachment",
            "Select a file to remove:",
            display_names,
            editable=False
        )

        if ok and selected_file:
            index = display_names.index(selected_file)
            rel_paths.pop(index)

            inputField.setText(", ".join(os.path.basename(f) for f in rel_paths))
            inputField.setToolTip(";".join(rel_paths))

    def setup_attachments(self):
        # Styling and other UI tweaks
        self.window.attachFileInput.setWordWrap(True)
        self.window.attachFileInput.setStyleSheet("QLabel { border-bottom: 1px solid black; padding: 5px; margin: 0px 10px 0px 0px; }")
        self.window.editAttachFileInput.setWordWrap(True)
        self.window.editAttachFileInput.setStyleSheet("QLabel { border-bottom: 1px solid black; padding: 5px; margin: 0px 10px 0px 0px;}")

        self.window.openAttachmentBtn.setStyleSheet("""
            QPushButton {
                color: black;
                text-decoration: underline;
                background: none;
                border: none;
                margin: 0px 10px 0px 0px;
            }
            QPushButton:hover {
                color: darkblue;
            }
        """)
        self.window.editAttachFileBtn.setStyleSheet("""
            QPushButton {
                color: black;
                text-decoration: underline;
                background: none;
                border: none;
                margin: 0px 10px 0px 0px;
            }
            QPushButton:hover {
                color: darkblue;
            }
        """)


        # Connect buttons
        self.window.openAttachmentBtn.clicked.connect(lambda: self.open_attachments(self.window, self.window.editAttachFileInput))
        self.window.removeAttachmentBtn.clicked.connect(lambda: self.remove_attachment(self.window, self.window.editAttachFileInput))
        self.window.editAttachFileBtn.clicked.connect(lambda: self.handle_attach_file(self.window, self.window.editAttachFileInput))
        self.window.attachFileBtn.clicked.connect(lambda: self.handle_attach_file(self.window, self.window.attachFileInput))

        # Make the text selectable (but not editable)
        self.window.editAttachFileInput.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)


    # --- Navigation Button Setup ---
    def setup_navigation(self):
        self.window.cancelBtn.clicked.connect(lambda: self.window.stackedWidget.setCurrentIndex(0))
        self.window.editCancelBtn.clicked.connect(lambda: self.window.stackedWidget.setCurrentIndex(0))

    # --- Search Popup Setup ---
    def setup_search(self):
        self.popup = SearchPopup(self.window, self.table)

        def show_search_popup():
            btn_rect = self.window.searchBtn.rect()
            pos = self.window.searchBtn.mapToGlobal(btn_rect.bottomRight())
            pos.setX(pos.x() - self.popup.width())
            pos.setY(pos.y() + 10)
            self.popup.move(pos)
            self.popup.show()

        self.window.searchBtn.clicked.connect(show_search_popup)

    def back_button(self):
        # from views.dashboardsample import Dashboard
        from views.DashboardView import Dashboard
        self.dashboard = Dashboard(self.username)
        self.dashboard.show()
        self.window.close()
        
    # --- Button Connections ---
    def setup_buttons(self):
        self.window.createBtn.clicked.connect(self.handle_create_new)
        self.window.submitBtn.clicked.connect(self.handle_submit)
        self.window.editsaveBtn.clicked.connect(self.save_form_data)
        self.window.backBtn.clicked.connect(self.back_button)

    # def run(self):
    #     self.window.show()
    #     sys.exit(self.app.exec())
    def show(self):
        self.window.show()


# --- Search Popup ---
class SearchPopup(QWidget):
    def __init__(self, parent=None, table_widget=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setFixedWidth(300)
        self.table_widget = table_widget

        layout = QVBoxLayout(self)
        self.search_field = QLineEdit(placeholderText="Search...")
        self.search_field.textChanged.connect(self.update_recommendations)
        layout.addWidget(self.search_field)

        self.recommendations_list = QListWidget()
        self.recommendations_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        layout.addWidget(self.recommendations_list)

        self.recommendations_list.itemClicked.connect(self.handle_item_clicked)

        self.setStyleSheet("""
            QLineEdit { padding: 6px 8px; border: 1px solid #aaa; border-radius: 4px; }
            QListWidget::item { padding: 4px; font-size: 12px; }
        """)

    def update_recommendations(self, text):
        self.recommendations_list.clear()
        if not text:
            return

        matches = []
        text_lower = text.lower()
        for row in range(self.table_widget.rowCount()):
            row_text = " | ".join(
                self.table_widget.item(row, col).text() if self.table_widget.item(row, col) else ""
                for col in range(1, self.table_widget.columnCount() - 1)
            )
            if text_lower in row_text.lower():
                matches.append((row, row_text))

        for row_index, display_text in matches:
            row_layout = QHBoxLayout()
            label = QLabel(display_text)
            view_btn = QPushButton("View")

            row_widget = QWidget()
            row_layout.addWidget(label)
            row_layout.addStretch()
            row_layout.addWidget(view_btn)
            row_widget.setLayout(row_layout)

            item = QListWidgetItem()
            item.setSizeHint(row_widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, row_index)

            self.recommendations_list.addItem(item)
            self.recommendations_list.setItemWidget(item, row_widget)

            view_btn.clicked.connect(lambda _, r=row_index: self.view_recommendation_by_row(r))

    def view_recommendation_by_row(self, row):
        self.table_widget.selectRow(row)
        self.table_widget.scrollToItem(self.table_widget.item(row, 1))
        self.hide()

    def handle_item_clicked(self, item: QListWidgetItem):
        row = item.data(Qt.ItemDataRole.UserRole)
        self.view_recommendation_by_row(row)


# if __name__ == "__main__":
#     app = ProposeMeasureApp()
#     app.run()

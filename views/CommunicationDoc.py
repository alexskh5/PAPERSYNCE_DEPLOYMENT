#views/CommunicationDoc.py

from PyQt6 import uic 
from PyQt6.QtWidgets import (
    QApplication, QAbstractScrollArea, QTableWidget, QHeaderView,
    QPushButton, QWidget, QHBoxLayout, QTableWidgetItem, QMenu,
    QVBoxLayout, QLineEdit, QLabel, QListWidget, QToolButton,
    QAbstractItemView, QListWidgetItem, QMessageBox, QFileDialog, QInputDialog
)
from PyQt6.QtCore import Qt, QSize, QDate
from PyQt6.QtGui import QIcon, QAction, QFont
import sys, os, shutil, subprocess, platform, re



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.insert(0, PROJECT_ROOT)

from database.connection import Database
from controller.CommunicationDocController import CommunicationDocController


def resource_path(*relative_paths):
    """ For PyInstaller: Get absolute path to resource """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, *relative_paths)




class CommunicationDocApp:
    def __init__(self, username, parent_geometry=None):
        self.username = username
        # Local development path (default)
        self.UPLOADS_DIR = os.path.join(PROJECT_ROOT, "uploads")

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

        self.db = Database()
        self.db.connect()

        # self.app = QApplication(sys.argv)
        self.window = uic.loadUi(resource_path("ui/commDocu.ui"))
        # if parent_geometry:
        #     self.window.setGeometry(parent_geometry)
        # else:
        #     self.window.setGeometry(300, 200, 1000, 500)
        # self.window.stackedWidget.setCurrentIndex(0)
        # print(f"Window size: {self.window.size()}")
        # print(f"Frame size: {self.window.frameSize()}")
        # --- to get today's date ---
        self.window.dateReceivedInput.setDate(QDate.currentDate())
        self.window.editDateReceivedInput.setDate(QDate.currentDate())
        
        # table setup 
        self.table: QTableWidget = self.window.communicationTableDetails
        
        self.controller = CommunicationDocController(self.table, self.db, ui=self.window)
        self.controller.load_data_display()
        
        self.setup_ui()
        
    def setup_ui(self):
        self.setup_table()
        self.setup_buttons()
        self.setup_sort_menu()
        self.set_icons()
        self.setup_attachments()
        self.setup_navigation()
        self.setup_search()
        self.window.setWindowTitle("Communication Document")
        self.window.setGeometry(300, 200, 1000, 500)


    
    def setup_table(self):
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        headerH = self.table.horizontalHeader()
        headerV = self.table.verticalHeader()
        headerV.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        
        
        font = QFont()
        font.setPointSize(14)  # Change 12 to any desired size
        self.table.setFont(font)

        # Optional: Adjust font for header
        header_font = QFont()
        header_font.setPointSize(16)  # Larger size for header
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
        

    # -- create button setup --
    def handle_create_new(self):
        # clear input fields
        self.window.eventTitleInput.clear()
        self.window.venueInput.clear()
        self.window.remarksInput.clear()
        self.window.attachFileInput.clear()
        self.window.liquidateInput.setCurrentIndex(0)
        self.window.attachFileInput.setToolTip("")
        
        self.window.stackedWidget.setCurrentIndex(1)


    # --- mapping and validation ---
    def map_form_data_to_db_keys(self, form_data):
        return {
                "comm_date_rcvd": form_data.get("date_rcvd"),
                "comm_title": form_data.get("title"),
                "comm_venue": form_data.get("venue"),
                "comm_remarks": form_data.get("remarks"),
                "comm_attachfile": form_data.get("attachFile"),
                "comm_is_liquidate": form_data.get("liquidate"),
                "created_by": form_data.get("created_by", 1),
                "updated_by": form_data.get("updated_by", 1),
            }

    def handle_submit(self):
        
        title = self.window.eventTitleInput.text().strip()
        # venue = self.window.venueInput.text().strip()
        
        if not title:
            QMessageBox.warning(self.window, "Missing Information", "Please fill in Event Title field.")
            self.window.stackedWidget.setCurrentIndex(1)
            return
        
        form_data = {
            "date_rcvd": self.window.dateReceivedInput.date().toPyDate(),
            "title": title,
            "venue": self.window.venueInput.text().strip(),
            "remarks": self.window.remarksInput.toPlainText(),
            "attachFile": self.window.attachFileInput.toolTip(),
            "liquidate": self.window.liquidateInput.currentText().strip().lower() == "yes",
            "created_by": 1,
            # "updated_by": 1, 
        }

        mapped_data = self.map_form_data_to_db_keys(form_data)
        communication_id = getattr(self.controller,'editing_communication_id', None)
        
        success = self.controller.save_to_database(mapped_data, communication_id=communication_id)
        
        if success:
                QMessageBox.information(self.window, "Success", "Communication Document successfully saved.")
                print("Attach file path:", form_data["attachFile"])
                self.controller.load_data_display()
                self.window.stackedWidget.setCurrentIndex(0)
        else:
            # Remain on form view to fix the issue
            self.window.stackedWidget.setCurrentIndex(1)


    def save_form_data(self):
        # collect data from form input (editing)
        
        selected_row = self.controller.editing_row
        if selected_row is None:
            QMessageBox.warning(self.window, "No Selection", "No row selected for editing.")
            return
        
        communication_id_item = self.controller.table.item(selected_row, 5)
        if not communication_id_item:
            QMessageBox.warning(self.window, "Error", "Could not determine the record ID.")
            return

        communication_id = int(communication_id_item.text())
        title = self.window.editEventTitleInput.text().strip()
        # rcvd_from = self.window.editReceivedFromInput.text().strip()
        
        if not title:
            QMessageBox.warning(self.window, "Missing Information", "Please fill in Event Title field.")
            self.window.stackedWidget.setCurrentIndex(2)
            return
        
        attachfile_tooltip = self.window.editAttachFileInput.toolTip()
        
        form_data = {
            "date_rcvd": self.window.editDateReceivedInput.date().toPyDate(),
            "title": title,
            "venue": self.window.editVenueInput.text().strip(),
            "remarks": self.window.editRemarksInput.toPlainText(),
            "attachFile": attachfile_tooltip,
            "liquidate": self.window.editLiquidateInput.currentText().strip().lower() == "yes",        "updated_by": 1, 
        }
        
        mapped_data = self.map_form_data_to_db_keys(form_data)

        success = self.controller.save_to_database(mapped_data, communication_id=communication_id)
        
        if success:
                QMessageBox.information(self.window, "Success", "Communication Document updated successfully.")
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
        files, _ = QFileDialog.getOpenFileNames(window, "Select Files", "", "All Files (*)")
        if files:
            os.makedirs(self.UPLOADS_DIR, exist_ok=True)

            current_files = inputField.toolTip().strip().split(";") if inputField.toolTip() else []
            new_files = []

            for file_path in files:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(self.UPLOADS_DIR, filename)

                if not os.path.exists(dest_path):
                    shutil.copy(file_path, dest_path)

                rel_path = os.path.join("uploads", filename)
                new_files.append(rel_path)

            all_files = list(dict.fromkeys(current_files + new_files))  # Remove duplicates

            inputField.setText("\n".join(os.path.basename(f) for f in all_files))
            inputField.setToolTip(";".join(all_files))

    def open_attachments(self, window, inputField):
        paths = inputField.toolTip().strip()
        if not paths:
            QMessageBox.information(window, "No Attachments", "No files to open.")
            return

        rel_paths = paths.split(";")
        display_names = [os.path.basename(p) for p in rel_paths]

        selected_file, ok = QInputDialog.getItem(window, "Open Attachment", "Select a file to open:", display_names, editable=False)
        if ok and selected_file:
            index = display_names.index(selected_file)
            full_path = os.path.join(PROJECT_ROOT, rel_paths[index])

            if os.path.exists(full_path):
                error = self.open_file(full_path)
                if error:
                    QMessageBox.warning(window, "Error", f"Cannot open file:\n{error}")
            else:
                QMessageBox.warning(window, "Not Found", f"File not found:\n{full_path}")

    def remove_attachment(self, window, inputField):
        paths = inputField.toolTip().strip()
        if not paths:
            QMessageBox.information(window, "No Attachments", "No files to remove.")
            return

        rel_paths = paths.split(";")
        display_names = [os.path.basename(p) for p in rel_paths]

        selected_file, ok = QInputDialog.getItem(window, "Remove Attachment", "Select a file to remove:", display_names, editable=False)
        if ok and selected_file:
            index = display_names.index(selected_file)
            rel_paths.pop(index)

            inputField.setText("\n".join(os.path.basename(p) for p in rel_paths))
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

    #back button
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
#     app = CommunicationDocApp()
#     app.run()
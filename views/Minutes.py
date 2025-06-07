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
from functools import partial

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.insert(0, PROJECT_ROOT)

from database.connection import Database
from controller.MinutesController import MinutesController

def resource_path(*relative_paths):
    """ For PyInstaller: Get absolute path to resource """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, *relative_paths)


class MinutesApp:
    def __init__(self, username, parent_geometry=None): 
        self.username = username
        
        self.db = Database()
        self.db.connect()
        self.staff_id = self.db.get_staff_id(username)
        
        # self.app = QApplication(sys.argv)
        self.window = uic.loadUi(resource_path("ui/minutes.ui"))
        if parent_geometry:
            self.window.setGeometry(parent_geometry)
        else:
            self.window.setGeometry(300, 200, 1000, 500)
        self.window.stackedWidget.setCurrentIndex(0)
        
        # Set today's date
        self.window.dateInput.setDate(QDate.currentDate())
        self.window.editDateInput.setDate(QDate.currentDate())
        self.window.seriesInput.setDate(QDate.currentDate())
        
        self.table: QTableWidget = self.window.minutesTableDetails
        self.controller = MinutesController(self.table, self.db, ui=self.window)
        self.controller.load_data_display()
        
        self.setup_ui()
        
    def setup_ui(self):
        self.load_minutes_types()
        self.load_minutes_subtypes()
        self.setup_table()
        self.setup_buttons()
        self.setup_sort_menu()
        self.set_icons()
        self.setup_navigation()
        self.setup_search()
        self.window.setWindowTitle("Minutes")
        self.window.setGeometry(300, 200, 1000, 500)
    
    def load_minutes_types(self):
        cursor = self.db.get_cursor()
        try:
            cursor.execute("SELECT type_id, type_name FROM minutes_type ORDER BY type_id")
            rows = cursor.fetchall()

            self.window.typeInput.clear()
            self.window.editTypeInput.clear()
            self.window.typeInput.addItem("Select here", None)
            self.window.editTypeInput.addItem("Select here", None)

            for type_id, type_name in rows:
                self.window.typeInput.addItem(type_name, type_id)
                self.window.editTypeInput.addItem(type_name, type_id)

        except Exception as e:
            print(f"Error loading minutes types: {e}")
            self.db.rollback()
    
    def load_minutes_subtypes(self):
        cursor = self.db.get_cursor()
        try:
            cursor.execute("SELECT sub_id, sub_name FROM minutes_subtype ORDER BY sub_id")
            rows = cursor.fetchall()
            
            self.window.subtypeInput.clear()
            self.window.editSubtypeInput.clear()
            self.window.subtypeInput.addItem("Select here", None)
            self.window.editSubtypeInput.addItem("Select here", None)
            
            for sub_id, sub_name in rows:
                self.window.subtypeInput.addItem(sub_name, sub_id)
                self.window.editSubtypeInput.addItem(sub_name, sub_id)

        except Exception as e:
            print(f"Error: {e}")
            self.db.rollback()
     
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
    
    def handle_create_new(self):
        self.window.dateInput.setDate(QDate.currentDate())
        self.window.typeInput.setCurrentIndex(0)
        self.window.subtypeInput.setCurrentIndex(0)
        self.window.linkInput.clear()
        self.window.stackedWidget.setCurrentIndex(1)
    
    def map_form_data_to_db_keys(self, form_data):
        return {
            "min_num": form_data["minutes_num"],
            "min_series_yr": form_data["series_yr"],   
            "min_date": form_data.get("date"),
            "min_link": form_data.get("link"),
            "type_id": form_data.get("type"),
            "sub_id": form_data.get("subtype"),
            "created_by": form_data.get("created_by", 1),
            "updated_by": form_data.get("updated_by", 1),
        }
        
    def validate_input_numbers(self, minutes_num):
        pattern = r'^[0-9]+[A-Za-z]*$'  # numbers followed optionally by letters, e.g. 101 or 101A
        if minutes_num and not re.match(pattern, minutes_num):
            QMessageBox.warning(None, "Invalid Input", "Minutes number must start with digits and optionally end with letters.")
            return False
        return True
    
    def handle_submit(self):
        
        # Collect data from form inputs (creation)
        minutes_num = self.window.minNumInput.text().strip()

        if not minutes_num:
            QMessageBox.warning(self.window, "Missing Information", "Please fill in Minutes Number fields.")
            self.window.stackedWidget.setCurrentIndex(1)
            return
        
        type_data = self.window.typeInput.currentData()
        sub_type = self.window.subtypeInput.currentData()
        
        form_data = {
            "minutes_num": minutes_num,
            "series_yr": self.window.seriesInput.date().toPyDate(),
            "date": self.window.dateInput.date().toPyDate(),
            "type": int(type_data) if type_data is not None else None,
            "subtype": int(sub_type) if sub_type is not None else None,
            "link": self.window.linkInput.toPlainText(),
            "created_by": 1,
            "updated_by": 1
        }
        
        

        # Validate format first
        if not self.validate_input_numbers(minutes_num):
            return

        
        
        mapped_data = self.map_form_data_to_db_keys(form_data)
        
        # Always pass minutes_id=None for new records
        success = self.controller.save_to_database(mapped_data, minutes_id=None)
        
        if success:
            QMessageBox.information(self.window, "Success", "Minutes successfully saved.")
            self.controller.load_data_display()
            self.window.stackedWidget.setCurrentIndex(0)
        else:
            QMessageBox.warning(self.window, "Error", "Failed to save minutes.")
            
            
            
    def save_form_data(self):
        selected_row = self.controller.editing_row
        if selected_row is None:
            QMessageBox.warning(self.window, "No Selection", "No row selected for editing.")
            return
        
        minutes_id_item = self.table.item(selected_row, 5)
        if not minutes_id_item:
            QMessageBox.warning(self.window, "Error", "Could not determine the record ID.")
            return
        
        

        minutes_id = int(minutes_id_item.text())
        
        
        # Collect data from form inputs (creation)
        minutes_num = self.window.editMinNumInput.text().strip()

        if not minutes_num:
            QMessageBox.warning(self.window, "Missing Information", "Please fill in Minutes Number fields.")
            self.window.stackedWidget.setCurrentIndex(2)
            return
        
        type_data = self.window.editTypeInput.currentData()
        sub_type = self.window.editSubtypeInput.currentData()
        
        form_data = {
            "minutes_num": minutes_num,
            "series_yr": self.window.seriesInput.date().toPyDate(),
            "date": self.window.editDateInput.date().toPyDate(),
            "type": int(type_data) if type_data is not None else None,
            "subtype": int(sub_type) if sub_type is not None else None,
            "link": self.window.editLinkInput.toPlainText(),
            "created_by": 1,
            "updated_by": 1
        }
        
        minutes_num = form_data["minutes_num"]
        
        # Validate format first
        if not self.validate_input_numbers(minutes_num):
            return

        mapped_data = self.map_form_data_to_db_keys(form_data)
        success = self.controller.save_to_database(mapped_data, minutes_id=minutes_id)

        if success:
            QMessageBox.information(self.window, "Success", "Minutes updated successfully.")
            self.window.stackedWidget.setCurrentIndex(0)
            self.controller.load_data_display()
        else:
            self.window.stackedWidget.setCurrentIndex(2)

    def setup_sort_menu(self):
        sort_menu = QMenu(self.window)
        
        sort_labels = [
            "Show all",
            "---",  
            "Session", "Public Hearing", "Other",
            "---",  
            "Newest",
            "Oldest"
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
        type_text = action.text()
        if type_text.lower() == "show all":
            self.controller.load_data_display()
        elif type_text in ["Newest", "Oldest"]:
            self.controller.sort_data(type_text)
        else:
            self.controller.filter_by_type(type_text)

    def set_icons(self):
        icons = {
            "searchBtn": "search(blue).svg",
            "backBtn": "arrow-left-circle.svg",
            "sortBtn": "sort.svg"
        }
        for name, icon in icons.items():
            btn = getattr(self.window, name)
            btn.setIcon(QIcon(resource_path("asset/icons", icon)))
      
    def setup_navigation(self):
        self.window.cancelBtn.clicked.connect(lambda: self.window.stackedWidget.setCurrentIndex(0))
        self.window.editCancelBtn.clicked.connect(lambda: self.window.stackedWidget.setCurrentIndex(0))
    
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

class SearchPopup(QWidget):
    def __init__(self, parent=None, table_widget=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setFixedWidth(300)
        self.setStyleSheet("background-color: white; border: 1px solid #ccc;")
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
#     try:
#         app = MinutesApp()
#         app.run()
#     except Exception as e:
#         print(f"Application failed to start: {e}")
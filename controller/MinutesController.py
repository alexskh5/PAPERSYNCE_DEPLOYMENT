from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import QSize, Qt, QDate
from PyQt6.QtGui import QIcon
from functools import partial
import os, sys
import json
from datetime import date, datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.insert(0, PROJECT_ROOT)

from database.connection import Database



def resource_path(*relative_paths):
    """ For PyInstaller: Get absolute path to resource """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, *relative_paths)



class MinutesController:
    def __init__(self, table_widget, db: Database, ui=None):
        self.table = table_widget
        self.db = db
        self.ui = ui
        self.editing_row = None
        self.editing_minutes_id = None
        self.table.setColumnCount(6)  # 0: actions, 1-4: data, 5: hidden ID
        self.load_data_display()
    
    def load_data_display(self):
        try:
            cursor = self.db.get_cursor()
            query = """
                SELECT m.min_id, m.min_num, t.type_name, s.sub_name, m.min_link
                FROM minutes m
                LEFT JOIN minutes_type t ON m.type_id = t.type_id
                LEFT JOIN minutes_subtype s ON m.sub_id = s.sub_id
                ORDER BY m.min_id DESC;
                """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            self.table.setRowCount(0)
            for row in rows:
                minutes_id, min_num, type_name, sub_name, link = row
                self.add_row(minutes_id, min_num, type_name or "", sub_name or "", link or "")
        except Exception as e:
            print("Error loading data:", e)
    
    def add_row(self, minutes_id, date, type, subtype, link):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Hidden ID column
        minutes_id_item = QTableWidgetItem(str(minutes_id))
        minutes_id_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, 5, minutes_id_item)
        self.table.setColumnHidden(5, True)

        # Actions cell
        action_cell = QWidget()
        edit_btn = QPushButton()
        delete_btn = QPushButton()

        edit_btn.setIcon(QIcon(resource_path("asset/icons/edit-2(blue).svg")))
        delete_btn.setIcon(QIcon(resource_path("asset/icons/trash-2(blue).svg")))

        for btn in (edit_btn, delete_btn):
            btn.setIconSize(QSize(24, 24))
            btn.setFixedSize(32, 32)

        h = QHBoxLayout()
        h.setContentsMargins(0,0,0,0)
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h.addWidget(edit_btn)
        h.addWidget(delete_btn)
        action_cell.setLayout(h)

        self.table.setCellWidget(row, 0, action_cell)

        # Data cells
        for col, val in enumerate([str(date), type, subtype, link], start=1):
            item = QTableWidgetItem(val)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, col, item)

        edit_btn.clicked.connect(partial(self.handle_edit_button_clicked, edit_btn))
        delete_btn.clicked.connect(partial(self.handle_delete_button_clicked, delete_btn))

    def filter_by_type(self, type_name):
        cursor = self.db.get_cursor()
        try:
            query = """
                SELECT m.min_id, m.min_num, t.type_name, s.sub_name, m.min_link
                FROM minutes m
                LEFT JOIN minutes_type t ON m.type_id = t.type_id
                LEFT JOIN minutes_subtype s ON m.sub_id = s.sub_id
                WHERE t.type_name = %s
                ORDER BY m.min_date DESC
            """
            cursor.execute(query, (type_name,))
            rows = cursor.fetchall()
            self.table.setRowCount(0)
            for row in rows:
                minutes_id, min_num, type_name, sub_name, min_link = row
                self.add_row(minutes_id, min_num, type_name or "", sub_name or "", min_link)
        except Exception as e:
            print(f"Error: {e}")
            self.db.rollback()
    
    def sort_data(self, sort_type):
        cursor = self.db.get_cursor()
        try:
            if sort_type == "Newest":
                cursor.execute("""
                    SELECT m.min_id, m.min_num, t.type_name, s.sub_name, m.min_link
                    FROM minutes m
                    LEFT JOIN minutes_type t ON m.type_id = t.type_id
                    LEFT JOIN minutes_subtype s ON m.sub_id = s.sub_id
                    ORDER BY m.min_date DESC
                """)
            elif sort_type == "Oldest":
                cursor.execute("""
                    SELECT m.min_id, m.min_num, t.type_name, s.sub_name, m.min_link
                    FROM minutes m
                    LEFT JOIN minutes_type t ON m.type_id = t.type_id
                    LEFT JOIN minutes_subtype s ON m.sub_id = s.sub_id
                    ORDER BY m.min_date ASC
                """)
            
            rows = cursor.fetchall()
            self.table.setRowCount(0)
            for row in rows:
                minutes_id, min_num, type_name, sub_name, min_link = row
                self.add_row(minutes_id, min_num, type_name or "", sub_name or "", min_link or "")
        
        except Exception as e:
            print(f"Error: {e}")
            self.db.rollback()
    
    def handle_delete_button_clicked(self, button):
        for row in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row, 0)
            if cell_widget and button in cell_widget.findChildren(QPushButton):
                minutes_id = self.table.item(row, 5).text()
                self.delete_minutes(minutes_id)
                break
            
    @staticmethod
    def convert_dates(obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
        
    def delete_minutes(self, minutes_id):
        try:
            # First get the row index for the minutes_id
            row = -1
            for r in range(self.table.rowCount()):
                if self.table.item(r, 5).text() == str(minutes_id):
                    row = r
                    break
            
            if row == -1:
                QMessageBox.warning(self.ui, "Error", "Record not found in table.")
                return

            reply = QMessageBox.question(
                self.ui,
                "Confirm Delete",
                "Are you sure you want to delete this record?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return  # User cancelled deletion

            cursor = self.db.get_cursor()

            # Fetch the full row data from DB as dict
            cursor.execute("""
                SELECT * FROM minutes WHERE min_id = %s;
            """, (minutes_id,))
            row_data = cursor.fetchone()
            if row_data is None:
                QMessageBox.warning(self.ui, "Error", "Data not found in database.")
                return

            # Get column names dynamically
            colnames = [desc[0] for desc in cursor.description]
            record_dict = dict(zip(colnames, row_data))

            # Insert into trash_bin (without deleted_by)
            insert_query = """
                INSERT INTO trash_bin (table_name, record_id, deleted_data)
                VALUES (%s, %s, %s::jsonb)
            """
            cursor.execute(insert_query, (
                'minutes',
                minutes_id,
                json.dumps(record_dict, default=self.convert_dates)
            ))

            # Delete from original table
            cursor.execute("DELETE FROM minutes WHERE min_id = %s;", (minutes_id,))
            self.db.commit()

            # Remove row from table widget
            self.table.removeRow(row)

            QMessageBox.information(self.ui, "Deleted", "Record moved to trash bin.")

        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self.ui, "Error", f"Failed to delete record: {e}")
            
    def handle_edit_button_clicked(self, button):
        for row in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row, 0)
            if cell_widget and button in cell_widget.findChildren(QPushButton):
                self.handle_edit(row)
                break
    
    def handle_edit(self, row):
        self.editing_row = row
        minutes_id_item = self.table.item(row, 5)
        if not minutes_id_item:
            print("No minutes_id found in the row")
            return

        minutes_id = minutes_id_item.text()
        self.editing_minutes_id = minutes_id

        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                SELECT min_num, min_series_yr, min_date, type_id, sub_id, min_link
                FROM minutes
                WHERE min_id = %s;
            """, (minutes_id,))
            result = cursor.fetchone()

            if not result:
                print(f"No data found for minutes_id: {minutes_id}")
                return

            (min_num, min_series_yr, min_date, type_id, sub_id, min_link) = result

            self.ui.editMinNumInput.setText(min_num or "")

            
            
            if min_series_yr:
                self.ui.editSeriesInput.setDate(QDate(min_series_yr.year, 1, 1))
            else:
                self.ui.editSeriesInput.setDate(QDate.currentDate())
                
            
            if min_date:
                self.ui.editDateInput.setDate(QDate(min_date.year, min_date.month, min_date.day))
            else:
                self.ui.editDateInput.setDate(QDate.currentDate())
                
            if type_id is not None:
                index = self.ui.editTypeInput.findData(type_id)
                self.ui.editTypeInput.setCurrentIndex(index if index != -1 else 0)
            else:
                self.ui.editTypeInput.setCurrentIndex(0)
            
            if sub_id is not None:
                index = self.ui.editSubtypeInput.findData(sub_id)
                self.ui.editSubtypeInput.setCurrentIndex(index if index != -1 else 0)
            else:
                self.ui.editSubtypeInput.setCurrentIndex(0)

            self.ui.editLinkInput.setText(min_link or "")
            self.ui.stackedWidget.setCurrentIndex(2)

        except Exception as e:
            print("Error retrieving minutes data:", e)
            self.ui.stackedWidget.setCurrentIndex(0)
    
    
    def validate_and_check_duplicates(self, min_num, min_id=None):
       
        # Prevent exact duplicates of reso_number
        cursor = self.db.get_cursor()
        if min_num:

            cursor.execute("""
                SELECT min_id FROM minutes
                WHERE min_num = %s
            """, (min_num,))
            result = cursor.fetchone()
            if result and (min_id is None or result[0] != min_id):
                QMessageBox.warning(None, "Duplicate", f"Minutes number '{min_num}' already exists.")
                return False
        return True
    
    
    
    def save_to_database(self, form_data, minutes_id=None):
        try:
            cursor = self.db.get_cursor()

            min_num = form_data.get("min_num", "").strip()

            # --- Check for duplicate Minutes number ---
            if min_num:
                num_check_query = """
                    SELECT COUNT(*) FROM minutes
                    WHERE min_num = %s
                    {exclude_clause}
                """.format(
                    exclude_clause="AND min_id != %s" if minutes_id else ""
                )
                params = [min_num] + ([minutes_id] if minutes_id else [])
                cursor.execute(num_check_query, params)
                min_num_exists = cursor.fetchone()[0] > 0

                if min_num_exists:
                    QMessageBox.warning(self.ui, "Duplicate Error", f"Minutes number '{min_num}' already exists.")
                    return False
            
            
            if minutes_id is None:
                # INSERT new record
                query = """
                    INSERT INTO minutes (
                        min_num, min_series_yr, min_date, type_id, sub_id, min_link, created_by, updated_by
                    ) VALUES (
                        %(min_num)s, %(min_series_yr)s, %(min_date)s, %(type_id)s, %(sub_id)s, %(min_link)s, 
                        %(created_by)s, %(updated_by)s
                    ) RETURNING min_id
                """
                cursor.execute(query, form_data)
                new_id = cursor.fetchone()[0]
                self.db.commit()
                return new_id is not None
            else:
                # UPDATE existing record
                query = """
                    UPDATE minutes SET
                        min_num = %(min_num)s, 
                        min_series_yr = %(min_series_yr)s,
                        min_date = %(min_date)s,
                        type_id = %(type_id)s,
                        sub_id = %(sub_id)s,
                        min_link = %(min_link)s,
                        updated_by = %(updated_by)s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE min_id = %(minutes_id)s
                """
                form_data['minutes_id'] = minutes_id
                cursor.execute(query, form_data)
                self.db.commit()
                return cursor.rowcount > 0

        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self.ui, "Database Error", f"An error occurred while saving:\n{e}")
            return False
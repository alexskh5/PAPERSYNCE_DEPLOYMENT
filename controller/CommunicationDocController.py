#controller/CommunicationDocController.py

from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox, QWidget, QPushButton, QHBoxLayout, QInputDialog
from PyQt6.QtCore import QSize, Qt, QDate
from PyQt6.QtGui import QIcon
from functools import partial
import platform, json, subprocess, shutil, os, sys, re
from datetime import date, datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
UPLOADS_DIR = os.path.join(PROJECT_ROOT, "uploads")
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)
    
sys.path.insert(0, PROJECT_ROOT)

from database.connection import Database


def resource_path(*relative_paths):
    """ For PyInstaller: Get absolute path to resource """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, *relative_paths)



class CommunicationDocController:
    def __init__(self, table_widget, db: Database, ui=None):
        self.table = table_widget
        self.db = db 
        self.ui = ui 
        self.editing_row = None 
        self.load_data_display()
        self.table.setColumnCount(6)
    
    # --- Loading Data Display ---
    def load_data_display(self):
        try:
            cursor = self.db.get_cursor()
            query = """
                SELECT comm_id, comm_title, comm_venue, comm_remarks, comm_is_liquidate
                FROM communication_doc 
                ORDER BY comm_id DESC;
                """
            cursor.execute(query)
            rows = cursor.fetchall()
            # print("Rows fetched:", rows)

            
            self.table.setRowCount(0)
            for row in rows:
                communication_id, title, venue, remarks, liquidate = row
                self.add_row(communication_id, title or "", venue or "", remarks or "", liquidate)
        except Exception as e:
            print("Error loading data from database:", e)
    
    
    # --- Row display setup ---
    def add_row(self, communication_id, title, venue, remarks, liquidate):
        row = self.table.rowCount()
        self.table.insertRow(row)

        
        # Store communication_id in hidden column 5
        communication_id_item = QTableWidgetItem(str(communication_id))
        communication_id_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, 5, communication_id_item)
        self.table.setColumnHidden(5, True)

        # Action buttons (edit, delete)
        action_cell = QWidget()
        edit_btn = QPushButton()
        delete_btn = QPushButton()
        edit_btn.setIcon(QIcon(resource_path("asset/icons/edit-2(blue).svg")))
        delete_btn.setIcon(QIcon(resource_path("asset/icons/rash-2(blue).svg")))
        for btn in (edit_btn, delete_btn):
            btn.setIconSize(QSize(24, 24))
            btn.setFixedSize(32, 32)

        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(edit_btn)
        h.addWidget(delete_btn)
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        action_cell.setLayout(h)

        self.table.setCellWidget(row, 0, action_cell)

        # Columns: 1-4 (reso, ordi, title, condition)
        for col, val in enumerate([title, venue, remarks, "Yes" if liquidate else "No"], start=1):
            item = QTableWidgetItem(str(val))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, col, item)


        # Connect edit button
        edit_btn.clicked.connect(partial(self.handle_edit_button_clicked, edit_btn))
        delete_btn.clicked.connect(partial(self.handle_delete_button_clicked, delete_btn))

    
    # --- sorting ---
    def sort_data(self, sort_type):
        cursor = self.db.get_cursor()
        try:
            if sort_type == "Newest":
                cursor.execute("""
                    SELECT comm_id, comm_title, comm_venue, comm_remarks, comm_is_liquidate
                    FROM communication_doc
                    ORDER BY created_at DESC
                """)
            elif sort_type == "Oldest":
                cursor.execute("""
                    SELECT comm_id, comm_title, comm_venue, comm_remarks, comm_is_liquidate
                    FROM communication_doc
                    ORDER BY created_at ASC
                """)
            elif sort_type == "Title A - Z":
                cursor.execute("""
                    SELECT comm_id, comm_title, comm_venue, comm_remarks, comm_is_liquidate
                    FROM communication_doc
                    ORDER BY LOWER(TRIM(comm_title)) ASC;

                """)
            elif sort_type == "Title Z - A":
                cursor.execute("""
                    SELECT comm_id, comm_title, comm_venue, comm_remarks, comm_is_liquidate
                    FROM communication_doc
                    ORDER BY LOWER(TRIM(comm_title)) DESC;

                """)
            else:
                cursor.execute("""
                    SELECT comm_id, comm_title, comm_venue, comm_remarks, comm_is_liquidate
                    FROM communication_doc 
                    ORDER BY comm_id DESC;
                """)

            rows = cursor.fetchall()
            self.table.setRowCount(0)
            for row in rows:
                communication_id, title, venue, remarks, liquidate = row
                self.add_row(communication_id, title or "", venue or "", remarks or "", liquidate or "")

        except Exception as e:
            print(f"Error sorting data: {e}")
            self.db.rollback()


    
    # --- Delete Function Set-up ---
    def handle_delete_button_clicked(self, button):
        for row in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row, 0)
            if cell_widget and button in cell_widget.findChildren(QPushButton):
                self.soft_delete_row(row)
                break

    
    @staticmethod
    def convert_dates(obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def soft_delete_row(self, row):
        reply = QMessageBox.question(
            self.ui,
            "Confirm Delete",
            "Are you sure you want to delete this record?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return  # User cancelled deletion

        try:
            communication_id_item = self.table.item(row, 5)
            if not communication_id_item:
                QMessageBox.warning(self.ui, "Error", "No communication_id found in the selected row.")
                return

            communication_id = int(communication_id_item.text())

            # Fetch the full row data from DB as dict
            cursor = self.db.get_cursor()
            cursor.execute("""
                SELECT * FROM communication_doc WHERE comm_id = %s;
            """, (communication_id,))
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
                'communication_doc',
                communication_id,
                json.dumps(record_dict, default=self.convert_dates)
            ))

            # Delete from original table
            cursor.execute("DELETE FROM communication_doc WHERE comm_id = %s;", (communication_id,))

            self.db.commit()

            # Remove row from table widget
            self.table.removeRow(row)

            QMessageBox.information(self.ui, "Deleted", "Record moved to trash bin.")

        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self.ui, "Error", f"Failed to delete record: {e}")
    
    
    # --- edit function Setup ---
    def handle_edit_button_clicked(self, button):
        for row in range(self.table.rowCount()):
            cell_widget = self.table.cellWidget(row, 0)
            if cell_widget and button in cell_widget.findChildren(QPushButton):
                self.handle_edit(row)
                break
    
    def handle_edit(self, row):
        self.editing_row = row
        communication_id_item = self.table.item(row, 5)
        if not communication_id_item:
            print("No communication_id found in the row")
            return

        communication_id = communication_id_item.text()
        self.editing_communication_id = communication_id

        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                SELECT comm_title, comm_venue,  comm_remarks,
                    comm_date_rcvd, comm_attachfile,
                    comm_is_liquidate
                FROM communication_doc
                WHERE comm_id = %s;
            """, (communication_id,))
            result = cursor.fetchone()

            if not result:
                print(f"No data found for propose_id: {communication_id}")
                return

            (title, venue, remarks, date_received, attachment,
            liquidate) = result

            # Fill other form fields as you had before ...
            self.ui.editEventTitleInput.setText(title or "")
            self.ui.editVenueInput.setText(venue or "")
            if date_received:
                self.ui.editDateReceivedInput.setDate(QDate(date_received.year, date_received.month, date_received.day))
            else:
                self.ui.editDateReceivedInput.setDate(QDate.currentDate())
            
            self.ui.editRemarksInput.setText(remarks or "")
            
            if attachment:
                clean_attachment_str = attachment.replace("\n", ";").replace("\r", ";")
                file_list = [f.strip() for f in clean_attachment_str.split(";") if f.strip()]

                existing_files = []
                missing_files = []

                for rel_path in file_list:
                    abs_path = os.path.join(PROJECT_ROOT, rel_path)
                    if os.path.isfile(abs_path):
                        existing_files.append(rel_path)
                    else:
                        missing_files.append(rel_path)

                self.current_attachment_files = existing_files
                display_text = "\n".join(os.path.basename(f) for f in existing_files)

                if missing_files:
                    display_text += f"\n(Missing: {', '.join(os.path.basename(f) for f in missing_files)})"
                    print(f"[Warning] Missing attachment file(s): {missing_files}")

                self.ui.editAttachFileInput.setText(display_text)
                self.ui.editAttachFileInput.setToolTip(";".join(existing_files))  # Use cleaned list only
            else:
                self.current_attachment_files = []
                self.ui.editAttachFileInput.clear()
                self.ui.editAttachFileInput.setToolTip("")
            

            def bool_to_index(val): return 1 if val else 0
            self.ui.editLiquidateInput.setCurrentIndex(bool_to_index(liquidate))
            

            self.ui.stackedWidget.setCurrentIndex(2)

        except Exception as e:
            print("Error retrieving full communication_doc data:", e)
            self.ui.stackedWidget.setCurrentIndex(0)
    
    
    # --- Save Data Function ---
    def save_to_database(self, form_data, communication_id=None):
        try:
            cursor = self.db.get_cursor()

            # --- Set the attachfile path ---
            if communication_id is None:
                attachfile_tooltip = self.ui.attachFileInput.toolTip().strip()
            else:
                attachfile_tooltip = self.ui.editAttachFileInput.toolTip().strip()

            form_data['comm_attachfile'] = attachfile_tooltip

            # --- INSERT ---
            if communication_id is None:
                query = """
                    INSERT INTO communication_doc (
                        comm_date_rcvd, comm_title, comm_venue, comm_remarks,
                        comm_attachfile, comm_is_liquidate, created_by
                    ) VALUES (
                        %(comm_date_rcvd)s, 
                        %(comm_title)s, 
                        %(comm_venue)s, 
                        %(comm_remarks)s,
                        %(comm_attachfile)s, 
                        %(comm_is_liquidate)s,
                        %(created_by)s
                    )
                """
                cursor.execute(query, form_data)

            # --- UPDATE ---
            else:
                query = """
                    UPDATE communication_doc SET
                        comm_date_rcvd = %(comm_date_rcvd)s,
                        comm_title = %(comm_title)s,
                        comm_venue = %(comm_venue)s,
                        comm_remarks = %(comm_remarks)s,
                        comm_attachfile = %(comm_attachfile)s,
                        comm_is_liquidate = %(comm_is_liquidate)s,
                        updated_by = %(updated_by)s
                    WHERE comm_id = %(communication_id)s
                """
                form_data['communication_id'] = communication_id
                cursor.execute(query, form_data)

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self.ui, "Database Error", f"An error occurred while saving:\n{e}")
            return False

        

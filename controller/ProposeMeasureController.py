#controller/pm4Controller.py

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

class ProposeMeasureController:
    def __init__(self, table_widget, db: Database, ui=None):
        self.table = table_widget
        self.db = db
        self.ui = ui # Reference to the UI window
        self.editing_row = None  # Track which row is being edited
        self.load_data_display()
        self.table.setColumnCount(6)
    
    # --- Loading Data Display ---
    def load_data_display(self):
        try:
            cursor = self.db.get_cursor()
            query = """
                SELECT pm.propose_id, pm.propose_reso_number, pm.propose_ordi_number, pm.propose_title, c.cond_name
                  FROM propose_measure pm
                LEFT JOIN condition_type c 
                ON pm.cond_id = c.cond_id
                ORDER BY pm.propose_id DESC;
                """
            cursor.execute(query)
            rows = cursor.fetchall()
            # print("Rows fetched:", rows)

            
            self.table.setRowCount(0)
            for row in rows:
                propose_id, reso_number, ordi_number, title, cond_name = row
                self.add_row(propose_id, reso_number or "", ordi_number or "", title or "", cond_name or "")
        except Exception as e:
            print("Error loading data from database:", e)
            
    
    # --- Row display setup ---
    def add_row(self, propose_id, reso, ordn, title, condition):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Modify inside add_row
        reso_display = f"Resolution {reso}" if reso else ""
        ordi_display = f"Ordinance {ordn}" if ordn else ""
                
        # Store propose_id in hidden column 5
        propose_id_item = QTableWidgetItem(str(propose_id))
        propose_id_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, 5, propose_id_item)
        self.table.setColumnHidden(5, True)

        # Action buttons (edit, delete)
        action_cell = QWidget()
        edit_btn = QPushButton()
        delete_btn = QPushButton()
        edit_btn.setIcon(QIcon(resource_path("asset/icons/edit-2(blue).svg")))
        delete_btn.setIcon(QIcon(resource_path("asset/icons/trash-2(blue).svg")))
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
        for col, val in enumerate([reso_display, ordi_display, title, condition], start=1):
            item = QTableWidgetItem(val)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, col, item)

        # Connect edit button
        edit_btn.clicked.connect(partial(self.handle_edit_button_clicked, edit_btn))
        delete_btn.clicked.connect(partial(self.handle_delete_button_clicked, delete_btn))


    # --- Filter and Sorting ---
    def filter_by_condition(self, condition_name):
        cursor = self.db.get_cursor()
        try:
            query = """
                SELECT pm.propose_id, pm.propose_reso_number, pm.propose_ordi_number, pm.propose_title, c.cond_name
                FROM propose_measure pm
                RIGHT JOIN condition_type c ON pm.cond_id = c.cond_id
                WHERE c.cond_name = %s
                ORDER BY pm.created_at DESC
            """
            cursor.execute(query, (condition_name,))
            rows = cursor.fetchall()
            self.table.setRowCount(0)
            for row in rows:
                propose_id, reso_number, ordi_number, title, cond_name = row
                self.add_row(propose_id, reso_number or "", ordi_number or "", title or "", cond_name or "")

        except Exception as e:
            print(f"Error filtering data: {e}")
            self.db.rollback()
    
    def sort_data(self, sort_type):
        cursor = self.db.get_cursor()
        try:
            if sort_type == "Newest":
                cursor.execute("""
                    SELECT pm.propose_id, pm.propose_reso_number, pm.propose_ordi_number, pm.propose_title, c.cond_name
                    FROM propose_measure pm
                    LEFT JOIN condition_type c 
                    ON pm.cond_id = c.cond_id
                    ORDER BY pm.created_at DESC
                """)
            elif sort_type == "Oldest":
                cursor.execute("""
                    SELECT pm.propose_id, pm.propose_reso_number, pm.propose_ordi_number, pm.propose_title, c.cond_name
                    FROM propose_measure pm
                    LEFT JOIN condition_type c 
                    ON pm.cond_id = c.cond_id
                    ORDER BY pm.created_at ASC
                """)
            elif sort_type == "Title A - Z":
                cursor.execute("""
                    SELECT pm.propose_id, pm.propose_reso_number, pm.propose_ordi_number, pm.propose_title, c.cond_name
                    FROM propose_measure pm
                    LEFT JOIN condition_type c 
                    ON pm.cond_id = c.cond_id
                    ORDER BY LOWER(TRIM(pm.propose_title)) ASC
                """)
            elif sort_type == "Title Z - A":
                cursor.execute("""
                    SELECT pm.propose_id, pm.propose_reso_number, pm.propose_ordi_number, pm.propose_title, c.cond_name
                    FROM propose_measure pm
                    LEFT JOIN condition_type c 
                    ON pm.cond_id = c.cond_id
                    ORDER BY LOWER(TRIM(pm.propose_title)) DESC
                """)
            else:
                cursor.execute("""
                    SELECT pm.propose_id, pm.propose_reso_number, pm.propose_ordi_number, pm.propose_title, c.cond_name
                    FROM propose_measure pm
                    LEFT JOIN condition_type c 
                    ON pm.cond_id = c.cond_id
                """)

            rows = cursor.fetchall()
            self.table.setRowCount(0)
            for row in rows:
                propose_id, reso_number, ordi_number, title, cond_name = row
                self.add_row(propose_id, reso_number or "", ordi_number or "", title or "", cond_name or "")

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
            propose_id_item = self.table.item(row, 5)
            if not propose_id_item:
                QMessageBox.warning(self.ui, "Error", "No propose_id found in the selected row.")
                return

            propose_id = int(propose_id_item.text())

            # Fetch the full row data from DB as dict
            cursor = self.db.get_cursor()
            cursor.execute("""
                SELECT * FROM propose_measure WHERE propose_id = %s;
            """, (propose_id,))
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
                'propose_measure',
                propose_id,
                json.dumps(record_dict, default=self.convert_dates)
            ))

            # Delete from original table
            cursor.execute("DELETE FROM propose_measure WHERE propose_id = %s;", (propose_id,))

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
        propose_id_item = self.table.item(row, 5)
        if not propose_id_item:
            print("No propose_id found in the row")
            return

        propose_id = propose_id_item.text()
        self.editing_propose_id = propose_id

        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                SELECT propose_reso_number, propose_ordi_number, propose_title,
                    propose_date_rcvd, propose_rcvd_from, remarks, propose_attachfile,
                    cond_id, propose_session_date, propose_author,
                    propose_is_scan, propose_is_furnish, propose_is_publication, propose_is_posting, series_yr
                FROM propose_measure
                WHERE propose_id = %s;
            """, (propose_id,))
            result = cursor.fetchone()

            if not result:
                print(f"No data found for propose_id: {propose_id}")
                return

            (reso, ordn, title, date_received, received_from, remarks, attachment,
            cond_id, session_date, author,
            is_scan, is_furnish, is_publication, is_posting, series_date) = result

            # Fill other form fields as you had before ...
            self.ui.lineEdit_3.setText(reso or "")
            self.ui.lineEdit_4.setText(ordn or "")
            self.ui.editTitleInput.setText(title or "")
            if date_received:
                self.ui.editDateReceivedInput.setDate(QDate(date_received.year, date_received.month, date_received.day))
            else:
                self.ui.editDateReceivedInput.setDate(QDate.currentDate())
                
            if series_date:
                self.ui.editSeriesDateInput.setDate(QDate(series_date.year, 1, 1))
            else:
                self.ui.editSeriesDateInput.setDate(QDate.currentDate())
                
            self.ui.editReceivedFromInput.setText(received_from or "")
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
            # The rest of your form filling logic...
            if cond_id is not None:
                index = self.ui.editConditionInput.findData(cond_id)
                self.ui.editConditionInput.setCurrentIndex(index if index != -1 else 0)
            else:
                self.ui.editConditionInput.setCurrentIndex(0)

            if session_date:
                self.ui.editSessionDateInput.setDate(QDate(session_date.year, session_date.month, session_date.day))
            else:
                self.ui.editSessionDateInput.setDate(QDate.currentDate())

            self.ui.editAuthorInput.setText(author or "")

            def bool_to_index(val): return 1 if val else 0
            self.ui.editScanInput.setCurrentIndex(bool_to_index(is_scan))
            self.ui.editFurnishInput.setCurrentIndex(bool_to_index(is_furnish))
            self.ui.editPublicationInput.setCurrentIndex(bool_to_index(is_publication))
            self.ui.editPostingInput.setCurrentIndex(bool_to_index(is_posting))

            self.ui.stackedWidget.setCurrentIndex(2)

        except Exception as e:
            print("Error retrieving full propose_measure data:", e)
            self.ui.stackedWidget.setCurrentIndex(0)
        
    def validate_and_check_duplicates(self, reso_number, ordi_number, propose_id=None):
       
        # Prevent exact duplicates of reso_number
        cursor = self.db.get_cursor()
        if reso_number:

            cursor.execute("""
                SELECT propose_id FROM propose_measure
                WHERE propose_reso_number = %s
            """, (reso_number,))
            result = cursor.fetchone()
            if result and (propose_id is None or result[0] != propose_id):
                QMessageBox.warning(None, "Duplicate", f"Resolution number '{reso_number}' already exists.")
                return False

        # Prevent exact duplicates of ordi_number
        if ordi_number:
            cursor.execute("""
                SELECT propose_id FROM propose_measure
                WHERE propose_ordi_number = %s
            """, (ordi_number,))
            result = cursor.fetchone()
            if result and (propose_id is None or result[0] != propose_id):
                QMessageBox.warning(None, "Duplicate", f"Ordinance number '{ordi_number}' already exists.")
                return False

        return True
    
    # --- Save Data Function ---
    def save_to_database(self, form_data, propose_id=None):
        try:
            cursor = self.db.get_cursor()

            reso_number = form_data.get("propose_reso_number", "").strip()
            ordi_number = form_data.get("propose_ordi_number", "").strip()

            # --- Check for duplicate Resolution number ---
            if reso_number:
                reso_check_query = """
                    SELECT COUNT(*) FROM propose_measure
                    WHERE propose_reso_number = %s
                    {exclude_clause}
                """.format(
                    exclude_clause="AND propose_id != %s" if propose_id else ""
                )
                params = [reso_number] + ([propose_id] if propose_id else [])
                cursor.execute(reso_check_query, params)
                reso_exists = cursor.fetchone()[0] > 0

                if reso_exists:
                    QMessageBox.warning(self.ui, "Duplicate Error", f"Resolution number '{reso_number}' already exists.")
                    return False

            # --- Check for duplicate Ordinance number ---
            if ordi_number:
                ordi_check_query = """
                    SELECT COUNT(*) FROM propose_measure
                    WHERE propose_ordi_number = %s
                    {exclude_clause}
                """.format(
                    exclude_clause="AND propose_id != %s" if propose_id else ""
                )
                params = [ordi_number] + ([propose_id] if propose_id else [])
                cursor.execute(ordi_check_query, params)
                ordi_exists = cursor.fetchone()[0] > 0

                if ordi_exists:
                    QMessageBox.warning(self.ui, "Duplicate Error", f"Ordinance number '{ordi_number}' already exists.")
                    return False  # <-- prevent further execution


            # --- Set the attachfile path ---
            if propose_id is None:
                attachfile_tooltip = self.ui.attachFileInput.toolTip().strip()
            else:
                attachfile_tooltip = self.ui.editAttachFileInput.toolTip().strip()

            form_data['propose_attachfile'] = attachfile_tooltip

            # --- INSERT ---
            if propose_id is None:
                query = """
                    INSERT INTO propose_measure (
                        propose_date_rcvd, propose_title, propose_rcvd_from, remarks,
                        propose_attachfile, propose_reso_number, propose_ordi_number,
                        propose_session_date, propose_author, propose_is_scan,
                        propose_is_furnish, propose_is_publication, propose_is_posting, series_yr,
                        cond_id, created_by
                    ) VALUES (
                        %(propose_date_rcvd)s, %(propose_title)s, %(propose_rcvd_from)s, %(remarks)s,
                        %(propose_attachfile)s, %(propose_reso_number)s, %(propose_ordi_number)s,
                        %(propose_session_date)s, %(propose_author)s, %(propose_is_scan)s,
                        %(propose_is_furnish)s, %(propose_is_publication)s, %(propose_is_posting)s, %(series_yr)s,
                        %(cond_id)s, %(created_by)s
                    )
                """
                cursor.execute(query, form_data)

            # --- UPDATE ---
            else:
                query = """
                    UPDATE propose_measure SET
                        propose_date_rcvd = %(propose_date_rcvd)s,
                        propose_title = %(propose_title)s,
                        propose_rcvd_from = %(propose_rcvd_from)s,
                        remarks = %(remarks)s,
                        propose_attachfile = %(propose_attachfile)s,
                        propose_reso_number = %(propose_reso_number)s,
                        propose_ordi_number = %(propose_ordi_number)s,
                        propose_session_date = %(propose_session_date)s,
                        propose_author = %(propose_author)s,
                        propose_is_scan = %(propose_is_scan)s,
                        propose_is_furnish = %(propose_is_furnish)s,
                        propose_is_publication = %(propose_is_publication)s,
                        propose_is_posting = %(propose_is_posting)s, 
                        series_yr = %(series_yr)s,
                        cond_id = %(cond_id)s,
                        updated_by = %(updated_by)s
                    WHERE propose_id = %(propose_id)s
                """
                form_data['propose_id'] = propose_id
                cursor.execute(query, form_data)

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self.ui, "Database Error", f"An error occurred while saving:\n{e}")
            return False

        


# controller/TrashbinController.py
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel, 
                            QPushButton, QMessageBox, QDialog, QScrollArea, QFormLayout)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
import os, json
from datetime import datetime
from functools import partial

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

class TrashbinController:
    def __init__(self, ui, db, username):
        self.ui = ui
        self.db = db
        self.username = username
        self.checkboxes = []
        self.trash_items = []
        
        # Connect UI elements
        self.setup_ui()
        
    def setup_ui(self):
        # Connect buttons
        self.ui.restoreBtn.clicked.connect(self.restore_selected)
        self.ui.deletePermBtn.clicked.connect(self.delete_permanently)
        self.ui.selectAllChkBox.stateChanged.connect(self.toggle_select_all)
        
        # Load trash data
        self.load_trash_data()
        
    def load_trash_data(self):
        try:
            cursor = self.db.get_cursor()
            query = """
                SELECT trash_id, table_name, record_id, deleted_data, deleted_at 
                FROM trash_bin 
                ORDER BY deleted_at DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            self.trash_items = []
            for row in rows:
                trash_id, table_name, record_id, deleted_data, deleted_at = row
                data = deleted_data if isinstance(deleted_data, dict) else json.loads(deleted_data)

                
                # Determine display title based on table
                if table_name == 'propose_measure':
                    title = data.get('propose_title', 'No Title')
                elif table_name == 'minutes':
                    title = f"Minutes {data.get('min_num', 'No Number')}"
                elif table_name == 'other_doc':
                    title = data.get('other_title', 'No Title')
                elif table_name == 'communication_doc':
                    title = data.get('comm_title', 'No Title')
                else:
                    title = f"Deleted {table_name} item"
                
                self.trash_items.append({
                    'trash_id': trash_id,
                    'table_name': table_name,
                    'record_id': record_id,
                    'title': title,
                    'data': data,
                    # 'deleted_by': deleted_by,
                    'deleted_at': deleted_at
                })
            
            self.display_trash_items()
            
        except Exception as e:
            print(f"Error loading trash data: {e}")
            QMessageBox.critical(self.ui, "Error", f"Failed to load trash data: {e}")
    
    def display_trash_items(self):
        # Clear existing items
        self.clear_trash_display()
        self.checkboxes = []
        
        # Get the scroll area widget and its layout
        scroll_widget = self.ui.trashScrollAreaWidget
        layout = scroll_widget.layout()
        if layout is None:
            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            scroll_widget.setLayout(layout)
        
        # Add items to layout
        for item in self.trash_items:
            widget = self.create_trash_item_widget(item)
            layout.addWidget(widget)
    
    def create_trash_item_widget(self, item):
        container = QWidget()
        container.setObjectName(f"trashItem_{item['trash_id']}")
        container.setStyleSheet("""
            QWidget {
                background-color: #8396a4;
                color: white;
                border-radius: 20px;
                padding: 5px;
            }
        """)
        container.setFixedHeight(50)
        
        layout = QHBoxLayout(container)
        
        # Checkbox
        checkbox = QCheckBox()
        checkbox.setObjectName(f"chk_{item['trash_id']}")
        self.checkboxes.append(checkbox)
        layout.addWidget(checkbox)
        
        # Title label
        title_label = QLabel(item['title'])
        title_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(title_label)
        
        # Spacer
        layout.addStretch(1)
        
        # View button
        view_btn = QPushButton("View")
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_btn.setStyleSheet("""
            QPushButton {
                color: white; 
                background: none; 
                border: none; 
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #d3d3d3;
            }
        """)
        view_btn.clicked.connect(partial(self.show_item_details, item))
        layout.addWidget(view_btn)
        
        return container
    
    def show_item_details(self, item):
        # Create a dialog to show details
        dialog = QDialog(self.ui)
        dialog.setStyleSheet("""
                QDialog {
                    background-color: #1b3652;
                    color: black;
                }
                QWidget {
                    background-color: #1b3652;
                }
                QLabel {
                    color: white;
                    font-size: 13px;
                }
                QPushButton {
                    background-color: #1b3652;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #3a5a7f;
                }
            """)

        dialog.setWindowTitle(f"Details - {item['title']}")
        dialog.setMinimumSize(500, 400)
                
        layout = QVBoxLayout()
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        form_layout = QFormLayout(content)
        
        # Add fields based on table type
        data = item['data']
        
        if item['table_name'] == 'propose_measure':
            self.add_propose_measure_fields(form_layout, data)
        elif item['table_name'] == 'minutes':
            self.add_minutes_fields(form_layout, data)
        elif item['table_name'] == 'other_doc':
            self.add_other_doc_fields(form_layout, data)
        elif item['table_name'] == 'communication_doc':
            self.add_communication_doc_fields(form_layout, data)
        
        # Add deleted date
        deleted_date = item['deleted_at'].strftime("%Y-%m-%d %H:%M:%S")
        form_layout.addRow("Deleted on:", QLabel(deleted_date))
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Close button
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)

        # Center the button using an HBox layout
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        
        dialog.setLayout(layout)
        dialog.exec()
        
    def get_condition_name(self, cond_id):
        if cond_id is None:
            return ""
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT cond_name FROM condition_type WHERE cond_id = %s", (cond_id,))
            result = cursor.fetchone()
            return result[0] if result else str(cond_id)
        except Exception as e:
            print(f"Error fetching condition name: {e}")
            return str(cond_id)

    def get_minutes_type_name(self, type_id):
        if type_id is None:
            return ""
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT type_name FROM minutes_type WHERE type_id = %s", (type_id,))
            result = cursor.fetchone()
            return result[0] if result else str(type_id)
        except Exception as e:
            print(f"Error fetching type name: {e}")
            return str(type_id)

    def get_minutes_subtype_name(self, sub_id):
        if sub_id is None:
            return ""
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT sub_name FROM minutes_subtype WHERE sub_id = %s", (sub_id,))
            result = cursor.fetchone()
            return result[0] if result else str(sub_id)
        except Exception as e:
            print(f"Error fetching subtype name: {e}")
            return str(sub_id)

    
    def add_propose_measure_fields(self, layout, data):
        
        series_yr_raw = data.get('series_yr', '')
        try:
            series_yr = datetime.strptime(series_yr_raw, "%Y-%m-%d").strftime("%Y") if series_yr_raw else ''
        except ValueError:
            series_yr = ''
        
        fields = [
            ("Title:", data.get('propose_title', '')),
            ("Resolution Number:", data.get('propose_reso_number', '')),
            ("Ordinance Number:", data.get('propose_ordi_number', '')),
            ("Series of:", series_yr),
            ("Date Received:", data.get('propose_date_rcvd', '')),
            ("Received From:", data.get('propose_rcvd_from', '')),
            ("Session Date:", data.get('propose_session_date', '')),
            ("Author:", data.get('propose_author', '')),
            ("Remarks:", data.get('remarks', '')),
            ("Attached File:", os.path.basename(data.get('propose_attachfile', ''))),
            ("Condition:", self.get_condition_name(data.get('cond_id')))
        ]
        
        for label, value in fields:
            layout.addRow(label, QLabel(str(value)))
    
    def add_minutes_fields(self, layout, data):
        
        min_series_yr_raw = data.get('min_series_yr', '')
        try:
            min_series_yr = datetime.strptime(min_series_yr_raw, "%Y-%m-%d").strftime("%Y") if min_series_yr_raw else ''
        except ValueError:
            min_series_yr = ''

        
        fields = [
            ("Minutes Number:", data.get('min_num', '')),
            ("Series of:", min_series_yr),
            ("Date:", data.get('min_date', '')),
            ("Type:", self.get_minutes_type_name(data.get('type_id'))),
            ("Subtype:", self.get_minutes_subtype_name(data.get('sub_id'))),
            ("Link:", data.get('min_link', ''))
        ]
        
        for label, value in fields:
            layout.addRow(label, QLabel(str(value)))
    
    def add_other_doc_fields(self, layout, data):
        fields = [
            ("Title:", data.get('other_title', '')),
            ("Date:", data.get('other_date', '')),
            ("From:", data.get('other_from', '')),
            ("Status:", data.get('other_status', '')),
            ("Attached File:", os.path.basename(data.get('other_attachfile', '')))

            
        ]
        
        for label, value in fields:
            layout.addRow(label, QLabel(str(value)))
    
    def add_communication_doc_fields(self, layout, data):
        fields = [
            ("Title:", data.get('comm_title', '')),
            ("Date Received:", data.get('comm_date_rcvd', '')),
            ("Venue:", data.get('comm_venue', '')),
            ("Remarks:", data.get('comm_remarks', '')),
            ("Is Liquidated:", "Yes" if data.get('comm_is_liquidate') else "No")
        ]
        
        for label, value in fields:
            layout.addRow(label, QLabel(str(value)))
    
    def toggle_select_all(self, state):
        for checkbox in self.checkboxes:
            checkbox.setChecked(state == Qt.CheckState.Checked.value)
    
    def get_selected_items(self):
        selected = []
        for i, checkbox in enumerate(self.checkboxes):
            if checkbox.isChecked():
                selected.append(self.trash_items[i])
        return selected
    
    def restore_selected(self):
        selected = self.get_selected_items()
        if not selected:
            QMessageBox.warning(self.ui, "No Selection", "Please select items to restore.")
            return
        
        success_count = 0
        failed_items = []
        
        for item in selected:
            try:
                if self.restore_item(item):
                    success_count += 1
                else:
                    failed_items.append(item['title'])
            except Exception as e:
                print(f"Error restoring item {item['trash_id']}: {e}")
                failed_items.append(item['title'])
        
        # Refresh display
        self.load_trash_data()
        
        # Show results
        msg = f"Successfully restored {success_count} item(s)."
        if failed_items:
            msg += f"\n\nFailed to restore:\n- " + "\n- ".join(failed_items)
        QMessageBox.information(self.ui, "Restore Complete", msg)
    
    def restore_item(self, item):
        cursor = self.db.get_cursor()
        
        # Check for duplicates before restoring
        if item['table_name'] == 'propose_measure':
            reso = item['data'].get('propose_reso_number')
            ordi = item['data'].get('propose_ordi_number')
            
            if reso:
                cursor.execute("""
                    SELECT COUNT(*) FROM propose_measure 
                    WHERE propose_reso_number = %s
                """, (reso,))
                if cursor.fetchone()[0] > 0:
                    QMessageBox.warning(self.ui, "Cannot Restore", 
                                      f"Resolution number '{reso}' already exists in the record.")
                    return False
            
            if ordi:
                cursor.execute("""
                    SELECT COUNT(*) FROM propose_measure 
                    WHERE propose_ordi_number = %s
                """, (ordi,))
                if cursor.fetchone()[0] > 0:
                    QMessageBox.warning(self.ui, "Cannot Restore", 
                                      f"Ordinance number '{ordi}' already exists in the current record.")
                    return False
        
        elif item['table_name'] == 'minutes':
            min_num = item['data'].get('min_num')
            if min_num:
                cursor.execute("""
                    SELECT COUNT(*) FROM minutes 
                    WHERE min_num = %s
                """, (min_num,))
                if cursor.fetchone()[0] > 0:
                    QMessageBox.warning(self.ui, "Cannot Restore", 
                                      f"Minutes number '{min_num}' already exists in the current record.")
                    return False
        
        # Restore the item
        try:
            # Insert back into original table
            table = item['table_name']
            data = item['data']
            
            # Remove fields that shouldn't be in INSERT
            data.pop('created_at', None)
            data.pop('updated_at', None)
            
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            
            query = f"""
                INSERT INTO {table} ({columns})
                VALUES ({placeholders})
                RETURNING *
            """
            
            cursor.execute(query, list(data.values()))
            self.db.commit()
            
            # Delete from trash bin
            cursor.execute("DELETE FROM trash_bin WHERE trash_id = %s", (item['trash_id'],))
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error restoring {table} record: {e}")
            return False
    
    def delete_permanently(self):
        selected = self.get_selected_items()
        if not selected:
            QMessageBox.warning(self.ui, "No Selection", "Please select items to delete permanently.")
            return
        
        reply = QMessageBox.question(
            self.ui,
            "Confirm Permanent Deletion",
            f"Are you sure you want to permanently delete {len(selected)} item(s)? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        success_count = 0
        failed_items = []
        
        for item in selected:
            try:
                cursor = self.db.get_cursor()
                cursor.execute("DELETE FROM trash_bin WHERE trash_id = %s", (item['trash_id'],))
                self.db.commit()
                success_count += 1
            except Exception as e:
                self.db.rollback()
                print(f"Error deleting item {item['trash_id']}: {e}")
                failed_items.append(item['title'])
        
        # Refresh display
        self.load_trash_data()
        
        # Show results
        msg = f"Successfully deleted {success_count} item(s) permanently."
        if failed_items:
            msg += f"\n\nFailed to delete:\n- " + "\n- ".join(failed_items)
        QMessageBox.information(self.ui, "Deletion Complete", msg)
    
    def clear_trash_display(self):
        scroll_widget = self.ui.trashScrollAreaWidget
        if scroll_widget.layout():
            while scroll_widget.layout().count():
                item = scroll_widget.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                    
    
    
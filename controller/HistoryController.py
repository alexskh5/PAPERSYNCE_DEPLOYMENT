# controller/HistoryController.py
from PyQt6.QtWidgets import QAbstractScrollArea, QHeaderView, QTableWidgetItem
from PyQt6.QtCore import Qt
from database.connection import Database

class HistoryController:
    def __init__(self, window, db, username):
        self.window = window
        self.db = db
        self.username = username
        self.setup_table()
        self.load_history_data()

    def setup_table(self):
        table = self.window.historyTable

        # Make table responsive
        table.setSizeAdjustPolicy(
            QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )

        # Stretch columns
        header = table.horizontalHeader()
        for col in range(table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        # Set row and header heights
        table.verticalHeader().setDefaultSectionSize(60)
        table.horizontalHeader().setFixedHeight(60)
        table.verticalHeader().setVisible(False)

    def load_history_data(self):
        query = """
                SELECT 
                    INITCAP(REPLACE(h.table_name, '_', ' ')) AS task,
                    h.row_title AS title,
                    s.staff_firstname || ' ' || s.staff_lastname AS staff,
                    split_part(h.action_detail, ':', 1) AS details,
                    TO_CHAR(h.action_date, 'YYYY-MM-DD HH24:MI') AS date
                FROM history h
                LEFT JOIN staff s ON h.staff_id = s.staff_id
                ORDER BY h.action_date DESC
                LIMIT 100
                """
        try:
            result = self.db.fetch_all(query)
            if not result:
                print("No history data found")
                return
                
            table = self.window.historyTable
            table.setRowCount(len(result))
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["Task", "Title", "Staff", "Details", "Date"])
            
            for row_idx, row_data in enumerate(result):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) 
                    table.setItem(row_idx, col_idx, item)
                    
        except Exception as e:
            print(f"Error loading history data: {e}")

    def filter_history(self, table_name=None, action_type=None, date_range=None):
        """Filter history records"""
        base_query = """
        SELECT 
            h.action_detail AS action,
            h.row_title AS document,
            s.staff_firstname || ' ' || s.staff_lastname AS staff,
            h.action_detail || ' ' || LOWER(h.table_name) AS details,
            TO_CHAR(h.action_date, 'YYYY-MM-DD HH24:MI') AS date
        FROM history h
        LEFT JOIN staff s ON h.staff_id = s.staff_id
        WHERE 1=1
        """
        
        params = []
        
        if table_name and table_name != "All Tables":
            base_query += " AND h.table_name = %s"
            params.append(table_name.upper())
            
        if action_type and action_type != "All Actions":
            base_query += " AND h.action_detail ILIKE %s"
            params.append(f"%{action_type}%")
            
        if date_range and len(date_range) == 2:
            base_query += " AND h.action_date BETWEEN %s AND %s"
            params.extend(date_range)
            
        base_query += " ORDER BY h.action_date DESC LIMIT 100"
        
        try:
            result = self.db.fetch_all(base_query, params)
            self.display_history_data(result)
        except Exception as e:
            print(f"Error filtering history: {e}")

    def display_history_data(self, data):
        """Display data in the table"""
        table = self.window.historyTable
        table.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value) if value is not None else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row_idx, col_idx, item)
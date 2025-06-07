#controller/LogInController.py

from database.connection import Database

class Login:
    def __init__(self):
        self.db = Database()

    def authenticate(self, username, password):
        try: 
            # Connect to the database
            self.db.connect()
            
            # Get cursor to execute query
            cur = self.db.get_cursor()

            # Perform SQL query to check credentials
            cur.execute("SELECT * FROM staff WHERE staff_username=%s AND staff_password=%s", (username, password))
            result = cur.fetchone()
            
            # Close connection after the query
            self.db.close()

            # Return True if result is found, meaning credentials are correct
            return result is not None

        except Exception as e:
            # Raise an error if any issues during the login process
            raise Exception(f"Login error: {str(e)}")
    
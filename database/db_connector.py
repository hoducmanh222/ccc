import mysql.connector
from mysql.connector import Error
import sys
import os

# Add parent directory to path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG

class DatabaseConnector:
    def __init__(self):
        self.connection = None
        self.connect()
        
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                return self.connection
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            return None
    
    def execute_query(self, query, params=None):
        cursor = None
        try:
            # Ensure connection is active
            if not self.connection or not self.connection.is_connected():
                self.connect()
                
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            # Force immediate commit for any command that modifies data
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'CALL', 'SET')):
                self.connection.commit()
                if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                    return cursor.lastrowid
                elif query.strip().upper().startswith('CALL'):
                    try:
                        return cursor.fetchall()  # Try to fetch results if any
                    except:
                        return cursor.rowcount   # If no results, return affected rows
            else:
                return cursor.fetchall()
        except Error as e:
            print(f"Error executing query: {e}")
            if self.connection:
                try:
                    self.connection.rollback()
                except:
                    pass
            return None
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
    
    def call_procedure(self, proc_name, params=None):
        cursor = None
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
                
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.callproc(proc_name, params)
            else:
                cursor.callproc(proc_name)
                
            # Get results from stored procedure
            results = []
            for result in cursor.stored_results():
                results.extend(result.fetchall())
            
            self.connection.commit()
            return results
        except Error as e:
            print(f"Error calling procedure: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def refresh_connection(self):
        """Force reconnection to the database"""
        try:
            if self.connection:
                if self.connection.is_connected():
                    self.connection.close()
            self.connection = mysql.connector.connect(**DB_CONFIG)
            return True
        except Error as e:
            print(f"Error refreshing connection: {e}")
            return False
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

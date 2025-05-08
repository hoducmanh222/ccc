from database.db_connector import DatabaseConnector

class CustomerModel:
    def __init__(self):
        self.db = DatabaseConnector()
        
    def get_all_customers(self):
        query = """
        SELECT CustomerID, CustomerName, PhoneNumber
        FROM Customers
        ORDER BY CustomerName
        """
        return self.db.execute_query(query)
    
    def get_customer(self, customer_id):
        query = "SELECT CustomerID, CustomerName, PhoneNumber FROM Customers WHERE CustomerID = %s"
        result = self.db.execute_query(query, (customer_id,))
        return result[0] if result else None
    
    def get_customer_by_phone(self, phone_number):
        query = "SELECT CustomerID, CustomerName, PhoneNumber FROM Customers WHERE PhoneNumber = %s"
        result = self.db.execute_query(query, (phone_number,))
        return result[0] if result else None
    
    def add_customer(self, name, phone_number):
        query = "INSERT INTO Customers (CustomerName, PhoneNumber) VALUES (%s, %s)"
        return self.db.execute_query(query, (name, phone_number))
    
    def update_customer(self, customer_id, name, phone_number):
        query = """
        UPDATE Customers 
        SET CustomerName = %s, PhoneNumber = %s
        WHERE CustomerID = %s
        """
        self.db.execute_query(query, (name, phone_number, customer_id))
    
    def delete_customer(self, customer_id):
        query = "DELETE FROM Customers WHERE CustomerID = %s"
        self.db.execute_query(query, (customer_id,))

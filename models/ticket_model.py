from database.db_connector import DatabaseConnector

class TicketModel:
    def __init__(self):
        self.db = DatabaseConnector()
        
    def get_all_tickets(self):
        query = """
        SELECT t.TicketID, c.CustomerName, m.MovieTitle, 
               s.ScreeningDate, s.ScreeningTime, t.SeatNumber
        FROM Tickets t
        JOIN Customers c ON t.CustomerID = c.CustomerID
        JOIN Screenings s ON t.ScreeningID = s.ScreeningID
        JOIN Movies m ON s.MovieID = m.MovieID
        ORDER BY s.ScreeningDate, s.ScreeningTime
        """
        return self.db.execute_query(query)
    
    def get_tickets_by_screening(self, screening_id):
        query = """
        SELECT t.TicketID, t.CustomerID, c.CustomerName, t.SeatNumber
        FROM Tickets t
        JOIN Customers c ON t.CustomerID = c.CustomerID
        WHERE t.ScreeningID = %s
        ORDER BY t.SeatNumber
        """
        return self.db.execute_query(query, (screening_id,))
    
    def book_ticket(self, customer_id, screening_id, seat_number, user_id=None, username=None):
        """Book a ticket and record who performed the action"""
        try:
            print(f"Booking ticket with username: {username}")
            # Always set the current user context before any operation
            if username:
                # Set the current_user session variable - this is what the trigger uses
                self.db.execute_query("SET @current_user = %s", [username])
                print(f"Set @current_user to {username}")
            else:
                # Default to system if no username provided
                self.db.execute_query("SET @current_user = 'system'")
            
            # Execute the booking procedure
            result = self.db.execute_query(
                "CALL sp_book_ticket(%s, %s, %s)",
                [customer_id, screening_id, seat_number]
            )
            
            # Reset the user context
            self.db.execute_query("SET @current_user = NULL")
            
            # Force commit to ensure data is written immediately
            if hasattr(self.db, 'connection'):
                self.db.connection.commit()
                
            return True
        except Exception as e:
            print(f"Error booking ticket: {e}")
            return False
    
    def cancel_ticket(self, ticket_id, user_id=None, username=None):
        """Cancel a ticket by ticket ID"""
        try:
            # Always set the current user context first
            if username:
                print(f"Setting user context to: {username}")
                self.db.execute_query("SET @current_user = %s", [username])
            else:
                # Default to system if no username provided
                self.db.execute_query("SET @current_user = 'system'")
            
            # Call the procedure with the username
            self.db.execute_query(
                "CALL sp_cancel_ticket(%s, %s)", 
                [ticket_id, username]
            )
            
            # Force explicit commit
            if hasattr(self.db, 'connection'):
                self.db.connection.commit()
                print(f"Ticket cancelled by {username if username else 'system'}")
            
            return True
        except Exception as e:
            print(f"Error cancelling ticket: {e}")
            return False
        finally:
            # Always reset the user context
            try:
                self.db.execute_query("SET @current_user = NULL")
            except:
                pass
    
    def get_occupied_seats(self, screening_id):
        query = """
        SELECT SeatNumber FROM Tickets WHERE ScreeningID = %s
        """
        results = self.db.execute_query(query, (screening_id,))
        return [r['SeatNumber'] for r in results]
    
    def get_user_tickets(self, status="All"):
        """
        Get tickets filtered by status using UNION to combine active and cancelled
        """
        try:
            print(f"Fetching tickets with status: {status}")
            # Force a database commit before querying to ensure we get fresh data
            if hasattr(self.db, 'connection'):
                try:
                    self.db.connection.commit()
                except:
                    pass
            
            # Query for active tickets
            active_query = """
                SELECT 
                    t.TicketID, 
                    m.MovieTitle, 
                    s.ScreeningDate, 
                    s.ScreeningTime, 
                    t.SeatNumber, 
                    'Active' AS Status
                FROM Tickets t
                JOIN Screenings s ON t.ScreeningID = s.ScreeningID
                JOIN Movies m ON s.MovieID = m.MovieID
            """
            
            # Query for cancelled tickets
            cancelled_query = """
                SELECT 
                    c.TicketID, 
                    m.MovieTitle, 
                    s.ScreeningDate, 
                    s.ScreeningTime, 
                    c.SeatNumber, 
                    'Cancelled' AS Status
                FROM CancelledTickets c
                JOIN Screenings s ON c.ScreeningID = s.ScreeningID
                JOIN Movies m ON s.MovieID = m.MovieID
            """
            
            # Apply status filter or combine both queries
            if status == "Active":
                query = active_query + " ORDER BY ScreeningDate DESC, ScreeningTime DESC"
            elif status == "Cancelled":
                query = cancelled_query + " ORDER BY ScreeningDate DESC, ScreeningTime DESC"
            else:  # "All"
                query = f"{active_query} UNION {cancelled_query} ORDER BY ScreeningDate DESC, ScreeningTime DESC"
            
            tickets = self.db.execute_query(query)
            print(f"Retrieved {len(tickets) if tickets else 0} tickets")
            return tickets
        except Exception as e:
            print(f"Error getting tickets: {e}")
            return []
            
    def get_booking_audit(self):
        """
        Get all booking audit entries.
        """
        try:
            query = """
                SELECT 
                    ba.AuditID, 
                    ba.OperationType, 
                    ba.AffectedScreeningID, 
                    ba.AffectedSeat, 
                    COALESCE(ba.UserID, 'system') AS UserID, 
                    ba.Timestamp
                FROM BookingAudit ba
                ORDER BY ba.Timestamp DESC
                LIMIT 100
            """
            
            return self.db.execute_query(query)
        except Exception as e:
            print(f"Error getting audit log: {e}")
            return []

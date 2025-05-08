from database.db_connector import DatabaseConnector

class ScreeningModel:
    def __init__(self):
        self.db = DatabaseConnector()
        
    def get_all_screenings(self):
        query = """
        SELECT s.ScreeningID, m.MovieTitle, r.RoomName, 
               s.ScreeningDate, s.ScreeningTime,
               fn_occupancy_rate(s.ScreeningID) AS OccupancyRate
        FROM Screenings s
        JOIN Movies m ON s.MovieID = m.MovieID
        JOIN CinemaRooms r ON s.RoomID = r.RoomID
        ORDER BY s.ScreeningDate, s.ScreeningTime
        """
        return self.db.execute_query(query)
    
    def get_screening(self, screening_id):
        query = """
        SELECT s.ScreeningID, s.MovieID, s.RoomID, 
               s.ScreeningDate, s.ScreeningTime
        FROM Screenings s
        WHERE s.ScreeningID = %s
        """
        result = self.db.execute_query(query, (screening_id,))
        return result[0] if result else None
    
    def add_screening(self, movie_id, room_id, screening_date, screening_time):
        query = """
        INSERT INTO Screenings (MovieID, RoomID, ScreeningDate, ScreeningTime)
        VALUES (%s, %s, %s, %s)
        """
        return self.db.execute_query(query, (movie_id, room_id, screening_date, screening_time))
    
    def update_screening(self, screening_id, movie_id, room_id, screening_date, screening_time):
        query = """
        UPDATE Screenings 
        SET MovieID = %s, RoomID = %s, ScreeningDate = %s, ScreeningTime = %s
        WHERE ScreeningID = %s
        """
        self.db.execute_query(query, (movie_id, room_id, screening_date, screening_time, screening_id))
    
    def delete_screening(self, screening_id):
        query = "DELETE FROM Screenings WHERE ScreeningID = %s"
        self.db.execute_query(query, (screening_id,))
    
    def get_seat_availability(self, screening_id, force_fresh=False):
        """Get seat availability for a screening, with option to force fresh data"""
        try:
            # Use a direct query instead of the view to ensure we get fresh data
            query = """
                SELECT
                    r.Capacity,
                    (r.Capacity - COUNT(t.TicketID)) AS AvailableSeats
                FROM Screenings s
                JOIN CinemaRooms r ON s.RoomID = r.RoomID
                LEFT JOIN Tickets t ON s.ScreeningID = t.ScreeningID
                WHERE s.ScreeningID = %s
                GROUP BY r.Capacity
            """
            
            result = self.db.execute_query(query, [screening_id])
            if result and len(result) > 0:
                return result[0]
            return None
        except Exception as e:
            print(f"Error getting seat availability: {e}")
            return None
    
    def get_screenings_by_date(self, date, force_fresh=False):
        """Get all screenings for a specific date"""
        try:
            query = """
                SELECT 
                    s.ScreeningID,
                    m.MovieTitle,
                    r.RoomName,
                    s.ScreeningDate,
                    s.ScreeningTime
                FROM Screenings s
                JOIN Movies m ON s.MovieID = m.MovieID
                JOIN CinemaRooms r ON s.RoomID = r.RoomID
                WHERE s.ScreeningDate = %s
                ORDER BY s.ScreeningTime
            """
            
            # Use a direct connection to ensure fresh data
            return self.db.execute_query(query, [date])
        except Exception as e:
            print(f"Error getting screenings by date: {e}")
            return []

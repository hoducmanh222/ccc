from database.db_connector import DatabaseConnector

class ReportModel:
    def __init__(self):
        self.db = DatabaseConnector()
        
    def get_daily_revenue(self, date, force_refresh=False):
        """Get daily revenue for a specific date"""
        try:
            # Force a direct query to ensure fresh data
            query = "SELECT fn_total_revenue_by_date(%s) AS Revenue"
            result = self.db.execute_query(query, [date])
            
            if result and len(result) > 0:
                return float(result[0]["Revenue"])
            return 0.0
        except Exception as e:
            print(f"Error getting daily revenue: {e}")
            return 0.0
            
    def get_occupancy_rates(self):
        query = """
        SELECT s.ScreeningID, m.MovieTitle, r.RoomName, s.ScreeningDate, s.ScreeningTime,
              fn_occupancy_rate(s.ScreeningID) AS OccupancyRate
        FROM Screenings s
        JOIN Movies m ON s.MovieID = m.MovieID
        JOIN CinemaRooms r ON s.RoomID = r.RoomID
        ORDER BY s.ScreeningDate, s.ScreeningTime
        """
        return self.db.execute_query(query)
    
    def get_popular_movies(self):
        query = """
        SELECT m.MovieID, m.MovieTitle, COUNT(t.TicketID) AS TicketCount
        FROM Movies m
        JOIN Screenings s ON m.MovieID = s.MovieID
        JOIN Tickets t ON s.ScreeningID = t.ScreeningID
        GROUP BY m.MovieID, m.MovieTitle
        ORDER BY TicketCount DESC
        """
        return self.db.execute_query(query)
    
    def get_screenings_by_date(self, date, force_refresh=False):
        """Get all screenings for a specific date with fresh occupancy data"""
        try:
            # Using direct joins to ensure we get fresh data
            query = """
                SELECT 
                    s.ScreeningID,
                    m.MovieTitle,
                    r.RoomName,
                    s.ScreeningDate,
                    s.ScreeningTime,
                    fn_occupancy_rate(s.ScreeningID) AS OccupancyRate
                FROM Screenings s
                JOIN Movies m ON s.MovieID = m.MovieID
                JOIN CinemaRooms r ON s.RoomID = r.RoomID
                WHERE s.ScreeningDate = %s
                ORDER BY s.ScreeningTime
            """
            
            return self.db.execute_query(query, [date])
        except Exception as e:
            print(f"Error getting screenings by date: {e}")
            return []
    
    def clear_cache(self):
        """Clear any cached data to force fresh database reads"""
        # This is just a placeholder - implement if you have caching logic
        pass

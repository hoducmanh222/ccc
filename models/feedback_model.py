from database.db_connector import DatabaseConnector

class FeedbackModel:
    def __init__(self):
        self.db = DatabaseConnector()
        
    def get_all_feedback(self):
        query = """
        SELECT f.FeedbackID, c.CustomerName, m.MovieTitle, 
               f.Rating, f.Comment, f.FeedbackDate
        FROM Feedback f
        JOIN Customers c ON f.CustomerID = c.CustomerID
        JOIN Movies m ON f.MovieID = m.MovieID
        ORDER BY f.FeedbackDate DESC
        """
        return self.db.execute_query(query)
    
    def get_feedback_by_movie(self, movie_id):
        query = """
        SELECT f.FeedbackID, c.CustomerName, f.Rating, 
               f.Comment, f.FeedbackDate
        FROM Feedback f
        JOIN Customers c ON f.CustomerID = c.CustomerID
        WHERE f.MovieID = %s
        ORDER BY f.FeedbackDate DESC
        """
        return self.db.execute_query(query, (movie_id,))
    
    def get_feedback_by_customer(self, customer_id):
        query = """
        SELECT f.FeedbackID, m.MovieTitle, f.Rating, 
               f.Comment, f.FeedbackDate
        FROM Feedback f
        JOIN Movies m ON f.MovieID = m.MovieID
        WHERE f.CustomerID = %s
        ORDER BY f.FeedbackDate DESC
        """
        return self.db.execute_query(query, (customer_id,))
    
    def add_feedback(self, customer_id, movie_id, rating, comment):
        query = """
        INSERT INTO Feedback (CustomerID, MovieID, Rating, Comment, FeedbackDate)
        VALUES (%s, %s, %s, %s, CURDATE())
        """
        return self.db.execute_query(query, (customer_id, movie_id, rating, comment))
    
    def update_feedback(self, feedback_id, rating, comment):
        query = """
        UPDATE Feedback
        SET Rating = %s, Comment = %s
        WHERE FeedbackID = %s
        """
        self.db.execute_query(query, (rating, comment, feedback_id))
        
    def delete_feedback(self, feedback_id):
        query = "DELETE FROM Feedback WHERE FeedbackID = %s"
        self.db.execute_query(query, (feedback_id,))
    
    def get_average_rating_by_movie(self, movie_id):
        query = """
        SELECT AVG(Rating) as AverageRating, COUNT(*) as RatingCount
        FROM Feedback
        WHERE MovieID = %s
        """
        result = self.db.execute_query(query, (movie_id,))
        return result[0] if result else {"AverageRating": 0, "RatingCount": 0}

from database.db_connector import DatabaseConnector

class MovieModel:
    def __init__(self):
        self.db = DatabaseConnector()
        
    def get_all_movies(self):
        query = """
        SELECT m.MovieID, m.MovieTitle, g.GenreName, m.DurationMinutes 
        FROM Movies m
        LEFT JOIN Genres g ON m.GenreID = g.GenreID
        ORDER BY m.MovieID
        """
        return self.db.execute_query(query)
    
    def get_movie(self, movie_id):
        query = """
        SELECT m.MovieID, m.MovieTitle, m.GenreID, g.GenreName, m.DurationMinutes 
        FROM Movies m
        LEFT JOIN Genres g ON m.GenreID = g.GenreID
        WHERE m.MovieID = %s
        """
        result = self.db.execute_query(query, (movie_id,))
        return result[0] if result else None
    
    def add_movie(self, title, genre_id, duration):
        query = """
        INSERT INTO Movies (MovieTitle, GenreID, DurationMinutes)
        VALUES (%s, %s, %s)
        """
        return self.db.execute_query(query, (title, genre_id, duration))
    
    def update_movie(self, movie_id, title, genre_id, duration):
        query = """
        UPDATE Movies 
        SET MovieTitle = %s, GenreID = %s, DurationMinutes = %s
        WHERE MovieID = %s
        """
        self.db.execute_query(query, (title, genre_id, duration, movie_id))
    
    def delete_movie(self, movie_id):
        query = "DELETE FROM Movies WHERE MovieID = %s"
        self.db.execute_query(query, (movie_id,))
    
    def get_all_genres(self):
        query = "SELECT GenreID, GenreName FROM Genres ORDER BY GenreName"
        return self.db.execute_query(query)
    
    def add_genre(self, genre_name):
        query = "INSERT INTO Genres (GenreName) VALUES (%s)"
        return self.db.execute_query(query, (genre_name,))

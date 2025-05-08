from database.db_connector import DatabaseConnector

class CinemaRoomModel:
    def __init__(self):
        self.db = DatabaseConnector()
        
    def get_all_rooms(self):
        query = """
        SELECT RoomID, RoomName, Capacity 
        FROM CinemaRooms
        ORDER BY RoomID
        """
        return self.db.execute_query(query)
    
    def get_room(self, room_id):
        query = "SELECT RoomID, RoomName, Capacity FROM CinemaRooms WHERE RoomID = %s"
        result = self.db.execute_query(query, (room_id,))
        return result[0] if result else None
    
    def add_room(self, room_name, capacity):
        query = "INSERT INTO CinemaRooms (RoomName, Capacity) VALUES (%s, %s)"
        return self.db.execute_query(query, (room_name, capacity))
    
    def update_room(self, room_id, room_name, capacity):
        query = """
        UPDATE CinemaRooms 
        SET RoomName = %s, Capacity = %s
        WHERE RoomID = %s
        """
        self.db.execute_query(query, (room_name, capacity, room_id))
    
    def delete_room(self, room_id):
        query = "DELETE FROM CinemaRooms WHERE RoomID = %s"
        self.db.execute_query(query, (room_id,))

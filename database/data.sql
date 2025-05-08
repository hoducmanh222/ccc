-- Creating the CinemaDBcc database
DROP DATABASE IF EXISTS CinemaDBcc;

DROP USER IF EXISTS 'admin_user'@'localhost';
DROP USER IF EXISTS 'clerk_user'@'localhost';
DROP USER IF EXISTS 'guest_user'@'localhost';


CREATE DATABASE CinemaDBcc;
USE CinemaDBcc;


-- Creating Genres table
CREATE TABLE Genres (
    GenreID INT PRIMARY KEY AUTO_INCREMENT,
    GenreName VARCHAR(50) NOT NULL UNIQUE
);


-- Creating Movies table
CREATE TABLE Movies (
    MovieID INT PRIMARY KEY AUTO_INCREMENT,
    MovieTitle VARCHAR(100) NOT NULL,
    GenreID INT,
    DurationMinutes INT CHECK (DurationMinutes > 0),
    FOREIGN KEY (GenreID) REFERENCES Genres(GenreID) ON UPDATE CASCADE ON DELETE SET NULL
);


-- Creating CinemaRooms table
CREATE TABLE CinemaRooms (
    RoomID INT PRIMARY KEY AUTO_INCREMENT,
    RoomName VARCHAR(50) NOT NULL UNIQUE,
    Capacity INT CHECK (Capacity > 0)
);


-- Creating Screenings table
CREATE TABLE Screenings (
    ScreeningID INT PRIMARY KEY AUTO_INCREMENT,
    MovieID INT,
    RoomID INT,
    ScreeningDate DATE,
    ScreeningTime TIME,
    FOREIGN KEY (MovieID) REFERENCES Movies(MovieID) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (RoomID) REFERENCES CinemaRooms(RoomID) ON UPDATE CASCADE ON DELETE CASCADE
);


-- Creating Customers table
CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerName VARCHAR(100) NOT NULL,
    PhoneNumber VARCHAR(15) UNIQUE
);


-- Creating Tickets table
CREATE TABLE Tickets (
    TicketID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT,
    ScreeningID INT,
    SeatNumber VARCHAR(10),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (ScreeningID) REFERENCES Screenings(ScreeningID) ON UPDATE CASCADE ON DELETE CASCADE
);


-- Creating CancelledTickets table to store information about cancelled tickets
CREATE TABLE CancelledTickets (
    CancellationID INT PRIMARY KEY AUTO_INCREMENT,
    TicketID INT NOT NULL,
    CustomerID INT,
    ScreeningID INT,
    SeatNumber VARCHAR(10),
    CancellationDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    CancelledBy VARCHAR(50),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (ScreeningID) REFERENCES Screenings(ScreeningID) ON UPDATE CASCADE ON DELETE SET NULL
);


-- Creating Staff table (Bonus)
CREATE TABLE Staff (
    StaffID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Role VARCHAR(50),
    Email VARCHAR(100) UNIQUE
);


-- Creating Promotions table (Bonus)
CREATE TABLE Promotions (
    PromotionID INT PRIMARY KEY AUTO_INCREMENT,
    Description VARCHAR(255),
    DiscountPercent DECIMAL(5,2) CHECK (DiscountPercent >= 0 AND DiscountPercent <= 100),
    StartDate DATE,
    EndDate DATE
);


-- Creating Feedback table (Bonus)
CREATE TABLE Feedback (
    FeedbackID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT,
    MovieID INT,
    Rating INT CHECK (Rating BETWEEN 1 AND 5),
    Comment TEXT,
    FeedbackDate DATE,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (MovieID) REFERENCES Movies(MovieID) ON DELETE CASCADE
);


-- Inserting sample data into Genres
INSERT INTO Genres (GenreName) VALUES ('Sci-Fi'), ('Thriller'), ('Action');


-- Inserting sample data into Movies
INSERT INTO Movies (MovieTitle, GenreID, DurationMinutes)
VALUES
    ('Inception', 1, 148),
    ('Parasite', 2, 132),
    ('Avengers: Endgame', 3, 181);


-- Inserting sample data into CinemaRooms
INSERT INTO CinemaRooms (RoomName, Capacity)
VALUES
    ('Room A', 100),
    ('Room B', 80);


-- Inserting sample data into Screenings
INSERT INTO Screenings (MovieID, RoomID, ScreeningDate, ScreeningTime)
VALUES
    (1, 1, '2025-05-02', '18:00:00'),
    (2, 1, '2025-05-02', '21:00:00'),
    (3, 2, '2025-05-03', '17:30:00'),
    (1, 2, '2025-05-04', '20:00:00');


-- Inserting sample data into Customers
INSERT INTO Customers (CustomerName, PhoneNumber)
VALUES
    ('Nguyen Van A', '0912345678'),
    ('Tran Thi B', '0923456789'),
    ('Le Van C', '0934567890');


-- Inserting sample data into Tickets
INSERT INTO Tickets (CustomerID, ScreeningID, SeatNumber)
VALUES
    (1, 1, 'A1'),
    (1, 1, 'A2'),
    (2, 2, 'B1'),
    (3, 3, 'C5'),
    (2, 4, 'D10');


-- Inserting sample data into Feedback
INSERT INTO Feedback (CustomerID, MovieID, Rating, Comment, FeedbackDate)
VALUES
    (1, 1, 5, 'Great movie!', '2025-05-02'),
    (2, 2, 4, 'Interesting plot.', '2025-05-02'),
    (3, 3, 3, 'It was okay.', '2025-05-03');


-- Creating indexes for performance optimization
CREATE INDEX idx_movie_title ON Movies(MovieTitle);
CREATE INDEX idx_screening_date ON Screenings(ScreeningDate);
CREATE INDEX idx_customer_phone ON Customers(PhoneNumber);


-- Creating view for daily screenings
CREATE VIEW vw_DailyScreenings AS
SELECT
    s.ScreeningID,
    m.MovieTitle,
    g.GenreName,
    r.RoomName,
    s.ScreeningDate,
    s.ScreeningTime
FROM Screenings s
JOIN Movies m ON s.MovieID = m.MovieID
JOIN CinemaRooms r ON s.RoomID = r.RoomID
JOIN Genres g ON m.GenreID = g.GenreID
WHERE s.ScreeningDate = CURDATE();


-- Creating view for seat availability
CREATE VIEW vw_SeatAvailability AS
SELECT
    s.ScreeningID,
    m.MovieTitle,
    r.RoomName,
    s.ScreeningDate,
    s.ScreeningTime,
    r.Capacity,
    (r.Capacity - COUNT(t.TicketID)) AS AvailableSeats
FROM Screenings s
JOIN CinemaRooms r ON s.RoomID = r.RoomID
JOIN Movies m ON s.MovieID = m.MovieID
LEFT JOIN Tickets t ON s.ScreeningID = t.ScreeningID
GROUP BY s.ScreeningID, m.MovieTitle, r.RoomName, s.ScreeningDate, s.ScreeningTime, r.Capacity;


-- Creating stored procedure for booking tickets
DELIMITER //
CREATE PROCEDURE sp_book_ticket(
    IN p_customer_id INT,
    IN p_screening_id INT,
    IN p_seat_number VARCHAR(10)
)
BEGIN
    DECLARE seat_taken INT;
    DECLARE room_capacity INT;
    DECLARE booked_seats INT;
   
    SELECT COUNT(*) INTO seat_taken
    FROM Tickets
    WHERE ScreeningID = p_screening_id AND SeatNumber = p_seat_number;
   
    SELECT r.Capacity INTO room_capacity
    FROM Screenings s
    JOIN CinemaRooms r ON s.RoomID = r.RoomID
    WHERE s.ScreeningID = p_screening_id;
   
    SELECT COUNT(*) INTO booked_seats
    FROM Tickets
    WHERE ScreeningID = p_screening_id;
   
    IF seat_taken > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seat already taken';
    ELSEIF booked_seats >= room_capacity THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Screening fully booked';
    ELSE
        INSERT INTO Tickets (CustomerID, ScreeningID, SeatNumber)
        VALUES (p_customer_id, p_screening_id, p_seat_number);
    END IF;
END //
DELIMITER ;


-- Creating stored procedure for cancelling tickets
DROP PROCEDURE IF EXISTS sp_cancel_ticket;
DELIMITER //
CREATE PROCEDURE sp_cancel_ticket(
    IN p_ticket_id INT,
    IN p_cancelled_by VARCHAR(50)
)
BEGIN
    DECLARE ticket_exists INT;
    DECLARE v_customer_id INT;
    DECLARE v_screening_id INT;
    DECLARE v_seat_number VARCHAR(10);
   
    -- Check if ticket exists
    SELECT COUNT(*) INTO ticket_exists
    FROM Tickets
    WHERE TicketID = p_ticket_id;
   
    IF ticket_exists = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ticket not found';
    ELSE
        -- Get ticket details before deletion
        SELECT CustomerID, ScreeningID, SeatNumber 
        INTO v_customer_id, v_screening_id, v_seat_number
        FROM Tickets
        WHERE TicketID = p_ticket_id;
        
        -- Create a single audit log entry with the proper user
        INSERT INTO BookingAudit (OperationType, AffectedScreeningID, AffectedSeat, UserID, Timestamp)
        VALUES ('Cancellation', v_screening_id, v_seat_number, IFNULL(p_cancelled_by, USER()), NOW());
        
        -- Insert into CancelledTickets
        INSERT INTO CancelledTickets (TicketID, CustomerID, ScreeningID, SeatNumber, CancelledBy)
        VALUES (p_ticket_id, v_customer_id, v_screening_id, v_seat_number, IFNULL(p_cancelled_by, USER()));
        
        -- Delete from Tickets - this won't trigger an additional audit due to our modified trigger
        DELETE FROM Tickets WHERE TicketID = p_ticket_id;
    END IF;
END //
DELIMITER ;


-- Creating BookingAudit table for audit logging
CREATE TABLE BookingAudit (
    AuditID INT PRIMARY KEY AUTO_INCREMENT,
    OperationType VARCHAR(50),
    AffectedScreeningID INT,
    AffectedSeat VARCHAR(10),
    UserID VARCHAR(50),
    Timestamp DATETIME
);


-- Creating trigger to prevent double booking
DROP TRIGGER IF EXISTS tr_prevent_double_booking;
DELIMITER //
CREATE TRIGGER tr_prevent_double_booking
BEFORE INSERT ON Tickets
FOR EACH ROW
BEGIN
    DECLARE seat_count INT;
   
    SELECT COUNT(*) INTO seat_count
    FROM Tickets
    WHERE ScreeningID = NEW.ScreeningID AND SeatNumber = NEW.SeatNumber;
   
    IF seat_count > 0 THEN
        INSERT INTO BookingAudit (OperationType, AffectedScreeningID, AffectedSeat, UserID, Timestamp)
        VALUES ('Failed Booking', NEW.ScreeningID, NEW.SeatNumber, IFNULL(@current_user, USER()), NOW());
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seat already booked';
    END IF;
END //
DELIMITER ;


-- Creating trigger for booking audit
DROP TRIGGER IF EXISTS tr_update_seat_availability;
DELIMITER //
CREATE TRIGGER tr_update_seat_availability
AFTER INSERT ON Tickets
FOR EACH ROW
BEGIN
    INSERT INTO BookingAudit (OperationType, AffectedScreeningID, AffectedSeat, UserID, Timestamp)
    VALUES ('Booking', NEW.ScreeningID, NEW.SeatNumber, IFNULL(@current_user, USER()), NOW());
END //
DELIMITER ;


-- Creating trigger for cancellation audit
DROP TRIGGER IF EXISTS tr_after_delete_ticket;
DELIMITER //
CREATE TRIGGER tr_after_delete_ticket
AFTER DELETE ON Tickets
FOR EACH ROW
BEGIN
    -- Only add audit log if it's not from sp_cancel_ticket
    -- This prevents duplicate entries when cancelling tickets
    IF NOT EXISTS (
        SELECT 1 FROM CancelledTickets 
        WHERE TicketID = OLD.TicketID AND 
              ScreeningID = OLD.ScreeningID AND 
              SeatNumber = OLD.SeatNumber
    ) THEN
        INSERT INTO BookingAudit (OperationType, AffectedScreeningID, AffectedSeat, UserID, Timestamp)
        VALUES ('Cancellation', OLD.ScreeningID, OLD.SeatNumber, IFNULL(@current_user, USER()), NOW());
    END IF;
END //
DELIMITER ;


-- Creating UDF for occupancy rate
DROP FUNCTION IF EXISTS fn_occupancy_rate;
DELIMITER //
CREATE FUNCTION fn_occupancy_rate(p_screening_id INT) RETURNS DECIMAL(5,2)
DETERMINISTIC
BEGIN
    DECLARE booked_seats INT;
    DECLARE total_seats INT;
    DECLARE occupancy DECIMAL(5,2);
   
    -- Count only active tickets (not cancelled)
    SELECT COUNT(*) INTO booked_seats
    FROM Tickets
    WHERE ScreeningID = p_screening_id;
   
    SELECT r.Capacity INTO total_seats
    FROM Screenings s
    JOIN CinemaRooms r ON s.RoomID = r.RoomID
    WHERE s.ScreeningID = p_screening_id;
   
    IF total_seats = 0 THEN
        RETURN 0.00;
    END IF;
   
    SET occupancy = (booked_seats / total_seats) * 100;
    RETURN occupancy;
END //
DELIMITER ;


-- Creating UDF for daily revenue
DROP FUNCTION IF EXISTS fn_total_revenue_by_date;
DELIMITER //
CREATE FUNCTION fn_total_revenue_by_date(p_date DATE) RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total_tickets INT;
    DECLARE cancelled_tickets INT;
    DECLARE ticket_price DECIMAL(5,2) DEFAULT 10.00;
   
    -- Count active tickets
    SELECT COUNT(*) INTO total_tickets
    FROM Tickets t
    JOIN Screenings s ON t.ScreeningID = s.ScreeningID
    WHERE s.ScreeningDate = p_date;
    
    -- Count cancelled tickets for the date
    SELECT COUNT(*) INTO cancelled_tickets
    FROM CancelledTickets c
    JOIN Screenings s ON c.ScreeningID = s.ScreeningID
    WHERE s.ScreeningDate = p_date
    AND DATE(c.CancellationDate) = p_date;  -- Only count tickets cancelled on the same day
   
    -- Revenue is based on active tickets only
    RETURN total_tickets * ticket_price;
END //
DELIMITER ;


-- Add a new view for revenue reporting that includes cancelled tickets
CREATE OR REPLACE VIEW vw_DailyRevenue AS
SELECT 
    s.ScreeningDate AS Date,
    COUNT(t.TicketID) AS TicketsSold,
    COUNT(c.CancellationID) AS TicketsCancelled,
    (COUNT(t.TicketID) * 10.00) AS Revenue
FROM Screenings s
LEFT JOIN Tickets t ON s.ScreeningID = t.ScreeningID
LEFT JOIN CancelledTickets c ON s.ScreeningID = c.ScreeningID
GROUP BY s.ScreeningDate
ORDER BY s.ScreeningDate;


-- Creating Users table for role-based access control
CREATE TABLE Users (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(50) NOT NULL UNIQUE,
    PasswordHash VARCHAR(256) NOT NULL,
    Role ENUM('Admin', 'TicketClerk', 'Guest') NOT NULL
);


-- Inserting sample users
INSERT INTO Users (Username, PasswordHash, Role)
VALUES
    ('admin_user', SHA2('admin123', 256), 'Admin'),
    ('clerk_user', SHA2('clerk123', 256), 'TicketClerk'),
    ('guest_user', SHA2('guest123', 256), 'Guest');


-- Creating MySQL users for role-based access control
CREATE USER 'admin_user'@'localhost' IDENTIFIED BY 'admin123';
CREATE USER 'clerk_user'@'localhost' IDENTIFIED BY 'clerk123';
CREATE USER 'guest_user'@'localhost' IDENTIFIED BY 'guest123';


-- Granting permissions for Admin
GRANT ALL PRIVILEGES ON CinemaDBcc.* TO 'admin_user'@'localhost';


-- Granting permissions for TicketClerk
GRANT SELECT, INSERT, UPDATE ON CinemaDBcc.Tickets TO 'clerk_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON CinemaDBcc.Customers TO 'clerk_user'@'localhost';
GRANT SELECT ON CinemaDBcc.Screenings TO 'clerk_user'@'localhost';
GRANT SELECT ON CinemaDBcc.Movies TO 'clerk_user'@'localhost';


-- Granting permissions for Guest
GRANT SELECT ON CinemaDBcc.Movies TO 'guest_user'@'localhost';
GRANT SELECT ON CinemaDBcc.Screenings TO 'guest_user'@'localhost';


-- Apply privilege changes
FLUSH PRIVILEGES;


-- Creating SecurityAudit table for security logging
CREATE TABLE SecurityAudit (
    AuditID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(50),
    Operation VARCHAR(100),
    Timestamp DATETIME
);






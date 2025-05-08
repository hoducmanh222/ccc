import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from tkcalendar import DateEntry
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.screening_model import ScreeningModel
from models.movie_model import MovieModel
from models.cinema_room_model import CinemaRoomModel

class ScreeningManagementFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.screening_model = ScreeningModel()
        self.movie_model = MovieModel()
        self.room_model = CinemaRoomModel()
        
        # Create UI elements
        self.create_widgets()
        
        # Load data
        self.refresh_data()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(self, text="Screening Management", font=("Helvetica", 16))
        title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")
        
        # Screening list
        self.screening_tree = ttk.Treeview(self, columns=("ID", "Movie", "Room", "Date", "Time", "Occupancy"), 
                                           show="headings", height=15)
        self.screening_tree.heading("ID", text="ID")
        self.screening_tree.heading("Movie", text="Movie")
        self.screening_tree.heading("Room", text="Room")
        self.screening_tree.heading("Date", text="Date")
        self.screening_tree.heading("Time", text="Time")
        self.screening_tree.heading("Occupancy", text="Occupancy %")
        
        self.screening_tree.column("ID", width=50, anchor="center")
        self.screening_tree.column("Movie", width=200)
        self.screening_tree.column("Room", width=100)
        self.screening_tree.column("Date", width=100, anchor="center")
        self.screening_tree.column("Time", width=100, anchor="center")
        self.screening_tree.column("Occupancy", width=100, anchor="center")
        
        self.screening_tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Add scrollbar to treeview
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.screening_tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.screening_tree.configure(yscrollcommand=scrollbar.set)
        
        # Frame for screening details
        details_frame = tk.LabelFrame(self, text="Screening Details")
        details_frame.grid(row=1, column=2, padx=10, pady=10, sticky="n")
        
        # Screening form
        tk.Label(details_frame, text="Movie:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.movie_var = tk.StringVar()
        self.movie_combo = ttk.Combobox(details_frame, textvariable=self.movie_var, width=25)
        self.movie_combo.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(details_frame, text="Room:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.room_var = tk.StringVar()
        self.room_combo = ttk.Combobox(details_frame, textvariable=self.room_var, width=25)
        self.room_combo.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(details_frame, text="Date:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.date_picker = DateEntry(details_frame, width=23, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_picker.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(details_frame, text="Time (HH:MM):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.time_var = tk.StringVar()
        self.time_entry = tk.Entry(details_frame, textvariable=self.time_var, width=25)
        self.time_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Buttons frame
        button_frame = tk.Frame(details_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.new_button = tk.Button(button_frame, text="New", command=self.clear_form)
        self.new_button.grid(row=0, column=0, padx=5)
        
        self.save_button = tk.Button(button_frame, text="Save", command=self.save_screening)
        self.save_button.grid(row=0, column=1, padx=5)
        
        self.delete_button = tk.Button(button_frame, text="Delete", command=self.delete_screening)
        self.delete_button.grid(row=0, column=2, padx=5)
        
        # Add refresh button
        self.refresh_button = tk.Button(button_frame, text="Refresh", command=self.refresh_data)
        self.refresh_button.grid(row=0, column=3, padx=5)
        
        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Bind treeview selection
        self.screening_tree.bind("<<TreeviewSelect>>", self.on_screening_select)
        
    def refresh_data(self):
        # Clear existing data
        for i in self.screening_tree.get_children():
            self.screening_tree.delete(i)
            
        # Load screenings
        screenings = self.screening_model.get_all_screenings()
        for screening in screenings:
            self.screening_tree.insert("", "end", values=(
                screening["ScreeningID"],
                screening["MovieTitle"],
                screening["RoomName"],
                screening["ScreeningDate"],
                screening["ScreeningTime"],
                f"{float(screening['OccupancyRate']):.2f}%"
            ))
            
        # Load movies and rooms for dropdowns
        movies = self.movie_model.get_all_movies()
        self.movie_combo["values"] = [movie["MovieTitle"] for movie in movies]
        self.movies_data = {movie["MovieTitle"]: movie["MovieID"] for movie in movies}
        
        rooms = self.room_model.get_all_rooms()
        self.room_combo["values"] = [room["RoomName"] for room in rooms]
        self.rooms_data = {room["RoomName"]: room["RoomID"] for room in rooms}
        
        # Clear form
        self.clear_form()
        
    def on_screening_select(self, event):
        selected_items = self.screening_tree.selection()
        if not selected_items:
            return
            
        # Get the selected screening ID
        screening_id = self.screening_tree.item(selected_items[0])["values"][0]
        
        # Get screening details
        screening = self.screening_model.get_screening(screening_id)
        if screening:
            movie_title = self.get_movie_title_by_id(screening["MovieID"])
            room_name = self.get_room_name_by_id(screening["RoomID"])
            
            self.movie_var.set(movie_title)
            self.room_var.set(room_name)
            self.date_picker.set_date(screening["ScreeningDate"])
            
            # Format the time correctly from timedelta
            time_delta = screening["ScreeningTime"]
            if hasattr(time_delta, 'seconds'):
                # Handle timedelta object
                total_seconds = time_delta.total_seconds()
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                formatted_time = f"{hours:02d}:{minutes:02d}"
            else:
                # Handle string or other time formats
                formatted_time = str(time_delta)
                if len(formatted_time) > 5:  # If it has seconds, remove them
                    formatted_time = formatted_time[:5]
                    
            self.time_var.set(formatted_time)
            self.current_id = screening["ScreeningID"]
    
    def get_movie_title_by_id(self, movie_id):
        for title, id in self.movies_data.items():
            if id == movie_id:
                return title
        return ""
    
    def get_room_name_by_id(self, room_id):
        for name, id in self.rooms_data.items():
            if id == room_id:
                return name
        return ""
        
    def clear_form(self):
        self.movie_var.set("")
        self.room_var.set("")
        self.date_picker.set_date(datetime.date.today())
        self.time_var.set("18:00")
        self.current_id = None
        
    def save_screening(self):
        # Validate inputs
        movie_title = self.movie_var.get()
        room_name = self.room_var.get()
        
        if not movie_title in self.movies_data:
            messagebox.showerror("Validation Error", "Please select a valid movie")
            return
            
        if not room_name in self.rooms_data:
            messagebox.showerror("Validation Error", "Please select a valid room")
            return
        
        movie_id = self.movies_data[movie_title]
        room_id = self.rooms_data[room_name]
        
        screening_date = self.date_picker.get_date()
        
        # Validate time format
        time_str = self.time_var.get().strip()
        try:
            hours, minutes = time_str.split(":")
            hours = int(hours)
            minutes = int(minutes)
            if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
                raise ValueError("Invalid time")
            screening_time = f"{hours:02d}:{minutes:02d}:00"
        except ValueError:
            messagebox.showerror("Validation Error", "Time must be in format HH:MM")
            return
            
        # Save or update screening
        if self.current_id:
            self.screening_model.update_screening(
                self.current_id, movie_id, room_id, 
                screening_date, screening_time
            )
            messagebox.showinfo("Success", "Screening updated successfully")
        else:
            self.screening_model.add_screening(
                movie_id, room_id, screening_date, screening_time
            )
            messagebox.showinfo("Success", "Screening added successfully")
            
        # Refresh the data
        self.refresh_data()
        
    def delete_screening(self):
        if not self.current_id:
            messagebox.showinfo("Info", "Please select a screening to delete")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this screening?"):
            self.screening_model.delete_screening(self.current_id)
            messagebox.showinfo("Success", "Screening deleted successfully")
            self.refresh_data()

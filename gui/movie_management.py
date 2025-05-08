import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.movie_model import MovieModel
from models.feedback_model import FeedbackModel

class MovieManagementFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.movie_model = MovieModel()
        self.feedback_model = FeedbackModel()
        
        # Create UI elements
        self.create_widgets()
        
        # Load data
        self.refresh_data()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(self, text="Movie Management", font=("Helvetica", 16))
        title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")
        
        # Movie list
        self.movie_tree = ttk.Treeview(self, columns=("ID", "Title", "Genre", "Duration", "Rating"), 
                                      show="headings", height=15)
        self.movie_tree.heading("ID", text="ID")
        self.movie_tree.heading("Title", text="Movie Title")
        self.movie_tree.heading("Genre", text="Genre")
        self.movie_tree.heading("Duration", text="Duration (min)")
        self.movie_tree.heading("Rating", text="Rating")
        
        self.movie_tree.column("ID", width=50, anchor="center")
        self.movie_tree.column("Title", width=250)
        self.movie_tree.column("Genre", width=150)
        self.movie_tree.column("Duration", width=100, anchor="center")
        self.movie_tree.column("Rating", width=100, anchor="center")
        
        self.movie_tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Add scrollbar to treeview
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.movie_tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.movie_tree.configure(yscrollcommand=scrollbar.set)
        
        # Frame for movie details
        details_frame = tk.LabelFrame(self, text="Movie Details")
        details_frame.grid(row=1, column=2, padx=10, pady=10, sticky="n")
        
        # Movie form
        tk.Label(details_frame, text="Title:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_var = tk.StringVar()
        tk.Entry(details_frame, textvariable=self.title_var, width=25).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(details_frame, text="Genre:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.genre_var = tk.StringVar()
        self.genre_combo = ttk.Combobox(details_frame, textvariable=self.genre_var, width=23)
        self.genre_combo.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(details_frame, text="Duration (mins):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.duration_var = tk.StringVar()
        tk.Entry(details_frame, textvariable=self.duration_var, width=25).grid(row=2, column=1, padx=5, pady=5)
        
        # Buttons frame
        button_frame = tk.Frame(details_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.new_button = tk.Button(button_frame, text="New", command=self.clear_form)
        self.new_button.grid(row=0, column=0, padx=5)
        
        self.save_button = tk.Button(button_frame, text="Save", command=self.save_movie)
        self.save_button.grid(row=0, column=1, padx=5)
        
        self.delete_button = tk.Button(button_frame, text="Delete", command=self.delete_movie)
        self.delete_button.grid(row=0, column=2, padx=5)
        
        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Bind treeview selection
        self.movie_tree.bind("<<TreeviewSelect>>", self.on_movie_select)
        
    def refresh_data(self):
        # Clear existing data
        for i in self.movie_tree.get_children():
            self.movie_tree.delete(i)
            
        # Load movies
        movies = self.movie_model.get_all_movies()
        for movie in movies:
            # Get movie rating
            rating_info = self.feedback_model.get_average_rating_by_movie(movie["MovieID"])
            avg_rating = rating_info["AverageRating"]
            rating_display = f"{avg_rating:.1f} ★" if avg_rating else "No ratings"
            
            self.movie_tree.insert("", "end", values=(
                movie["MovieID"],
                movie["MovieTitle"],
                movie["GenreName"] if movie["GenreName"] else "",
                movie["DurationMinutes"],
                rating_display
            ))
            
        # Load genres
        genres = self.movie_model.get_all_genres()
        self.genre_combo["values"] = [g["GenreName"] for g in genres]
        
        # Clear form
        self.clear_form()
        
    def on_movie_select(self, event):
        selected_items = self.movie_tree.selection()
        if not selected_items:
            return
            
        # Get the selected movie ID
        movie_id = self.movie_tree.item(selected_items[0])["values"][0]
        
        # Get movie details
        movie = self.movie_model.get_movie(movie_id)
        if movie:
            self.title_var.set(movie["MovieTitle"])
            self.genre_var.set(movie["GenreName"] if movie["GenreName"] else "")
            self.duration_var.set(movie["DurationMinutes"])
            self.current_id = movie["MovieID"]
            self.current_genre_id = movie["GenreID"]
        
    def clear_form(self):
        self.title_var.set("")
        self.genre_var.set("")
        self.duration_var.set("")
        self.current_id = None
        self.current_genre_id = None
        
    def save_movie(self):
        # Validate inputs
        title = self.title_var.get().strip()
        genre_name = self.genre_var.get().strip()
        
        try:
            duration = int(self.duration_var.get().strip())
            if duration <= 0:
                raise ValueError("Duration must be positive")
        except ValueError:
            messagebox.showerror("Validation Error", "Duration must be a positive integer")
            return
            
        if not title:
            messagebox.showerror("Validation Error", "Title is required")
            return
            
        # Get genre ID
        genre_id = None
        genres = self.movie_model.get_all_genres()
        for g in genres:
            if g["GenreName"] == genre_name:
                genre_id = g["GenreID"]
                break
                
        # If genre doesn't exist, create it
        if genre_name and not genre_id:
            genre_id = self.movie_model.add_genre(genre_name)
            
        # Save or update movie
        if self.current_id:
            self.movie_model.update_movie(self.current_id, title, genre_id, duration)
            messagebox.showinfo("Success", "Movie updated successfully")
        else:
            self.movie_model.add_movie(title, genre_id, duration)
            messagebox.showinfo("Success", "Movie added successfully")
            
        # Refresh the data
        self.refresh_data()
        
        # Refresh related frames
        if hasattr(self.controller, 'frames'):
            for frame_name, frame_instance in self.controller.frames.items():
                # Only refresh other frames with refresh_data method
                if hasattr(frame_instance, 'refresh_data') and frame_instance != self:
                    frame_instance.refresh_data()
                    
        # Update dashboard if available
        if hasattr(self.controller, 'update_dashboard'):
            self.controller.update_dashboard()
        
    def delete_movie(self):
        if not self.current_id:
            messagebox.showinfo("Info", "Please select a movie to delete")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this movie?"):
            self.movie_model.delete_movie(self.current_id)
            messagebox.showinfo("Success", "Movie deleted successfully")
            self.refresh_data()

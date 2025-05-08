import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.cinema_room_model import CinemaRoomModel

class CinemaRoomManagementFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.room_model = CinemaRoomModel()
        
        # Create UI elements
        self.create_widgets()
        
        # Load data
        self.refresh_data()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(self, text="Cinema Room Management", font=("Helvetica", 16))
        title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")
        
        # Room list
        self.room_tree = ttk.Treeview(self, columns=("ID", "Name", "Capacity"), 
                                      show="headings", height=15)
        self.room_tree.heading("ID", text="ID")
        self.room_tree.heading("Name", text="Room Name")
        self.room_tree.heading("Capacity", text="Capacity")
        
        self.room_tree.column("ID", width=50, anchor="center")
        self.room_tree.column("Name", width=200)
        self.room_tree.column("Capacity", width=100, anchor="center")
        
        self.room_tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Add scrollbar to treeview
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.room_tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.room_tree.configure(yscrollcommand=scrollbar.set)
        
        # Frame for room details
        details_frame = tk.LabelFrame(self, text="Room Details")
        details_frame.grid(row=1, column=2, padx=10, pady=10, sticky="n")
        
        # Room form
        tk.Label(details_frame, text="Room Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_var = tk.StringVar()
        tk.Entry(details_frame, textvariable=self.name_var, width=25).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(details_frame, text="Capacity:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.capacity_var = tk.StringVar()
        tk.Entry(details_frame, textvariable=self.capacity_var, width=25).grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons frame
        button_frame = tk.Frame(details_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.new_button = tk.Button(button_frame, text="New", command=self.clear_form)
        self.new_button.grid(row=0, column=0, padx=5)
        
        self.save_button = tk.Button(button_frame, text="Save", command=self.save_room)
        self.save_button.grid(row=0, column=1, padx=5)
        
        self.delete_button = tk.Button(button_frame, text="Delete", command=self.delete_room)
        self.delete_button.grid(row=0, column=2, padx=5)
        
        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Bind treeview selection
        self.room_tree.bind("<<TreeviewSelect>>", self.on_room_select)
        
    def refresh_data(self):
        # Clear existing data
        for i in self.room_tree.get_children():
            self.room_tree.delete(i)
            
        # Load rooms
        rooms = self.room_model.get_all_rooms()
        for room in rooms:
            self.room_tree.insert("", "end", values=(
                room["RoomID"],
                room["RoomName"],
                room["Capacity"]
            ))
        
        # Clear form
        self.clear_form()
        
    def on_room_select(self, event):
        selected_items = self.room_tree.selection()
        if not selected_items:
            return
            
        # Get the selected room ID
        room_id = self.room_tree.item(selected_items[0])["values"][0]
        
        # Get room details
        room = self.room_model.get_room(room_id)
        if room:
            self.name_var.set(room["RoomName"])
            self.capacity_var.set(room["Capacity"])
            self.current_id = room["RoomID"]
        
    def clear_form(self):
        self.name_var.set("")
        self.capacity_var.set("")
        self.current_id = None
        
    def save_room(self):
        # Validate inputs
        name = self.name_var.get().strip()
        
        try:
            capacity = int(self.capacity_var.get().strip())
            if capacity <= 0:
                raise ValueError("Capacity must be positive")
        except ValueError:
            messagebox.showerror("Validation Error", "Capacity must be a positive integer")
            return
            
        if not name:
            messagebox.showerror("Validation Error", "Room name is required")
            return
            
        # Save or update room
        if self.current_id:
            self.room_model.update_room(self.current_id, name, capacity)
            messagebox.showinfo("Success", "Room updated successfully")
        else:
            self.room_model.add_room(name, capacity)
            messagebox.showinfo("Success", "Room added successfully")
            
        # Refresh the data
        self.refresh_data()
        
        # Refresh screening management if it exists
        if hasattr(self.controller, 'frames'):
            for frame_class, frame in self.controller.frames.items():
                if frame.__class__.__name__ == "ScreeningManagementFrame":
                    if hasattr(frame, 'refresh_data'):
                        frame.refresh_data()
        
        # Update dashboard if available
        if hasattr(self.controller, 'update_dashboard'):
            self.controller.update_dashboard()
        
    def delete_room(self):
        if not self.current_id:
            messagebox.showinfo("Info", "Please select a room to delete")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this room?"):
            self.room_model.delete_room(self.current_id)
            messagebox.showinfo("Success", "Room deleted successfully")
            self.refresh_data()

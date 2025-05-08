import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
from tkcalendar import DateEntry
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.movie_model import MovieModel
from models.screening_model import ScreeningModel
from models.customer_model import CustomerModel
from models.ticket_model import TicketModel

class TicketBookingFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.movie_model = MovieModel()
        self.screening_model = ScreeningModel()
        self.customer_model = CustomerModel()
        self.ticket_model = TicketModel()
        
        # Initialize variables
        self.selected_screening_id = None
        self.selected_customer_id = None
        self.seat_buttons = {}
        self.phone_numbers = []  # Will store all phone numbers for auto-completion
        
        # Create UI elements
        self.create_widgets()
        
        # Load initial data
        self.refresh_data()
        
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel - Screening selection
        left_frame = tk.LabelFrame(main_frame, text="Screening Selection")
        left_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        # Date selection
        tk.Label(left_frame, text="Select Date:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_picker = DateEntry(left_frame, width=12, background='darkblue',
                               foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_picker.grid(row=0, column=1, padx=5, pady=5)
        self.date_picker.set_date(datetime.date.today())
        self.date_picker.bind("<<DateEntrySelected>>", lambda e: self.load_screenings())
        
        # Search button
        search_button = tk.Button(left_frame, text="Search", command=self.load_screenings)
        search_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Screenings table
        self.screenings_tree = ttk.Treeview(left_frame, columns=("ID", "Movie", "Room", "Time", "Available"), 
                                           show="headings", height=8)
        self.screenings_tree.heading("ID", text="ID")
        self.screenings_tree.heading("Movie", text="Movie")
        self.screenings_tree.heading("Room", text="Room")
        self.screenings_tree.heading("Time", text="Time")
        self.screenings_tree.heading("Available", text="Available Seats")
        
        self.screenings_tree.column("ID", width=40, anchor="center")
        self.screenings_tree.column("Movie", width=180)
        self.screenings_tree.column("Room", width=80)
        self.screenings_tree.column("Time", width=80, anchor="center")
        self.screenings_tree.column("Available", width=100, anchor="center")
        
        self.screenings_tree.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.screenings_tree.bind("<<TreeviewSelect>>", self.on_screening_select)
        
        screening_scroll = ttk.Scrollbar(left_frame, orient="vertical", command=self.screenings_tree.yview)
        screening_scroll.grid(row=1, column=3, sticky="ns")
        self.screenings_tree.configure(yscrollcommand=screening_scroll.set)
        
        # Middle panel - Seat selection
        middle_frame = tk.LabelFrame(main_frame, text="Seat Selection")
        middle_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        
        # Seats layout will be created dynamically
        self.seats_frame = tk.Frame(middle_frame)
        self.seats_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Right panel - Customer and ticket info
        right_frame = tk.LabelFrame(main_frame, text="Customer Information")
        right_frame.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")
        
        # Customer form
        tk.Label(right_frame, text="Phone Number:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.phone_var = tk.StringVar()
        
        # Create a combobox for phone entry with autocompletion
        self.phone_entry = ttk.Combobox(right_frame, textvariable=self.phone_var, width=15)
        self.phone_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.phone_entry.bind("<KeyRelease>", self.on_phone_keyrelease)
        self.phone_entry.bind("<<ComboboxSelected>>", self.on_phone_selected)
        
        search_customer_btn = tk.Button(right_frame, text="Find", command=self.find_customer)
        search_customer_btn.grid(row=0, column=2, padx=5, pady=5)
        
        tk.Label(right_frame, text="Customer Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(right_frame, textvariable=self.name_var, width=25)
        self.name_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Selected seat label
        tk.Label(right_frame, text="Selected Seat:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.selected_seat_var = tk.StringVar()
        self.selected_seat_label = tk.Label(right_frame, textvariable=self.selected_seat_var, font=("Helvetica", 12, "bold"))
        self.selected_seat_label.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Book button
        self.book_button = tk.Button(right_frame, text="Book Ticket", command=self.book_ticket, state="disabled")
        self.book_button.grid(row=3, column=0, columnspan=3, padx=5, pady=15)
        
        # Add a prominent manual refresh button
        self.manual_refresh_btn = tk.Button(main_frame, text="↻ REFRESH SEATS & DATA", 
                                         bg="lightblue", font=("Helvetica", 12, "bold"),
                                         command=self.force_refresh)
        self.manual_refresh_btn.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Configure grid weights
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
    
    def force_refresh(self):
        """Force a complete refresh of all data in this frame"""
        print("Manual refresh triggered in TicketBooking")
        
        # Refresh screenings data
        self.load_screenings()
        
        # Refresh seat layout if a screening is selected
        if self.selected_screening_id:
            self.create_seat_layout(self.selected_screening_id)
            
        # Refresh customer data
        self.load_phone_numbers()
        
        # Force UI update
        self.update_idletasks()
        
    def refresh_data(self):
        self.load_screenings()
        self.load_phone_numbers()  # Load all phone numbers for autocompletion
        self.clear_form()
        
    def load_phone_numbers(self):
        """Load all customer phone numbers for autocomplete functionality"""
        customers = self.customer_model.get_all_customers()
        
        if customers and len(customers) > 0:
            # Use PhoneNumber key which is what's defined in the CustomerModel SQL query
            self.phone_numbers = [customer["PhoneNumber"] for customer in customers]
        else:
            self.phone_numbers = []
    
    def on_phone_keyrelease(self, event):
        # Filter phone numbers based on current input
        current_input = self.phone_var.get().strip()
        if current_input:
            filtered_numbers = [phone for phone in self.phone_numbers 
                               if current_input.lower() in phone.lower()]
            self.phone_entry["values"] = filtered_numbers
            
            # If we have an exact match, auto-fill customer name
            if current_input in self.phone_numbers:
                self.auto_fill_customer(current_input)
        else:
            self.phone_entry["values"] = self.phone_numbers
    
    def on_phone_selected(self, event):
        # When a suggestion is selected from dropdown, fill customer details
        selected_phone = self.phone_var.get().strip()
        if selected_phone:
            self.auto_fill_customer(selected_phone)
    
    def auto_fill_customer(self, phone_number):
        # Get customer by phone and fill details
        customer = self.customer_model.get_customer_by_phone(phone_number)
        if customer:
            self.name_var.set(customer["CustomerName"])
            self.selected_customer_id = customer["CustomerID"]
            
            # Enable book button if seat is selected
            if self.selected_seat_var.get():
                self.book_button["state"] = "normal"
    
    def load_screenings(self):
        """Load all screenings for the selected date with fresh availability data"""
        # Clear existing screenings
        for i in self.screenings_tree.get_children():
            self.screenings_tree.delete(i)
        
        # Get selected date
        selected_date = self.date_picker.get_date()
        
        # Force fresh data from database
        screenings = self.screening_model.get_screenings_by_date(selected_date, force_fresh=True)
        
        for screening in screenings:
            # Get FRESH seat availability data directly
            availability = self.screening_model.get_seat_availability(screening["ScreeningID"], force_fresh=True)
            
            self.screenings_tree.insert("", "end", values=(
                screening["ScreeningID"],
                screening["MovieTitle"],
                screening["RoomName"],
                screening["ScreeningTime"],
                f"{availability['AvailableSeats']} / {availability['Capacity']}" if availability else "N/A"
            ))
    
    def on_screening_select(self, event):
        selected_items = self.screenings_tree.selection()
        if not selected_items:
            return
        
        # Get the selected screening ID
        screening_id = self.screenings_tree.item(selected_items[0])["values"][0]
        self.selected_screening_id = screening_id
        
        # Clear selected seat
        self.selected_seat_var.set("")
        self.book_button["state"] = "disabled"
        
        # Get seat availability and create seat layout
        self.create_seat_layout(screening_id)
    
    def create_seat_layout(self, screening_id):
        # Clear previous seat layout
        for widget in self.seats_frame.winfo_children():
            widget.destroy()
        
        self.seat_buttons = {}
        
        # Get seat availability for the screening
        availability = self.screening_model.get_seat_availability(screening_id)
        if not availability:
            return
        
        # Get already occupied seats
        occupied_seats = self.ticket_model.get_occupied_seats(screening_id)
        
        # Create room layout with rows (letters) and columns (numbers)
        rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
        columns = 10  # Assuming 10 seats per row
        
        # Screen label
        screen_label = tk.Label(self.seats_frame, text="SCREEN", bg="lightgray", width=30)
        screen_label.grid(row=0, column=0, columnspan=columns+1, padx=5, pady=10)
        
        # Create seat grid
        for r, row in enumerate(rows):
            # Row label
            tk.Label(self.seats_frame, text=row).grid(row=r+1, column=0, padx=2)
            
            for col in range(1, columns+1):
                seat_id = f"{row}{col}"
                
                # Check if seat is occupied
                is_occupied = seat_id in occupied_seats
                
                # Create seat button
                btn = tk.Button(self.seats_frame, text=seat_id, width=3, height=1,
                               bg="red" if is_occupied else "green",
                               state="disabled" if is_occupied else "normal")
                
                if not is_occupied:
                    btn.config(command=lambda s=seat_id, b=btn: self.select_seat(s, b))
                
                btn.grid(row=r+1, column=col, padx=2, pady=2)
                self.seat_buttons[seat_id] = btn
    
    def select_seat(self, seat_id, button):
        # Reset all unoccupied seats to green
        for s, btn in self.seat_buttons.items():
            if btn["state"] != "disabled":
                btn.config(bg="green")
        
        # Highlight the selected seat
        button.config(bg="blue")
        self.selected_seat_var.set(seat_id)
        
        # Enable book button if customer is selected
        if self.selected_customer_id:
            self.book_button["state"] = "normal"
    
    def find_customer(self):
        phone = self.phone_var.get().strip()
        if not phone:
            messagebox.showerror("Error", "Please enter a phone number")
            return
        
        # Look up customer by phone
        customer = self.customer_model.get_customer_by_phone(phone)
        
        if customer:
            self.name_var.set(customer["CustomerName"])
            self.selected_customer_id = customer["CustomerID"]
            
            # Enable book button if seat is selected
            if self.selected_seat_var.get():
                self.book_button["state"] = "normal"
        else:
            # Check if we should create a new customer
            if messagebox.askyesno("Customer Not Found", 
                                 "Customer not found. Would you like to create a new customer?"):
                name = self.name_var.get().strip()
                if not name:
                    name = simpledialog.askstring("Customer Name", "Enter customer name:")
                
                if name:
                    # Create new customer
                    self.selected_customer_id = self.customer_model.add_customer(name, phone)
                    messagebox.showinfo("Success", "New customer added successfully")
                    
                    # Refresh the phone number list
                    self.load_phone_numbers()
                    
                    # Enable book button if seat is selected
                    if self.selected_seat_var.get():
                        self.book_button["state"] = "normal"
                else:
                    messagebox.showerror("Error", "Customer name is required")
    
    def book_ticket(self):
        """Book a ticket for the selected seat and customer"""
        if not self.selected_screening_id:
            messagebox.showerror("Error", "Please select a screening")
            return
            
        if not self.selected_customer_id:
            messagebox.showerror("Error", "Please select or create a customer")
            return
            
        seat = self.selected_seat_var.get()
        if not seat:
            messagebox.showerror("Error", "Please select a seat")
            return
        
        # Get IDs for booking
        customer_id = self.selected_customer_id
        screening_id = self.selected_screening_id
        seat = self.selected_seat_var.get()
        
        # Pass the username from controller to ensure proper audit trail
        success = self.ticket_model.book_ticket(
            customer_id, 
            screening_id, 
            seat,
            user_id=getattr(self.controller, 'user_id', None),
            username=getattr(self.controller, 'username', None)  # Pass the username from the controller
        )
        
        if success:
            messagebox.showinfo("Success", "Ticket booked successfully!")
            
            # Force refresh of ticket history frame IMMEDIATELY
            for frame_class, frame in self.controller.frames.items():
                if frame.__class__.__name__ == "TicketHistoryFrame" and hasattr(frame, 'refresh_data'):
                    print("Forcing refresh of TicketHistoryFrame after booking")
                    frame.refresh_data()
            
            # Refresh the seat display
            self.load_seats()
            
            # Update dashboard if available
            if hasattr(self.controller, 'update_dashboard'):
                self.controller.update_dashboard()
                
            # Force UI update
            self.controller.update()
            
            # Clear selection
            self.clear_form()
        else:
            messagebox.showerror("Error", "Failed to book ticket. Seat might be already taken.")
    
    def clear_form(self):
        """Clear all form selections and reset UI"""
        self.name_var.set("")
        self.phone_var.set("")
        self.selected_customer_id = None
        self.selected_seat_var.set("")
        self.book_button["state"] = "disabled"
        
        # Reset all seat buttons to green (if any exist)
        for seat_id, button in self.seat_buttons.items():
            if button["state"] != "disabled":
                button.config(bg="green")
    
    def load_seats(self):
        """Reload seat layout for the selected screening"""
        if self.selected_screening_id:
            self.create_seat_layout(self.selected_screening_id)

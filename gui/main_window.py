import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import datetime
import sys
import os
from tkcalendar import DateEntry
from tkinter import messagebox

# Add the parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import frames
from gui.movie_management import MovieManagementFrame
from gui.screening_management import ScreeningManagementFrame
from gui.customer_management import CustomerManagementFrame
from gui.ticket_booking import TicketBookingFrame
from gui.reports import ReportsFrame
from gui.feedback_management import FeedbackManagementFrame
from gui.ticket_history import TicketHistoryFrame

# Import models
from models.report_model import ReportModel
from models.screening_model import ScreeningModel

class MainWindow(tk.Tk):
    def __init__(self, role='admin_user', user_id=None, username=None):
        super().__init__()
        # Override OS DPI scaling (set scaling factor to 1.0)
        self.tk.call('tk', 'scaling', 1.0)
        
        # Store the user role, ID, and username
        self.role = role
        self.user_id = user_id
        self.username = username
        
        # Store original window size to enforce
        self.target_width = 1280
        self.target_height = 800
        
        # Configure window before creating any frames
        self.title("Cinema Management System")
        
        # Fix window size to be consistent for all roles
        self.geometry(f"{self.target_width}x{self.target_height}")
        self.minsize(self.target_width, self.target_height)
        
        # Prevent resizing for admin users to avoid shrinking issues
        if self.role == 'admin_user':
            self.resizable(False, False)
        
        # Initialize models for dashboard data
        self.report_model = ReportModel()
        self.screening_model = ScreeningModel()
        
        # Create the main layout
        self.setup_layout()
        
        # Initialize frames
        self.frames = {}
        self.initialize_frames()
        
        # Process pending geometry events before showing dashboard
        self.update_idletasks()
        
        # Show dashboard first
        self.show_dashboard()
        
        # Update title with role display name
        self.title(f"Cinema Management System - {self.get_role_display_name()}")
        
        # Add this to fix window shrinking for Admin
        self.container.pack_propagate(False)
        
        # Bind to Configure event for admin window size enforcement
        # This triggers whenever window size changes
        if self.role == 'admin_user':
            self.bind("<Configure>", self.check_window_size)

    def check_window_size(self, event=None):
        """Check if window size has changed and correct it if needed"""
        if self.role != 'admin_user':
            return
            
        # Don't react to height-only changes to avoid recursion
        current_width = self.winfo_width()
        current_height = self.winfo_height()
        
        # Only enforce size if it's smaller than target
        if current_width < self.target_width or current_height < self.target_height:
            print(f"Admin window wrong size: {current_width}x{current_height}, forcing to {self.target_width}x{self.target_height}")
            self.geometry(f"{self.target_width}x{self.target_height}")
            self.update_idletasks()

    def get_role_display_name(self):
        """Convert role identifier to display name"""
        role_names = {
            "admin_user": "Administrator",
            "clerk_user": "Ticket Clerk",
            "guest_user": "Guest"
        }
        return role_names.get(self.role, "User")
        
    def setup_layout(self):
        # Top menu frame
        self.menu_frame = tk.Frame(self, bg="#333333", height=50)
        self.menu_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Create buttons instead of a menu
        btn_dashboard = tk.Button(self.menu_frame, text="Dashboard", 
                                  command=self.show_dashboard,
                                  bg="#333333", fg="white", 
                                  activebackground="#555555", activeforeground="white",
                                  bd=0, padx=15, pady=10)
        btn_dashboard.pack(side=tk.LEFT)
        
        # Movies dropdown frame and button - limit based on role
        movies_btn = tk.Menubutton(self.menu_frame, text="Movies", 
                                   bg="#333333", fg="white",
                                   activebackground="#555555", activeforeground="white",
                                   bd=0, padx=15, pady=10, relief=tk.FLAT)
        movies_btn.pack(side=tk.LEFT)
        
        movies_menu = tk.Menu(movies_btn, tearoff=0)
        
        # Movie Management (admin only)
        if self.role == "admin_user":
            movies_menu.add_command(label="Movie Management", 
                                   command=lambda: self.show_frame(MovieManagementFrame))
        
        # Screening Management (admin only)
        if self.role == "admin_user":
            movies_menu.add_command(label="Screening Management",  
                                   command=lambda: self.show_frame(ScreeningManagementFrame))
        
        # Feedback Management (all users)
        movies_menu.add_command(label="Feedback Management",  
                               command=lambda: self.show_frame(FeedbackManagementFrame))
        
        movies_btn['menu'] = movies_menu
        
        # Bookings dropdown - show based on role
        if self.role in ["admin_user", "clerk_user"]:
            bookings_btn = tk.Menubutton(self.menu_frame, text="Bookings", 
                                        bg="#333333", fg="white",
                                        activebackground="#555555", activeforeground="white",
                                        bd=0, padx=15, pady=10, relief=tk.FLAT)
            bookings_btn.pack(side=tk.LEFT)
            
            bookings_menu = tk.Menu(bookings_btn, tearoff=0)
            
            # Customer Management
            bookings_menu.add_command(label="Customer Management", 
                                     command=lambda: self.show_frame(CustomerManagementFrame))
            
            # Ticket Booking
            bookings_menu.add_command(label="Ticket Booking",  
                                     command=lambda: self.show_frame(TicketBookingFrame))
            
            # Ticket History (New)
            bookings_menu.add_command(label="Ticket History",  
                                     command=lambda: self.show_frame(TicketHistoryFrame))
            
            bookings_btn['menu'] = bookings_menu
        
        # Reports button (admin only)
        if self.role == "admin_user":
            btn_reports = tk.Button(self.menu_frame, text="Reports", 
                                   command=lambda: self.show_frame(ReportsFrame),
                                   bg="#333333", fg="white", 
                                   activebackground="#555555", activeforeground="white",
                                   bd=0, padx=15, pady=10)
            btn_reports.pack(side=tk.LEFT)
        
        # Show current user role on the right
        role_label = tk.Label(self.menu_frame, text=f"Role: {self.get_role_display_name()}", 
                             bg="#333333", fg="white", padx=15, pady=10)
        role_label.pack(side=tk.RIGHT)
        
        # Main content container - always make sure this exists with proper size
        self.container = tk.Frame(self, width=1280, height=750)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
    
    def initialize_frames(self):
        # Create only the frames the user has permission to access
        frame_classes = []
        
        # Admin has access to all frames
        if self.role == "admin_user":
            frame_classes = [MovieManagementFrame, ScreeningManagementFrame, CustomerManagementFrame, 
                           TicketBookingFrame, ReportsFrame, FeedbackManagementFrame, TicketHistoryFrame]
        
        # Clerk has access to customer and ticket management
        elif self.role == "clerk_user":
            frame_classes = [CustomerManagementFrame, TicketBookingFrame, FeedbackManagementFrame, TicketHistoryFrame]
        
        # Guest has access to feedback only
        else:
            frame_classes = [FeedbackManagementFrame]
        
        # Create the available frames
        for F in frame_classes:
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Add references so frames can access each other directly
        for frame_class, frame in self.frames.items():
            frame.all_frames = self.frames
    
    def show_frame(self, cont):
        # Check if user has permission to access this frame
        if cont not in self.frames:
            messagebox.showwarning("Access Denied", f"You don't have permission to access this feature.")
            return
            
        # Hide the dashboard frame if it exists
        if hasattr(self, 'dashboard_frame'):
            self.dashboard_frame.grid_remove()
        
        # Hide all frames
        for frame in self.frames.values():
            frame.grid_remove()
        
        # Bring the selected frame to the top
        frame = self.frames[cont]
        frame.grid(row=0, column=0, sticky="nsew")
        
        # Store current frame reference for refresh operations
        self.current_frame = frame
        
        # Refresh data in the frame if it has a refresh_data method
        if hasattr(frame, 'refresh_data'):
            frame.refresh_data()
    
    def show_dashboard(self):
        # Hide all other frames
        for frame in self.frames.values():
            frame.grid_remove()
        
        # Create dashboard if it doesn't exist
        if not hasattr(self, 'dashboard_frame'):
            self.create_dashboard()
        else:
            # Update dashboard data
            self.update_dashboard()
        
        # Show dashboard
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
    
    def create_dashboard(self):
        # Create dashboard frame
        self.dashboard_frame = tk.Frame(self.container)
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
        
        # Title with role indicator
        title_label = tk.Label(self.dashboard_frame, 
                             text=f"Cinema Dashboard - {self.get_role_display_name()}", 
                             font=("Helvetica", 16))
        title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")
        
        # Create charts
        self.create_occupancy_chart()
        self.create_revenue_chart()
        
        # Navigation buttons - show only buttons for accessible features
        button_frame = tk.Frame(self.dashboard_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        # All roles can see movies
        ttk.Button(button_frame, text="View Movies", 
                  command=lambda: self.show_frame(FeedbackManagementFrame)).grid(row=0, column=0, padx=10)
        
        # Only admin and clerk can book tickets
        if self.role in ["admin_user", "clerk_user"]:
            ttk.Button(button_frame, text="Book Tickets", 
                      command=lambda: self.show_frame(TicketBookingFrame)).grid(row=0, column=1, padx=10)
        
        # Only admin and clerk can view ticket history
        if self.role in ["admin_user", "clerk_user"]:
            ttk.Button(button_frame, text="Ticket History", 
                      command=lambda: self.show_frame(TicketHistoryFrame)).grid(row=0, column=2, padx=10)
        
        # Only admin can manage movies, screenings, and view reports
        if self.role == "admin_user":
            ttk.Button(button_frame, text="Manage Movies", 
                      command=lambda: self.show_frame(MovieManagementFrame)).grid(row=0, column=3, padx=10)
            ttk.Button(button_frame, text="Manage Screenings", 
                      command=lambda: self.show_frame(ScreeningManagementFrame)).grid(row=0, column=4, padx=10)
            ttk.Button(button_frame, text="View Reports", 
                      command=lambda: self.show_frame(ReportsFrame)).grid(row=0, column=5, padx=10)
    
    def create_occupancy_chart(self):
        # Create frame for chart
        chart_frame = tk.Frame(self.dashboard_frame)
        chart_frame.grid(row=1, column=0, padx=10, pady=10)
        
        # Add a title label above the chart to explain the data
        title_label = tk.Label(chart_frame, 
                              text="Current Theater Occupancy Rates",
                              font=("Helvetica", 12, "bold"))
        title_label.pack(side="top", pady=(0, 5))
        
        # Create filter frame
        filter_frame = tk.Frame(chart_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        
        # Room filter
        tk.Label(filter_frame, text="Room:").pack(side=tk.LEFT, padx=5)
        self.room_filter = ttk.Combobox(filter_frame, width=15)
        self.room_filter.pack(side=tk.LEFT, padx=5)
        
        # Movie filter
        tk.Label(filter_frame, text="Movie:").pack(side=tk.LEFT, padx=5)
        self.movie_filter = ttk.Combobox(filter_frame, width=20)
        self.movie_filter.pack(side=tk.LEFT, padx=5)
        
        # Apply filter button
        apply_button = tk.Button(filter_frame, text="Apply Filter", 
                              command=self.update_occupancy_chart)
        apply_button.pack(side=tk.LEFT, padx=10)
        
        # Load filter options
        self.load_filter_options()
        
        # Create figure for matplotlib
        fig = Figure(figsize=(6, 4), dpi=100)
        self.occupancy_ax = fig.add_subplot(111)
        self.occupancy_ax.set_title('Theater Occupancy by Screening')
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.occupancy_canvas = canvas
        
        # Update with data
        self.update_occupancy_chart()
    
    def load_filter_options(self):
        """Load options for room and movie filters"""
        try:
            # Get room and movie data directly from db connector
            # Get all rooms
            room_query = "SELECT RoomName FROM CinemaRooms ORDER BY RoomName"
            rooms = self.screening_model.db.execute_query(room_query)
            
            # Get all active movies
            movie_query = "SELECT DISTINCT MovieTitle FROM Movies JOIN Screenings ON Movies.MovieID = Screenings.MovieID ORDER BY MovieTitle"
            movies = self.screening_model.db.execute_query(movie_query)
            
            # Set combobox values
            if rooms:
                self.room_filter['values'] = ['All Rooms'] + [room["RoomName"] for room in rooms]
                self.room_filter.current(0)
            
            if movies:
                self.movie_filter['values'] = ['All Movies'] + [movie["MovieTitle"] for movie in movies]
                self.movie_filter.current(0)
            
        except Exception as e:
            print(f"Error loading filter options: {e}")
            # Set default values in case of error
            self.room_filter['values'] = ['All Rooms']
            self.movie_filter['values'] = ['All Movies']
            self.room_filter.current(0)
            self.movie_filter.current(0)
    
    def create_revenue_chart(self):
        # Create frame for chart
        chart_frame = tk.Frame(self.dashboard_frame)
        chart_frame.grid(row=1, column=1, padx=10, pady=10)
        
        # Add title label
        title_label = tk.Label(chart_frame, 
                              text="Revenue Analysis",
                              font=("Helvetica", 12, "bold"))
        title_label.pack(side="top", pady=(0, 5))
        
        # Create filter frame
        filter_frame = tk.Frame(chart_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        
        # Date filter
        tk.Label(filter_frame, text="Date:").pack(side=tk.LEFT, padx=5)
        self.revenue_date_picker = DateEntry(filter_frame, width=12, background='darkblue',
                                        foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.revenue_date_picker.pack(side=tk.LEFT, padx=5)
        self.revenue_date_picker.set_date(datetime.date.today())
        
        # Date range radio buttons
        self.date_range_var = tk.StringVar(value="week")
        tk.Radiobutton(filter_frame, text="Last 7 days", variable=self.date_range_var, 
                      value="week").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(filter_frame, text="Single day", variable=self.date_range_var, 
                      value="day").pack(side=tk.LEFT, padx=5)
        
        # Apply filter button
        apply_button = tk.Button(filter_frame, text="Apply", 
                              command=self.update_revenue_chart)
        apply_button.pack(side=tk.LEFT, padx=10)
        
        # Create figure for matplotlib
        fig = Figure(figsize=(6, 4), dpi=100)
        self.revenue_ax = fig.add_subplot(111)
        self.revenue_ax.set_title('Weekly Revenue')
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.revenue_canvas = canvas
        
        # Update with data
        self.update_revenue_chart()
    
    def update_dashboard(self):
        # Update all dashboard components
        self.update_occupancy_chart()
        self.update_revenue_chart()
    
    def refresh_visible_frames(self):
        """Refresh the currently visible frame"""
        try:
            print("Refreshing UI...")
            
            # Update dashboard if visible
            if hasattr(self, 'dashboard_frame') and hasattr(self.dashboard_frame, 'winfo_ismapped'):
                if self.dashboard_frame.winfo_ismapped():
                    self.update_dashboard()
            
            # Find the currently visible frame
            if hasattr(self, 'frames'):
                for frame_class, frame in self.frames.items():
                    if frame.winfo_ismapped():
                        if hasattr(frame, 'refresh_data'):
                            print(f"Refreshing {frame.__class__.__name__}")
                            frame.refresh_data()
            
            # Force UI update
            self.update()
            
        except Exception as e:
            print(f"Error during refresh: {e}")
        
        # Schedule next refresh
        if hasattr(self, 'auto_refresh_interval'):
            self.after(self.auto_refresh_interval, self.refresh_visible_frames)
    
    def force_global_refresh(self):
        """Force an immediate refresh of all UI elements"""
        # Cancel any pending refresh
        if hasattr(self, '_refresh_job'):
            self.after_cancel(self._refresh_job)
        
        # Perform immediate refresh
        self.refresh_visible_frames()
    
    def force_refresh_all(self):
        """Force immediate refresh of all UI components by directly querying the database"""
        print("Forcing complete refresh of all UI components")
        
        # Force refresh dashboard
        if hasattr(self, 'update_dashboard'):
            print("Refreshing dashboard")
            self.update_dashboard()
        
        # Force refresh all frames
        if hasattr(self, 'frames'):
            for name, frame in self.frames.items():
                if hasattr(frame, 'refresh_data'):
                    print(f"Refreshing {name.__name__}")
                    frame.refresh_data()
    
    def update_occupancy_chart(self):
        # Get selected values from filters
        selected_room = self.room_filter.get()
        selected_movie = self.movie_filter.get()
        
        try:
            # Get real occupancy data from database based on filters
            # Base query
            query = """
                SELECT m.MovieTitle, r.RoomName, s.ScreeningTime, s.ScreeningDate,
                       fn_occupancy_rate(s.ScreeningID) AS OccupancyRate
                FROM Screenings s
                JOIN Movies m ON s.MovieID = m.MovieID
                JOIN CinemaRooms r ON s.RoomID = r.RoomID
                WHERE 1=1
            """
            
            params = []
            
            # Add filters
            if selected_room != 'All Rooms':
                query += " AND r.RoomName = %s"
                params.append(selected_room)
                
            if selected_movie != 'All Movies':
                query += " AND m.MovieTitle = %s"
                params.append(selected_movie)
                
            # Get recent screenings - limit results for readability
            query += " ORDER BY s.ScreeningDate DESC, s.ScreeningTime DESC LIMIT 10"
            
            # Execute query using the db connector's execute_query method
            screenings = self.screening_model.db.execute_query(query, params)
            
            # Clear previous data
            self.occupancy_ax.clear()
            
            if screenings and len(screenings) > 0:
                labels = []
                occupancy_rates = []
                
                for screening in screenings:
                    # Correctly access dictionary values
                    movie_title = screening["MovieTitle"]
                    room_name = screening["RoomName"]
                    time_str = screening["ScreeningTime"]
                    date_str = screening["ScreeningDate"]
                    occupancy = screening["OccupancyRate"]
                    
                    # Format the label
                    label = f"{movie_title}\n{room_name} ({str(time_str)[:5]})"
                    labels.append(label)
                    occupancy_rates.append(float(occupancy))
                    
                # Reverse lists to show oldest first
                labels.reverse()
                occupancy_rates.reverse()
                
                # If we have more than 6 screenings, limit to 6 for readability
                if len(labels) > 6:
                    labels = labels[:6]
                    occupancy_rates = occupancy_rates[:6]
                
                # Create bar chart
                bars = self.occupancy_ax.bar(range(len(labels)), occupancy_rates, color='cornflowerblue')
                
                # Set title to reflect filters
                title = 'Theater Occupancy'
                if selected_room != 'All Rooms':
                    title += f" - {selected_room}"
                if selected_movie != 'All Movies':
                    title += f" - {selected_movie}"
                self.occupancy_ax.set_title(f'{title} (%)')
                
                self.occupancy_ax.set_ylim(0, 100)
                
                # Fix for the warning - set ticks before ticklabels
                self.occupancy_ax.set_xticks(range(len(labels)))
                self.occupancy_ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
                
                # Add occupancy rate values on top of bars
                for bar in bars:
                    height = bar.get_height()
                    self.occupancy_ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                                          f'{height:.1f}%', ha='center', va='bottom')
                
                # Add a horizontal line at 70% capacity (industry target)
                self.occupancy_ax.axhline(y=70, color='red', linestyle='--', alpha=0.7)
                self.occupancy_ax.text(len(labels)-1, 71, 'Target (70%)', color='red', ha='right')
                
                # Add grid lines for better readability
                self.occupancy_ax.yaxis.grid(True, linestyle='--', alpha=0.3)
            else:
                # Display a message when no data is available
                self.occupancy_ax.text(0.5, 0.5, 'No occupancy data available for the selected filters',
                                      ha='center', va='center', fontsize=12)
                self.occupancy_ax.set_xticks([])
                self.occupancy_ax.set_yticks([])
        except Exception as e:
            print(f"Error loading occupancy data: {e}")
            # Display error message in chart
            self.occupancy_ax.clear()
            self.occupancy_ax.text(0.5, 0.5, f'Error loading data:\n{str(e)}',
                                  ha='center', va='center', fontsize=10, color='red')
            self.occupancy_ax.set_xticks([])
            self.occupancy_ax.set_yticks([])
        
        # Adjust layout to prevent label cutoff
        self.occupancy_ax.figure.tight_layout()
        self.occupancy_ax.figure.canvas.draw()
        
        # Draw the chart
        self.occupancy_canvas.draw()
    
    def update_revenue_chart(self):
        # Get date range selection
        date_range = self.date_range_var.get()
        selected_date = self.revenue_date_picker.get_date()
        
        try:
            # Clear previous data
            self.revenue_ax.clear()
            
            if date_range == "day":
                # Get revenue for a single day
                daily_revenue = self.report_model.get_daily_revenue(selected_date)
                
                if daily_revenue:
                    days = [selected_date.strftime('%Y-%m-%d')]
                    revenue_data = [float(daily_revenue)]
                    
                    # Create bar chart for single day
                    self.revenue_ax.bar(days, revenue_data, color='green')
                    self.revenue_ax.set_title(f'Revenue for {selected_date}')
                    self.revenue_ax.set_ylabel('Revenue ($)')
                    self.revenue_ax.set_ylim(bottom=0)  # Ensure y-axis starts at 0
                else:
                    # No revenue data for selected day
                    self.revenue_ax.text(0.5, 0.5, f'No revenue data available for {selected_date}',
                                       ha='center', va='center', fontsize=12)
                    self.revenue_ax.set_xticks([])
                    self.revenue_ax.set_yticks([])
            else:
                # Get revenue for the last 7 days
                today = datetime.date.today()
                days = []
                revenue_data = []
                has_data = False
                
                # Get revenue for the last 7 days
                for i in range(6, -1, -1):
                    date = today - datetime.timedelta(days=i)
                    days.append(date.strftime('%a'))  # Day abbreviation
                    daily_revenue = self.report_model.get_daily_revenue(date)
                    amount = float(daily_revenue) if daily_revenue else 0
                    revenue_data.append(amount)
                    if amount > 0:
                        has_data = True
                
                if has_data:
                    # Create line chart for weekly data
                    self.revenue_ax.plot(range(len(days)), revenue_data, marker='o', 
                                       linestyle='-', linewidth=2, color='green')
                    self.revenue_ax.set_title('Weekly Revenue ($)')
                    self.revenue_ax.set_xticks(range(len(days)))
                    self.revenue_ax.set_xticklabels(days)
                    self.revenue_ax.set_ylabel('Revenue ($)')
                    self.revenue_ax.yaxis.grid(True, linestyle='--', alpha=0.7)
                else:
                    # No revenue data for the week
                    self.revenue_ax.text(0.5, 0.5, 'No revenue data available for the past week',
                                       ha='center', va='center', fontsize=12)
                    self.revenue_ax.set_xticks([])
                    self.revenue_ax.set_yticks([])
                
        except Exception as e:
            print(f"Error loading revenue data: {e}")
            # Display error message in chart
            self.revenue_ax.clear()
            self.revenue_ax.text(0.5, 0.5, f'Error loading data:\n{str(e)}',
                               ha='center', va='center', fontsize=10, color='red')
            self.revenue_ax.set_xticks([])
            self.revenue_ax.set_yticks([])
        
        # Draw the chart
        self.revenue_canvas.draw()

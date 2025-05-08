import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from tkcalendar import DateEntry
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.report_model import ReportModel
from models.movie_model import MovieModel

class ReportsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.report_model = ReportModel()
        self.movie_model = MovieModel()
        
        # Create tabs for different reports
        self.create_widgets()
        
        # Load initial data
        self.refresh_data()
        
    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.revenue_tab = tk.Frame(self.notebook)
        self.occupancy_tab = tk.Frame(self.notebook)
        self.movies_tab = tk.Frame(self.notebook)
        
        self.notebook.add(self.revenue_tab, text="Revenue")
        self.notebook.add(self.occupancy_tab, text="Occupancy")
        self.notebook.add(self.movies_tab, text="Popular Movies")
        
        # Set up each tab
        self.setup_revenue_tab()
        self.setup_occupancy_tab()
        self.setup_popular_movies_tab()
        
    def setup_revenue_tab(self):
        # Date selection frame
        date_frame = tk.Frame(self.revenue_tab)
        date_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(date_frame, text="Select Date:").pack(side="left", padx=5, pady=5)
        self.revenue_date_picker = DateEntry(date_frame, width=12, background='darkblue',
                                          foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.revenue_date_picker.pack(side="left", padx=5, pady=5)
        self.revenue_date_picker.set_date(datetime.date.today())
        
        generate_button = tk.Button(date_frame, text="Generate Report", command=self.generate_revenue_report)
        generate_button.pack(side="left", padx=5, pady=5)
        
        # Add manual refresh button
        manual_refresh_btn = tk.Button(date_frame, text="↻ FORCE REFRESH", 
                                     bg="lightblue", font=("Helvetica", 10, "bold"),
                                     command=self.force_refresh_revenue)
        manual_refresh_btn.pack(side="left", padx=5, pady=5)
        
        # Revenue display frame
        revenue_display_frame = tk.Frame(self.revenue_tab)
        revenue_display_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Revenue label
        self.revenue_label = tk.Label(revenue_display_frame, text="", font=("Helvetica", 16))
        self.revenue_label.pack(pady=20)
        
        # Revenue by screening
        tk.Label(revenue_display_frame, text="Screenings for selected date:").pack(anchor="w")
        
        # Create treeview
        self.revenue_tree = ttk.Treeview(revenue_display_frame, columns=("ID", "Movie", "Time", "Tickets", "Revenue"), 
                                       show="headings", height=10)
        self.revenue_tree.heading("ID", text="ID")
        self.revenue_tree.heading("Movie", text="Movie")
        self.revenue_tree.heading("Time", text="Time")
        self.revenue_tree.heading("Tickets", text="Tickets Sold")
        self.revenue_tree.heading("Revenue", text="Revenue")
        
        self.revenue_tree.column("ID", width=50, anchor="center")
        self.revenue_tree.column("Movie", width=200)
        self.revenue_tree.column("Time", width=100, anchor="center")
        self.revenue_tree.column("Tickets", width=100, anchor="center")
        self.revenue_tree.column("Revenue", width=100, anchor="center")
        
        self.revenue_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
    def force_refresh_revenue(self):
        """Force refresh of revenue data directly from database"""
        print("Manual refresh triggered in Revenue tab")
        
        # Force database refresh
        selected_date = self.revenue_date_picker.get_date()
        
        # Use direct SQL query for revenue
        daily_revenue = 0.0
        try:
            # Connect directly to database if possible
            if hasattr(self.report_model, 'db'):
                result = self.report_model.db.execute_query(
                    "SELECT fn_total_revenue_by_date(%s) AS Revenue",
                    [selected_date]
                )
                if result and len(result) > 0:
                    daily_revenue = float(result[0]["Revenue"] or 0)
        except Exception as e:
            print(f"Error getting revenue: {e}")
            # Fallback to model
            daily_revenue = self.report_model.get_daily_revenue(selected_date)
        
        self.revenue_label.config(text=f"Total Revenue for {selected_date}: ${daily_revenue:.2f}")
        
        # Generate the full report
        self.generate_revenue_report()
        
    def setup_occupancy_tab(self):
        # Frame for occupancy data
        occupancy_frame = tk.Frame(self.occupancy_tab)
        occupancy_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create treeview for occupancy data
        self.occupancy_tree = ttk.Treeview(occupancy_frame, 
                                         columns=("ID", "Movie", "Room", "Date", "Time", "Occupancy"), 
                                         show="headings", height=10)
        self.occupancy_tree.heading("ID", text="ID")
        self.occupancy_tree.heading("Movie", text="Movie")
        self.occupancy_tree.heading("Room", text="Room")
        self.occupancy_tree.heading("Date", text="Date")
        self.occupancy_tree.heading("Time", text="Time")
        self.occupancy_tree.heading("Occupancy", text="Occupancy Rate")
        
        self.occupancy_tree.column("ID", width=50, anchor="center")
        self.occupancy_tree.column("Movie", width=180)
        self.occupancy_tree.column("Room", width=100)
        self.occupancy_tree.column("Date", width=100, anchor="center")
        self.occupancy_tree.column("Time", width=100, anchor="center")
        self.occupancy_tree.column("Occupancy", width=120, anchor="center")
        
        self.occupancy_tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(occupancy_frame, orient="vertical", command=self.occupancy_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.occupancy_tree.configure(yscrollcommand=scrollbar.set)
        
        # Frame for chart
        self.chart_frame = tk.Frame(self.occupancy_tab)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
    def setup_popular_movies_tab(self):
        # Frame for popular movies
        movies_frame = tk.Frame(self.movies_tab)
        movies_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create treeview for movie data
        self.movies_tree = ttk.Treeview(movies_frame, 
                                      columns=("ID", "Title", "Tickets"), 
                                      show="headings", height=10)
        self.movies_tree.heading("ID", text="ID")
        self.movies_tree.heading("Title", text="Movie Title")
        self.movies_tree.heading("Tickets", text="Tickets Sold")
        
        self.movies_tree.column("ID", width=50, anchor="center")
        self.movies_tree.column("Title", width=250)
        self.movies_tree.column("Tickets", width=100, anchor="center")
        
        self.movies_tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(movies_frame, orient="vertical", command=self.movies_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.movies_tree.configure(yscrollcommand=scrollbar.set)
        
        # Frame for chart
        self.movies_chart_frame = tk.Frame(self.movies_tab)
        self.movies_chart_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
    def refresh_data(self):
        # Load data for each tab
        self.generate_revenue_report()
        self.load_occupancy_data()
        self.load_popular_movies()
        
        # Schedule automatic refresh every 60 seconds if needed
        if hasattr(self, 'auto_refresh') and self.auto_refresh:
            self.after(60000, self.refresh_data)
        
    def generate_revenue_report(self):
        # First, explicitly clear any database connection caches
        self.report_model.db.connection.commit()  # Commit any pending transactions
        
        selected_date = self.revenue_date_picker.get_date()
        
        # Get daily revenue - force direct database query
        query = "SELECT fn_total_revenue_by_date(%s) AS Revenue"
        result = self.report_model.db.execute_query(query, [selected_date])
        daily_revenue = float(result[0]["Revenue"]) if result and result[0]["Revenue"] else 0.0
        
        self.revenue_label.config(text=f"Total Revenue for {selected_date}: ${daily_revenue:.2f}")
        
        # Clear existing data
        for i in self.revenue_tree.get_children():
            self.revenue_tree.delete(i)
            
        # Use direct query for fresh data
        screening_query = """
            SELECT 
                s.ScreeningID,
                m.MovieTitle,
                s.ScreeningTime,
                (SELECT COUNT(*) FROM Tickets t WHERE t.ScreeningID = s.ScreeningID) AS TicketCount,
                (SELECT COUNT(*) FROM Tickets t WHERE t.ScreeningID = s.ScreeningID) * 10.00 AS Revenue
            FROM Screenings s
            JOIN Movies m ON s.MovieID = m.MovieID
            WHERE s.ScreeningDate = %s
        """
        screenings = self.report_model.db.execute_query(screening_query, [selected_date])
        
        # Populate treeview with fresh data
        for screening in screenings:
            self.revenue_tree.insert("", "end", values=(
                screening["ScreeningID"],
                screening["MovieTitle"],
                screening["ScreeningTime"],
                screening["TicketCount"],
                f"${screening['Revenue']:.2f}"
            ))
        
    def load_occupancy_data(self):
        # Clear existing data
        for i in self.occupancy_tree.get_children():
            self.occupancy_tree.delete(i)
            
        # Load occupancy rates for screenings
        occupancy_rates = self.report_model.get_occupancy_rates()
        
        # Data for chart
        movie_names = []
        occupancy_values = []
        
        for data in occupancy_rates:
            self.occupancy_tree.insert("", "end", values=(
                data["ScreeningID"],
                data["MovieTitle"],
                data["RoomName"],
                data["ScreeningDate"],
                data["ScreeningTime"],
                f"{float(data['OccupancyRate']):.2f}%"
            ))
            
            # Collect data for chart (limit to first 10 for readability)
            if len(movie_names) < 10:
                movie_names.append(f"{data['MovieTitle']} ({data['ScreeningDate']})")
                occupancy_values.append(float(data['OccupancyRate']))
        
        # Create chart
        self.create_occupancy_chart(movie_names, occupancy_values)
        
    def create_occupancy_chart(self, labels, values):
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        if not labels:
            return
        
        # Create figure and axes
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create bar chart
        bars = ax.bar(labels, values, color='skyblue')
        
        # Add title and labels
        ax.set_title('Occupancy Rates by Screening')
        ax.set_ylabel('Occupancy Rate (%)')
        ax.set_xticks(range(len(labels)))  # Set the positions of ticks first
        ax.set_xticklabels(labels, rotation=45, ha='right')  # Then set the labels
        
        # Add a horizontal line at 80% capacity
        ax.axhline(y=80, color='r', linestyle='-', label='80% Target')
        
        # Add data labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                  f'{height:.1f}%', ha='center', va='bottom')
        
        # Add legend
        ax.legend()
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def load_popular_movies(self):
        # Clear existing data
        for i in self.movies_tree.get_children():
            self.movies_tree.delete(i)
            
        # Load popular movies
        popular_movies = self.report_model.get_popular_movies()
        
        # Data for chart
        movie_names = []
        ticket_counts = []
        
        for movie in popular_movies:
            self.movies_tree.insert("", "end", values=(
                movie["MovieID"],
                movie["MovieTitle"],
                movie["TicketCount"]
            ))
            
            # Collect data for chart (limit to top 5 for readability)
            if len(movie_names) < 5:
                movie_names.append(movie["MovieTitle"])
                ticket_counts.append(movie["TicketCount"])
        
        # Create chart
        self.create_movies_chart(movie_names, ticket_counts)
        
    def create_movies_chart(self, labels, values):
        # Clear previous chart
        for widget in self.movies_chart_frame.winfo_children():
            widget.destroy()
        
        if not labels:
            return
        
        # Create figure and axes
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create pie chart
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, shadow=True)
        
        # Add title
        ax.set_title('Ticket Sales by Movie')
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.movies_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

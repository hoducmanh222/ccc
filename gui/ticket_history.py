import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.ticket_model import TicketModel

class TicketHistoryFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.ticket_model = TicketModel()
        
        # Create UI elements
        self.create_widgets()
        
        # Load initial data
        self.refresh_data()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(self, text="Ticket History", font=("Helvetica", 16))
        title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")
        
        # Add a PROMINENT manual refresh button at the top
        self.manual_refresh_btn = tk.Button(self, text="↻ REFRESH DATA", 
                                         bg="lightblue", font=("Helvetica", 12, "bold"),
                                         command=self.force_refresh)
        self.manual_refresh_btn.grid(row=0, column=1, pady=10, padx=10, sticky="e")
        
        # Filter panel
        filter_frame = ttk.LabelFrame(self, text="Filters")
        filter_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        ttk.Label(filter_frame, text="Status:").grid(row=0, column=0, padx=5, pady=5)
        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_var, 
                                   values=["All", "Active", "Cancelled"], width=15)
        status_combo.grid(row=0, column=1, padx=5, pady=5)
        
        apply_button = ttk.Button(filter_frame, text="Apply Filters", command=self.refresh_data)
        apply_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Tickets List
        self.ticket_tree = ttk.Treeview(self, columns=("ID", "Movie", "Date", "Time", "Seat", "Status"), 
                                      show="headings", height=15)
        self.ticket_tree.heading("ID", text="Ticket ID")
        self.ticket_tree.heading("Movie", text="Movie")
        self.ticket_tree.heading("Date", text="Date")
        self.ticket_tree.heading("Time", text="Time")
        self.ticket_tree.heading("Seat", text="Seat")
        self.ticket_tree.heading("Status", text="Status")
        
        self.ticket_tree.column("ID", width=70, anchor="center")
        self.ticket_tree.column("Movie", width=200)
        self.ticket_tree.column("Date", width=100, anchor="center")
        self.ticket_tree.column("Time", width=100, anchor="center")
        self.ticket_tree.column("Seat", width=70, anchor="center")
        self.ticket_tree.column("Status", width=100, anchor="center")
        
        self.ticket_tree.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        # Add scrollbar to treeview
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.ticket_tree.yview)
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.ticket_tree.configure(yscrollcommand=scrollbar.set)
        
        # Actions Frame
        actions_frame = ttk.LabelFrame(self, text="Actions")
        actions_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        self.cancel_button = ttk.Button(actions_frame, text="Cancel Ticket", 
                                       command=self.cancel_ticket)
        self.cancel_button.pack(side="left", padx=5, pady=5)
        
        self.refresh_button = ttk.Button(actions_frame, text="Refresh", 
                                        command=self.refresh_data)
        self.refresh_button.pack(side="left", padx=5, pady=5)
        
        # Audit Log Frame
        log_frame = ttk.LabelFrame(self, text="Ticket Audit Log")
        log_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        
        self.log_tree = ttk.Treeview(log_frame, columns=("ID", "Operation", "Screening", "Seat", "User", "Timestamp"), 
                                    show="headings", height=5)
        self.log_tree.heading("ID", text="ID")
        self.log_tree.heading("Operation", text="Operation")
        self.log_tree.heading("Screening", text="Screening ID")
        self.log_tree.heading("Seat", text="Seat")
        self.log_tree.heading("User", text="User")
        self.log_tree.heading("Timestamp", text="Timestamp")
        
        self.log_tree.column("ID", width=50, anchor="center")
        self.log_tree.column("Operation", width=100)
        self.log_tree.column("Screening", width=100, anchor="center")
        self.log_tree.column("Seat", width=70, anchor="center")
        self.log_tree.column("User", width=150)
        self.log_tree.column("Timestamp", width=150, anchor="center")
        
        self.log_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_tree.yview)
        log_scrollbar.pack(side="right", fill="y")
        self.log_tree.configure(yscrollcommand=log_scrollbar.set)
        
        # Configure grid weights
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Bind treeview selection
        self.ticket_tree.bind("<<TreeviewSelect>>", self.on_ticket_select)
        
    def refresh_data(self):
        """Refresh all data in the ticket history view"""
        # Clear existing data
        for i in self.ticket_tree.get_children():
            self.ticket_tree.delete(i)
        
        # Get status filter
        status_filter = self.status_var.get()
        
        # Fetch tickets
        tickets = self.ticket_model.get_user_tickets(status_filter)
        
        # Populate treeview
        if tickets:
            for ticket in tickets:
                ticket_id = ticket["TicketID"]
                movie_title = ticket["MovieTitle"]
                date = ticket["ScreeningDate"]
                time = ticket["ScreeningTime"]
                seat = ticket["SeatNumber"]
                status = ticket["Status"]  # This now comes directly from the query
                
                self.ticket_tree.insert("", "end", values=(
                    ticket_id, movie_title, date, time, seat, status
                ))
        
        # Load audit log data
        self.refresh_audit_log()
        
    def refresh_audit_log(self):
        """Refresh the audit log data"""
        # Clear existing log data
        for i in self.log_tree.get_children():
            self.log_tree.delete(i)
        
        # Fetch audit log entries
        logs = self.ticket_model.get_booking_audit()
        
        # Populate log treeview
        if logs:
            for log in logs:
                self.log_tree.insert("", "end", values=(
                    log["AuditID"],
                    log["OperationType"],
                    log["AffectedScreeningID"],
                    log["AffectedSeat"],
                    log["UserID"],  # Should show the username properly now
                    log["Timestamp"]
                ))
        
    def on_ticket_select(self, event):
        selected_items = self.ticket_tree.selection()
        if not selected_items:
            return
        
        # Get the selected ticket status
        status = self.ticket_tree.item(selected_items[0])["values"][5]
        
        # Disable cancel button if ticket is already cancelled
        if status == "Cancelled":
            self.cancel_button["state"] = "disabled"
        else:
            self.cancel_button["state"] = "normal"
    
    def cancel_ticket(self):
        selected_items = self.ticket_tree.selection()
        if not selected_items:
            messagebox.showinfo("Select Ticket", "Please select a ticket to cancel.")
            return
            
        ticket_id = self.ticket_tree.item(selected_items[0])["values"][0]
        status = self.ticket_tree.item(selected_items[0])["values"][5]
        
        # Check if ticket is already cancelled
        if status == "Cancelled":
            messagebox.showinfo("Info", "This ticket is already cancelled.")
            return
        
        # Confirm cancellation
        if messagebox.askyesno("Confirm Cancellation", "Are you sure you want to cancel this ticket?"):
            # Pass user info to the cancel_ticket method
            success = self.ticket_model.cancel_ticket(
                ticket_id, 
                user_id=getattr(self.controller, 'user_id', None),
                username=getattr(self.controller, 'username', None)
            )
            if success:
                messagebox.showinfo("Success", "Ticket cancelled successfully.")
                
                # DIRECT APPROACH: Force complete refresh of EVERYTHING
                if hasattr(self.controller, 'force_refresh_all'):
                    print("Forcing complete refresh after cancellation")
                    self.controller.force_refresh_all()
                else:
                    # Fallback to manually refreshing current view
                    self.refresh_data()
            else:
                messagebox.showerror("Error", "Failed to cancel ticket.")
    
    def force_refresh(self):
        """Force refresh all data directly from database"""
        print("Manual refresh triggered in TicketHistory")
        
        # Clear any existing data first
        for i in self.ticket_tree.get_children():
            self.ticket_tree.delete(i)
        
        for i in self.log_tree.get_children():
            self.log_tree.delete(i)
        
        # Force fetch fresh data
        status_filter = self.status_var.get()
        tickets = self.ticket_model.get_user_tickets(status_filter)
        logs = self.ticket_model.get_booking_audit()
        
        print(f"Retrieved {len(tickets)} tickets and {len(logs)} audit entries")
        
        # Populate the trees
        self.populate_ticket_tree(tickets)
        self.populate_audit_tree(logs)
    
    def populate_ticket_tree(self, tickets):
        """Helper to populate the ticket tree with data"""
        if tickets:
            for ticket in tickets:
                ticket_id = ticket["TicketID"]
                movie_title = ticket["MovieTitle"]
                date = ticket["ScreeningDate"]
                time = ticket["ScreeningTime"]
                seat = ticket["SeatNumber"]
                status = ticket.get("Status", "Active")
                
                self.ticket_tree.insert("", "end", values=(
                    ticket_id, movie_title, date, time, seat, status
                ))
    
    def populate_audit_tree(self, logs):
        """Helper to populate the audit log tree with data"""
        if logs:
            for log in logs:
                self.log_tree.insert("", "end", values=(
                    log["AuditID"],
                    log["OperationType"],
                    log["AffectedScreeningID"],
                    log["AffectedSeat"],
                    log["UserID"],
                    log["Timestamp"]
                ))

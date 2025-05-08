import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.feedback_model import FeedbackModel
from models.movie_model import MovieModel
from models.customer_model import CustomerModel

class FeedbackManagementFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.feedback_model = FeedbackModel()
        self.movie_model = MovieModel()
        self.customer_model = CustomerModel()
        
        # Create UI elements
        self.create_widgets()
        
        # Load data
        self.refresh_data()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(self, text="Feedback Management", font=("Helvetica", 16))
        title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")
        
        # Left panel - Feedback list
        feedback_frame = tk.Frame(self)
        feedback_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        # Filter options
        filter_frame = tk.LabelFrame(feedback_frame, text="Filter")
        filter_frame.pack(fill="x", padx=5, pady=5)
        
        # Movie filter
        tk.Label(filter_frame, text="Movie:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.movie_var = tk.StringVar()
        self.movie_combo = ttk.Combobox(filter_frame, textvariable=self.movie_var, width=25)
        self.movie_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.movie_combo.bind("<<ComboboxSelected>>", self.filter_feedback)
        
        # Customer filter
        tk.Label(filter_frame, text="Customer:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(filter_frame, textvariable=self.customer_var, width=25)
        self.customer_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.customer_combo.bind("<<ComboboxSelected>>", self.filter_feedback)
        
        # Clear filter button
        clear_button = tk.Button(filter_frame, text="Clear Filters", command=self.clear_filters)
        clear_button.grid(row=0, column=2, rowspan=2, padx=5, pady=5)
        
        # Feedback list
        self.feedback_tree = ttk.Treeview(feedback_frame, 
                                          columns=("ID", "Customer", "Movie", "Rating", "Date"), 
                                          show="headings", height=15)
        self.feedback_tree.heading("ID", text="ID")
        self.feedback_tree.heading("Customer", text="Customer")
        self.feedback_tree.heading("Movie", text="Movie")
        self.feedback_tree.heading("Rating", text="Rating")
        self.feedback_tree.heading("Date", text="Date")
        
        self.feedback_tree.column("ID", width=50, anchor="center")
        self.feedback_tree.column("Customer", width=150)
        self.feedback_tree.column("Movie", width=200)
        self.feedback_tree.column("Rating", width=70, anchor="center")
        self.feedback_tree.column("Date", width=100, anchor="center")
        
        self.feedback_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add scrollbar to treeview
        tree_scroll = ttk.Scrollbar(feedback_frame, orient="vertical", command=self.feedback_tree.yview)
        tree_scroll.pack(side="right", fill="y")
        self.feedback_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.feedback_tree.bind("<<TreeviewSelect>>", self.on_feedback_select)
        
        # Right panel - Feedback details
        details_frame = tk.LabelFrame(self, text="Feedback Details")
        details_frame.grid(row=1, column=1, padx=10, pady=5, sticky="n")
        
        # Feedback form
        tk.Label(details_frame, text="Customer:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.detail_customer_var = tk.StringVar()
        self.customer_entry = ttk.Combobox(details_frame, textvariable=self.detail_customer_var, width=25)
        self.customer_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(details_frame, text="Movie:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.detail_movie_var = tk.StringVar()
        self.movie_entry = ttk.Combobox(details_frame, textvariable=self.detail_movie_var, width=25)
        self.movie_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(details_frame, text="Rating (1-5):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.rating_var = tk.IntVar(value=5)
        rating_frame = tk.Frame(details_frame)
        rating_frame.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Create rating as radio buttons with stars
        for i in range(1, 6):
            rb = tk.Radiobutton(rating_frame, text="★", variable=self.rating_var, value=i, 
                               indicatoron=0, selectcolor="gold", width=2)
            rb.pack(side="left")
        
        tk.Label(details_frame, text="Comment:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.comment_text = tk.Text(details_frame, width=30, height=5)
        self.comment_text.grid(row=3, column=1, padx=5, pady=5)
        
        # Buttons frame
        button_frame = tk.Frame(details_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.new_button = tk.Button(button_frame, text="New", command=self.clear_form)
        self.new_button.grid(row=0, column=0, padx=5)
        
        self.save_button = tk.Button(button_frame, text="Save", command=self.save_feedback)
        self.save_button.grid(row=0, column=1, padx=5)
        
        self.delete_button = tk.Button(button_frame, text="Delete", command=self.delete_feedback)
        self.delete_button.grid(row=0, column=2, padx=5)
        
        # Configure grid weights
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
    def refresh_data(self):
        # Clear existing data
        for i in self.feedback_tree.get_children():
            self.feedback_tree.delete(i)
            
        # Load feedback
        all_feedback = self.feedback_model.get_all_feedback()
        for feedback in all_feedback:
            self.feedback_tree.insert("", "end", values=(
                feedback["FeedbackID"],
                feedback["CustomerName"],
                feedback["MovieTitle"],
                "★" * feedback["Rating"],
                feedback["FeedbackDate"]
            ))
        
        # Load movies for dropdown
        movies = self.movie_model.get_all_movies()
        self.movie_combo["values"] = ["All"] + [movie["MovieTitle"] for movie in movies]
        self.movie_entry["values"] = [movie["MovieTitle"] for movie in movies]
        self.movies_data = {movie["MovieTitle"]: movie["MovieID"] for movie in movies}
        
        # Load customers for dropdown
        customers = self.customer_model.get_all_customers()
        self.customer_combo["values"] = ["All"] + [customer["CustomerName"] for customer in customers]
        self.customer_entry["values"] = [customer["CustomerName"] for customer in customers]
        self.customers_data = {customer["CustomerName"]: customer["CustomerID"] for customer in customers}
        
        # Clear form
        self.clear_form()
        
    def filter_feedback(self, event=None):
        # Clear existing data
        for i in self.feedback_tree.get_children():
            self.feedback_tree.delete(i)
            
        movie_filter = self.movie_var.get()
        customer_filter = self.customer_var.get()
        
        # Get filtered feedback
        if movie_filter != "All" and movie_filter in self.movies_data:
            movie_id = self.movies_data[movie_filter]
            feedback_list = self.feedback_model.get_feedback_by_movie(movie_id)
        elif customer_filter != "All" and customer_filter in self.customers_data:
            customer_id = self.customers_data[customer_filter]
            feedback_list = self.feedback_model.get_feedback_by_customer(customer_id)
        else:
            feedback_list = self.feedback_model.get_all_feedback()
            
        # Populate tree
        for feedback in feedback_list:
            customer_name = feedback.get("CustomerName", "")
            movie_title = feedback.get("MovieTitle", "")
            
            self.feedback_tree.insert("", "end", values=(
                feedback["FeedbackID"],
                customer_name,
                movie_title,
                "★" * feedback["Rating"],
                feedback["FeedbackDate"]
            ))
            
    def clear_filters(self):
        self.movie_var.set("All")
        self.customer_var.set("All")
        self.refresh_data()
        
    def on_feedback_select(self, event):
        selected_items = self.feedback_tree.selection()
        if not selected_items:
            return
            
        # Get the selected feedback ID
        feedback_id = self.feedback_tree.item(selected_items[0])["values"][0]
        
        # Get all feedback details
        all_feedback = self.feedback_model.get_all_feedback()
        selected_feedback = None
        
        for feedback in all_feedback:
            if feedback["FeedbackID"] == feedback_id:
                selected_feedback = feedback
                break
                
        if selected_feedback:
            self.detail_customer_var.set(selected_feedback["CustomerName"])
            self.detail_movie_var.set(selected_feedback["MovieTitle"])
            self.rating_var.set(selected_feedback["Rating"])
            
            # Clear and set comment text
            self.comment_text.delete(1.0, tk.END)
            self.comment_text.insert(tk.END, selected_feedback["Comment"] if selected_feedback["Comment"] else "")
            
            self.current_id = feedback_id
        
    def clear_form(self):
        self.detail_customer_var.set("")
        self.detail_movie_var.set("")
        self.rating_var.set(5)
        self.comment_text.delete(1.0, tk.END)
        self.current_id = None
        
    def save_feedback(self):
        # Validate inputs
        customer_name = self.detail_customer_var.get().strip()
        movie_title = self.detail_movie_var.get().strip()
        rating = self.rating_var.get()
        comment = self.comment_text.get(1.0, tk.END).strip()
        
        if not customer_name:
            messagebox.showerror("Validation Error", "Please select a customer")
            return
            
        if not movie_title:
            messagebox.showerror("Validation Error", "Please select a movie")
            return
            
        if rating < 1 or rating > 5:
            messagebox.showerror("Validation Error", "Rating must be between 1 and 5")
            return
            
        if customer_name not in self.customers_data:
            messagebox.showerror("Validation Error", "Invalid customer selected")
            return
            
        if movie_title not in self.movies_data:
            messagebox.showerror("Validation Error", "Invalid movie selected")
            return
            
        customer_id = self.customers_data[customer_name]
        movie_id = self.movies_data[movie_title]
        
        # Save or update feedback
        if self.current_id:
            self.feedback_model.update_feedback(self.current_id, rating, comment)
            messagebox.showinfo("Success", "Feedback updated successfully")
        else:
            self.feedback_model.add_feedback(customer_id, movie_id, rating, comment)
            messagebox.showinfo("Success", "Feedback added successfully")
            
        # Refresh the data
        self.refresh_data()
        
        # Refresh related frames (especially movie management for ratings)
        if hasattr(self.controller, 'frames'):
            for frame_class, frame in self.controller.frames.items():
                if frame.__class__.__name__ == "MovieManagementFrame" and frame != self:
                    if hasattr(frame, 'refresh_data'):
                        frame.refresh_data()
                        
        # Update dashboard if available
        if hasattr(self.controller, 'update_dashboard'):
            self.controller.update_dashboard()
        
    def delete_feedback(self):
        if not self.current_id:
            messagebox.showinfo("Info", "Please select a feedback to delete")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this feedback?"):
            self.feedback_model.delete_feedback(self.current_id)
            messagebox.showinfo("Success", "Feedback deleted successfully")
            self.refresh_data()

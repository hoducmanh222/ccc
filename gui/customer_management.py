import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.customer_model import CustomerModel

class CustomerManagementFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.customer_model = CustomerModel()
        
        # Create UI elements
        self.create_widgets()
        
        # Load data
        self.refresh_data()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(self, text="Customer Management", font=("Helvetica", 16))
        title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")
        
        # Customer list
        self.customer_tree = ttk.Treeview(self, columns=("ID", "Name", "Phone"), 
                                          show="headings", height=15)
        self.customer_tree.heading("ID", text="ID")
        self.customer_tree.heading("Name", text="Customer Name")
        self.customer_tree.heading("Phone", text="Phone Number")
        
        self.customer_tree.column("ID", width=50, anchor="center")
        self.customer_tree.column("Name", width=250)
        self.customer_tree.column("Phone", width=150, anchor="center")
        
        self.customer_tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Add scrollbar to treeview
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.customer_tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.customer_tree.configure(yscrollcommand=scrollbar.set)
        
        # Frame for customer details
        details_frame = tk.LabelFrame(self, text="Customer Details")
        details_frame.grid(row=1, column=2, padx=10, pady=10, sticky="n")
        
        # Customer form
        tk.Label(details_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_var = tk.StringVar()
        tk.Entry(details_frame, textvariable=self.name_var, width=25).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(details_frame, text="Phone:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.phone_var = tk.StringVar()
        tk.Entry(details_frame, textvariable=self.phone_var, width=25).grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons frame
        button_frame = tk.Frame(details_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.new_button = tk.Button(button_frame, text="New", command=self.clear_form)
        self.new_button.grid(row=0, column=0, padx=5)
        
        self.save_button = tk.Button(button_frame, text="Save", command=self.save_customer)
        self.save_button.grid(row=0, column=1, padx=5)
        
        self.delete_button = tk.Button(button_frame, text="Delete", command=self.delete_customer)
        self.delete_button.grid(row=0, column=2, padx=5)
        
        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Bind treeview selection
        self.customer_tree.bind("<<TreeviewSelect>>", self.on_customer_select)
        
    def refresh_data(self):
        # Clear existing data
        for i in self.customer_tree.get_children():
            self.customer_tree.delete(i)
            
        # Load customers
        customers = self.customer_model.get_all_customers()
        for customer in customers:
            self.customer_tree.insert("", "end", values=(
                customer["CustomerID"],
                customer["CustomerName"],
                customer["PhoneNumber"]
            ))
        
        # Clear form
        self.clear_form()
        
    def on_customer_select(self, event):
        selected_items = self.customer_tree.selection()
        if not selected_items:
            return
            
        # Get the selected customer ID
        customer_id = self.customer_tree.item(selected_items[0])["values"][0]
        
        # Get customer details
        customer = self.customer_model.get_customer(customer_id)
        if customer:
            self.name_var.set(customer["CustomerName"])
            self.phone_var.set(customer["PhoneNumber"])
            self.current_id = customer["CustomerID"]
        
    def clear_form(self):
        self.name_var.set("")
        self.phone_var.set("")
        self.current_id = None
        
    def save_customer(self):
        # Validate inputs
        name = self.name_var.get().strip()
        phone = self.phone_var.get().strip()
        
        if not name:
            messagebox.showerror("Validation Error", "Customer name is required")
            return
            
        if not phone:
            messagebox.showerror("Validation Error", "Phone number is required")
            return
        
        # Save or update customer
        if self.current_id:
            self.customer_model.update_customer(self.current_id, name, phone)
            messagebox.showinfo("Success", "Customer updated successfully")
        else:
            self.customer_model.add_customer(name, phone)
            messagebox.showinfo("Success", "Customer added successfully")
            
        # Refresh the data
        self.refresh_data()
        
        # Refresh related frames that might use customer data
        if hasattr(self.controller, 'frames'):
            for frame_name, frame_instance in self.controller.frames.items():
                if hasattr(frame_instance, 'refresh_customer_data'):
                    frame_instance.refresh_customer_data()
                elif hasattr(frame_instance, 'refresh_data') and frame_instance != self:
                    # Check if this is a frame that might need customer data
                    if frame_name.__name__ in ["TicketBookingFrame", "FeedbackManagementFrame"]:
                        frame_instance.refresh_data()
        
    def delete_customer(self):
        if not self.current_id:
            messagebox.showinfo("Info", "Please select a customer to delete")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this customer?"):
            self.customer_model.delete_customer(self.current_id)
            messagebox.showinfo("Success", "Customer deleted successfully")
            self.refresh_data()

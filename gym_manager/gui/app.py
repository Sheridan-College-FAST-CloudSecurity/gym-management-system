import tkinter as tk
from tkinter import ttk, messagebox
from gym_manager.database import init_db, Session, Member
from gym_manager.members import add_member, get_all_members, delete_member
from gym_manager.payments import record_payment, get_payments_by_member
from gym_manager.checkins import log_checkin, get_checkins_by_member
from datetime import datetime

class GymManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gym Management System")
        init_db()
        
        self.create_widgets()
    
    def create_widgets(self):
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)
        
        # Members Tab
        self.member_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.member_frame, text="Members")
        
        # Add Member Form
        ttk.Label(self.member_frame, text="First Name:").grid(row=0, column=0, padx=5, pady=5)
        self.first_name = ttk.Entry(self.member_frame)
        self.first_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.member_frame, text="Last Name:").grid(row=1, column=0, padx=5, pady=5)
        self.last_name = ttk.Entry(self.member_frame)
        self.last_name.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.member_frame, text="Email:").grid(row=2, column=0, padx=5, pady=5)
        self.email = ttk.Entry(self.member_frame)
        self.email.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(self.member_frame, text="Add Member", command=self.add_member).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Member List (Treeview)
        self.member_tree = ttk.Treeview(self.member_frame, columns=("ID", "Name", "Email", "Membership", "Expiry"))
        self.member_tree.heading("#0", text="")
        self.member_tree.heading("ID", text="ID")
        self.member_tree.heading("Name", text="Name")
        self.member_tree.heading("Email", text="Email")
        self.member_tree.heading("Membership", text="Membership")
        self.member_tree.heading("Expiry", text="Expiry")
        self.member_tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        
        # Load initial data
        self.load_members()
    
    def load_members(self):
        # Clear existing data
        for item in self.member_tree.get_children():
            self.member_tree.delete(item)
            
        # Load from database
        members = get_all_members()
        for member in members:
            self.member_tree.insert("", "end", values=(
                member.id,
                f"{member.first_name} {member.last_name}",
                member.email,
                member.membership_type,
                member.expiration_date.strftime('%Y-%m-%d')
            ))
    
    def add_member(self):
        first_name = self.first_name.get()
        last_name = self.last_name.get()
        email = self.email.get()
        
        if not first_name or not last_name or not email:
            messagebox.showerror("Error", "First name, last name, and email are required!")
            return
        
        success, msg = add_member(first_name, last_name, email)
        if success:
            messagebox.showinfo("Success", msg)
            self.load_members()
        else:
            messagebox.showerror("Error", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = GymManagerApp(root)
    root.mainloop()
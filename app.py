import tkinter as tk
from tkinter import simpledialog, messagebox
import hashlib
import json
import os
from datetime import datetime

DATA_FILE = "atm_data.json"

class ATM:
    def __init__(self, root):
        self.root = root
        self.root.title("ATM Machine")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.data = self.load_data()
        self.current_user = None
        self.pin_attempts = 0
        self.max_attempts = 3
        self.create_main_frame()
        self.login_screen()

    def create_main_frame(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill=tk.BOTH)
    
    def switch_screen(self, new_screen):
        for widget in self.frame.winfo_children():
            widget.destroy()
        new_screen()

    def hash_pin(self, pin):
        return hashlib.sha256(pin.encode()).hexdigest()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as file:
                return json.load(file)
        return {}

    def save_data(self):
        with open(DATA_FILE, "w") as file:
            json.dump(self.data, file)
    
    def login_screen(self):
        self.switch_screen(self.build_login_screen)
    
    def build_login_screen(self):
        tk.Label(self.frame, text="Enter PIN to Login", font=("Arial", 14)).pack(pady=10)
        pin = simpledialog.askstring("Login", "Enter your 4-digit PIN:", show='*')
        if pin and pin.isdigit() and len(pin) == 4:
            hashed_pin = self.hash_pin(pin)
            if hashed_pin not in self.data:
                self.data[hashed_pin] = {"balance": 0, "daily_withdrawal": 0, "monthly_withdrawal": 0, "last_reset": ""}
                self.save_data()
                messagebox.showinfo("New User", "New account created!")
            self.current_user = hashed_pin
            self.check_reset_limits()
            self.main_menu()
        else:
            messagebox.showerror("Error", "Invalid PIN. Enter a 4-digit number.")
            self.login_screen()

    def check_reset_limits(self):
        today = datetime.today().strftime('%Y-%m-%d')
        user_data = self.data[self.current_user]
        last_reset = user_data.get("last_reset", "")
        if last_reset and last_reset[:7] != today[:7]:
            user_data["monthly_withdrawal"] = 0
        if last_reset != today:
            user_data["daily_withdrawal"] = 0
        user_data["last_reset"] = today
        self.save_data()

    def main_menu(self):
        self.switch_screen(self.build_main_menu)
    
    def build_main_menu(self):
        tk.Label(self.frame, text="Welcome to the ATM", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.frame, text="Deposit", command=lambda: self.switch_screen(self.deposit)).pack(pady=5)
        tk.Button(self.frame, text="Withdraw", command=lambda: self.switch_screen(self.withdraw)).pack(pady=5)
        tk.Button(self.frame, text="Check Balance", command=lambda: self.switch_screen(self.check_balance)).pack(pady=5)
        tk.Button(self.frame, text="Logout", command=self.login_screen).pack(pady=10)
        tk.Button(self.frame, text="Exit", command=self.root.quit).pack(pady=10)

    def deposit(self):
        amount = simpledialog.askstring("Deposit", "Enter deposit amount:")
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
            self.data[self.current_user]["balance"] += amount
            self.save_data()
            messagebox.showinfo("Success", "Deposit successful!")
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Invalid amount.")
        self.main_menu()

    def withdraw(self):
        amount = simpledialog.askstring("Withdraw", "Enter withdrawal amount:")
        try:
            amount = float(amount)
            user_data = self.data[self.current_user]
            if amount <= 0:
                raise ValueError("Amount must be positive.")
            if amount > user_data["balance"]:
                messagebox.showerror("Error", "Insufficient balance.")
            elif amount > 25000:
                messagebox.showerror("Error", "Exceeds daily withdrawal limit of 25,000.")
            elif user_data["monthly_withdrawal"] + amount > 50000:
                messagebox.showerror("Error", "Exceeds monthly withdrawal limit of 50,000.")
            else:
                user_data["balance"] -= amount
                user_data["daily_withdrawal"] += amount
                user_data["monthly_withdrawal"] += amount
                self.save_data()
                messagebox.showinfo("Success", "Withdrawal successful!")
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Invalid amount.")
        self.main_menu()

    def check_balance(self):
        balance = self.data[self.current_user]["balance"]
        messagebox.showinfo("Balance", f"Your current balance is: {balance}")
        self.main_menu()


def main():
    root = tk.Tk()
    atm = ATM(root)
    root.mainloop()

if __name__ == "__main__":
    main()

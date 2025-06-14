#!/usr/bin/env python3

import os
from pathlib import Path
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from .capital_one_importer import CapitalOneImporter
from .ally_importer import AllyImporter

class ImporterGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bank to Tiller Importer")
        self.root.geometry("700x400")  # Made slightly taller for bank selection
        self.root.resizable(True, False)
        
        # Variables for file paths and bank selection
        self.csv_var = tk.StringVar()
        self.excel_var = tk.StringVar()
        self.bank_var = tk.StringVar(value="CapitalOne")  # Default bank
        
        # Available banks
        self.banks = {
            "CapitalOne": CapitalOneImporter,
            "Ally": AllyImporter
        }
        
        # Current importer instance
        self.importer = self.banks[self.bank_var.get()]()
        
        # Config file path
        self.config_file = os.path.join(os.path.expanduser("~"), ".bank_tiller_config.json")
        
        # Load saved settings
        self.load_settings()
        
        self.create_widgets()
    
    def load_settings(self):
        """Load previously saved file paths from config file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                # Load saved paths and bank
                csv_path = config.get('last_csv_path', '')
                excel_path = config.get('last_excel_path', '')
                saved_bank = config.get('last_bank', 'CapitalOne')
                
                # Set bank if it's still available
                if saved_bank in self.banks:
                    self.bank_var.set(saved_bank)
                    self.importer = self.banks[saved_bank]()
                
                # Set defaults
                downloads_path = str(Path.home() / "Downloads")
                
                # Use saved CSV path if it exists and directory is valid
                if csv_path and os.path.exists(csv_path):
                    self.csv_var.set(csv_path)
                elif csv_path and os.path.exists(os.path.dirname(csv_path)):
                    self.csv_var.set(csv_path)
                else:
                    # Look for common CSV file names in Downloads
                    common_names = ["transactions.csv", "download.csv"]
                    for name in common_names:
                        potential_path = os.path.join(downloads_path, name)
                        if os.path.exists(potential_path):
                            self.csv_var.set(potential_path)
                            break
                    else:
                        self.csv_var.set(os.path.join(downloads_path, "transactions.csv"))
                
                # Use saved Excel path if it exists and is valid
                if excel_path and os.path.exists(excel_path):
                    self.excel_var.set(excel_path)
                else:
                    # Look for Tiller template in common locations
                    common_locations = [
                        os.getcwd(),
                        downloads_path,
                        str(Path.home() / "Documents")
                    ]
                    common_names = [
                        "Tiller-Foundation-Template.xlsx",
                        "tiller.xlsx",
                        "budget.xlsx"
                    ]
                    
                    found = False
                    for location in common_locations:
                        for name in common_names:
                            potential_path = os.path.join(location, name)
                            if os.path.exists(potential_path):
                                self.excel_var.set(potential_path)
                                found = True
                                break
                        if found:
                            break
                    
                    if not found:
                        self.excel_var.set(os.path.join(downloads_path, "Tiller-Foundation-Template.xlsx"))
            
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save current file paths to config file."""
        try:
            config = {
                'last_csv_path': self.csv_var.get(),
                'last_excel_path': self.excel_var.get(),
                'last_bank': self.bank_var.get()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def create_widgets(self):
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Bank CSV to Tiller Excel Importer", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Bank selection
        bank_label = ttk.Label(main_frame, text="Select Bank:", font=('Arial', 11, 'bold'))
        bank_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        bank_combo = ttk.Combobox(main_frame, textvariable=self.bank_var, 
                                 values=list(self.banks.keys()), state='readonly')
        bank_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        bank_combo.bind('<<ComboboxSelected>>', self.on_bank_change)
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                                text="Select your bank CSV file and Tiller Excel spreadsheet to import transactions.",
                                font=('Arial', 10))
        instructions.grid(row=2, column=0, columnspan=3, pady=(0, 15))
        
        # CSV file selection
        csv_label = ttk.Label(main_frame, text="Bank CSV File:", font=('Arial', 11, 'bold'))
        csv_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        csv_entry = ttk.Entry(main_frame, textvariable=self.csv_var, width=60)
        csv_entry.grid(row=3, column=1, padx=(10, 5), pady=5, sticky=(tk.W, tk.E))
        csv_browse = ttk.Button(main_frame, text="Browse...", command=self.browse_csv)
        csv_browse.grid(row=3, column=2, padx=(5, 0), pady=5)
        
        # Excel file selection
        excel_label = ttk.Label(main_frame, text="Tiller Excel File:", font=('Arial', 11, 'bold'))
        excel_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        excel_entry = ttk.Entry(main_frame, textvariable=self.excel_var, width=60)
        excel_entry.grid(row=4, column=1, padx=(10, 5), pady=5, sticky=(tk.W, tk.E))
        excel_browse = ttk.Button(main_frame, text="Browse...", command=self.browse_excel)
        excel_browse.grid(row=4, column=2, padx=(5, 0), pady=5)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=5, column=0, columnspan=3, pady=15, sticky=(tk.W, tk.E))
        
        # File status indicators
        self.csv_status = ttk.Label(status_frame, text="", font=('Arial', 9))
        self.csv_status.grid(row=0, column=0, sticky=tk.W)
        
        self.excel_status = ttk.Label(status_frame, text="", font=('Arial', 9))
        self.excel_status.grid(row=1, column=0, sticky=tk.W)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        # Import button
        import_btn = ttk.Button(button_frame, text="Import Transactions", 
                               command=self.import_transactions)
        import_btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.root.quit)
        cancel_btn.pack(side=tk.LEFT, padx=15)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        status_frame.columnconfigure(0, weight=1)
        
        # Initial status check
        self.update_file_status()
        
        # Bind events to update status
        self.csv_var.trace('w', lambda *args: self.update_file_status())
        self.excel_var.trace('w', lambda *args: self.update_file_status())
    
    def on_bank_change(self, event=None):
        """Handle bank selection change."""
        selected_bank = self.bank_var.get()
        self.importer = self.banks[selected_bank]()
        self.update_file_status()
    
    def update_file_status(self):
        """Update file status indicators."""
        # Check CSV file
        csv_path = self.csv_var.get().strip()
        if csv_path and os.path.exists(csv_path):
            self.csv_status.config(text="✓ CSV file found", foreground="green")
        elif csv_path:
            self.csv_status.config(text="✗ CSV file not found", foreground="red")
        else:
            self.csv_status.config(text="Please select a CSV file", foreground="gray")
        
        # Check Excel file
        excel_path = self.excel_var.get().strip()
        if excel_path and os.path.exists(excel_path):
            self.excel_status.config(text="✓ Excel file found", foreground="green")
        elif excel_path:
            self.excel_status.config(text="✗ Excel file not found", foreground="red")
        else:
            self.excel_status.config(text="Please select an Excel file", foreground="gray")
    
    def browse_csv(self):
        """Open file dialog to select CSV file."""
        filetypes = [
            ('CSV files', '*.csv'),
            ('All files', '*.*')
        ]
        filename = filedialog.askopenfilename(
            title="Select Bank CSV File",
            filetypes=filetypes,
            initialdir=os.path.dirname(self.csv_var.get()) if self.csv_var.get() else None
        )
        if filename:
            self.csv_var.set(filename)
    
    def browse_excel(self):
        """Open file dialog to select Excel file."""
        filetypes = [
            ('Excel files', '*.xlsx;*.xls'),
            ('All files', '*.*')
        ]
        filename = filedialog.askopenfilename(
            title="Select Tiller Excel File",
            filetypes=filetypes,
            initialdir=os.path.dirname(self.excel_var.get()) if self.excel_var.get() else None
        )
        if filename:
            self.excel_var.set(filename)
    
    def import_transactions(self):
        """Import transactions from CSV to Excel."""
        csv_file = self.csv_var.get().strip()
        excel_file = self.excel_var.get().strip()
        
        if not csv_file or not excel_file:
            messagebox.showerror("Error", "Please select both CSV and Excel files")
            return
        
        if not os.path.exists(csv_file):
            messagebox.showerror("Error", "CSV file not found")
            return
        
        if not os.path.exists(excel_file):
            messagebox.showerror("Error", "Excel file not found")
            return
        
        # Save settings before attempting import
        self.save_settings()
        
        # Show progress dialog
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Importing...")
        progress_window.geometry("300x100")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Center the progress window
        progress_window.geometry("+{}+{}".format(
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        progress_label = ttk.Label(progress_window, text="Importing transactions...")
        progress_label.pack(pady=20)
        
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(pady=10, padx=20, fill=tk.X)
        progress_bar.start()
        
        # Update the GUI
        self.root.update()
        
        try:
            # Perform import
            success, message = self.importer.import_transactions(csv_file, excel_file)
            
            # Close progress window
            progress_window.destroy()
            
            if success:
                messagebox.showinfo("Success", message)
                self.root.quit()
            else:
                messagebox.showerror("Error", message)
                
        except Exception as e:
            import traceback
            # Print full traceback to console
            print(f"Error during import:\n{traceback.format_exc()}")
            # Show user-friendly error message
            progress_window.destroy()
            messagebox.showerror("Error", f"An error occurred during import: {str(e)}")
    
    def run(self):
        # Center the main window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        self.root.mainloop()
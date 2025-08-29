#!/usr/bin/env python3

"""
This module provides the graphical user interface for importing transaction files.

It defines the `ImporterGUIFrame`, which contains all the widgets and logic
for the import user interface, and the main `ImporterGUI` class which acts
as a controller.
"""

import json
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .ally_importer import AllyImporter
from .capital_one_importer import CapitalOneImporter
from .logger import logger

class ImporterGUIFrame(ttk.Frame):
    """
    Manages the user interface frame for the transaction importer.

    This class creates and lays out all the GUI widgets, including file
    selectors, the bank selection dropdown, and the import button. It also
    handles user interactions, such as browsing for files and initiating the
    import process.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
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
        
        self.create_widgets()
        self.load_settings()

    def on_show(self):
        """Called when the frame is shown."""
        self.load_settings()
        self.update_file_status()

    def load_settings(self):
        """Load previously saved file paths from config file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                csv_path = config.get('last_csv_path', '')
                excel_path = config.get('last_excel_path', '')
                saved_bank = config.get('last_bank', 'CapitalOne')
                
                if saved_bank in self.banks:
                    self.bank_var.set(saved_bank)
                    self.importer = self.banks[saved_bank]()
                
                if csv_path and os.path.exists(csv_path):
                    self.csv_var.set(csv_path)
                
                if excel_path and os.path.exists(excel_path):
                    self.excel_var.set(excel_path)
        except (OSError, ValueError, json.JSONDecodeError) as e:
            logger.error("Error loading settings: %s", e)

    def save_settings(self):
        """Save current file paths to config file."""
        try:
            config = {
                'last_csv_path': self.csv_var.get(),
                'last_excel_path': self.excel_var.get(),
                'last_bank': self.bank_var.get()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except (OSError, ValueError) as e:
            logger.error("Error saving settings: %s", e)

    def create_widgets(self):
        """Create and layout all GUI widgets."""
        main_frame = ttk.Frame(self, padding="30", style="TFrame")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        title_label = ttk.Label(main_frame, text="Import Bank Transactions", style="Header.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="w")
        
        instructions = ttk.Label(main_frame, text="Select your bank CSV file and Tiller Excel spreadsheet to import transactions.", wraplength=500, justify=tk.LEFT)
        instructions.grid(row=1, column=0, columnspan=3, pady=(0, 15), sticky="w")
        
        bank_label = ttk.Label(main_frame, text="Select Bank:", font=('Arial', 11, 'bold'))
        bank_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        bank_combo = ttk.Combobox(main_frame, textvariable=self.bank_var, values=list(self.banks.keys()), state='readonly')
        bank_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        bank_combo.bind('<<ComboboxSelected>>', self.on_bank_change)
        
        csv_label = ttk.Label(main_frame, text="Bank CSV File:", font=('Arial', 11, 'bold'))
        csv_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        csv_entry = ttk.Entry(main_frame, textvariable=self.csv_var, width=70)
        csv_entry.grid(row=4, column=0, columnspan=2, padx=(0, 5), pady=5, sticky="we")
        csv_browse = ttk.Button(main_frame, text="Browse...", command=self.browse_csv)
        csv_browse.grid(row=4, column=2, pady=5)
        
        excel_label = ttk.Label(main_frame, text="Tiller Excel File:", font=('Arial', 11, 'bold'))
        excel_label.grid(row=5, column=0, sticky=tk.W, pady=5)
        excel_entry = ttk.Entry(main_frame, textvariable=self.excel_var, width=70)
        excel_entry.grid(row=6, column=0, columnspan=2, padx=(0, 5), pady=5, sticky="we")
        excel_browse = ttk.Button(main_frame, text="Browse...", command=self.browse_excel)
        excel_browse.grid(row=6, column=2, pady=5)
        
        status_frame = ttk.Frame(main_frame, style="TFrame")
        status_frame.grid(row=7, column=0, columnspan=3, pady=10, sticky="we")
        self.csv_status = ttk.Label(status_frame, text="", font=('Arial', 9))
        self.csv_status.grid(row=0, column=0, sticky=tk.W)
        self.excel_status = ttk.Label(status_frame, text="", font=('Arial', 9))
        self.excel_status.grid(row=1, column=0, sticky=tk.W)
        
        button_frame = ttk.Frame(main_frame, style="TFrame")
        button_frame.grid(row=8, column=0, columnspan=3, pady=20, sticky="w")
        
        import_btn = ttk.Button(button_frame, text="Import Transactions", command=self.import_transactions, style="ActionButton.TButton", width=22)
        import_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        back_btn = ttk.Button(button_frame, text="Cancel", command=lambda: self.controller.show_frame("MainMenuFrame"), width=22, style="Cancel.TButton")
        back_btn.pack(side=tk.LEFT)
        
        main_frame.columnconfigure(1, weight=1)
        self.csv_var.trace('w', lambda *args: self.update_file_status())
        self.excel_var.trace('w', lambda *args: self.update_file_status())
    
    def on_bank_change(self, _=None):
        """Handle bank selection change."""
        selected_bank = self.bank_var.get()
        self.importer = self.banks[selected_bank]()
        self.update_file_status()
    
    def update_file_status(self):
        """Update the status indicators for CSV and Excel files."""
        csv_path = self.csv_var.get().strip()
        if csv_path and os.path.exists(csv_path):
            self.csv_status.config(text="✓ CSV file found", foreground="green")
        else:
            self.csv_status.config(text="✗ CSV file not found", foreground="red")
        
        excel_path = self.excel_var.get().strip()
        if excel_path and os.path.exists(excel_path):
            self.excel_status.config(text="✓ Excel file found", foreground="green")
        else:
            self.excel_status.config(text="✗ Excel file not found", foreground="red")
    
    def browse_csv(self):
        """Open file dialog to browse for CSV file."""
        filetypes = [('CSV files', '*.csv'), ('All files', '*.*')]
        initial_dir = os.path.dirname(self.csv_var.get()) if self.csv_var.get() and os.path.exists(os.path.dirname(self.csv_var.get())) else str(Path.home() / "Downloads")
        filename = filedialog.askopenfilename(title="Select Bank CSV File", filetypes=filetypes, initialdir=initial_dir)
        if filename:
            self.csv_var.set(filename)
    
    def browse_excel(self):
        """Open file dialog to browse for Excel file."""
        filetypes = [('Excel files', '*.xlsx'), ('All files', '*.*')]
        initial_dir = os.path.dirname(self.excel_var.get()) if self.excel_var.get() and os.path.exists(os.path.dirname(self.excel_var.get())) else str(Path.home() / "Documents")
        filename = filedialog.askopenfilename(title="Select Tiller Excel File", filetypes=filetypes, initialdir=initial_dir)
        if filename:
            self.excel_var.set(filename)
            
    def import_transactions(self):
        """Import transactions from CSV to Excel file."""
        self.save_settings()
        
        csv_path = self.csv_var.get()
        excel_path = self.excel_var.get()
        
        if not csv_path or not excel_path or not os.path.exists(csv_path) or not os.path.exists(excel_path):
            messagebox.showerror("Error", "Please ensure both file paths are correct.")
            return

        try:
            success, message = self.importer.import_transactions(csv_path, excel_path)
            
            if success:
                messagebox.showinfo("Success", message)
                self.controller.show_frame("MainMenuFrame")
            else:
                messagebox.showerror("Error", message)
                
        except (OSError, ValueError, FileNotFoundError, PermissionError) as e:
            logger.error("Error during import: %s", e)
            messagebox.showerror("Import Failed", f"An error occurred:\n{str(e)}")
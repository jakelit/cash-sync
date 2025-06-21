#!/usr/bin/env python3

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
import traceback
from .logger import logger
from .auto_categorizer import AutoCategorizer

class AutoCategorizeFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.excel_var = tk.StringVar()
        self.config_file = os.path.join(os.path.expanduser("~"), ".excel_finance_tools_config.json")
        self.create_widgets()
        self.load_saved_path()

    def on_show(self):
        """Called when the frame is shown."""
        self.load_saved_path()
        self.update_file_status()

    def create_widgets(self):
        style = ttk.Style()
        style.configure("Header.TLabel", font=('Arial', 18, 'bold'))

        main_frame = ttk.Frame(self, padding="30", style="TFrame")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        title_label = ttk.Label(main_frame, text="Auto Categorize Transactions", style="Header.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="w")
        
        instructions = ttk.Label(main_frame, text="Select your Excel spreadsheet to automatically categorize transactions.", wraplength=500, justify=tk.LEFT)
        instructions.grid(row=1, column=0, columnspan=3, pady=(0, 20), sticky="w")
        
        excel_label = ttk.Label(main_frame, text="Excel File:", font=('Arial', 11, 'bold'))
        excel_label.grid(row=2, column=0, sticky="w", pady=5)
        excel_entry = ttk.Entry(main_frame, textvariable=self.excel_var, width=70)
        excel_entry.grid(row=3, column=0, columnspan=2, padx=(0, 5), pady=5, sticky="we")
        excel_browse = ttk.Button(main_frame, text="Browse...", command=self.browse_excel)
        excel_browse.grid(row=3, column=2, padx=(5, 0), pady=5)
        
        status_frame = ttk.Frame(main_frame, style="TFrame")
        status_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky="we")
        self.excel_status = ttk.Label(status_frame, text="", font=('Arial', 9))
        self.excel_status.grid(row=0, column=0, sticky="w")
        
        button_frame = ttk.Frame(main_frame, style="TFrame")
        button_frame.grid(row=5, column=0, columnspan=3, pady=20, sticky="w")
        
        categorize_btn = ttk.Button(button_frame, text="Auto Categorize", command=self.auto_categorize, style="ActionButton.TButton", width=22)
        categorize_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        back_btn = ttk.Button(button_frame, text="Cancel", command=lambda: self.controller.show_frame("MainMenuFrame"), width=22, style="Cancel.TButton")
        back_btn.pack(side=tk.LEFT)
        
        main_frame.columnconfigure(1, weight=1)
        self.excel_var.trace('w', lambda *args: self.update_file_status())
    
    def load_saved_path(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    saved_path = config.get('last_excel_path', '')
                    if saved_path and os.path.exists(saved_path):
                        self.excel_var.set(saved_path)
        except Exception as e:
            logger.error(f"Error loading saved path: {e}")

    def save_path(self):
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            config['last_excel_path'] = self.excel_var.get()
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving path: {e}")
    
    def update_file_status(self):
        excel_path = self.excel_var.get()
        if excel_path and os.path.exists(excel_path) and excel_path.lower().endswith('.xlsx'):
            self.excel_status.config(text="✓ Excel file found", foreground="green")
        elif excel_path:
            self.excel_status.config(text="✗ File not found or not an .xlsx file", foreground="red")
        else:
            self.excel_status.config(text="")
    
    def browse_excel(self):
        file_path = tk.filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.excel_var.set(file_path)
            self.update_file_status()
    
    def auto_categorize(self):
        excel_path = self.excel_var.get()
        if not excel_path or not os.path.exists(excel_path):
            messagebox.showerror("Error", "Please select a valid Excel file.")
            return
        
        self.save_path()
        
        try:
            categorizer = AutoCategorizer(excel_path)
            success, message = categorizer.run_auto_categorization()
            
            if success:
                messagebox.showinfo("Success", message)
                self.controller.show_frame("MainMenuFrame")
            else:
                messagebox.showerror("Error", f"Auto-categorization failed: {message}")
        except Exception as e:
            logger.error(f"Failed to run auto-categorization: {e}")
            logger.debug(traceback.format_exc())
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}") 
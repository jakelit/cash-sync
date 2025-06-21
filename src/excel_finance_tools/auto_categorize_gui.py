"""
This module provides the graphical user interface for the auto-categorization feature.

It defines the `AutoCategorizeFrame` class, which creates and manages the user interface
for selecting Excel files and running the auto-categorization process on transactions.
"""
#!/usr/bin/env python3

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
import traceback
from .logger import logger
from .auto_categorizer import AutoCategorizer

class AutoCategorizeFrame(ttk.Frame):
    """
    Manages the user interface for the auto-categorization feature.

    This class creates a frame with widgets for selecting an Excel file and
    triggering the auto-categorization process. It handles file validation,
    user feedback, and integration with the AutoCategorizer backend.
    """
    def __init__(self, parent, controller):
        """
        Initialize the AutoCategorizeFrame.

        Args:
            parent: The parent widget
            controller: The main application controller
        """
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
        """
        Create and layout all the GUI widgets for the auto-categorization interface.

        This method sets up the main frame, title, instructions, file selection
        controls, status indicators, and action buttons.
        """
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
        """
        Load the previously saved Excel file path from the configuration file.

        This method reads the configuration file and restores the last used
        Excel file path if it exists and is still valid.
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    saved_path = config.get('last_excel_path', '')
                    if saved_path and os.path.exists(saved_path):
                        self.excel_var.set(saved_path)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
            logger.error("Error loading saved path: %s", e)

    def save_path(self):
        """
        Save the current Excel file path to the configuration file.

        This method preserves the user's file selection for future sessions
        by writing the current path to the configuration file.
        """
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            config['last_excel_path'] = self.excel_var.get()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError, OSError) as e:
            logger.error("Error saving path: %s", e)
    
    def update_file_status(self):
        """
        Update the file status indicator based on the current Excel file path.

        This method validates the selected file path and updates the status
        label to show whether the file exists and is a valid Excel file.
        """
        excel_path = self.excel_var.get()
        if excel_path and os.path.exists(excel_path) and excel_path.lower().endswith('.xlsx'):
            self.excel_status.config(text="✓ Excel file found", foreground="green")
        elif excel_path:
            self.excel_status.config(text="✗ File not found or not an .xlsx file", foreground="red")
        else:
            self.excel_status.config(text="")
    
    def browse_excel(self):
        """
        Open a file dialog to select an Excel file.

        This method opens a file browser dialog that filters for Excel files
        and updates the file path variable when a file is selected.
        """
        file_path = tk.filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.excel_var.set(file_path)
            self.update_file_status()
    
    def auto_categorize(self):
        """
        Execute the auto-categorization process on the selected Excel file.

        This method validates the file selection, creates an AutoCategorizer
        instance, runs the categorization process, and displays the results
        to the user with appropriate success or error messages.
        """
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
        except (ValueError, FileNotFoundError, PermissionError, OSError) as e:
            logger.error("Failed to run auto-categorization: %s", e)
            logger.debug(traceback.format_exc())
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}") 
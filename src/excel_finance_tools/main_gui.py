#!/usr/bin/env python3

"""
This module provides the main graphical user interface for the Excel Finance Tools.

It defines the main application window, `ExcelFinanceToolsApp`, which serves as
the controller for managing different UI frames, and the `MainMenuFrame`, which
is the initial screen that allows users to navigate to the application's
different features like importing and auto-categorizing transactions.
"""

import tkinter as tk
from tkinter import ttk
from .importer_gui import ImporterGUIFrame
from .auto_categorize_gui import AutoCategorizeFrame

class ExcelFinanceToolsApp(tk.Tk):
    """
    Main application class for Excel Finance Tools.
    Manages a single window with multiple frames for different functionalities.
    """
    
    def __init__(self):
        super().__init__()
        self.title("Excel Finance Tools")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")

        self.center_window()
        self.setup_styles()

        container = ttk.Frame(self, style="TFrame")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (MainMenuFrame, ImporterGUIFrame, AutoCategorizeFrame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenuFrame")

    def setup_styles(self):
        """Configure the visual styles for the application."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=('Arial', 11))
        style.configure("Title.TLabel", font=('Arial', 24, 'bold'))
        style.configure("Subtitle.TLabel", font=('Arial', 12), foreground="#555555")
        style.configure("Card.TFrame", background="#ffffff", borderwidth=1, relief="solid", bordercolor="#e0e0e0")
        style.map("Card.TFrame", bordercolor=[('active', '#008080')])
        style.configure("Icon.TLabel", background="#ffffff", font=('Segoe UI Emoji', 48))
        style.configure("CardTitle.TLabel", background="#ffffff", font=('Arial', 16, 'bold'))
        style.configure("CardDesc.TLabel", background="#ffffff", font=('Arial', 10), foreground="#666666")
        
        # Primary button style
        style.configure("ActionButton.TButton", font=('Arial', 11, 'bold'), padding=10)
        style.map("ActionButton.TButton",
                  background=[('!disabled', '#008080'), ('active', '#005f5f')],
                  foreground=[('!disabled', 'white')])

        # Secondary/Cancel button style
        style.configure("Cancel.TButton", font=('Arial', 11), padding=10)

    def show_frame(self, cont_name):
        """Switch to the specified frame and call its on_show method if available."""
        frame = self.frames[cont_name]
        frame.tkraise()
        # If the frame has an 'on_show' method, call it
        if hasattr(frame, 'on_show'):
            frame.on_show()

    def center_window(self):
        """Center the main window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def run(self):
        """Run the main application."""
        self.mainloop()

class MainMenuFrame(ttk.Frame):
    """
    The main menu frame, providing a central navigation hub for the application.

    This frame displays the primary actions a user can take, such as importing
    transactions or running the auto-categorizer, and it directs the user to
    the appropriate interface for each tool.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        """Create the main menu widgets."""
        self.configure_styles()
        
        main_frame = ttk.Frame(self, padding="40", style="TFrame")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        title_label = ttk.Label(main_frame, text="Excel Finance Tools", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Select an action to get started", style="Subtitle.TLabel")
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 40))
        
        actions_frame = ttk.Frame(main_frame, style="TFrame")
        actions_frame.grid(row=2, column=0, columnspan=2, pady=20, sticky="nsew")
        
        import_frame = self.create_action_card(actions_frame, 
                                              "Import Transactions", 
                                              "Import bank CSV transactions into your Excel spreadsheet.",
                                              "📥",
                                              lambda: self.controller.show_frame("ImporterGUIFrame"))
        import_frame.grid(row=0, column=0, padx=(0, 20), pady=10, sticky="nsew")
        
        categorize_frame = self.create_action_card(actions_frame, 
                                                  "Auto Categorize", 
                                                  "Automatically categorize transactions in your Excel spreadsheet.",
                                                  "🏷️",
                                                  lambda: self.controller.show_frame("AutoCategorizeFrame"))
        categorize_frame.grid(row=0, column=1, padx=(20, 0), pady=10, sticky="nsew")
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        actions_frame.columnconfigure(0, weight=1)
        actions_frame.columnconfigure(1, weight=1)
        actions_frame.rowconfigure(0, weight=1)
    
    def create_action_card(self, parent, title, description, icon, command):
        """Create an action card widget with icon, title, description, and button."""
        card_frame = ttk.Frame(parent, style="Card.TFrame")
        card_frame.columnconfigure(0, weight=1)

        icon_label = ttk.Label(card_frame, text=icon, style="Icon.TLabel")
        icon_label.grid(row=0, column=0, pady=(30, 10), padx=20)
        
        title_label = ttk.Label(card_frame, text=title, style="CardTitle.TLabel")
        title_label.grid(row=1, column=0, pady=(0, 10), padx=20)
        
        desc_label = ttk.Label(card_frame, text=description, style="CardDesc.TLabel", wraplength=250, justify=tk.CENTER)
        desc_label.grid(row=2, column=0, pady=(0, 30), padx=20, sticky="n")
        
        card_frame.rowconfigure(2, weight=1)

        action_btn = ttk.Button(card_frame, text="Open", command=command, style="ActionButton.TButton")
        action_btn.grid(row=3, column=0, pady=(0, 30))

        def on_enter(_event):
            """Handle mouse enter event for card highlighting."""
            card_frame.state(['active'])
        def on_leave(_event):
            """Handle mouse leave event for card highlighting."""
            card_frame.state(['!active'])   

        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        for child in card_frame.winfo_children():
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)

        return card_frame

    def configure_styles(self):
        """Configure the visual styles for the main menu frame."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=('Arial', 11))
        style.configure("Title.TLabel", font=('Arial', 24, 'bold'))
        style.configure("Subtitle.TLabel", font=('Arial', 12), foreground="#555555")
        style.configure("Card.TFrame", background="#ffffff", borderwidth=1, relief="solid", bordercolor="#e0e0e0")
        style.map("Card.TFrame", bordercolor=[('active', '#008080')])
        style.configure("Icon.TLabel", background="#ffffff", font=('Segoe UI Emoji', 48))
        style.configure("CardTitle.TLabel", background="#ffffff", font=('Arial', 16, 'bold'))
        style.configure("CardDesc.TLabel", background="#ffffff", font=('Arial', 10), foreground="#666666")
        style.configure("ActionButton.TButton", font=('Arial', 11, 'bold'), padding=10)
        style.map("ActionButton.TButton",
                  background=[('!disabled', '#008080'), ('active', '#005f5f')],
                  foreground=[('!disabled', 'white')])
import tkinter as tk
from tkinter import ttk

def create_status_bar(parent):
    """Vytvoří stavový řádek"""
    status_var = tk.StringVar()
    status_var.set("Připraveno")
    
    status_bar = tk.Label(
        parent,
        textvariable=status_var,
        relief=tk.SUNKEN,
        anchor=tk.W,
        bg="#eafbe7",
        fg="#1b7e2c",
        font=("Arial", 10)
    )
    
    return status_bar, status_var

def create_header(parent, text):
    """Vytvoří záhlaví s textem"""
    header = ttk.Label(
        parent,
        text=text,
        font=("Arial", 16, "bold")
    )
    return header

def create_button_with_style(parent, text, command, width=None, style=None):
    """Vytvoří tlačítko s volitelným stylem"""
    button = ttk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        style=style
    )
    return button

def create_labeled_frame(parent, text, padding="10"):
    """Vytvoří rámeček s popiskem"""
    frame = ttk.LabelFrame(
        parent,
        text=text,
        padding=padding
    )
    return frame
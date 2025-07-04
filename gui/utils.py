import tkinter as tk
from datetime import datetime

def log_message(log_widget, message):
    """Přidá zprávu do log okna"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_widget.insert(tk.END, f"[{timestamp}] {message}\n")
    log_widget.see(tk.END)  # Posunutí na konec textu

def validate_float_input(value):
    """Ověří, že vstup je platné desetinné číslo"""
    if value == "":
        return True
        
    try:
        float(value)
        return True
    except ValueError:
        return False

def lighten_color(color, amount=0.8):
    """Zesvětlí barvu pro použití v pozadí"""
    # Převést hex barvu na RGB
    color = color.lstrip('#')
    r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
    
    # Zesvětlit
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    
    # Vrátit jako hex
    return f"#{r:02x}{g:02x}{b:02x}"

def get_color_for_index(index):
    """Vrátí barvu pro daný index"""
    base_colors = [
        "#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6",
        "#1abc9c", "#34495e", "#95a5a6", "#d35400", "#27ae60",
    ]
    return base_colors[index % len(base_colors)]
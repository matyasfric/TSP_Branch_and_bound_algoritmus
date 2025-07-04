import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import random
from gui.utils import validate_float_input

class MatrixEditor:
    def __init__(self, parent, notebook):
        self.parent = parent
        self.notebook = notebook
        self.create_matrix_tab = ttk.Frame(notebook, padding=10)
        self.notebook.add(self.create_matrix_tab, text="Vytvořit matici")

        # Přidejte callback pro předání matice
        self.on_matrix_created = None

        
        # Proměnné pro ukládání dat
        self.matrix_size_var = tk.IntVar(value=3)  # Výchozí velikost matice
        self.matrix_names = []  # Názvy bodů
        self.matrix_values = {}  # Hodnoty v matici
        
        self.create_ui()
    
    def create_ui(self):
        """Vytvoří prvky pro vytváření a editaci matice"""
        # Hlavní kontejner s vertikálním uspořádáním
        main_container = ttk.Frame(self.create_matrix_tab)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Horní část - nastavení velikosti matice
        setup_frame = ttk.LabelFrame(main_container, text="Nastavení velikosti matice", padding="10")
        setup_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Počet bodů
        ttk.Label(setup_frame, text="Počet bodů (velikost matice):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        size_spinner = ttk.Spinbox(setup_frame, from_=2, to=20, textvariable=self.matrix_size_var, width=5)
        size_spinner.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Tlačítko pro inicializaci matice
        create_button = ttk.Button(setup_frame, text="Vytvořit formulář matice", 
                                 command=self.initialize_matrix_editor)
        create_button.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        # Středová část - editace názvů bodů a hodnot matice
        self.editor_frame = ttk.Frame(main_container)
        self.editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Dolní část - tlačítka pro akce s maticí
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Tlačítka pro pomoc při vytváření matice
        ttk.Button(action_frame, text="Symetrická matice", 
                  command=self.mirror_matrix_values).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="Náhodné hodnoty", 
                  command=self.fill_random_matrix_values).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="Vymazat hodnoty", 
                  command=self.clear_matrix_values).pack(side=tk.LEFT, padx=5)
        
        # Tlačítko pro vytvoření matice
        ttk.Button(action_frame, text="Použít matici", 
                  command=self.apply_created_matrix,
                  style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
        
        # Zobrazit počáteční formulář
        self.initialize_matrix_editor()
    
    def initialize_matrix_editor(self):
        """Inicializuje editor matice podle vybrané velikosti"""
        # Vyčistit existující editor
        for widget in self.editor_frame.winfo_children():
            widget.destroy()
        
        size = self.matrix_size_var.get()
        
        # Vytvořit scrollovatelný rámec
        canvas = tk.Canvas(self.editor_frame)
        scrollbar = ttk.Scrollbar(self.editor_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Sekce pro názvy bodů
        names_frame = ttk.LabelFrame(scrollable_frame, text="Názvy bodů", padding="10")
        names_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.matrix_names = []
        for i in range(size):
            row_frame = ttk.Frame(names_frame)
            row_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(row_frame, text=f"Bod {i+1}:").pack(side=tk.LEFT, padx=5)
            
            name_var = tk.StringVar(value=f"Bod {i+1}")
            self.matrix_names.append(name_var)
            
            name_entry = ttk.Entry(row_frame, textvariable=name_var, width=20)
            name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Sekce pro hodnoty matice
        matrix_frame = ttk.LabelFrame(scrollable_frame, text="Matice vzdáleností", padding="10")
        matrix_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Záhlaví tabulky
        ttk.Label(matrix_frame, text="", width=10).grid(row=0, column=0)
        for i in range(size):
            ttk.Label(matrix_frame, text=f"Bod {i+1}", width=10).grid(row=0, column=i+1, padx=2, pady=2)
        
        # Vytvoření vstupních polí matice
        self.matrix_values = {}
        
        for i in range(size):
            ttk.Label(matrix_frame, text=f"Bod {i+1}", width=10).grid(row=i+1, column=0, padx=2, pady=2)
            
            for j in range(size):
                var = tk.StringVar()
                
                # Na diagonále použijeme hodnotu 0
                if i == j:
                    var.set("0")
                    entry = ttk.Entry(matrix_frame, textvariable=var, width=10, state="readonly")
                else:
                    var.set("")
                    entry = ttk.Entry(matrix_frame, textvariable=var, width=10)
                    
                    # Validace vstupu na číselné hodnoty
                    vcmd = (self.parent.register(validate_float_input), '%P')
                    entry.config(validate="key", validatecommand=vcmd)
                
                entry.grid(row=i+1, column=j+1, padx=2, pady=2)
                self.matrix_values[(i, j)] = var
        
        # Přepnout na záložku vytvořit matici
        self.notebook.select(self.create_matrix_tab)

    def mirror_matrix_values(self):
        """Zkopíruje hodnoty z horní trojúhelníkové části matice do spodní části"""
        size = self.matrix_size_var.get()
        
        for i in range(size):
            for j in range(i+1, size):
                value = self.matrix_values[(i, j)].get()
                
                if value and value.strip():
                    self.matrix_values[(j, i)].set(value)

    def fill_random_matrix_values(self):
        """Vyplní matici náhodnými hodnotami"""
        size = self.matrix_size_var.get()
        
        for i in range(size):
            for j in range(size):
                if i != j:  # Přeskočit diagonálu
                    # Generovat náhodnou vzdálenost mezi 1 a 100
                    random_value = round(random.uniform(1, 100), 1)
                    self.matrix_values[(i, j)].set(str(random_value))

    def clear_matrix_values(self):
        """Vymaže všechny hodnoty v matici kromě diagonály"""
        size = self.matrix_size_var.get()
        
        for i in range(size):
            for j in range(size):
                if i != j:  # Přeskočit diagonálu
                    self.matrix_values[(i, j)].set("")

    def apply_created_matrix(self):
        """Vytvoří matici z hodnot zadaných v editoru"""
        size = self.matrix_size_var.get()
        
        # Kontrola, zda jsou všechny hodnoty zadány
        missing = []
        for i in range(size):
            for j in range(size):
                if i != j and not self.matrix_values[(i, j)].get().strip():
                    missing.append((i+1, j+1))
        
        if missing:
            missing_str = ", ".join([f"({i},{j})" for i, j in missing])
            messagebox.showerror(
                "Chybějící hodnoty",
                f"Některé vzdálenosti nejsou zadány: {missing_str}\n\n"
                "Pro vytvoření matice musí být vyplněny všechny hodnoty."
            )
            return None
        
        # Získat názvy bodů
        node_labels = [name_var.get() for name_var in self.matrix_names]
        
        # Sestavit dataframe
        matrix_data = {}
        for j in range(size):
            col_data = []
            for i in range(size):
                if i == j:
                    col_data.append(0)  # Diagonála je vždy 0
                else:
                    col_data.append(float(self.matrix_values[(i, j)].get()))
                    
            matrix_data[node_labels[j]] = col_data
        
        # Vytvořit pandas DataFrame
        matrix = pd.DataFrame(matrix_data, index=node_labels)
        
        # Informovat uživatele
        messagebox.showinfo("Matice vytvořena", "Nová matice byla úspěšně vytvořena a je připravena k použití.")
        
        # Předat matici rodiči pomocí callbacku
        if self.on_matrix_created:
            self.on_matrix_created(matrix)
    
        # Vrátit vytvořenou matici
        return matrix
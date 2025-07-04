import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
import threading
import os
from datetime import datetime
import pandas as pd

# Import modulů z aplikace
from core.io_handlers import read_excel, write_excel
from core.solvers import solve_tsp, find_cycles
from gui.matrix_editor import MatrixEditor
from gui.matrix_view import MatrixView
from gui.route_view import RouteView
from gui.utils import log_message

class TSPOptimizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Konfigurace hlavního okna
        self.title("TSP Optimalizační nástroj")
        self.geometry("1000x800")
        
        # Proměnné pro uchovávání cest k souborům
        self.input_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.output_file_path.set("output_metoda_branch_and_bound.xlsx")
        
        # Proměnná pro volbu generování Excel souboru
        self.generate_excel = tk.BooleanVar(value=True)
        
        # Proměnné pro výsledky
        self.result_distance = tk.StringVar()
        self.result_distance.set("Celková vzdálenost: -")
        self.result_sequence = tk.StringVar()
        self.result_sequence.set("Pořadí bodů: -")
        
        # Data pro výpočet a vizualizaci
        self.matrix = None
        self.solution = None
        self.cycles = None
        self.route_sequence = None
        
        # Stav výpočtu
        self.calculation_running = False
        
        # Vytvoření UI
        self.create_ui()
        
    def create_ui(self):
        """Vytvoří uživatelské rozhraní aplikace"""

        # Hlavní kontejner pro vše (vertikální stack)
        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        # Hlavní rámec pro obsah aplikace
        main_frame = ttk.Frame(container, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Záhlaví
        header_label = ttk.Label(main_frame, 
                                text="Optimalizace trasy metodou Branch and Bound",
                                font=("Arial", 16, "bold"))
        header_label.pack(pady=(0, 10))
        
        # Horní část s formulářem
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X)
        
        # Sekce pro vstupní soubor
        input_frame = ttk.LabelFrame(form_frame, text="Vstupní soubor", padding="10")
        input_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        input_path_entry = ttk.Entry(input_frame, textvariable=self.input_file_path, width=40)
        input_path_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        browse_button = ttk.Button(input_frame, text="Procházet...", command=self.browse_input_file)
        browse_button.pack(side=tk.RIGHT)
        
        # Sekce pro výstupní soubor s podmíněným zobrazením
        self.output_frame = ttk.LabelFrame(form_frame, text="Výstupní soubor", padding="10")
        self.output_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Zaškrtávací pole pro generování Excel souboru
        self.excel_check = ttk.Checkbutton(self.output_frame, 
                                          text="Generovat Excel soubor", 
                                          variable=self.generate_excel,
                                          command=self.toggle_output_widgets)
        self.excel_check.pack(anchor="w", padx=5, pady=2)
        
        # Frame pro výběr cesty k výstupnímu souboru
        self.output_path_frame = ttk.Frame(self.output_frame)
        self.output_path_frame.pack(fill=tk.X, expand=True, pady=2)
        
        self.output_path_entry = ttk.Entry(self.output_path_frame, textvariable=self.output_file_path, width=40)
        self.output_path_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        self.output_button = ttk.Button(self.output_path_frame, text="Procházet...", command=self.browse_output_file)
        self.output_button.pack(side=tk.RIGHT)
        
        # Nastavení vah sloupců
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)
        
        # Tlačítka pro ovládání aplikace
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10, fill=tk.X)
        
        calculate_button = ttk.Button(button_frame, text="Spustit optimalizaci", 
                                     command=self.start_optimization, 
                                     style="Accent.TButton", width=20)
        calculate_button.pack(side=tk.LEFT, padx=5)
        
        view_matrix_button = ttk.Button(button_frame, text="Zobrazit matici", 
                                      command=self.load_and_display_matrix,
                                      width=15)
        view_matrix_button.pack(side=tk.LEFT, padx=5)
        
        # Tlačítko pro reset
        reset_button = ttk.Button(button_frame, text="Nový projekt", 
                                 command=self.reset_application,
                                 width=15)
        reset_button.pack(side=tk.RIGHT, padx=5)
        
        # Vytvoření stylu pro zvýrazněné tlačítko
        self.style = ttk.Style()
        self.style.configure("Accent.TButton", font=("Arial", 12, "bold"))
        
        # Sekce pro výsledky
        results_frame = ttk.LabelFrame(main_frame, text="Výsledky", padding="10")
        results_frame.pack(fill=tk.X, pady=10)
        
        # Zobrazení celkové vzdálenosti
        ttk.Label(results_frame, textvariable=self.result_distance,
                 font=("Arial", 11, "bold")).pack(anchor="w")
        
        # Zobrazení pořadí bodů (s možností scrollování)
        sequence_frame = ttk.Frame(results_frame)
        sequence_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(sequence_frame, text="Pořadí bodů:", 
                 font=("Arial", 11)).pack(side=tk.LEFT, anchor="w")
        
        self.sequence_entry = ttk.Entry(sequence_frame, textvariable=self.result_sequence,
                                  state="readonly", width=80)
        self.sequence_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Záložkový systém
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Záložka pro log
        self.log_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.log_tab, text="Log")
        
        # Vytvoření obsahu záložky s logem
        self.log_text = scrolledtext.ScrolledText(self.log_tab, height=15, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Vytvoření komponent pro práci s maticí a vizualizaci
        self.matrix_view = MatrixView(self, self.notebook)
        self.route_view = RouteView(self, self.notebook)
        self.matrix_editor = MatrixEditor(self, self.notebook)

        # Přidejte propojení s MatrixEditor
        self.matrix_editor.on_matrix_created = self.on_matrix_created
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, 
                                       length=100, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)
        
        # Spodní rámec pro status bar a copyright
        bottom_frame = tk.Frame(container)
        bottom_frame.grid(row=1, column=0, sticky="ew")
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=0)

        # Stavový řádek - vždy dole, zelené pozadí, roztažený
        self.status_var = tk.StringVar()
        self.status_var.set("Připraveno")
        status_bar = tk.Label(
            bottom_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#eafbe7",
            fg="#1b7e2c",
            font=("Arial", 10)
        )
        status_bar.grid(row=0, column=0, sticky="ew")

        # Copyright - vždy vpravo dole
        # Nastavíme barvu textu podle režimu (světlý/tmavý) - na macOS může být tmavý režim
        # Tkinter nemá přímou detekci tmavého režimu, ale použijeme pouze fg barvu a necháme bg defaultní
        copyright_label = tk.Label(
            bottom_frame,
            text="© 2025 Matyáš Fric",
            font=("Arial", 9),
            anchor="e",
            fg="#888888",  # světle šedá, dobře viditelná na světlém i tmavém pozadí
            bg=bottom_frame.cget("bg")  # použijeme stejnou barvu jako má parent frame
        )
        copyright_label.grid(row=0, column=1, sticky="e", padx=12, pady=2)

        # Zajistit, že spodní rámec je vždy viditelný
        container.rowconfigure(1, weight=0)

    def toggle_output_widgets(self):
        """Přepíná viditelnost widgetů pro výstupní soubor podle zaškrtnutí checkboxu"""
        if self.generate_excel.get():
            self.output_path_frame.pack(fill=tk.X, expand=True, pady=2)
        else:
            self.output_path_frame.pack_forget()
    
    def browse_input_file(self):
        """Otevře dialog pro výběr vstupního souboru"""
        file_path = filedialog.askopenfilename(
            title="Vyberte vstupní Excel soubor",
            filetypes=[("Excel soubory", "*.xlsx;*.xls"), ("Všechny soubory", "*.*")]
        )
        if file_path:
            self.input_file_path.set(file_path)
            self.log("Vybrán vstupní soubor: " + file_path)
            
            # Pokud výstupní soubor nebyl nastaven, vygenerujeme název automaticky
            if self.generate_excel.get() and (not self.output_file_path.get() or self.output_file_path.get() == "output_metoda_branch_and_bound.xlsx"):
                dir_name = os.path.dirname(file_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                out_file = os.path.join(dir_name, f"optimalizovana_trasa_{timestamp}.xlsx")
                self.output_file_path.set(out_file)
    
    def browse_output_file(self):
        """Otevře dialog pro výběr výstupního souboru"""
        file_path = filedialog.asksaveasfilename(
            title="Zvolte umístění výstupního souboru",
            defaultextension=".xlsx",
            filetypes=[("Excel soubory", "*.xlsx"), ("Všechny soubory", "*.*")]
        )
        if file_path:
            self.output_file_path.set(file_path)
            self.log("Výstupní soubor bude uložen jako: " + file_path)
    
    def log(self, message):
        """Přidá zprávu do log okna"""
        log_message(self.log_text, message)
    
    def start_optimization(self):
        """Spustí proces optimalizace"""
        # Kontrola vstupních souborů
        if not self.input_file_path.get() and self.matrix is None:
            messagebox.showerror("Chyba", "Prosím vyberte vstupní soubor nebo vytvořte matici.")
            return
            
        # Kontrola výstupního souboru, pokud se má generovat
        if self.generate_excel.get() and not self.output_file_path.get():
            messagebox.showerror("Chyba", "Prosím zadejte název výstupního souboru.")
            return
        
        # Zamezení spuštění více výpočtů současně
        if self.calculation_running:
            messagebox.showinfo("Informace", "Výpočet již probíhá. Počkejte prosím na dokončení.")
            return
            
        # Spuštění výpočtu v novém vlákně, aby GUI zůstalo responsivní
        self.calculation_running = True
        self.status_var.set("Výpočet probíhá...")
        self.progress.start()
        
        # Vytvoření a spuštění vlákna
        thread = threading.Thread(target=self.run_optimization)
        thread.daemon = True  # Vlákno se ukončí spolu s hlavním programem
        thread.start()
    
    def run_optimization(self):
        """Provede optimalizaci v odděleném vláknu"""
        try:
            # Načtení matice ze souboru pouze pokud není již vytvořena
            if self.matrix is None:
                self.log("Načítání vstupního souboru...")
                self.matrix = read_excel(self.input_file_path.get())
                self.log(f"Soubor načten. Velikost matice: {len(self.matrix)}x{len(self.matrix)}")
            else:
                self.log(f"Použití existující matice. Velikost: {len(self.matrix)}x{len(self.matrix)}")
            
            # Řešení TSP
            self.log("Spouštím výpočet metodou Branch and Bound...")
            self.solution = solve_tsp(self.matrix)
            self.log("Výpočet dokončen!")
            
            # Nalezení alternativních cyklů
            self.log("Hledám alternativní okruhy...")
            self.cycles = find_cycles(self.matrix, self.solution)
            
            # Sestavení pořadí uzlů
            self.route_sequence = self.get_route_sequence()
            
            # Výpis výsledků
            total_distance = sum(self.matrix.loc[node[0], node[1]] for node in self.solution)
            self.log(f"Nalezeno optimální řešení s celkovou vzdáleností: {total_distance}")
            
            # Export do Excelu pouze pokud je zaškrtnuto
            if self.generate_excel.get():
                self.log(f"Zapisuji výsledky do výstupního souboru: {self.output_file_path.get()}")
                write_excel(self.matrix, self.solution, self.cycles, self.output_file_path.get())
                self.log("Export dokončen!")
            else:
                self.log("Export do Excelu byl přeskočen (není zaškrtnuto).")
            
            # Aktualizace zobrazení výsledků
            self.update_results_display()
            
            # Předání dat komponentám pro zobrazení
            self.matrix_view.set_matrix(self.matrix)
            self.matrix_view.set_solution(self.solution)
            self.route_view.set_data(self.matrix, self.solution, self.route_sequence)
            
            # Přepnutí na záložku s vizualizací
            self.notebook.select(self.route_view.route_tab)
            
            # Potvrzení dokončení
            success_message = f"Optimalizace úspěšně dokončena!\nCelková vzdálenost: {total_distance}"
            
            if self.generate_excel.get():
                success_message += f"\nVýsledky uloženy do: {self.output_file_path.get()}"
                
            messagebox.showinfo("Dokončeno", success_message)
            
        except Exception as e:
            import traceback
            trace_info = traceback.format_exc()
            self.log(f"CHYBA: {str(e)}")
            self.log(f"Detaily chyby:\n{trace_info}")
            print(f"Detailní traceback chyby:\n{trace_info}")
            messagebox.showerror("Chyba", f"Nastala chyba při výpočtu:\n{str(e)}")
            
        finally:
            # Ukončení progress baru a obnovení stavu
            self.progress.stop()
            self.calculation_running = False
            self.status_var.set("Připraveno")
    
    def update_results_display(self):
        """Aktualizuje zobrazení výsledků v hlavním okně"""
        if not self.solution:
            return
            
        # Výpočet celkové vzdálenosti
        total_distance = sum(self.matrix.loc[node[0], node[1]] for node in self.solution)
        self.result_distance.set(f"Celková vzdálenost: {total_distance}")
        
        # Zobrazení pořadí bodů
        if self.route_sequence:
            self.result_sequence.set(" → ".join(self.route_sequence))
        
        # Povolení výběru textu v entry pro pořadí bodů
        self.sequence_entry.configure(state="readonly")
    
    def get_route_sequence(self):
        """Získá sekvenci bodů z řešení"""
        if not self.solution:
            return []
        
        # Sestavíme slovník pro každý uzel a jeho následovníka
        next_node = {}
        for edge in self.solution:
            next_node[edge[0]] = edge[1]
        
        # Začneme na libovolném uzlu (první z hran)
        if not self.solution:  # Explicitní kontrola pro jistotu
            return []
            
        start_node = self.solution[0][0]
        current_node = start_node
        route_sequence = [current_node]
        
        # Postupně projdeme trasu
        while len(route_sequence) < len(self.solution):
            if current_node in next_node:
                current_node = next_node[current_node]
                route_sequence.append(current_node)
            else:
                break
        
        return route_sequence
    
    def load_and_display_matrix(self):
        """Načte matici ze souboru a zobrazí ji"""
        if not self.input_file_path.get() and self.matrix is None:
            messagebox.showerror("Chyba", "Prosím vyberte vstupní soubor nebo nejprve vytvořte matici.")
            return
        
        try:
            # Načtení matice pokud ještě nebyla načtena
            if self.matrix is None:
                self.matrix = read_excel(self.input_file_path.get())
            
            # Zobrazení matice
            self.matrix_view.set_matrix(self.matrix)
            
            # Přepnutí na záložku s maticí
            self.notebook.select(self.matrix_view.matrix_tab)
            
        except Exception as e:
            messagebox.showerror("Chyba", f"Nastala chyba při načítání matice:\n{str(e)}")
    
    def reset_application(self):
        """Reset celé aplikace pro načtení nového souboru"""
        if messagebox.askyesno("Potvrdit reset", "Opravdu chcete vymazat všechna načtená data a začít znovu?"):
            # Reset vstupních polí
            self.input_file_path.set("")
            self.output_file_path.set("output_metoda_branch_and_bound.xlsx")
            
            # Reset výsledků
            self.result_distance.set("Celková vzdálenost: -")
            self.result_sequence.set("Pořadí bodů: -")
            
            # Reset dat
            self.matrix = None
            self.solution = None
            self.cycles = None
            self.route_sequence = None
            
            # Reset logu
            self.log_text.delete(1.0, tk.END)
            self.log("Aplikace byla resetována a je připravena pro nový vstup.")
            
            # Přepnutí na záložku s logem
            self.notebook.select(self.log_tab)
            
            # Aktualizace stavové řádky
            self.status_var.set("Připraveno pro nový vstup")
            
            # Resetovat GUI komponenty
            self.matrix_editor.initialize_matrix_editor()
            self.matrix_view.set_matrix(None)
            self.route_view.init_empty_graph()

    def on_matrix_created(self, matrix):
        """Callback metoda volaná z MatrixEditor, když je vytvořena nová matice"""
        self.matrix = matrix
        self.matrix_view.set_matrix(matrix)
        self.log("Vytvořena nová matice vzdáleností")
        self.status_var.set("Nová matice vytvořena")
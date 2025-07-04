import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class MatrixView:
    def __init__(self, parent, notebook):
        self.parent = parent
        self.notebook = notebook
        self.matrix_tab = ttk.Frame(notebook, padding=10)
        self.notebook.add(self.matrix_tab, text="Matice")
        
        self.matrix = None
        self.solution = None
        self.highlight_var = tk.BooleanVar(value=True)
        
        self.create_ui()
    
    def create_ui(self):
        """Vytvoří komponenty pro zobrazení matice"""
        # Frame pro kontrolní prvky
        control_frame = ttk.Frame(self.matrix_tab)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Vysvětlující text
        ttk.Label(control_frame, text="Matice vzdáleností:").pack(side=tk.LEFT)
        
        # Přidání tlačítka pro uložení matice
        save_button = ttk.Button(control_frame, text="Uložit matici", 
                               command=self.save_matrix_to_excel)
        save_button.pack(side=tk.LEFT, padx=10)
        
        # Přidání tlačítka pro kontrolu symetrie
        check_symmetry_button = ttk.Button(control_frame, text="Kontrola symetrie", 
                                         command=self.check_matrix_symmetry)
        check_symmetry_button.pack(side=tk.LEFT, padx=10)
        
        # Přidání přepínače pro zobrazení zvýraznění v matici
        ttk.Checkbutton(control_frame, text="Zvýraznit vybrané hrany", 
                       variable=self.highlight_var,
                       command=lambda: self.display_matrix() if self.matrix is not None else None).pack(side=tk.RIGHT)
        
        # Frame pro Treeview (tabulku) s fixed layout
        self.matrix_container = ttk.Frame(self.matrix_tab)
        self.matrix_container.pack(fill=tk.BOTH, expand=True)
        
        # Vytvoříme Panedwindow pro tabulku a legendu
        paned = ttk.PanedWindow(self.matrix_container, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Frame pro tabulku
        tree_frame = ttk.Frame(paned)
        paned.add(tree_frame, weight=4)
        
        # Vytvoření Treeview pro zobrazení matice s lepším nastavením sloupců
        self.matrix_tree = ttk.Treeview(tree_frame)
        
        # Přidání scrollbarů
        y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.matrix_tree.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.matrix_tree.xview)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.matrix_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        self.matrix_tree.pack(fill=tk.BOTH, expand=True)
        
        # Nastavení fixní šířky pro sloupec indexů
        self.matrix_tree.column("#0", width=120, stretch=False)
        
        # Frame pro legendu
        legend_frame = ttk.LabelFrame(paned, text="Legenda", padding=10)
        paned.add(legend_frame, weight=1)
        
        ttk.Label(legend_frame, text="• Tučné písmo v exportovaném Excel souboru označuje hrany zahrnuté v optimálním řešení").pack(anchor="w")
        ttk.Label(legend_frame, text="• Hodnoty na diagonále by měly být výrazně vyšší než ostatní (nebo 0)").pack(anchor="w")
        ttk.Label(legend_frame, text="• Řešení zahrnuje návrat do výchozího bodu").pack(anchor="w")
    
    def set_matrix(self, matrix):
        """Nastaví matici a zobrazí ji"""
        self.matrix = matrix
        self.display_matrix()
    
    def set_solution(self, solution):
        """Nastaví řešení pro zvýraznění v matici"""
        self.solution = solution
        if self.matrix is not None:
            self.display_matrix()
    
    def display_matrix(self):
        """Zobrazí matici v Treeview"""
        if self.matrix is None:
            return
            
        # Vyčištění Treeview
        for item in self.matrix_tree.get_children():
            self.matrix_tree.delete(item)
        
        # Resetování sloupců
        self.matrix_tree["columns"] = list(self.matrix.columns)
        
        # Konfigurace hlavičky
        self.matrix_tree.heading("#0", text="Index")
        self.matrix_tree.column("#0", width=120, stretch=False)  # Fixní šířka pro indexy
        
        # Nastavení sloupců s optimalizovanými šířkami
        for col in self.matrix.columns:
            self.matrix_tree.heading(col, text=str(col))
            # Výpočet optimální šířky na základě délky obsahu
            max_width = max(len(str(col)) * 8, 50)  # Minimálně 50px
            self.matrix_tree.column(col, width=min(max_width, 100), stretch=True, anchor="center")
        
        # Přidání dat
        for idx, row in self.matrix.iterrows():
            values = [row[col] for col in self.matrix.columns]
            item_id = self.matrix_tree.insert("", "end", text=str(idx), values=values)
            
            # Zvýraznění buněk, které jsou v řešení (pokud existuje řešení)
            if self.solution and self.highlight_var.get():
                for edge in self.solution:
                    if edge[0] == idx:
                        col_idx = self.matrix.columns.get_loc(edge[1])
                        # Pouze celých řádků, což zde není ideální
                        self.matrix_tree.item(item_id, tags=("highlight",))
                        break
        
        # Přidání tagu pro zvýraznění
        self.matrix_tree.tag_configure("highlight", background='#e6f2ff')
    
    def save_matrix_to_excel(self):
        """Uloží aktuální matici do Excel souboru"""
        if self.matrix is None:
            messagebox.showerror("Chyba", "Žádná matice není načtena nebo vytvořena.")
            return
        
        # Otevřít dialog pro uložení
        file_path = filedialog.asksaveasfilename(
            title="Uložit matici do Excel souboru",
            defaultextension=".xlsx",
            filetypes=[("Excel soubory", "*.xlsx"), ("Všechny soubory", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Uložit matici do Excelu
            self.matrix.to_excel(file_path)
            self.parent.log(f"Matice uložena do souboru: {file_path}")
            messagebox.showinfo("Uloženo", f"Matice byla úspěšně uložena do:\n{file_path}")
            
            # Nastavit cestu k souboru jako vstupní soubor
            self.parent.input_file_path.set(file_path)
        except Exception as e:
            messagebox.showerror("Chyba při ukládání", f"Nastala chyba:\n{str(e)}")

    def check_matrix_symmetry(self):
        """Zkontroluje, zda je matice symetrická"""
        if self.matrix is None:
            messagebox.showinfo("Informace", "Žádná matice není načtena.")
            return
        
        # Kontrola symetrie
        is_symmetric = True
        asymmetric_points = []
        
        for i in range(len(self.matrix)):
            for j in range(i+1, len(self.matrix)):  # Pouze horní trojúhelníková část
                if abs(self.matrix.iloc[i, j] - self.matrix.iloc[j, i]) > 0.001:  # Tolerance pro float
                    is_symmetric = False
                    asymmetric_points.append((self.matrix.index[i], self.matrix.columns[j]))
                    
                    # Omezit počet nalezených bodů
                    if len(asymmetric_points) >= 5:
                        break
            
            if not is_symmetric and len(asymmetric_points) >= 5:
                break
        
        # Zobrazit výsledek
        if is_symmetric:
            messagebox.showinfo("Kontrola matice", "Matice je symetrická.")
        else:
            points_str = ", ".join([f"({a}, {b})" for a, b in asymmetric_points[:5]])
            if len(asymmetric_points) > 5:
                points_str += ", ..."
                
            if messagebox.askyesno(
                "Kontrola matice", 
                f"Matice není symetrická. Nesymetrické body: {points_str}\n\n"
                "Pro běžný TSP problém by matice měla být symetrická.\n"
                "Chcete vytvořit symetrickou verzi matice?"):
                self.create_symmetric_matrix()

    def create_symmetric_matrix(self):
        """Vytvoří symetrickou verzi aktuální matice (průměrováním hodnot)"""
        if self.matrix is None:
            return
        
        # Vytvořit kopii matice
        symmetric_matrix = self.matrix.copy()
        
        # Pro každou dvojici bodů vzít průměr hodnot
        for i in range(len(self.matrix)):
            for j in range(i+1, len(self.matrix)):  # Pouze horní trojúhelníková část
                avg_value = (self.matrix.iloc[i, j] + self.matrix.iloc[j, i]) / 2
                symmetric_matrix.iloc[i, j] = avg_value
                symmetric_matrix.iloc[j, i] = avg_value
        
        # Nahradit původní matici
        self.matrix = symmetric_matrix
        
        # Zobrazit aktualizovanou matici
        self.display_matrix()
        
        # Informovat uživatele
        self.parent.log("Vytvořena symetrická verze matice.")
        messagebox.showinfo("Matice aktualizována", "Byla vytvořena symetrická verze matice.")
        
        # Aktualizovat matici v aplikaci
        self.parent.matrix = symmetric_matrix
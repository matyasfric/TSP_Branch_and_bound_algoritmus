import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import FancyArrowPatch
from gui.utils import get_color_for_index, lighten_color

class RouteView:
    def __init__(self, parent, notebook):
        self.parent = parent
        self.notebook = notebook
        self.route_tab = ttk.Frame(notebook, padding=10)
        self.notebook.add(self.route_tab, text="Vizualizace trasy")
        
        # Proměnné pro vizualizaci
        self.matrix = None
        self.solution = None
        self.route_sequence = None
        self.selected_node = None
        self.node_colors = {}
        
        self.viz_style = tk.StringVar(value="modern")
        
        self.create_ui()
    
    def create_ui(self):
        """Vytvoří komponenty pro vizualizaci trasy"""
        # Rozdělit okno vizualizace na dvě části - graf a detaily
        self.route_paned = ttk.PanedWindow(self.route_tab, orient=tk.HORIZONTAL)
        self.route_paned.pack(fill=tk.BOTH, expand=True)
        
        # Levá část - graf
        self.graph_frame = ttk.Frame(self.route_paned)
        self.route_paned.add(self.graph_frame, weight=3)
        
        # Pravá část - detaily trasy
        self.detail_frame = ttk.Frame(self.route_paned)
        self.route_paned.add(self.detail_frame, weight=1)
        
        # Nastavení grafu
        self.fig, self.ax = plt.subplots(figsize=(6, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Připojení událostí pro interakci s grafem
        self.canvas.mpl_connect('button_press_event', self.on_graph_click)
        
        # Toolbar pro graf
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph_frame)
        self.toolbar.update()
        
        # Přidání popisku pro instruktáž
        self.graph_instr = ttk.Label(self.graph_frame, 
                                   text="Klikněte na bod v grafu pro zobrazení detailů")
        self.graph_instr.pack(pady=5)
        
        # Vytvoření ovládacích prvků pro detaily
        self.create_detail_panel()
        
        # Inicializovat prázdný graf
        self.init_empty_graph()
    
    def create_detail_panel(self):
        """Vytvoří panel s detaily o trase"""
        # Hlavní kontejner pro detaily s možností scrollování
        detail_container = ttk.Frame(self.detail_frame)
        detail_container.pack(fill=tk.BOTH, expand=True)
        
        # Ovládací prvky
        control_frame = ttk.LabelFrame(detail_container, text="Nastavení zobrazení")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Přepínač mezi režimy vizualizace
        ttk.Radiobutton(control_frame, text="Moderní styl", 
                      variable=self.viz_style, value="modern",
                      command=self.update_visualization).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        ttk.Radiobutton(control_frame, text="Klasický styl", 
                      variable=self.viz_style, value="classic",
                      command=self.update_visualization).grid(row=1, column=0, sticky="w", padx=5, pady=2)
                      
        ttk.Radiobutton(control_frame, text="Schematický styl", 
                      variable=self.viz_style, value="schema",
                      command=self.update_visualization).grid(row=2, column=0, sticky="w", padx=5, pady=2)
        
        # Vytvoření tabulky pro zobrazení seznamu bodů a jejich návazností
        list_frame = ttk.LabelFrame(detail_container, text="Seznam bodů")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview pro seznam bodů
        self.node_tree = ttk.Treeview(list_frame, columns=("pořadí", "do_bodu", "vzdálenost"))
        self.node_tree.heading("#0", text="Bod")
        self.node_tree.heading("pořadí", text="Pořadí")
        self.node_tree.heading("do_bodu", text="Do bodu")
        self.node_tree.heading("vzdálenost", text="Vzdálenost")
        
        self.node_tree.column("#0", width=100)
        self.node_tree.column("pořadí", width=50, anchor="center")
        self.node_tree.column("do_bodu", width=100)
        self.node_tree.column("vzdálenost", width=80, anchor="center")
        
        # Scrollbar pro seznam
        node_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.node_tree.yview)
        self.node_tree.configure(yscrollcommand=node_scroll.set)
        
        # Umístění seznamu a scrollbaru
        node_scroll.pack(side="right", fill="y")
        self.node_tree.pack(side="left", fill="both", expand=True)
        
        # Připojení události při výběru uzlu v seznamu
        self.node_tree.bind("<<TreeviewSelect>>", self.on_node_select)
        
        # Sekce pro statistiky trasy
        stats_frame = ttk.LabelFrame(detail_container, text="Statistiky trasy")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Celková vzdálenost
        self.route_stats = ttk.Label(stats_frame, text="Celková vzdálenost: -")
        self.route_stats.pack(anchor="w", padx=5, pady=2)
        
        # Počet bodů
        self.node_count = ttk.Label(stats_frame, text="Počet bodů: -")
        self.node_count.pack(anchor="w", padx=5, pady=2)
        
        # Vybraný bod - detailní informace
        self.node_detail_frame = ttk.LabelFrame(detail_container, text="Detaily vybraného bodu")
        self.node_detail_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.node_detail = ttk.Label(self.node_detail_frame, text="Klikněte na bod v grafu nebo v seznamu")
        self.node_detail.pack(anchor="w", padx=5, pady=5)
    
    def init_empty_graph(self):
        """Inicializuje prázdný graf s instrukcemi"""
        self.ax.clear()
        self.ax.text(0.5, 0.5, "Pro vizualizaci spusťte optimalizaci", 
                    ha='center', va='center', fontsize=14, color='gray',
                    transform=self.ax.transAxes)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()
    
    def set_data(self, matrix, solution, route_sequence):
        """Nastaví data pro vizualizaci trasy"""
        self.matrix = matrix
        self.solution = solution
        self.route_sequence = route_sequence
        
        # Generovat barvy pro uzly
        self.generate_node_colors()
        
        # Aktualizovat vizualizaci
        self.update_visualization()
        
        # Aktualizovat statistiky
        self.update_stats()
        
        # Naplnit seznam bodů
        self.populate_node_list()
    
    def generate_node_colors(self):
        """Vygeneruje konzistentní barvy pro uzly"""
        if not self.route_sequence:
            return
            
        # Použít předem definované barvy pro lepší čitelnost
        base_colors = [
            "#3498db",  # modrá
            "#e74c3c",  # červená
            "#2ecc71",  # zelená
            "#f39c12",  # oranžová
            "#9b59b6",  # fialová
            "#1abc9c",  # tyrkysová
            "#34495e",  # tmavě modrá
            "#95a5a6",  # šedá
            "#d35400",  # hnědá
            "#27ae60",  # tmavě zelená
        ]
        
        # Resetovat slovník barev
        self.node_colors = {}
        
        # Přiřadit každému uzlu barvu
        for i, node in enumerate(self.route_sequence):
            color_idx = i % len(base_colors)
            self.node_colors[node] = base_colors[color_idx]
    
    def update_stats(self):
        """Aktualizuje statistiky o trase"""
        if not self.solution or self.matrix is None:
            return
            
        # Výpočet celkové vzdálenosti
        total_distance = sum(self.matrix.loc[node[0], node[1]] for node in self.solution)
        
        # Aktualizovat statistiky
        self.route_stats.config(text=f"Celková vzdálenost: {total_distance}")
        self.node_count.config(text=f"Počet bodů: {len(set(self.route_sequence))}")
    
    def populate_node_list(self):
        """Naplní seznam uzlů v detailním panelu"""
        if not self.solution or not self.route_sequence or self.matrix is None:
            return
            
        # Nejprve vyčistit seznam
        for item in self.node_tree.get_children():
            self.node_tree.delete(item)
        
        # Pro každý uzel v sekvenci přidat řádek do seznamu
        for i, node in enumerate(self.route_sequence):
            next_node = self.route_sequence[(i + 1) % len(self.route_sequence)]
            distance = self.matrix.loc[node, next_node]
            
            # Přidat řádek do seznamu
            self.node_tree.insert("", "end", text=node, values=(i+1, next_node, distance),
                                 tags=(f"color_{i % 10}",))
        
        # Nastavit barvy řádků
        for i in range(10):
            color = get_color_for_index(i)
            self.node_tree.tag_configure(f"color_{i}", background=lighten_color(color))
    
    def update_visualization(self):
        """Aktualizuje vizualizaci trasy podle zvoleného stylu"""
        if not self.solution:
            self.init_empty_graph()
            return
        
        # Získat zvolený styl vizualizace
        viz_style = self.viz_style.get()
        
        if viz_style == "modern":
            self.visualize_modern_style()
        elif viz_style == "classic":
            self.visualize_classic_style()
        elif viz_style == "schema":
            self.visualize_schema_style()
    
    def visualize_modern_style(self):
        """Moderní styl vizualizace s barevným odlišením a dynamickým rozmístěním"""
        self.ax.clear()
        
        if not self.route_sequence:
            self.init_empty_graph()
            return
        
        # Generovat pozice bodů v kruhu
        positions = {}
        num_nodes = len(set(self.route_sequence))
        
        # Upravit layout podle počtu bodů
        radius = 0.8
        angle_start = -np.pi / 2  # Začít nahoře
        
        for i, node in enumerate(self.route_sequence):
            if node in positions:
                continue
                
            angle = angle_start + (i * 2 * np.pi / num_nodes)
            positions[node] = (radius * np.cos(angle), radius * np.sin(angle))
        
        # Vykreslit hrany jako průhledné šipky s plynulým barevným přechodem
        for i in range(len(self.route_sequence)):
            node = self.route_sequence[i]
            next_node = self.route_sequence[(i + 1) % len(self.route_sequence)]
            
            # Souřadnice bodů
            x1, y1 = positions[node]
            x2, y2 = positions[next_node]
            
            # Barva podle pořadí s plynulým přechodem
            color = self.node_colors.get(node, '#3498db')
            next_color = self.node_colors.get(next_node, '#3498db')
            
            # Vykreslení plynulé šipky
            arrow = FancyArrowPatch(
                (x1, y1),
                (x2, y2),
                connectionstyle=f"arc3,rad=0.1",
                arrowstyle="Simple,head_width=10,head_length=12",
                color=color,
                linewidth=2,
                alpha=0.7,
                zorder=1
            )
            self.ax.add_patch(arrow)
            
            # Přidat číslo pořadí hrany
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            # Posunout mírně stranou od šipky
            angle = np.arctan2(y2 - y1, x2 - x1)
            mid_x += 0.05 * np.sin(angle)
            mid_y -= 0.05 * np.cos(angle)
            
            # Přidat číslo se světlým pozadím
            self.ax.text(mid_x, mid_y, f"{i+1}", ha='center', va='center',
                       fontsize=9, fontweight='bold',
                       bbox=dict(boxstyle="circle", fc="white", ec=color, alpha=0.8))
        
        # Vykreslit body s čísly pořadí
        for i, node in enumerate(self.route_sequence):
            if node == self.route_sequence[0]:  # Zvýraznit první bod
                continue  # Bude vykreslen zvlášť
                
            x, y = positions[node]
            
            # Základní barva bodu
            color = self.node_colors.get(node, '#3498db')
            
            # Vykreslit bod
            self.ax.scatter(x, y, s=300, color=color, edgecolor='white', 
                          linewidth=2, alpha=0.8, zorder=2)
            
            # Přidat číslo do bodu
            self.ax.text(x, y, str(self.route_sequence.index(node) + 1), 
                       ha='center', va='center', color='white', 
                       fontsize=10, fontweight='bold', zorder=3)
        
        # Zvýraznit startovací/cílový bod
        start_node = self.route_sequence[0]
        x, y = positions[start_node]
        self.ax.scatter(x, y, s=400, color='#e74c3c', edgecolor='white',
                      linewidth=2, alpha=0.8, zorder=2)
        self.ax.text(x, y, "1", ha='center', va='center', color='white',
                   fontsize=10, fontweight='bold', zorder=3)
        
        # Přidat popisky bodů vedle bodů
        for node, pos in positions.items():
            x, y = pos
            # Vypočítat pozici popisku (mírně posunutou od bodu)
            label_x = x * 1.15
            label_y = y * 1.15
            
            self.ax.text(label_x, label_y, str(node), ha='center', va='center',
                       fontsize=9, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7))
        
        # Nastavení grafu
        self.ax.set_title("Optimalizovaná trasa", fontsize=14)
        self.ax.axis('equal')
        self.ax.axis('off')
        self.ax.set_xlim(-1.3, 1.3)
        self.ax.set_ylim(-1.3, 1.3)
        
        # Přidat legendu pro barevné značení
        if len(self.route_sequence) <= 20:  # Pouze pro menší grafy
            legend_elements = []
            for i, node in enumerate(self.route_sequence[:10]):  # Max 10 položek v legendě
                color = self.node_colors.get(node, '#3498db')
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                              markerfacecolor=color, markersize=10, 
                                              label=f"{i+1}: {node}"))
            
            self.ax.legend(handles=legend_elements, loc='upper right', 
                         bbox_to_anchor=(1.3, 1.0), fontsize=9)
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def visualize_classic_style(self):
        """Klasický styl vizualizace s číselnými popisky"""
        self.ax.clear()
        
        if not self.route_sequence:
            self.init_empty_graph()
            return
        
        # Generovat pozice bodů v mřížce
        positions = {}
        nodes_list = list(set(self.route_sequence))
        num_nodes = len(nodes_list)
        
        # Vypočítat velikost mřížky
        grid_size = int(np.ceil(np.sqrt(num_nodes)))
        
        # Rozmístit body v mřížce
        for i, node in enumerate(nodes_list):
            row = i // grid_size
            col = i % grid_size
            
            # Normalizovat pozice do rozsahu [-1, 1]
            x = (col * 2.0 / (grid_size - 1 or 1)) - 1.0
            y = 1.0 - (row * 2.0 / (grid_size - 1 or 1))
            
            positions[node] = (x, y)
        
        # Vykreslit hrany jako čáry
        for i in range(len(self.route_sequence)):
            node = self.route_sequence[i]
            next_node = self.route_sequence[(i + 1) % len(self.route_sequence)]
            
            x1, y1 = positions[node]
            x2, y2 = positions[next_node]
            
            # Vykreslení šipky
            self.ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                           arrowprops=dict(arrowstyle="->", lw=1.5, color='blue'))
            
            # Přidat číslo pořadí hrany
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            self.ax.text(mid_x, mid_y, f"{i+1}", ha='center', va='center',
                       fontsize=8, bbox=dict(boxstyle="round", fc="white", alpha=0.7))
        
        # Vykreslit body
        for node, pos in positions.items():
            x, y = pos
            
            # Zjistit pořadí bodu v sekvenci
            node_index = self.route_sequence.index(node) + 1
            
            # Vykreslit bod s popiskem uvnitř
            self.ax.scatter(x, y, s=200, color='lightblue', edgecolor='blue', linewidth=1.5)
            self.ax.text(x, y, str(node_index), ha='center', va='center', fontsize=10)
            
            # Přidat popisek pod bod
            self.ax.text(x, y - 0.1, str(node), ha='center', va='top', fontsize=8)
        
        # Nastavení grafu
        self.ax.set_title("Optimalizovaná trasa - klasický styl", fontsize=14)
        self.ax.grid(True, linestyle='--', alpha=0.3)
        self.ax.set_xlim(-1.2, 1.2)
        self.ax.set_ylim(-1.2, 1.2)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def visualize_schema_style(self):
        """Schematický styl vizualizace jako liniové schéma"""
        self.ax.clear()
        
        if not self.route_sequence:
            self.init_empty_graph()
            return
        
        # Lineární schéma - body v řadě s šipkami mezi nimi
        num_nodes = len(self.route_sequence)
        
        # Vytvořit lineární rozvržení
        x_positions = np.linspace(-0.9, 0.9, num_nodes)
        y_positions = np.zeros(num_nodes)
        
        # Přidat mírné vychýlení pro lepší čitelnost
        for i in range(num_nodes):
            if i % 2 == 1:
                y_positions[i] = 0.1
            else:
                y_positions[i] = -0.1
        
        # Vykreslit hrany jako šipky
        for i in range(num_nodes):
            node = self.route_sequence[i]
            next_node = self.route_sequence[(i + 1) % num_nodes]
            next_idx = (i + 1) % num_nodes
            
            x1, y1 = x_positions[i], y_positions[i]
            x2, y2 = x_positions[next_idx], y_positions[next_idx]
            
            # Vykreslení šipky mezi body
            self.ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                           arrowprops=dict(arrowstyle="->", lw=1.5, 
                                          connectionstyle="arc3,rad=0.2",
                                          color='gray'))
            
            # Přidat vzdálenost nad šipku
            distance = self.matrix.loc[node, next_node]
            
            # Vypočítat pozici pro text vzdálenosti
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            
            # Posunout text vzdálenosti nad šipku
            if y1 == y2:
                text_y = mid_y + 0.05
            else:
                text_y = mid_y + 0.1
                
            self.ax.text(mid_x, text_y, f"{distance}", ha='center', va='bottom',
                       fontsize=8, bbox=dict(boxstyle="round", fc="white", alpha=0.7))
        
        # Vykreslit body
        for i, node in enumerate(self.route_sequence):
            x, y = x_positions[i], y_positions[i]
            
            # První bod zvýraznit
            if i == 0:
                node_color = 'red'
            else:
                node_color = 'skyblue'
                
            # Vykreslit bod
            self.ax.scatter(x, y, s=300, color=node_color, edgecolor='black', linewidth=1)
            
            # Přidat popisek bodu
            self.ax.text(x, y, f"{i+1}", ha='center', va='center', fontsize=10, fontweight='bold', color='white')
            
            # Přidat název bodu pod bod
            self.ax.text(x, y - 0.15, str(node), ha='center', va='top', fontsize=9,
                       bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.9))
        
        # Nastavení grafu
        self.ax.set_title("Schéma trasy", fontsize=14)
        self.ax.axis('equal')
        self.ax.axis('off')
        self.ax.set_xlim(-1.1, 1.1)
        self.ax.set_ylim(-0.5, 0.5)
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def on_graph_click(self, event):
        """Reakce na kliknutí do grafu"""
        if not self.solution or not self.route_sequence or self.matrix is None:
            return
            
        if event.xdata is None or event.ydata is None:
            return
            
        # Generovat pozice bodů (musí být stejné jako ve vizualizaci)
        positions = {}
        viz_style = self.viz_style.get()
        
        if viz_style == "modern":
            # Pozice v kruhu (stejné jako ve visualize_modern_style)
            radius = 0.8
            angle_start = -np.pi / 2
            num_nodes = len(set(self.route_sequence))
            
            for i, node in enumerate(self.route_sequence):
                if node in positions:
                    continue
                    
                angle = angle_start + (i * 2 * np.pi / num_nodes)
                positions[node] = (radius * np.cos(angle), radius * np.sin(angle))
                
        elif viz_style == "classic":
            # Pozice v mřížce (stejné jako ve visualize_classic_style)
            nodes_list = list(set(self.route_sequence))
            num_nodes = len(nodes_list)
            grid_size = int(np.ceil(np.sqrt(num_nodes)))
            
            for i, node in enumerate(nodes_list):
                row = i // grid_size
                col = i % grid_size
                
                # Normalizovat pozice do rozsahu [-1, 1]
                x = (col * 2.0 / (grid_size - 1 or 1)) - 1.0
                y = 1.0 - (row * 2.0 / (grid_size - 1 or 1))
                
                positions[node] = (x, y)
                
        elif viz_style == "schema":
            # Lineární pozice (stejné jako ve visualize_schema_style)
            num_nodes = len(self.route_sequence)
            x_positions = np.linspace(-0.9, 0.9, num_nodes)
            y_positions = np.zeros(num_nodes)
            
            # Přidat mírné vychýlení
            for i in range(num_nodes):
                if i % 2 == 1:
                    y_positions[i] = 0.1
                else:
                    y_positions[i] = -0.1
            
            for i, node in enumerate(self.route_sequence):
                positions[node] = (x_positions[i], y_positions[i])
        
        # Najít nejbližší bod ke kliknutí
        min_distance = float('inf')
        closest_node = None
        
        for node, pos in positions.items():
            x, y = pos
            distance = ((x - event.xdata) ** 2 + (y - event.ydata) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_node = node
        
        # Pokud je bod dostatečně blízko (tolerance kliknutí)
        if min_distance < 0.1:
            self.selected_node = closest_node
            self.update_node_details(closest_node)
            
            # Označit vybraný řádek v seznamu
            for item in self.node_tree.get_children():
                if self.node_tree.item(item, "text") == closest_node:
                    self.node_tree.selection_set(item)
                    self.node_tree.see(item)
                    break
    
    def on_node_select(self, event):
        """Reakce na výběr uzlu v seznamu"""
        selected_items = self.node_tree.selection()
        if not selected_items:
            return
            
        item = selected_items[0]
        node = self.node_tree.item(item, "text")
        
        self.selected_node = node
        self.update_node_details(node)
    
    def update_node_details(self, node):
        """Aktualizuje detaily o vybraném uzlu"""
        if not node or not self.route_sequence or self.matrix is None:
            return
        
        # Najít pozici uzlu v sekvenci
        node_index = self.route_sequence.index(node)
        next_node = self.route_sequence[(node_index + 1) % len(self.route_sequence)]
        prev_node = self.route_sequence[(node_index - 1) % len(self.route_sequence)]
        
        # Získat vzdálenosti
        dist_to_next = self.matrix.loc[node, next_node]
        dist_from_prev = self.matrix.loc[prev_node, node]
        
        # Sestavit text s detaily
        details = f"Bod: {node}\n"
        details += f"Pořadí v trase: {node_index + 1}/{len(self.route_sequence)}\n"
        details += f"Předchozí bod: {prev_node} (vzdálenost: {dist_from_prev})\n"
        details += f"Následující bod: {next_node} (vzdálenost: {dist_to_next})\n"
        
        # Celková vzdálenost od tohoto bodu
        total_from_here = 0
        curr = node
        for _ in range(len(self.route_sequence)):
            next_n = self.route_sequence[(self.route_sequence.index(curr) + 1) % len(self.route_sequence)]
            total_from_here += self.matrix.loc[curr, next_n]
            curr = next_n
        
        details += f"Celková vzdálenost od tohoto bodu: {total_from_here}"
        
        # Aktualizovat text v detailním panelu
        self.node_detail.config(text=details)
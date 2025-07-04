import pandas as pd
import re
from openpyxl.utils import get_column_letter

def read_excel(filename):
    """Načte data z Excel souboru"""
    df = pd.read_excel(filename, index_col=0)
    return df

# odstraneni spec. znaku z nazvu listu
def sanitize_sheet_name(name):
    return re.sub(r'[\\/*?[\]:]', '', name)[:31]

# zapis vystupu do excelu - openpyxl
def write_excel(matrix, solution, cycles, filename):
    print("Zapisovani do Excelu.")
    writer = pd.ExcelWriter(filename, engine='openpyxl')
    matrix.to_excel(writer, sheet_name='Matice_optimum')
    workbook = writer.book
    worksheet = writer.sheets['Matice_optimum']
    
    # tucne oznacit hodnoty vybrane algoritmem v matici
    for edge in solution:
        row_index = matrix.index.get_loc(edge[0]) + 2
        col_index = matrix.columns.get_loc(edge[1]) + 2
        cell = worksheet.cell(row=row_index, column=col_index)
        cell.font = cell.font.copy(bold=True)

    # výpočet vzdálenosti
    sum_distance = sum(matrix.loc[node[0], node[1]] for node in solution)
    pd.DataFrame({'Soucet_vzdalenosti': [sum_distance]}).to_excel(writer, sheet_name='Soucet_vzdalenosti', index=False)

    # posloupnost míst-zapis do excelu
    if solution:  # kontrola, zda máme řešení
        nodes_sequence = [solution[0][0]]
        current_node = solution[0][1]
        while current_node != solution[0][0]:
            nodes_sequence.append(current_node)
            for edge in solution:
                if edge[0] == current_node:
                    current_node = edge[1]
                    break
        nodes_sequence.append(solution[0][0])  # přidání návratu do výchozího bodu
        pd.DataFrame({'Posloupnost_mist': nodes_sequence}).to_excel(writer, sheet_name='Posloupnost_mist', index=False)

    # okruhy a jejich delky-zapis do excelu
    cycle_data = []
    for cycle in cycles:
        cycle_length = matrix.loc[cycle[-1], cycle[0]] + sum(matrix.loc[cycle[j], cycle[j + 1]] for j in range(len(cycle) - 1))
        cycle_data.append((", ".join(cycle), cycle_length))
    
    if cycle_data:  # kontrola, zda máme data
        pd.DataFrame({'Okruh': [data[0] for data in cycle_data],
                    'Vzdalenost': [data[1] for data in cycle_data]}).to_excel(
            writer, sheet_name='Alternativni_okruhy', index=False)

    writer._save()
    print("Vystup se ulozi do: ", filename)
import pandas as pd
from pulp import *
from itertools import permutations
import re


# načtení dat excelu
def read_excel(filename):
    df = pd.read_excel(filename, index_col=0)
    return df

# definování fce pro řešení ODP
def solve_tsp(matrix):
    num_nodes = len(matrix)
    nodes = list(matrix.index)

    # inicializace linearniho programovani
    prob = LpProblem("TSP", LpMinimize)

    # existence hrany mezi dvěma hranami
    x = LpVariable.dicts("x", [(i, j) for i in nodes for j in nodes], 0, 1, LpBinary)

    # účelová fce-->minimalizace
    prob += lpSum(matrix.iloc[i, j] * x[(nodes[i], nodes[j])] for i in range(num_nodes) for j in range(num_nodes))

    # podm. každé místo jen jednou navštívit
    for i in nodes:
        prob += lpSum(x[(i, j)] for j in nodes) == 1
        prob += lpSum(x[(j, i)] for j in nodes) == 1

    # zamezeni zacykleni
    u = LpVariable.dicts("u", nodes, 0, num_nodes - 1, LpInteger)
    for i in nodes:
        for j in nodes:
            if i != j and (i != nodes[0] and j != nodes[0]):
                prob += u[i] - u[j] + num_nodes * x[(i, j)] <= num_nodes - 1

    # reseni problemu LP - PuLP knihovna
    prob.solve()

    # overeni hrany maji hodnotu 1, pridani do seznamu solution
    solution = []
    for i in range(num_nodes):
        for j in range(num_nodes):
            if value(x[(nodes[i], nodes[j])]) == 1:
                solution.append((nodes[i], nodes[j]))

    return solution

# další možné okruhy
def find_cycles(matrix, solution):
    cycles = []
    visited = set()
    for edge in solution:
        visited.add(edge[0])
        visited.add(edge[1])

    nodes = list(matrix.index)
    for node in nodes:
        if node not in visited:
            continue
        current_node = node
        cycle = [current_node]
        while True:
            next_node = None
            for edge in solution:
                if edge[0] == current_node:
                    next_node = edge[1]
                    break
            if next_node is None:
                break
            if next_node == node:
                cycles.append(cycle)
                break
            cycle.append(next_node)
            current_node = next_node

    return cycles

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
    nodes_sequence = [solution[0][0]]
    current_node = solution[0][1]
    while current_node != solution[0][0]:
        nodes_sequence.append(current_node)
        for edge in solution:
            if edge[0] == current_node:
                current_node = edge[1]
                break
    nodes_sequence.append(solution[0][0])
    pd.DataFrame({'Posloupnost_mist': nodes_sequence}).to_excel(writer, sheet_name='Posloupnost_mist', index=False)

    # okruhy a jejich delky-zapis do excelu
    cycle_data = []
    for cycle in cycles:
        cycle_length = matrix.loc[cycle[-1], cycle[0]] + sum(matrix.loc[cycle[j], cycle[j + 1]] for j in range(len(cycle) - 1))
        cycle_data.append((", ".join(cycle), cycle_length))
    
    pd.DataFrame({'Okruh': [data[0] for data in cycle_data],
                  'Vzdalenost': [data[1] for data in cycle_data]}).to_excel(
        writer, sheet_name='Alternativni_okruhy', index=False)

    writer._save()
    print("Vystup se ulozi do: ", filename)

# main fce
def main(input_file, output_file):
    # nacteni vstupni matice z excelu
    matrix = read_excel(input_file)

    # reseni TSP
    solution = solve_tsp(matrix)

    # alternativni okruhy
    cycles = find_cycles(matrix, solution)

    # zapsani vystupu do excelu
    write_excel(matrix, solution, cycles, output_file)

if __name__ == "__main__":
    input_file = "input.xlsx"  # tohle je nazev excelu se vstupni matici sazeb, lze zmenit na nazev excel souboru
    output_file = "output_metoda_branch_and_bound.xlsx"  # takhle se bude jmenovat soubor s vystupem, lze prejmenovat
    main(input_file, output_file)

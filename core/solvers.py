from pulp import *

# definování fce pro řešení ODP
def solve_tsp(matrix):
    num_nodes = len(matrix)
    nodes = list(matrix.index)

    # inicializace linearniho programovani
    prob = LpProblem("TSP", LpMinimize)

    # existence hrany mezi dvěma hranami - nyní vynecháváme diagonálu (i != j)
    x = LpVariable.dicts("x", [(i, j) for i in nodes for j in nodes if i != j], 0, 1, LpBinary)

    # účelová fce-->minimalizace - vynecháváme diagonální prvky
    # Opravená verze - explicitně získáváme hodnotu z DataFrame
    prob += lpSum(matrix.loc[i, j] * x[(i, j)] for i in nodes for j in nodes if i != j)

    # podm. každé místo jen jednou navštívit - vynecháváme diagonálu
    for i in nodes:
        prob += lpSum(x[(i, j)] for j in nodes if i != j) == 1  # z každého bodu vychází právě jedna hrana
        prob += lpSum(x[(j, i)] for j in nodes if i != j) == 1  # do každého bodu vchází právě jedna hrana

    # zamezeni zacykleni - Miller-Tucker-Zemlin podmínky
    u = LpVariable.dicts("u", nodes, 0, num_nodes - 1, LpInteger)
    for i in nodes:
        for j in nodes:
            # Oprava podmínky - explicitně porovnáváme s prvním uzlem
            if i != j and i != nodes[0] and j != nodes[0]:  # vynecháváme diagonálu a výchozí bod
                prob += u[i] - u[j] + num_nodes * x[(i, j)] <= num_nodes - 1

    # reseni problemu LP - PuLP knihovna
    prob.solve(PULP_CBC_CMD(msg=False))  # potlačíme výpis zpráv

    # overeni které hrany maji hodnotu 1, pridani do seznamu solution
    solution = []
    for i in nodes:
        for j in nodes:
            if i != j and value(x[(i, j)]) == 1:  # ignorujeme diagonálu
                solution.append((i, j))

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
        # Opravena podmínka - explicitní kontrola
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
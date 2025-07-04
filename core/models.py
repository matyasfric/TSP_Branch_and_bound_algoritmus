# Tento soubor může obsahovat datové modely a struktury pro TSP problém
# V současné implementaci nejsou explicitní datové modely - používají se pandas DataFrame
# a seznamy, ale můžeme zde připravit místo pro budoucí rozšíření

from dataclasses import dataclass
from typing import List, Tuple, Optional

# Příklad možného datového modelu (nepoužívá se v současné implementaci)
@dataclass
class TSPSolution:
    """Datový model pro řešení TSP problému"""
    edges: List[Tuple[str, str]]
    total_distance: float
    node_sequence: List[str]
    
    @property
    def num_nodes(self) -> int:
        """Vrátí počet uzlů v řešení"""
        return len(set([node for edge in self.edges for node in edge]))
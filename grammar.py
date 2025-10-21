from collections import defaultdict
from typing import Set, Dict, List, Tuple


class Grammar:
    """Representa una gramática libre de contexto"""

    def __init__(self, productions: Dict[str, List[List[str]]], start_symbol: str):
        """
        Args:
            productions: {no_terminal: [[símbolos], [símbolos], ...]}
            start_symbol: símbolo inicial de la gramática

        Ejemplo:
            Grammar({'S': [['C', 'C']], 'C': [['c', 'C'], ['d']]}, 'S')
        """
        self.productions = productions
        self.start_symbol = start_symbol
        # Crear símbolo inicial aumentado (solo una capa)
        self.augmented_start = f"{start_symbol}'"

        # Crear la producción aumentada: S' -> S
        self.all_productions = [(self.augmented_start, [start_symbol])]

        # Agregar el resto de las producciones de la gramática original
        for lhs, rhs_list in productions.items():
            for rhs in rhs_list:
                self.all_productions.append((lhs, rhs))

        # Ajustar el símbolo inicial (el original sigue siendo 'S')
        self.start_symbol = start_symbol

        # Definir los no terminales
        self.non_terminals = set(productions.keys()) | {self.augmented_start}

        # Detectar terminales
        self.terminals = set()
        for _, rhs_list in productions.items():
            for rhs in rhs_list:
                for symbol in rhs:
                    if symbol not in self.non_terminals and symbol != 'ε':
                        self.terminals.add(symbol)

        # Identificar terminales y no terminales
        self.non_terminals = set(productions.keys()) | {self.augmented_start}
        self.terminals = set()
        for _, rhs_list in productions.items():
            for rhs in rhs_list:
                for symbol in rhs:
                    if symbol not in self.non_terminals and symbol != 'ε':
                        self.terminals.add(symbol)

    def is_terminal(self, symbol: str) -> bool:
        """Verifica si un símbolo es terminal"""
        return symbol not in self.non_terminals and symbol != 'ε'

    def get_production_number(self, lhs: str, rhs: List[str]) -> int:
        """Obtiene el número de una producción"""
        for idx, (prod_lhs, prod_rhs) in enumerate(self.all_productions):
            if prod_lhs == lhs and prod_rhs == rhs:
                return idx
        return -1

    def __str__(self):
        """Representación en string de la gramática"""
        result = []
        for lhs, rhs_list in self.productions.items():
            for rhs in rhs_list:
                rhs_str = ' '.join(rhs) if rhs else 'ε'
                result.append(f"{lhs} -> {rhs_str}")
        return '\n'.join(result)


def read_grammar_from_file(filename: str) -> Grammar:
    """
    Lee una gramática desde un archivo.

    Formato del archivo:
        S -> C C
        C -> c C | d
        # Comentarios con #

    Args:
        filename: ruta del archivo

    Returns:
        Grammar: objeto Grammar construido
    """
    productions = defaultdict(list)
    start_symbol = None

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split('->')
            if len(parts) != 2:
                continue

            lhs = parts[0].strip()
            if start_symbol is None:
                start_symbol = lhs

            rhs_alternatives = parts[1].split('|')
            for rhs in rhs_alternatives:
                symbols = rhs.strip().split()
                productions[lhs].append(symbols)

    return Grammar(dict(productions), start_symbol)

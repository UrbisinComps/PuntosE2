from typing import Set, List


class FirstCalculator:
    """Calcula los conjuntos FIRST para una gramática"""

    def __init__(self, grammar):
        """
        Args:
            grammar: objeto Grammar
        """
        self.grammar = grammar
        self.first_sets = {}
        self._compute()

    def _compute(self):
        """Calcula los conjuntos FIRST para todos los símbolos"""
        # Inicializar FIRST para terminales
        for terminal in self.grammar.terminals:
            self.first_sets[terminal] = {terminal}

        # Inicializar FIRST para no terminales
        for non_terminal in self.grammar.non_terminals:
            self.first_sets[non_terminal] = set()

        # Iteración hasta punto fijo
        changed = True
        while changed:
            changed = False
            for lhs, rhs in self.grammar.all_productions:
                old_size = len(self.first_sets[lhs])

                if not rhs or rhs == ['ε']:
                    self.first_sets[lhs].add('ε')
                else:
                    for symbol in rhs:
                        if symbol == 'ε':
                            self.first_sets[lhs].add('ε')
                            break

                        # Agregar FIRST(symbol) - {ε}
                        symbol_first = self.first_sets.get(symbol, {symbol})
                        self.first_sets[lhs].update(symbol_first - {'ε'})

                        # Si symbol no puede derivar en ε, parar
                        if 'ε' not in symbol_first:
                            break
                    else:
                        # Todos los símbolos pueden derivar en ε
                        self.first_sets[lhs].add('ε')

                if len(self.first_sets[lhs]) > old_size:
                    changed = True

    def get_first(self, symbol: str) -> Set[str]:
        """Obtiene FIRST de un símbolo"""
        return self.first_sets.get(symbol, {symbol})

    def first_of_string(self, symbols: List[str]) -> Set[str]:
        """Calcula FIRST de una cadena de símbolos"""
        if not symbols:
            return {'ε'}

        result = set()
        for symbol in symbols:
            symbol_first = self.first_sets.get(symbol, {symbol})
            result.update(symbol_first - {'ε'})

            if 'ε' not in symbol_first:
                break
        else:
            result.add('ε')

        return result

    def print_sets(self):
        """Imprime los conjuntos FIRST"""
        print("\n" + "=" * 60)
        print("CONJUNTOS FIRST")
        print("=" * 60)
        for symbol in sorted(self.grammar.non_terminals):
            first = sorted(self.first_sets[symbol])
            print(f"FIRST({symbol}) = {{{', '.join(first)}}}")
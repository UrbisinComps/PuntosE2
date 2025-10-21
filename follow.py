from typing import Set


class FollowCalculator:
    """Calcula los conjuntos FOLLOW para una gramática"""

    def __init__(self, grammar, first_calculator):
        """
        Args:
            grammar: objeto Grammar
            first_calculator: objeto FirstCalculator
        """
        self.grammar = grammar
        self.first_calc = first_calculator
        self.follow_sets = {}
        self._compute()

    def _compute(self):
        """Calcula los conjuntos FOLLOW para todos los no terminales"""
        # Inicializar FOLLOW
        for non_terminal in self.grammar.non_terminals:
            self.follow_sets[non_terminal] = set()

        # $ está en FOLLOW del símbolo inicial
        self.follow_sets[self.grammar.start_symbol].add('$')

        # Iteración hasta punto fijo
        changed = True
        while changed:
            changed = False

            for lhs, rhs in self.grammar.all_productions:
                for i, symbol in enumerate(rhs):
                    if symbol in self.grammar.non_terminals:
                        old_size = len(self.follow_sets[symbol])

                        # FIRST(β) - {ε} está en FOLLOW(symbol)
                        beta = rhs[i + 1:]
                        first_beta = self.first_calc.first_of_string(beta)
                        self.follow_sets[symbol].update(first_beta - {'ε'})

                        # Si ε está en FIRST(β), FOLLOW(lhs) está en FOLLOW(symbol)
                        if 'ε' in first_beta or not beta:
                            self.follow_sets[symbol].update(self.follow_sets[lhs])

                        if len(self.follow_sets[symbol]) > old_size:
                            changed = True

    def get_follow(self, non_terminal: str) -> Set[str]:
        """Obtiene FOLLOW de un no terminal"""
        return self.follow_sets.get(non_terminal, set())

    def print_sets(self):
        """Imprime los conjuntos FOLLOW"""
        print("\n" + "=" * 60)
        print("CONJUNTOS FOLLOW")
        print("=" * 60)
        for symbol in sorted(self.grammar.non_terminals):
            if symbol != self.grammar.augmented_start:
                follow = sorted(self.follow_sets[symbol])
                print(f"FOLLOW({symbol}) = {{{', '.join(follow)}}}")
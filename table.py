from typing import Set, FrozenSet, Dict, List, Tuple


class LR1Item:
    """Representa un item LR(1): [A -> α.β, a]"""

    def __init__(self, lhs: str, rhs: List[str], dot: int, lookahead: str):
        self.lhs = lhs
        self.rhs = rhs
        self.dot = dot
        self.lookahead = lookahead

    def __eq__(self, other):
        return (self.lhs == other.lhs and
                self.rhs == other.rhs and
                self.dot == other.dot and
                self.lookahead == other.lookahead)

    def __hash__(self):
        return hash((self.lhs, tuple(self.rhs), self.dot, self.lookahead))

    def __repr__(self):
        rhs_with_dot = self.rhs[:self.dot] + ['.'] + self.rhs[self.dot:]
        rhs_str = ' '.join(rhs_with_dot) if rhs_with_dot else '.'
        return f"[{self.lhs} -> {rhs_str}, {self.lookahead}]"

    def next_symbol(self):
        """Retorna el símbolo después del punto"""
        if self.dot < len(self.rhs):
            return self.rhs[self.dot]
        return None

    def is_complete(self):
        """Verifica si el item está completo (punto al final)"""
        return self.dot >= len(self.rhs)


class LR1Table:
    """Construye la tabla LR(1) con estados y transiciones"""

    def __init__(self, grammar, first_calculator):
        """
        Args:
            grammar: objeto Grammar
            first_calculator: objeto FirstCalculator
        """
        self.grammar = grammar
        self.first_calc = first_calculator
        self.states = []
        self.state_transitions = {}
        self.action_table = {}
        self.goto_table = {}

        self._build_states()
        self._build_tables()

    def closure(self, items: Set[LR1Item]) -> FrozenSet[LR1Item]:
        """Calcula la clausura de un conjunto de items LR(1)"""
        closure_set = set(items)

        changed = True
        while changed:
            changed = False
            new_items = set()

            for item in closure_set:
                next_sym = item.next_symbol()

                if next_sym and not self.grammar.is_terminal(next_sym):
                    # Calcular FIRST(β a) donde β es lo que sigue al punto
                    beta = item.rhs[item.dot + 1:] + [item.lookahead]
                    first_beta = self.first_calc.first_of_string(beta)

                    # Para cada producción de next_sym
                    for prod_lhs, prod_rhs in self.grammar.all_productions:
                        if prod_lhs == next_sym:
                            for lookahead in first_beta:
                                if lookahead != 'ε':
                                    new_item = LR1Item(prod_lhs, prod_rhs, 0, lookahead)
                                    if new_item not in closure_set:
                                        new_items.add(new_item)
                                        changed = True

            closure_set.update(new_items)

        return frozenset(closure_set)

    def goto(self, items: FrozenSet[LR1Item], symbol: str) -> FrozenSet[LR1Item]:
        """Calcula GOTO(I, X)"""
        goto_set = set()

        for item in items:
            if item.next_symbol() == symbol:
                new_item = LR1Item(item.lhs, item.rhs, item.dot + 1, item.lookahead)
                goto_set.add(new_item)

        if goto_set:
            return self.closure(goto_set)
        return frozenset()

    def _build_states(self):
        """Construye todos los estados LR(1)"""
        # Estado inicial
        initial_item = LR1Item(self.grammar.augmented_start,
                               [self.grammar.start_symbol],
                               0, '$')
        initial_state = self.closure({initial_item})

        self.states = [initial_state]
        state_map = {initial_state: 0}
        pending = [initial_state]

        while pending:
            current_state = pending.pop(0)
            current_index = state_map[current_state]

            # Símbolos que pueden seguir al punto
            symbols = set()
            for item in current_state:
                next_sym = item.next_symbol()
                if next_sym:
                    symbols.add(next_sym)

            for symbol in symbols:
                next_state = self.goto(current_state, symbol)

                if next_state:
                    if next_state not in state_map:
                        state_map[next_state] = len(self.states)
                        self.states.append(next_state)
                        pending.append(next_state)

                    # Guardar transición
                    next_index = state_map[next_state]
                    self.state_transitions[(current_index, symbol)] = next_index

    def _build_tables(self):
        """Construye las tablas ACTION y GOTO"""
        for i, state in enumerate(self.states):
            self.action_table[i] = {}
            self.goto_table[i] = {}

            for item in state:
                if item.is_complete():
                    # Reducción
                    if item.lhs == self.grammar.augmented_start:
                        # Accept
                        self.action_table[i]['$'] = 'acc'
                    else:
                        # Buscar número de producción
                        prod_num = self.grammar.get_production_number(item.lhs, item.rhs)

                        if prod_num != -1:
                            self.action_table[i][item.lookahead] = ('r', prod_num)
                else:
                    next_sym = item.next_symbol()

                    if next_sym and self.grammar.is_terminal(next_sym):
                        # Shift
                        if (i, next_sym) in self.state_transitions:
                            next_index = self.state_transitions[(i, next_sym)]
                            self.action_table[i][next_sym] = ('s', next_index)

            # GOTO para no terminales
            for non_term in self.grammar.non_terminals:
                if (i, non_term) in self.state_transitions:
                    next_index = self.state_transitions[(i, non_term)]
                    self.goto_table[i][non_term] = next_index

    def print_closure_table(self):
        """Imprime la tabla de closure con los kernels"""
        print("\n" + "=" * 80)
        print("TABLA LR(1) CLOSURE")
        print("=" * 80)
        print(f"{'Goto':<20}{'Kernel':<30}{'State':<8}{'Closure'}")
        print("-" * 80)

        for i, state in enumerate(self.states):
            # Buscar qué goto lleva a este estado
            goto_str = ""
            for (from_state, symbol), to_state in self.state_transitions.items():
                if to_state == i:
                    goto_str = f"goto({from_state}, {symbol})"
                    break

            # Obtener kernel (items iniciales antes del closure)
            kernel_items = [item for item in state if item.dot > 0 or
                            item.lhs == self.grammar.augmented_start]

            if not kernel_items:
                kernel_items = list(state)[:1]

            kernel_str = str(kernel_items[0]) if kernel_items else ""

            # Primera línea
            print(f"{goto_str:<20}{kernel_str:<30}{i:<8}", end="")

            # Closure
            closure_strs = [str(item) for item in sorted(state, key=lambda x: str(x))]
            if closure_strs:
                print(closure_strs[0])
                for closure_str in closure_strs[1:]:
                    print(f"{'':<58}{closure_str}")

    def print_states(self):
        """Imprime todos los estados LR(1)"""
        print("\n" + "=" * 80)
        print("ESTADOS LR(1)")
        print("=" * 80)
        for i, state in enumerate(self.states):
            print(f"\nEstado {i}:")
            for item in sorted(state, key=lambda x: str(x)):
                print(f"  {item}")

    def print_action_goto_tables(self):
        """Imprime las tablas ACTION y GOTO en formato de tabla"""
        print("\n" + "=" * 100)
        print("TABLA LR(1) - ACTION Y GOTO")
        print("=" * 100)

        # Encabezados
        terminals = sorted(self.grammar.terminals) + ['$']
        non_terminals = sorted([nt for nt in self.grammar.non_terminals
                                if nt != self.grammar.augmented_start])

        # Encabezado principal
        print(f"{'State':<8}", end="")
        print("ACTION".ljust(len(terminals) * 12), end="")
        print("GOTO".ljust(len(non_terminals) * 12))

        # Sub-encabezados
        print(" " * 8, end="")
        for term in terminals:
            print(f"{term:<12}", end="")
        for nt in non_terminals:
            print(f"{nt:<12}", end="")
        print()
        print("-" * 100)

        # Filas de la tabla
        for i in range(len(self.states)):
            print(f"{i:<8}", end="")

            # Columnas ACTION
            for term in terminals:
                action = self.action_table[i].get(term, '')
                if action == 'acc':
                    print(f"{'acc':<12}", end="")
                elif isinstance(action, tuple):
                    action_str = f"{action[0]}{action[1]}"
                    print(f"{action_str:<12}", end="")
                else:
                    print(f"{'':<12}", end="")

            # Columnas GOTO
            for nt in non_terminals:
                goto = self.goto_table[i].get(nt, '')
                print(f"{str(goto):<12}", end="")

            print()
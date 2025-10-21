from typing import List


class Parser:
    """Parser LR(1) que analiza cadenas de entrada"""

    def __init__(self, grammar, lr1_table):
        """
        Args:
            grammar: objeto Grammar
            lr1_table: objeto LR1Table
        """
        self.grammar = grammar
        self.table = lr1_table

    def parse(self, input_string: str, show_trace: bool = True) -> bool:
        """
        Parsea una cadena de entrada

        Args:
            input_string: cadena a parsear (sin $)
            show_trace: si se muestra la traza del parsing

        Returns:
            bool: True si la cadena es aceptada, False en caso contrario
        """
        tokens = list(input_string.replace(" ", "")) + ['$']
        stack = [0]
        input_pos = 0
        step = 1
        derivations = []

        if show_trace:
            print("\n" + "=" * 100)
            print("TRAZA DEL PARSING")
            print("=" * 100)
            print(f"{'Step':<6}{'Stack':<30}{'Input':<20}{'Action':<44}")
            print("-" * 100)

        while True:
            current_state = stack[-1]
            current_token = tokens[input_pos]

            if show_trace:
                stack_str = " ".join(str(s) for s in stack)
                input_str = "".join(tokens[input_pos:])
                print(f"{step:<6}{stack_str:<30}{input_str:<20}", end="")

            # Verificar estado válido
            if current_state not in self.table.action_table:
                if show_trace:
                    print("ERROR: Estado inválido")
                return False

            # Verificar token esperado
            if current_token not in self.table.action_table[current_state]:
                if show_trace:
                    print(f"ERROR: Token inesperado '{current_token}'")
                return False

            action = self.table.action_table[current_state][current_token]

            if isinstance(action, tuple) and action[0] == 's':
                # SHIFT
                next_state = action[1]
                stack.append(current_token)
                stack.append(next_state)
                input_pos += 1

                if show_trace:
                    print(f"Shift {next_state}")

                step += 1

            elif isinstance(action, tuple) and action[0] == 'r':
                # REDUCE
                prod_num = action[1]
                lhs, rhs = self.grammar.all_productions[prod_num]

                # Pop 2 * len(rhs) elementos
                for _ in range(len(rhs) * 2):
                    if stack:
                        stack.pop()

                # Consultar GOTO
                current_state = stack[-1] if stack else 0
                if lhs in self.table.goto_table[current_state]:
                    next_state = self.table.goto_table[current_state][lhs]
                    stack.append(lhs)
                    stack.append(next_state)

                    rhs_str = ' '.join(rhs) if rhs else 'ε'
                    derivation = f"{lhs} -> {rhs_str}"
                    derivations.append(derivation)

                    if show_trace:
                        print(f"Reduce {prod_num}: {derivation}")
                else:
                    if show_trace:
                        print("ERROR: GOTO inválido")
                    return False

                step += 1

            elif action == 'acc':
                # ACCEPT
                if show_trace:
                    print("Accept")
                    print("-" * 100)
                    print("✓ CADENA ACEPTADA")
                    print("\nDerivaciones aplicadas:")
                    for i, deriv in enumerate(derivations, 1):
                        print(f"  {i}. {deriv}")
                    print("=" * 100)
                return True

            else:
                if show_trace:
                    print(f"ERROR: Acción desconocida")
                return False

            if step > 1000:  # Límite de seguridad
                if show_trace:
                    print("ERROR: Demasiados pasos")
                return False

        return False


# ============================================================================
# utils.py
# Utilidades generales del proyecto
# ============================================================================


def print_header(title: str):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80)


def print_grammar(grammar):
    """Imprime la gramática de forma legible"""
    print_header("GRAMÁTICA")
    print("\nProducciones:")
    for i, (lhs, rhs) in enumerate(grammar.all_productions):
        rhs_str = ' '.join(rhs) if rhs else 'ε'
        print(f"  ({i}) {lhs} -> {rhs_str}")

    print(f"\nSímbolo inicial: {grammar.start_symbol}")
    print(f"No terminales: {{{', '.join(sorted(grammar.non_terminals))}}}")
    print(f"Terminales: {{{', '.join(sorted(grammar.terminals))}}}")
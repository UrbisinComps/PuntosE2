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

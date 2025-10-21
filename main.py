from grammar import Grammar, read_grammar_from_file
from parser import Parser, print_grammar, print_grammar
from first import FirstCalculator
from follow import FollowCalculator
from table import LR1Table, LR1Item
from utils import *

def main():
    """Programa principal del parser LR(1)"""

    print_header("GENERADOR Y PARSER LR(1)")

    print("\n¿Cómo desea cargar la gramática?")
    print("1. Usar gramática de ejemplo (S -> CC, C -> cC | d)")
    print("2. Cargar desde archivo")

    choice = input("\nSeleccione una opción (1 o 2): ").strip()

    if choice == '1':
        # Gramática de ejemplo
        grammar = Grammar({
            'S': [['C', 'C']],
            'C': [['c', 'C'], ['d']]
        }, 'S')

    elif choice == '2':
        filename = input("Ingrese el nombre del archivo de gramática: ").strip()
        try:
            grammar = read_grammar_from_file(filename)
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo '{filename}'")
            return
        except Exception as e:
            print(f"Error al leer la gramática: {e}")
            return
    else:
        print("Opción inválida")
        return

    # Mostrar gramática
    print_grammar(grammar)

    # Calcular FIRST
    print("\nCalculando conjuntos FIRST...")
    first_calc = FirstCalculator(grammar)
    first_calc.print_sets()

    # Calcular FOLLOW (opcional)
    print("\nCalculando conjuntos FOLLOW...")
    follow_calc = FollowCalculator(grammar, first_calc)
    follow_calc.print_sets()

    # Construir tabla LR(1)
    print("\nConstruyendo tabla LR(1)...")
    lr1_table = LR1Table(grammar, first_calc)

    # Mostrar closure table
    lr1_table.print_closure_table()

    # Mostrar estados
    lr1_table.print_states()

    # Mostrar tablas ACTION y GOTO
    lr1_table.print_action_goto_tables()

    # Crear parser
    parser = Parser(grammar, lr1_table)

    # Parsear entrada
    while True:
        print("\n" + "=" * 80)
        input_string = input("\nIngrese la cadena a parsear (o 'salir' para terminar): ").strip()

        if input_string.lower() == 'salir':
            break

        parser.parse(input_string)

    print("\n¡Gracias por usar el parser LR(1)!")


if __name__ == "__main__":
    main()
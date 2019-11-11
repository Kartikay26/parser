from grammar import *
from lr0_parser import *
from slr1_parser import *


def main():
    g = Grammar("grammar.txt", "E")

    tokens = input().split()
    tokens = [Symbol(t) for t in tokens]

    parser = SLR1_Parser(g)

    parser.print_table()

    try:
        p_tree = parser.parse(tokens)
    except RuntimeError as e:
        # print(g)
        # print(parser.canonical_sets)
        # try:
        #     parser.parse(tokens, debug=True)
        # except RuntimeError:
        #     pass
        # raise e
        pass

    print_tree(p_tree)


if __name__ == '__main__':
    main()

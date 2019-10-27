from grammar import *
from lr0_parser import *
from pprint import pprint

def main():

    g = Grammar("grammar.txt", "E")
    print(g)

    # TODO: refactor, create LR0_parser class and do this in it
    # first_sets = construct_first_sets(g)
    canonical_sets = construct_canonical_sets(g)
    gotos = construct_goto(g, canonical_sets)
    actions = construct_actions(g, canonical_sets)

    print("Item Sets:")
    for iset in canonical_sets:
        print(iset)
    print()

    print("Goto:")
    pprint(gotos)
    print()

    print("Actions:")
    pprint(actions)
    print()

    tokens = input().split()
    tokens.append("$")
    tokens = [Symbol(t) for t in tokens]

    p_tree = parse(tokens, gotos, actions, g)
    
    print_tree(p_tree)


if __name__ == '__main__':
    main()

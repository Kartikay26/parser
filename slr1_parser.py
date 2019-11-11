from grammar import *
from lr0_parser import *


class SLR1_Parser(LR0_Parser):
    def __init__(self, g: Grammar):
        """Overrides LR0 parser's code, simply change the way actions work"""
        self.g = g
        self.canonical_sets = construct_canonical_sets(g)
        self.gotos = construct_goto(g, self.canonical_sets)
        self.actions = construct_actions_with_follow(g, self.canonical_sets)


def construct_actions_with_follow(g: Grammar, canonical_sets):
    actions = {}
    for i in range(len(canonical_sets)):
        for item in canonical_sets[i].items:
            if item.dotAtEnd:
                for sym in g.follow(item.p.sym):
                    actions[(i, sym)] = ("reduce", item.p.num)
        else:
            for sym in g.terminals:
                new_set = apply_symbol(canonical_sets[i], sym)
                if new_set in canonical_sets:
                    j = canonical_sets.index(new_set)
                    actions[(i, sym)] = ("shift", j)
    return actions

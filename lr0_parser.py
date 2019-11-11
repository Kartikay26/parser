from grammar import *


class LR0_Parser():
    def __init__(self, g: Grammar):
        self.g = g
        self.canonical_sets = construct_canonical_sets(g)
        self.check_conflicts()
        self.gotos = construct_goto(g, self.canonical_sets)
        self.actions = construct_actions(g, self.canonical_sets)

    def check_conflicts(self):
        for iset in self.canonical_sets:
            reduces = len([item for item in iset.items if item.dotAtEnd])
            shifts = len(set([item.next_sym for item in iset.items]))
            if reduces > 1:
                raise RuntimeError("Reduce-Reduce Conflict in %s" % iset)
            elif reduces == 1 and shifts > 0:
                raise RuntimeError("Shift-Reduce Conflict in %s" % iset)

    def parse(self, tokens, debug=False):
        tokens.append(Symbol("$"))
        dot = 0
        symbol_stack = []
        state_stack = [0]
        while len(state_stack) > 0:
            state = state_stack[-1]
            next_sym = next_sym = tokens[dot]
            if debug:
                print(" ".join(str(x)
                    for x in symbol_stack + [Symbol(".")] + tokens[dot:-1]))
                if (state, next_sym) in self.actions or (
                        state, next_sym) in self.gotos:
                    action = self.actions[(state, next_sym)]
                if debug:
                    print(" ".join(str(x) for x in action))
                if action[0] == "accept":
                    state_stack.pop()  # remove 1
                    state_stack.pop()  # remove 0
                elif action[0] == "shift":
                    symbol_stack.append(next_sym)
                    state = action[1]
                    state_stack.append(state)
                    dot += 1
                    next_sym = tokens[dot]
                elif action[0] == "reduce":
                    prod_num = action[1]
                    prod = self.g.productionsList[prod_num]
                    next_sym = Symbol(prod.sym.s)
                    next_sym.children = []
                    remove_syms = prod.prod[:]
                    while len(remove_syms) > 0:
                        assert symbol_stack[-1] == remove_syms[-1]
                        next_sym.children.append(symbol_stack[-1])
                        symbol_stack.pop()
                        remove_syms.pop()
                        state_stack.pop()
                    next_sym.children = list(reversed(next_sym\
                            .children))
                    state = state_stack[-1]
                    assert (state, next_sym) in self.gotos
                    state = self.gotos[(state, next_sym)]
                    state_stack.append(state)
                    symbol_stack.append(next_sym)
            else:
                raise RuntimeError("Syntax error at input position\
                        : %d" % dot)
        return symbol_stack[0]

    def print_table(self):
        """Prints out the parse tables"""
        N = 60
        def p(x = "\n"):
            print(x, end="")
        p("-"*N)
        p()
        p("Sym\t")
        for c in self.g.terminals:
            p(str(c).ljust(3))
        p("\t|\t")
        for c in self.g.nonTerminals:
            p(str(c).ljust(3))
        p()
        p("-"*N)
        p()
        for i in range(len(self.canonical_sets)):
            p(str(i)+"\t")
            for c in self.g.terminals:
                if (i, c) in self.actions:
                    s = self.actions[(i, c)]
                    p(str(s[0][0]+str(s[1])).ljust(3))
                else:
                    p("-  ")
            p("\t|\t")
            for c in self.g.nonTerminals:
                if (i, c) in self.gotos:
                    s = self.gotos[(i, c)]
                    p(str(s).ljust(3))
                else:
                    p("-  ")
            p()
        p("-"*N)
        p()


class LR0_Item():
    """LR0_Item: Production with a dot somewhere"""

    def __init__(self, p: Production, dot: int):
        self.p = p
        self.dot = dot
        self.dotAtEnd = (self.dot == len(self.p.prod))
        if not self.dotAtEnd:
            self.next_sym = self.p.prod[self.dot]
        else:
            self.next_sym = None

    def __repr__(self):
        s = f"{self.p}"
        lhs = s.split()[:self.dot + 3]
        rhs = s.split()[self.dot + 3:]
        return " ".join(lhs) + " . " + " ".join(rhs)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)


class LR0_ItemSet():
    """LR0_ItemSet: set of LR0_Items"""

    def __init__(self, items, g: Grammar):
        """items: list of item to construct item set from"""
        self.items = items
        self.grammar = g
        self.state_number = None
        self.apply_closure()

    def apply_closure(self):
        done = False
        while not done:
            for item in self.items:
                if not item.dotAtEnd and item.next_sym.isNonTerminal:
                    if item.next_sym not in self.grammar.productionsMap:
                        continue
                    for prod in self.grammar.productionsMap[item.next_sym]:
                        new_item = LR0_Item(prod, 0)
                        if new_item not in self.items:
                            self.items.append(new_item)
                            done = False
            done = True

    def __repr__(self):
        if self.state_number is not None:
            s = f"<ItemSet #{self.state_number}>\n"
        else:
            s = f"<ItemSet>\n"
        for i in self.items:
            s += f"\t{i}\n"
        return s

    def __hash__(self):
        return hash(frozenset(self.items))

    def __eq__(self, other):
        return frozenset(self.items) == frozenset(other.items)


def apply_symbol(itemset: LR0_ItemSet, sym: Symbol) -> LR0_ItemSet:
    new_item_list = []
    for item in itemset.items:
        if not item.dotAtEnd and item.next_sym == sym:
            new_item = LR0_Item(item.p, item.dot + 1)
            new_item_list.append(new_item)
    return LR0_ItemSet(new_item_list, itemset.grammar)


def construct_canonical_sets(g: Grammar):
    initialItem = LR0_Item(g.productionsList[0], 0)
    i0 = LR0_ItemSet([initialItem], g)
    canonical_item_sets = []
    new_sets = [i0]
    while len(new_sets) > 0:
        canonical_item_sets += new_sets
        freshly_added = []
        for iset in new_sets:
            applicable_symbols = []
            for item in iset.items:
                if item.next_sym:
                    applicable_symbols += [item.next_sym]
            for sym in applicable_symbols:
                iset_new = apply_symbol(iset, sym)
                if (len(iset_new.items) > 0 and
                        iset_new not in
                        canonical_item_sets + freshly_added):
                    freshly_added += [iset_new]
        new_sets = freshly_added
    for i, iset in enumerate(canonical_item_sets):
        iset.state_number = i
    return canonical_item_sets


def construct_goto(g: Grammar, canonical_sets):
    gotos = {}
    for i in range(len(canonical_sets)):
        for sym in g.nonTerminals:
            new_set = apply_symbol(canonical_sets[i], sym)
            if new_set in canonical_sets:
                j = canonical_sets.index(new_set)
                gotos[(i, sym)] = j
    return gotos


def construct_actions(g: Grammar, canonical_sets):
    actions = {}
    for i in range(len(canonical_sets)):
        for item in canonical_sets[i].items:
            if item.dotAtEnd:
                if item.p.num == 0:
                    actions[(i, Symbol("$"))] = ("accept", 0)
                else:
                    for sym in g.terminals:
                        actions[(i, sym)] = ("reduce", item.p.num)
                break
        else:
            for sym in g.terminals:
                new_set = apply_symbol(canonical_sets[i], sym)
                if new_set in canonical_sets:
                    j = canonical_sets.index(new_set)
                    actions[(i, sym)] = ("shift", j)
    return actions


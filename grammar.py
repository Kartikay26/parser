from random import randint

class Symbol():
    """Symbol: either a terminal or nonterminal symbol"""

    def __init__(self, s: str):
        self.s = s
        self.isNonTerminal = s[0].isupper()
        self.isTerminal = not self.isNonTerminal
        self.children = []
        self.rand = randint(1,100000)

    def __repr__(self):
        return f"{self.s}"

    def __hash__(self):
        return hash(self.s)

    def __eq__(self, other):
        return self.s == other.s


class Production():
    """Production: maps a symbol to a list of symbols"""

    def __init__(self, line: str, num: int):
        self.line = line
        tokens = line.split()
        self.len = len(tokens) - 2
        assert len(tokens) >= 3 and tokens[1] == ':='
        self.sym = Symbol(tokens[0])
        # self.sym = tokens[0]
        self.prod = [Symbol(x) for x in tokens[2:]]
        self.num = num
        self.grammar = None

    def __repr__(self):
        return (f"({self.num}) {self.sym} -> " +
                " ".join(f"{s}" for s in self.prod))

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)


class Grammar():
    """Grammar: list of productions starting with startSymbol"""

    def __init__(self, filename: str, startSymbol: str):
        self.filename = filename
        self.startSymbol = Symbol(startSymbol)
        self.productionsList = []
        self.productionsMap = {}
        self.terminals = []
        self.nonTerminals = []
        self.loadFromFile(filename)

    def loadFromFile(self, filename):
        lines = open(filename).readlines()
        # to add comments in the grammar
        lines = [l for l in lines if not l.startswith("#")]
        self.productionsList = [Production(f"Start := {self.startSymbol} $", 0)]
        self.productionsList += [Production(l, i + 1)
                                 for i, l in enumerate(lines)]
        for p in self.productionsList:
            p.grammar = self
        self.productionsMap = {}
        for p in self.productionsList:
            self.productionsMap.setdefault(p.sym, [])
            self.productionsMap[p.sym].append(p)
        for p in self.productionsList[1:]:
            for s in [p.sym] + p.prod:
                if s.isTerminal and s not in self.terminals:
                    self.terminals.append(s)
                if s.isNonTerminal and s not in self.nonTerminals:
                    self.nonTerminals.append(s)
        self.terminals.append(Symbol("$"))

    def first(self, sym: Symbol):
        first = set()
        if sym.isTerminal:
            return set([sym])
        for p in self.productionsList:
            if sym == p.sym:
                if p.prod[0] != sym:
                    first.update(self.first(p.prod[0]))
        return first

    def follow(self, sym: Symbol):
        follow = set()
        following_syms = set()
        for p in self.productionsList:
            for i in range(len(p.prod)):
                if p.prod[i] == sym:
                    j = 1
                    while i+j < len(p.prod):
                        fst = self.first(p.prod[i+j])
                        for s in fst:
                            if s.isTerminal:
                                follow.add(s)
                            if s.isNonTerminal:
                                fst = self.first(s)
                                follow.update(fst)
                        if Symbol("eps") not in fst:
                            break
                        j += 1
        return follow

    def __repr__(self):
        ans = f"<Grammar G ({self.startSymbol})>\n"
        for s in self.productionsMap:
            ans += f"\t{s} : " + \
                " | ".join(f"{p}" for p in self.productionsMap[s]) + \
                "\n"
        return ans


def print_tree(p, d=0):
    """Prints out the (concrete) parse tree in graphviz dot format"""
    if d == 0:
        print("digraph G {")
    if len(p.children) > 0:
        for ch in p.children:
            print(f"\t{p.rand} [label=\"{p.s}\"];")
            print(f"\t{ch.rand} [label=\"{ch.s}\"];")
            print(f"\t{p.rand} -> {ch.rand};")
            print_tree(ch, d + 1)
    if d == 0:
        print("}")

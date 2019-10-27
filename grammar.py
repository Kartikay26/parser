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
        self.productionsList = [Production(f"Start := {self.startSymbol}", 0)]
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

    def __repr__(self):
        ans = f"<Grammar G ({self.startSymbol})>\n"
        for s in self.productionsMap:
            ans += f"\t{s} : " + \
                " | ".join(f"{p}" for p in self.productionsMap[s]) + "\n"
        return ans

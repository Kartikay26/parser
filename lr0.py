from pprint import pprint

class Symbol():
	"""Symbol: either a terminal or nonterminal symbol"""
	def __init__(self, s: str):
		self.s = s
		self.isNonTerminal = s[0].isupper()
		self.isTerminal = not self.isNonTerminal

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
		l = line.split()
		self.len = len(l) - 2
		assert len(l) >= 3 and l[1] == ':='
		self.sym = Symbol(l[0])
		# self.sym = l[0]
		self.prod = [Symbol(x) for x in l[2:]]
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
		self.productionsList += [Production(l, i+1) for i, l in enumerate(lines)]
		for p in self.productionsList:
			p.grammar = self
		self.productionsMap = {}
		for p in self.productionsList:
			self.productionsMap.setdefault(p.sym, [])
			self.productionsMap[p.sym].append(p)
		for p in self.productionsList[1:]:
			for s in [p.sym] + p.prod:
				if s.isTerminal:
					self.terminals.append(s)
				else:
					self.nonTerminals.append(s)
	
	def __repr__(self):
		ans = f"<Grammar G ({self.startSymbol})>\n"
		for s in self.productionsMap:
			ans += f"\t{s} : " + " | ".join(f"{p}" for p in self.productionsMap[s]) + "\n"
		return ans

class LR0_Item():
	"""LR0_Item: Production with a dot somewhere"""
	def __init__(self, p: Production, dot: int):
		self.p = p
		self.dot = dot
		self.dotAtEnd = (self.dot == len(self.p.prod))
		if not self.dotAtEnd:
			self.next_sym = self.p.prod[self.dot]

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
	item_sets_produced = 0

	def __init__(self, items, g: Grammar):
		"""items: list of item to construct item set from"""
		self.items = items
		self.grammar = g
		self.apply_closure()
		self.item_set_number = LR0_ItemSet.item_sets_produced
		LR0_ItemSet.item_sets_produced += 1

	def apply_closure(self):
		done = False
		while not done:
			for item in self.items:
				if not item.dotAtEnd and item.next_sym.isNonTerminal:
					for prod in self.grammar.productionsMap[item.next_sym]:
						new_item = LR0_Item(prod, 0)
						if not new_item in self.items:
							self.items.append(new_item)
							done = False
			done = True

	def __repr__(self):
		s = f"<ItemSet #{self.item_set_number}>\n"
		for i in self.items:
			s += f"\t{i}\n"
		return s

	def __hash__(self):
		return hash(str(self))

	def __eq__(self, other):
		return str(self) == str(other)

def apply_symbol(itemset: LR0_ItemSet, sym: Symbol) -> LR0_ItemSet:
	new_item_list = []
	for item in itemset.items:
		if not item.dotAtEnd and item.next_sym == sym:
			new_item = LR0_Item(item.p, item.dot+1)
			new_item_list.append(new_item)
	print(new_item_list)
	return LR0_ItemSet(new_item_list, itemset.grammar)

def main():
	g = Grammar("grammar.txt", "S")
	print(g)
	initialItem = LR0_Item(g.productionsList[0], 0)
	i0 = LR0_ItemSet([initialItem], g)
	print(i0)
	i1 = apply_symbol(i0, Symbol("B"))
	print(i1)
	i2 = apply_symbol(i1, Symbol("B"))
	print(i2)

if __name__ == '__main__':
	main()
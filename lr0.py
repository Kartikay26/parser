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
				if s.isTerminal and s not in self.terminals:
					self.terminals.append(s)
				if s.isNonTerminal and s not in self.nonTerminals:
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
					for prod in self.grammar.productionsMap[item.next_sym]:
						new_item = LR0_Item(prod, 0)
						if not new_item in self.items:
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
		return hash(self.items)

	def __eq__(self, other):
		return self.items == other.items

def apply_symbol(itemset: LR0_ItemSet, sym: Symbol) -> LR0_ItemSet:
	new_item_list = []
	for item in itemset.items:
		if not item.dotAtEnd and item.next_sym == sym:
			new_item = LR0_Item(item.p, item.dot+1)
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
						iset_new not in canonical_item_sets):
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
			if len(new_set.items) == 0:
				gotos[(i, sym)] = -1 # error
			else:
				j = canonical_sets.index(new_set)
				gotos[(i, sym)] = j
	return gotos

def construct_actions(g: Grammar, canonical_sets):
	actions = {}
	for i in range(len(canonical_sets)):
		for sym in g.terminals:
			new_set = apply_symbol(canonical_sets[i], sym)
			if len(new_set.items) == 0:
				actions[(i, sym)] = -1 # error
			elif any(item.dotAtEnd for item in new_set.items):
				actions[(i, sym)] = ("reduce", "?")
			else:
				j = canonical_sets.index(new_set)
				actions[(i, sym)] = ("shift", j)
	return actions

def main():
	g = Grammar("grammar.txt", "S")
	print(g)
	canonical_sets = construct_canonical_sets(g)
	gotos = construct_goto(g, canonical_sets)
	actions = construct_actions(g, canonical_sets)
	print("Goto:")
	pprint(gotos)
	print()
	print("Actions:")
	pprint(actions)

if __name__ == '__main__':
	main()
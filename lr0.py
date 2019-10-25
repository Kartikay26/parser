from pprint import pprint

class Symbol():
	"""Symbol: either a terminal or nonterminal symbol"""
	def __init__(self, s: str):
		self.s = s

	def __repr__(self):
		return f"{self.s}"

	def __hash__(self):
		return hash(self.s)

	def __eq__(self, o):
		return self.s == o.s


class Production():
	"""Production: maps a symbol to a list of symbols"""
	def __init__(self, line: str, num: int):
		self.line = line
		l = line.split()
		assert len(l) >= 3 and l[1] == '->'
		self.sym = Symbol(l[0])
		# self.sym = l[0]
		self.prod = [Symbol(x) for x in l[2:]]
		self.num = num

	def __repr__(self):
		return (f"({self.num}) {self.sym} -> " +
						" ".join(f"{s}" for s in self.prod))


class Grammar():
	"""Grammar: list of productions starting with startSymbol"""
	def __init__(self, filename: str, startSymbol: str):
		self.filename = filename
		self.startSymbol = Symbol(startSymbol)
		self.productionsList = []
		self.productionsMap = {}
		self.loadFromFile(filename)

	def loadFromFile(self, filename):
		lines = open(filename).readlines()
		self.productionsList = [Production(l, i+1) for i, l in enumerate(lines)]
		self.productionsMap = {}
		for p in self.productionsList:
			self.productionsMap.setdefault(p.sym, [])
			self.productionsMap[p.sym].append(p)
	
	def __repr__(self):
		ans = f"<Grammar G ({self.startSymbol})>\n"
		for s in self.productionsMap:
			ans += f"\t{s} : " + " | ".join(f"{p}" for p in self.productionsMap[s]) + "\n"
		return ans

def main():
	g = Grammar("grammar.txt", "E")
	print(g)

if __name__ == '__main__':
	main()
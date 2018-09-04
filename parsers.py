#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2018, University of California, Berkeley
# author: Kevin Laeufer <laeufer@cs.berkeley.edu>


class Symbol:
	def __init__(self, name, bold=False):
		self.name = name
		self._bold = bold

	def __str__(self):
		if self._bold:
			return f"\033[1m{self.name}\033[0m"
		else:
			return f"{self.name}"

	def __repr__(self):
		return self.name

class NonTerminal(Symbol):
	def __init__(self, name):
		super().__init__(name, bold=True)

class Terminal(Symbol):
	def __init__(self, name):
		super().__init__(name)

class Epsilon(Terminal):
	def __init__(self):
		super().__init__("ε")

class Grammar:
	def __init__(self):
		self._syms = [Epsilon(), Terminal('$')]
		self._rules = []
		self._root = None

	def _make_syms(self, Type, names):
		syms = [Type(name) for name in names]
		self._syms += syms
		return syms

	def non_terminal(self, *names):
		return self._make_syms(NonTerminal, names)

	def terminal(self, *names):
		return self._make_syms(Terminal, names)

	def epsilon(self):
		return self._syms[0]

	def eof(self):
		return  self._syms[1]

	def r(self, lhs, rhs):
		assert isinstance(lhs, NonTerminal)
		assert isinstance(rhs, list)
		assert all(isinstance(sym, Symbol) for sym in rhs)
		if len(rhs) < 1: rhs = [self.epsilon()]
		if self._root is None:
			self._root = lhs # by convention
		self._rules.append((lhs, rhs))

	def first(self, sym):
		assert isinstance(sym, Symbol), f"{sym} : {type(sym)}"
		#print(f"FIRST({sym})")
		if isinstance(sym, Terminal):
			return {sym}
		_first = set()
		for lhs, rhs in self._rules:
			if lhs != sym:
				continue
			annullable = True
			for s in rhs:
				if s == sym:
					annullable = False
					break
				s_first = self.first(s)
				s_annullable = self.epsilon() in s_first
				_first = _first | (s_first - {self.epsilon()})
				if not s_annullable:
					annullable = False
					break
			if annullable:
				_first |= {self.epsilon()}
		return _first

	def follow(self, non_term):
		assert isinstance(non_term, NonTerminal)
		_follow = set()
		for lhs, rhs in self._rules:
			if non_term not in rhs:
				continue
			for ii, sym in enumerate(rhs):
				if sym != non_term:
					continue
				# scan following symbols
				followed_by_annulable = True
				for ff in rhs[ii+1:]:
					_first = self.first(ff)
					_follow |= (_first - {self.epsilon()})
					if self.epsilon() not in _first:
						followed_by_annulable = False
						break
				if followed_by_annulable:
					_follow |= self.follow(lhs)
		if non_term == self._root:
			_follow |= {self.eof()}
		return _follow


if __name__ == "__main__":
	g = Grammar()
	S, B, D, E, F = non_term = g.non_terminal('S', 'B', 'D', 'E', 'F')
	u, v, w, x, y, z = term = g.terminal('u', 'v', 'w', 'x', 'y', 'z')
	g.r(S, [u, B, D, z])
	g.r(B, [B, v])
	g.r(B, [w])
	g.r(D, [E, F])
	g.r(E, [y])
	g.r(E, [])
	g.r(F, [x])
	g.r(F, [])

	for nt in non_term:
		print(f"FIRST({nt}): {g.first(nt)}")

	print()

	for nt in non_term:
		print(f"FOLLOW({nt}): {g.follow(nt)}")
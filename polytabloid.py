#!/usr/bin/env/python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from itertools import permutations, product
from copy import copy
from numpy import column_stack, linalg
from math import factorial
from partition import Partition

class Tableaux(object):
    def __init__(self, shape, vals=None):
        if not vals:
            vals = range(1, sum(shape) + 1)
        assert sum(shape) == len(vals)
        self.vals = list(vals)
        self.shape = shape

    def __str__(self):
        rows = self.rows()
        _format = lambda r: " ".join(map(str, r))
        return "\n".join([_format(row) for row in rows])

    def __hash__(self):
        return hash((self.shape, str(self.vals)))

    def __eq__(self, other):
        return (self.shape, self.vals) == (other.shape, other.vals)

    def __neq__(self, other):
        return not self == other

    def coords_of_index(self, i):
        """
        Convert an index i of self.vals into (row, col) coords of the 
        position of self.vals[i].
        """
        if i > sum(self.shape):
            return False
        for r,length in enumerate(self.shape):
            if i < length:
                return (r, i)
            i -= length 
        return False #not found

    def coords(self, r, c):
        if r < 0:
            return None
        if r == 0:
            return self.vals[c]
        rows = self.rows()
        for i in range(r + 1):
            row = next(rows)
        return row[c]

    def rows(self, indices=False):
        start = 0
        for i,row in enumerate(self.shape):
            if i > 0:
                prev = self.shape[i-1]
                if indices:
                    yield range(start, start + row)
                else:
                    yield self.vals[start : start + row]
            else:
                if indices:
                    yield range(row)
                else:
                    yield self.vals[0:row]
            start += row
    
    def columns(self):
        for i in range(self.shape[0]):
            col, x = [], 0
            for row in self.shape:
                if i + 1 > row:
                    break
                col.append(self.vals[i + x])
                x += row
            yield col

    def sort_rows(self):
        new_vals = []
        for row in self.rows():
            new_vals += sorted(row)
        self.vals = new_vals
        return self

    def is_standard(self):
        for row in self.rows():
            if not row == sorted(row):
                return False
        if len(self.shape) <= 1: #single row; don't need to check cols
            return True
        for col in self.columns():
            if not col == sorted(col):
                return False
        return True

    def col_stabilizer(self):
        for col in self.columns():
            yield list(permutations(col))
            #TODO: still need to include products, via itertools product.

    def permute(self, *args):
        new_vals = [v for v in self.vals]
        if not args:
            return False
        if len(args) == 1:
            return self #identity permutation (need to make a copy?)
        for i,num in enumerate(args):
            j = self.vals.index(num)
            if i < len(args) - 1:
                new_vals[j] = args[i + 1]
            else:
                new_vals[j] = args[0]
        return Tableaux(self.shape, new_vals)

    def set_column(self, i, col):
        _col = list(col)
        new_vals = []
        for row in self.rows():
            if len(row) > i: 
                row[i] = _col.pop(0)
            for node in row:
                new_vals.append(node)
        self.vals = new_vals

    def polytabloid(self, include_nonstandard=False):
        for col_perm in product(*self.col_stabilizer()):
            if col_perm[0][0] != 1 and not include_nonstandard: # 1 must be fixed for permuted tableaux to be standard
                continue
            _vals = copy(self.vals)
            t = Tableaux(self.shape, vals=_vals)
            for i,c in enumerate(col_perm): # apply each permutation in column-indexed list
                t.set_column(i, c)
            t.sort_rows()
            if include_nonstandard:
                yield t
            elif t.is_standard():
                yield t

    def generates(self, other):
        mapping = {}
        for i,k in enumerate(self.vals):
            self_r, self_c = self.coords_of_index(i)
            other_r, other_c = other.coords_of_index(other.vals.index(k))
            if self_r == other_r:
                target = k
            else:
                try:
                    target = self.coords(other_r, self_c)
                except IndexError: # required column permutation is impossible
                    return False
            if mapping.get(target): # is this value already being mapped to?
                return False
            mapping[target] = True
        return True

def total_order(shape, t=None, adding=None):
    # generates all standard tableaux, in order.
    if not adding:
        adding = sum(shape)
    if not t:
        t = Tableaux(shape, vals=[0] * adding)
    rows = [r for r in t.rows()]
    for i,k in enumerate(t.vals):
        if k != 0:
            #print "k nonzero"
            continue
        r, c = t.coords_of_index(i)
        #print (r,c)
        #print r
        if r == len(shape) - 1: # must place in last row, or...
            #print "in last row"
            pass
        else: # ...if not in last row, must be above a higher value
            if len(rows[r+1]) - 1 < c:
                #print "not in last row but is an overhang"
                pass
            elif t.coords(r+1, c) not in (0, None):
                #print "not in last row but above hihger value"
                pass
            else:
                #print "neither last row nor higher value nor overhang"
                continue
        if c == len(rows[r]) - 1: # must place in last column, or...
            #print "in last col"
            pass
        else: # ...if not in last column, must be left of a higher value
            if t.coords(r, c+1) != 0:
                #print "not in last col but left of higher val"
                pass
            else:
                #print "neither last col nor higher val"
                continue
        next_vals = [val for val in t.vals]
        next_vals[i] = adding
        #print next_vals
        if adding == 1: # base case
            #print "base case"
            yield Tableaux(shape, vals=next_vals)
        else: # recursive case
            #print "recursive case"
            for child in total_order(shape, t=Tableaux(shape, vals=next_vals), adding=adding-1):
                yield child

def find_solution(shape, verbose=False, skip_known_families=True, return_matrix=False):
    if type(shape) is Partition:
        shape = shape.vals
    if skip_known_families:
        p = Partition(*shape)
        if p.is_one_dimensional():
            if verbose:
                print "Skipping 1D partition"
            return 1
        elif p.is_self_conjugate():
            if verbose:
                print "Skipping self-conjugate partition"
            return 0
        elif p.is_hook():
            if verbose:
                print "Skipping hook partition"
            i = sum(p.vals)
            r = p.vals[1:].count(1)
            choose = factorial(i - 1) / (factorial(r) * factorial(i - 1 - r))
            if (i % 2, r % 2, choose % 2) == (1, 0, 1):
                return 1
            else:
                return 0
    if shape == (1,):
        # isolate this case to avoid numpy exception when building matrix
        return 1
    if verbose:
        print "Generating all standard {}-tableaux...\n".format(shape)
    polys = []
    if verbose:
        print "-" * 20
    for t in [t for t in total_order(shape)][::-1]:
        standards = [t]
        #if verbose:
        #    print "Next tableaux:\n{}\n".format(t)
        poly = set([tab for tab in t.polytabloid() if tab != t])
        if len(poly) > 1:
            for s in poly:
                if s.vals != t.vals:
                    print "{} --> {}".format(t.vals, s.vals)
                    standards.append(s)
        polys.append(standards)
    columns = []
    if verbose:
        print "Creating matrix from polytabloids."
    for i, poly in enumerate(polys):
        vec = [0] * len(polys)
        vec[i] = 1
        if len(poly) > 1:
            for s in poly:
                #find the index of the standard tableaux
                x = [l[0] for l in polys].index(s)
                vec[x] = 1
        columns.append(vec)
    matrix = column_stack(columns)
    if return_matrix:
        print matrix
        return matrix
    if verbose:
        print matrix
    solution = map(int, linalg.solve(matrix, [1] * len(polys)))
    if verbose:
        print "Solution vector: {}".format(solution)
        print "Sum of standard coefficients is congruent to {} (mod 2).".format(sum(solution) % 2)
    return sum(solution)

def find_solution_new(shape, verbosity=0):
    if type(shape) == Partition:
        shape = shape.vals
    standards = [s for s in total_order(shape)][::-1]
    vector = [0] * len(standards)
    solution = 0
    for i,t in enumerate(standards):
        if verbosity > 1:
            print "Next tableau:\n{}".format(t)
        if vector[i] == 1:
            if verbosity > 1:
                print "Skipping polytabloid computation."
            continue
        for j,t2 in enumerate(standards[:i]):
            if t == t2:
                vector[i] = (vector[i] + 1) % 2
            elif t.generates(t2):
                vector[j] = (vector[j] + 1) % 2
        solution = (solution + 1) % 2
    return solution

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("partition", nargs="*")
    args = parser.parse_args()
    if args.partition:
        shape = tuple(map(int, args.partition))
    else:
        shape = (3,2)
    print find_solution(shape)

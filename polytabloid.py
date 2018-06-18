from itertools import permutations
from copy import copy
from numpy import column_stack, linalg

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
        if i > sum(shape):
            return False
        for r,length in enumerate(self.shape):
            if i < length:
                return (r, i)
            i -= length 
        return False #not found

    def coords(self, r, c):
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
            yield [(1,)] + list(permutations(col))
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

    def polytabloid(self, include_nonstandard=False):
        for col_perm in self.col_stabilizer():
            for p in col_perm:
                s = self.permute(*p).sort_rows()
                if include_nonstandard:
                    yield s
                elif s.is_standard():
                    yield s

def tableaux_gen(shape):
    """
    Generates all standard tableaux for a particular partition, via brute force.
    """
    n = sum(shape)
    vals = range(1, n + 1)
    for perm in permutations(vals):
        t = Tableaux(shape, vals=list(perm))
        if t.is_standard():
            yield t

def tableaux_gen_recursive(shape, t=None, adding=2):
    if not t:
        t = Tableaux(shape, vals=[1] + [None] * (sum(shape) - 1))
    if adding == sum(shape):
        new_vals = copy(t.vals)
        missing = t.vals.index(None)
        new_vals[missing] = adding
        yield Tableaux(shape, vals=new_vals)
    else:
        for (i, node) in enumerate(t.vals):
            if node == None:
                r, c = t.coords_of_index(i)
                if c > 0:
                    if not t.coords(r, c-1): # left neighbor node must not be empty
                        continue
                if r > 0:
                    if not t.coords(r-1, c): # above neighbor node must not be empty
                        continue
                new_vals = copy(t.vals)
                new_vals[i] = adding
                new_t = Tableaux(shape, vals=new_vals)
                recurs = tableaux_gen_recursive(shape, t = new_t, adding = adding + 1)
                for result in recurs:
                    yield result

if __name__ == "__main__":
    shape = (3,2)
    gen = tableaux_gen_recursive(shape)
    print "Generating all standard {}-tableaux...\n".format(shape)
    polys = []
    print "-" * 20
    for t in gen:
        standards = [t]
        print "Next tableaux:\n{}\n".format(t)
        poly = set([tab for tab in t.polytabloid() if tab != t])
        if len(poly) > 0:
            print "Found standards in polytabloid:"
            for s in poly:
                print "{}\n".format(s)
                standards.append(s)
        polys.append(standards)
        print "-" * 20
    columns = []
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
    print matrix
    solution = map(int, linalg.solve(matrix, [1] * len(polys)))
    print "Solution vector: {}".format(solution)
    print "Sum of standard coefficients is congruent to {} (mod 2).".format(sum(solution) % 2)

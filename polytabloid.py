from itertools import permutations

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

    def rows(self):
        start = 0
        for i,row in enumerate(self.shape):
            if i > 0:
                prev = self.shape[i-1]
                yield self.vals[start : start + row]
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
    Generates all tableaux for a particular partition.
    """
    n = sum(shape)
    vals = range(1, n + 1)
    for perm in permutations(vals):
        t = Tableaux(shape, vals=list(perm))
        if t.is_standard():
            yield t

if __name__ == "__main__":
    shape = (4,2)
    gen = tableaux_gen(shape)
    print "Generating all standard {}-tableaux...".format(shape)
    for t in gen:
        print "Next tableaux:\n{}\n".format(t)
        poly = set([tab for tab in t.polytabloid() if tab != t])
        if len(poly) > 0:
            print "Found standards in polytabloid:"
            for s in poly:
                print "{}\n".format(s)
        print "-" * 20

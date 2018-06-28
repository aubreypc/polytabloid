class Partition(object):
    def __init__(self, *vals):
        self.vals = tuple(sorted(vals))[::-1]

    def __eq__(self, other):
        return self.vals == other.vals

    def conjugate(self):
        _vals = [v for v in self.vals]
        con = []
        while len(_vals) > 0:
            l = len(_vals)
            v = _vals.pop()
            con += [l] * v
            _vals = [x - v for x in _vals]
        return Partition(*con)

    def is_2special(self):
        for i,v in enumerate(self.vals):
            if i < len(self.vals) - 1:
                next_v = self.vals[i+1]
                mod = 2 ** least_greater_power(2, next_v)
                if v % mod != (mod - 1):
                    return False
        return True
    
    def is_hook(self):
        if len(self.vals) > 1:
            if self.vals[1:] == (1,) * (sum(self.vals) - self.vals[0]):
                return True
        return False

    def is_one_dimensional(self):
        if len(self.vals) == 1:
            return True
        for r in self.vals:
            if r != 1:
                return False
        return True

    def is_self_conjugate(self):
        return self == self.conjugate()

def least_greater_power(x, y):
    """
    Returns least positive integer n such that x^n > y.
    """
    n = 0
    while True:
        if x ** n > y:
            return n
        n += 1

def partition_gen(n):
    """
    accel_asc - Fastest known algorithm for computing partitions of an integer n.
    Credit to Jerome Kellehr, http://jeromekelleher.net/generating-integer-partitions.html
    """
    a = [0 for i in range(n + 1)]
    k = 1
    y = n - 1
    while k != 0:
        x = a[k - 1] + 1
        k -= 1
        while 2 * x <= y:
            a[k] = x
            y -= x
            k += 1
        l = k + 1
        while x <= y:
            a[k] = x
            a[l] = y
            yield a[:k + 2]
            x += 1
            y -= 1
        a[k] = x + y
        y = x + y - 1
        yield a[:k + 1][::-1]

def hooks_gen(n):
    """
    Generates all hook partitions of an integer n,
    i.e. partitions of the form (k-r, 1^r).
    """
    for i in range(1,n):
        yield (n - i,) + (1,) * i

def self_conjugates_gen(n):
    """
    Generates all partitions of an integer n such that
    the partition is its own conjugate.
    """
    for p in partition_gen(n):
        p = Partition(*p)
        if p == p.conjugate():
            yield p
    
def one_dimensional_gen(n):
    yield Partition(n)
    yield Partition(*((1,) * n))

if __name__ == "__main__":
    n = 4
    print "Finding all 2-special partitions of {} with 2-special conjugates.".format(n)
    gen = partition_gen(n)
    for g in gen:
        p = Partition(*g)
        if p.is_2special() and p.conjugate().is_2special:
            print p.vals

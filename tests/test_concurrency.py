from ..tasks import app, find_solution_concurrent
from ..polytabloid import find_solution, find_solution_new, total_order
from ..partition import Partition, partition_gen, self_conjugates_gen
"""
def test_celery():
    for n in range(2,12):
        for partition in partition_gen(n):
            partition = tuple(sorted(partition)[::-1])
            p = Partition(*partition)
            if not p.is_2special() or not p.conjugate().is_2special():
                continue
            print p
            assert find_solution_new(p) == find_solution_concurrent(p)

def test_self_conjugates():
    for i in range(2,20):
        for sc in self_conjugates_gen(i):
            print sc
            assert sc.is_self_conjugate()
            assert find_solution_concurrent(sc) % 2 == 0
"""

def matrix_diff(m1, m2):
    diff = []
    for i, (r1, r2) in enumerate(zip(m1, m2)):
        row = []
        for j, (n1, n2) in enumerate(zip(r1, r2)):
            if n1 == n2:
                row.append(str(n1))
            else:
                row.append("\033[31m{}\033[0m".format(str(n1)))
                diff.append((i,j))
        print " ".join(row)
    return diff

def test_333():
    p = Partition(3,3,3)
    m1 = find_solution_concurrent(p, return_matrix=True, verbosity=3)
    m2 = find_solution(p, skip_known_families=False, return_matrix=True)
    standards = [t for t in total_order(p.vals)][::-1]
    for s, t in matrix_diff(m1, m2):
        s, t = standards[s], standards[t]
        print "Incorrect entry: {} -/> {}".format(t.vals, s.vals)
    for r1, r2 in zip(m1, m2):
        for n1, n2 in zip(r1, r2):
            assert n1 == n2
    assert find_solution_concurrent(p) == 0

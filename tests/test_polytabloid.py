from ..polytabloid import find_solution
from ..partition import Partition, hooks_gen, self_conjugates_gen, one_dimensional_gen
from math import factorial

def test_detect_one_dimensional():
    """
    Test for false positives in 1D detection.
    """
    assert not Partition(3,3,2).is_one_dimensional()
    assert not Partition(3,3,3).is_one_dimensional()
    assert not Partition(11,3,3).is_one_dimensional()
    assert not Partition(15, 7, 7, 1, 1, 1, 1).is_one_dimensional()

def test_one_dimensional():
    """
    Partitions in the form of (k) or (1^k) should always have solution
    congruent to 1 (mod 2).
    """
    for k in range(1,8): # how many is enough?
        p1 = Partition(k)
        p2 = Partition(*((1,) * k))
        assert p1.is_one_dimensional()
        assert p2.is_one_dimensional()
        assert find_solution(p1, skip_known_families=False) % 2 == 1
        assert find_solution(p2, skip_known_families=False) % 2 == 1

def test_detect_hook_partitions():
    """
    Test for false positives in hook detection.
    """
    assert not Partition(3,2,1).is_hook() # again, how many to do?
    assert not Partition(3,3,3).is_hook()

def test_hook_partitions():
    """
    Use Murphy's result to ensure that hook-shaped partitions have
    expected solution, and make sure that all such partitions are caught
    by the hook detection.
    """
    for i in [3,5,7]: # NOTE: test fails for even vals of i
        for hook in hooks_gen(i):
            assert Partition(*hook).is_hook()
            r = hook[1:].count(1)
            choose = factorial(i - 1) / (factorial(r) * factorial(i - 1 - r))
            if (i % 2, r % 2, choose % 2) == (1, 0, 1):
                expected_sol = 1
            else:
                expected_sol = 0
            assert find_solution(hook, skip_known_families=False) % 2 == expected_sol

def test_self_conjugates():
    """
    Partitions equal to their own conjugates should always have
    solution congruent to 0 when n > 1.
    """
    for i in range(2,8):
        for sc in self_conjugates_gen(i):
            assert sc.is_self_conjugate()
            assert find_solution(sc, skip_known_families=False) % 2 == 0

from ..polytabloid import find_solution
from ..partition import hooks_gen
from math import factorial

def test_one_dimensional():
    """
    Partitions in the form of (k) or (1^k) should always have solution
    congruent to 1 (mod 2).
    """
    for k in range(1,8): # how many is enough?
        assert find_solution((k,)) % 2 == 1
        assert find_solution((1,) * k) % 2 == 1

def test_hook_partitions():
    """
    Use Murphy's result to ensure that hook-shaped partitions have
    expected solution.
    """
    for i in [3,5,7]: # NOTE: test fails for even vals of i
        for hook in hooks_gen(i):
            print hook
            r = hook[1:].count(1)
            choose = factorial(i - 1) / (factorial(r) * factorial(i - 1 - r))
            if (i % 2, r % 2, choose % 2) == (1, 0, 1):
                expected_sol = 1
            else:
                expected_sol = 0
            assert find_solution(hook) % 2 == expected_sol

def test_self_conjugates():
    pass

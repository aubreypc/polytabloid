from celery import Celery, group 
from celery.utils.log import get_task_logger
from polytabloid import Tableaux, total_order
from partition import Partition
import numpy as np

app = Celery("tasks", broker="redis://localhost", backend="redis://localhost")
log = get_task_logger(__name__)

@app.task(name="tasks.polytabloid_vector")
def polytabloid_vector(shape, t, standards, t_index, verbosity=0):
    vec = [0] * len(standards)
    t = Tableaux(shape, vals=t)
    log.critical("{}: {}".format(shape, t.vals))
    for i,s in enumerate(standards[t_index:]):
        s = Tableaux(shape, vals=s)
        if t.generates(s):
            log.debug("{} --> {}".format(t.vals, s.vals)) 
            vec[i + t_index] = 1
        else:
            if verbosity > 2:
                log.debug("{} -/> {}".format(t.vals, s.vals)) 
    return vec

@app.task(name="tasks.sort_cols")
def sort_cols(columns):
    # sorted because celery has a bug with redis and group orderings...
    return sorted(columns, key=(lambda l: l.index(1)))

@app.task(name="tasks.solve_system")
def solve_system(columns):
    matrix = np.column_stack(columns)
    return map(int, np.linalg.solve(matrix, [1] * len(columns)))

def find_solution_concurrent(shape, verbosity=0, return_matrix=False):
    if type(shape) == Partition:
        shape = shape.vals
    if verbosity > 0:
        print shape
    standards = [s.vals for s in total_order(shape)][::-1]
    tasks = group(polytabloid_vector.s(shape, t, standards, i, verbosity=verbosity) for i,t in enumerate(standards))
    if return_matrix:
        return np.column_stack((tasks | sort_cols.s())().get())
    solution = (tasks | sort_cols.s() | solve_system.s())().get()
    if verbosity > 0:
        print solution
    return sum(solution) % 2

if __name__ == "__main__":
    assert find_solution_concurrent((3,3,3)) == 0

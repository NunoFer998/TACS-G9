"""Backward mapping (bonus): measured bitstring -> problem-model Items, through the T1 trace.

bitstring --T2 layout--> {y_<item>: 0/1} --name--> Unknown objects --T1 trace--> Item objects
"""
from transformations.t1 import _slot
from transformations.t2 import decode_bitstring


def back(bitstring, layout, solution_model, trace):
    """Return the set of problem-model Item objects packed by a measured bitstring."""
    unknown = {_slot(o, "name"): o for o in solution_model.objects
               if o.classifier.name == "Unknown"}
    return {trace[unknown[n]] for n, v in decode_bitstring(bitstring, layout).items() if v}


def is_solution(items, problem):
    """Check the mapped-back choice directly on the problem model (weight <= C, value >= V)."""
    return (sum(_slot(i, "weight") for i in items) <= _slot(problem, "capacity")
            and sum(_slot(i, "value") for i in items) >= _slot(problem, "minValue"))


if __name__ == "__main__":
    # every assignment: mapping back and checking on the problem model == brute force
    from itertools import product
    from models.instances import INSTANCES
    from models.solver_configs import CONFIGS
    from transformations import t1, t2
    from validation.baseline import read_problem, brute_force
    for name, model in INSTANCES.items():
        sol, trace = t1.transform(model, CONFIGS[name])
        _, layout = t2.t2(sol)
        problem = next(o for o in model.objects if o.classifier.name == "KnapsackProblem")
        _, cap, v, items = read_problem(model)
        expected = set(brute_force(cap, v, items))
        got = set()
        for bits in product((0, 1), repeat=len(layout.unknown_names)):
            s = "".join(map(str, bits[::-1]))                 # Qiskit: rightmost char = unknown 0
            if is_solution(back(s, layout, sol, trace), problem):
                got.add(bits)
        print(f"{name:10s} backward mapping matches brute force: {'OK' if got == expected else 'FAIL'}")

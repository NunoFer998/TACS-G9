"""Classical baseline for knapsack feasibility (problem DSL models).

- brute_force: enumerates all 2^n choices and returns every feasible one
  (weight <= C and value >= V). Gives M, the number of solutions, used to pick
  the number of Grover rounds (Boyer et al. 1998).
- dp_max_value: 0/1 knapsack dynamic programming, O(n*C). The instance is
  feasible iff the best value >= V. Knapsack is only weakly NP-complete, so DP
  solves these instances efficiently.
- qubit_estimate: rough size of the circuit (search qubits + two signed
  registers holding e - 1 for each "e <= 0" atom), to check the ~20 qubit limit.

Usage: python -m validation.baseline            (all instances)
       python -m validation.baseline f4 tiny    (some instances)
"""
import math
import sys
from itertools import product


def read_problem(model):
    """Return (name, capacity, min_value, [(item_name, weight, value), ...])."""
    def slots(obj):
        return {s.attribute.name: s.value.value for s in obj.slots}

    problem = next(o for o in model.objects if o.classifier.name == "KnapsackProblem")
    p = slots(problem)
    items = sorted((slots(o) for o in model.objects if o.classifier.name == "Item"),
                   key=lambda s: s["name"])
    return p["name"], p["capacity"], p["minValue"], [(i["name"], i["weight"], i["value"]) for i in items]


def brute_force(capacity, min_value, items):
    """All feasible choices as tuples of 0/1, in item order."""
    solutions = []
    for choice in product((0, 1), repeat=len(items)):
        w = sum(c * it[1] for c, it in zip(choice, items))
        v = sum(c * it[2] for c, it in zip(choice, items))
        if w <= capacity and v >= min_value:
            solutions.append(choice)
    return solutions


def dp_max_value(capacity, items):
    best = [0] * (capacity + 1)
    for _, w, v in items:
        for c in range(capacity, w - 1, -1):
            best[c] = max(best[c], best[c - w] + v)
    return best[capacity]


def grover_rounds(n, m):
    """Optimal number of rounds for M marked states out of N = 2^n."""
    if m == 0:
        return 0
    return math.floor(math.pi / 4 * math.sqrt(2 ** n / m))


def grover_success_probability(n, m, rounds):
    """Theoretical P(measuring a solution) after `rounds` iterations."""
    if m == 0:
        return 0.0
    theta = math.asin(math.sqrt(m / 2 ** n))
    return math.sin((2 * rounds + 1) * theta) ** 2


def signed_bits(lo, hi):
    """Bits of a two's complement register that holds every value in [lo, hi]."""
    b = 1
    while not (-(2 ** (b - 1)) <= lo and hi <= 2 ** (b - 1) - 1):
        b += 1
    return b


def qubit_estimate(capacity, min_value, items):
    n = len(items)
    total_w = sum(w for _, w, _ in items)
    total_v = sum(v for _, _, v in items)
    # weight atom: sum(w*y) - C <= 0, stored as e - 1 (sign bit = 1 iff e <= 0)
    bits_w = signed_bits(-capacity - 1, total_w - capacity - 1)
    # value atom: V - sum(v*y) <= 0
    bits_v = signed_bits(min_value - total_v - 1, min_value - 1)
    return n + bits_w + bits_v


def describe(choice, items):
    return "{" + ", ".join(it[0] for c, it in zip(choice, items) if c) + "}"


def report(model):
    name, capacity, min_value, items = read_problem(model)
    n = len(items)
    sols = brute_force(capacity, min_value, items)
    m = len(sols)
    best = dp_max_value(capacity, items)
    rounds = grover_rounds(n, m)
    assert (best >= min_value) == (m > 0), "brute force and DP disagree"
    return {
        "name": name, "n": n, "C": capacity, "V": min_value,
        "M": m, "dp_best": best, "rounds": rounds,
        "p_success": grover_success_probability(n, m, rounds),
        "qubits": qubit_estimate(capacity, min_value, items),
        "solutions": [describe(s, items) for s in sols],
    }


def main(names):
    from models.instances import INSTANCES
    names = names or list(INSTANCES)
    print("| instance | n | C | V | M | DP best | rounds | P(success) | ~qubits | solutions |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for name in names:
        r = report(INSTANCES[name])
        sols = " ".join(r["solutions"][:4]) + (" ..." if r["M"] > 4 else "") or "none"
        print(f"| {r['name']} | {r['n']} | {r['C']} | {r['V']} | {r['M']} | {r['dp_best']} "
              f"| {r['rounds']} | {r['p_success']:.3f} | {r['qubits']} | {sols} |")


if __name__ == "__main__":
    main(sys.argv[1:])

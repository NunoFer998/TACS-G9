# REPORT (Part II)

## Test instances

In Part I we picked three of Pisinger's low-dimensional instances [Pis] (f4, f7, f1) sized by number of items: 4, 7 and 10. That is the natural notion of size for a knapsack, but it is not what limits us here. When we started designing T2 we realised that the circuit needs more than one qubit per item: the oracle has to compute the total weight and the total value inside the circuit, in two's complement registers, so that it can read the sign bit of each constraint `e <= 0`. The size of those registers depends on the numbers, not on the number of items.

We therefore estimate the circuit size as:

```
qubits = n (one per item) + bits(Σw·y − C − 1) + bits(V − Σv·y − 1)
```

where `bits(e)` is the smallest two's complement width that holds every value `e` can take (we store `e − 1` because the sign bit tells us `e − 1 < 0`, which for integers is the same as `e <= 0`). For f4, for example, `Σw·y − 11 − 1` ranges from −12 to 7 (5 bits) and `23 − Σv·y − 1` from −19 to 22 (6 bits), giving 4 + 5 + 6 = 15 qubits. This is a lower bound: depending on the adder used in T2, a few ancilla qubits may be added on top.

With this estimate, f7 needs about 22 qubits and f1 about 30, which is past what we can simulate. We kept f4 unchanged and reworked the rest:

| Instance | Role (Annex A) | n | C | V | Solutions (M) | ≈ Qubits |
|---|---|---|---|---|---|---|
| toy | tiny, checkable by hand (Part I example) | 3 | 5 | 7 | 1 | 11 |
| tiny | Annex A example | 4 | 10 | 15 | 1 | 14 |
| f4 | medium, known optimum (Pisinger, unchanged) | 4 | 11 | 23 | 1 | 15 |
| f4_multi | several solutions | 4 | 11 | 16 | 5 | 15 |
| f4_none | no solution | 4 | 11 | 24 | 0 | 15 |
| f7_sub5 | near the 20-qubit limit | 5 | 25 | 46 | 1 | 20 |

f7_sub5 keeps the first five items of f7 with the capacity to half (C = 25) and V set to the new optimum. The instances with several solutions and with none reuse f4 and only change V: below the optimum several subsets qualify, and above it (V = Opt + 1) none can. f1 is left out of the simulated tests and is mentioned as a limitation. All instances are written as problem DSL object models in `models/instances.py`; the original list stays in `instances/instances.md`.

## Classical baseline

To tell whether the quantum chain is correct, we first need to know the right answer for every instance before running it on Aer. So we wanted a baseline that gives us three things: (1) whether the instance is feasible, (2) the exact list of solutions, so that we can check that every bitstring measured with high probability is one of them, and (3) their number M, which we need to configure Grover itself (see below). The answers have to be exact; an approximate answer cannot validate anything.

We started from the assignment, which suggests brute force as a baseline [TACS26, 7.3], and looked at what is normally used for knapsack, where the textbook exact method is dynamic programming [KPP04, ch. 2]. Heuristics such as greedy by value/weight ratio are faster, but they can miss the optimum and so do not give an exact answer. An external ILP solver would be exact too, but it adds a dependency and gives us nothing extra at this size.

In the end we implemented both brute force and dynamic programming in `validation/baseline.py`, reading the same problem DSL models that feed T1, and the script checks that they agree on every instance:

- **Brute force** enumerates all 2^n subsets and keeps those with weight ≤ C and value ≥ V. It is the only one of the two that gives the full list of solutions and their number, which we call M: the number of subsets that satisfy both constraints. In Grover's terms these are the marked states the oracle must flag, out of N = 2^n possible subsets. With n ≤ 5 this is at most 32 subsets, so the exponential cost does not matter here.
- **Dynamic programming** computes the best value that fits in capacity C in O(n·C) time; the instance is feasible iff that value is ≥ V. Knapsack is only weakly NP-complete, so dynamic programming solves instances with small numbers like ours efficiently. It does not list the solutions, but it is an independent check on brute force: two methods that work in different ways and agree on feasibility make a bug in the baseline itself unlikely.

A classical computer will always win at this size; the point of the project is the correctness of the transformation chain, not a speedup.

We needed M for more than validation, because it is also an input to the chain: the number of Grover rounds is `floor(π/4 · √(2^n / M))` [BBHT98], and with too many or too few rounds the probability of measuring a solution drops. For f4 (n = 4, M = 1) this gives 3 rounds and a theoretical success probability of 0.96; for f4_multi (M = 5) a single round is enough. When M = 0 there is nothing to amplify, which is the case f4_none is meant to show.

Reproduce with `python -m validation.baseline`.

## Transformations

[T1, T2 — later.]

## Validation results

[Later: quantum vs baseline per instance.]

## Limitations

[Later.]

## References

- [KPP04] H. Kellerer, U. Pferschy, D. Pisinger. Knapsack Problems. Springer, 2004.
- [BBHT98] M. Boyer, G. Brassard, P. Høyer, A. Tapp. “Tight bounds on quantum searching”, Fortschritte der Physik, 1998.
- [Pis] D. Pisinger, low-dimensional 0/1 knapsack instances, as collected in https://github.com/dnlfm/knapsack-01-instances/tree/main/pisinger_instances_01_KP/low-dimensional
- [TACS26] Assignment: "TACS 2627 Assignment, QMDE"

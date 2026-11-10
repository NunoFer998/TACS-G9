# Transformations

## Run T1

```bash
python -m transformations.t1 problem_dsl/problem_objectmodel.py solver_config.py
```

Output:

```
problem_dsl/problem_objectmodel.py: 19 objects -> out/t1\Knapsack_solution.py
```

It loads `object_model` from both the problem and configuration `.py` files, runs T1 and saves the solution model (metamodel + objects)
to `out/t1/<problem name>_solution.py`. T2 can load it back with
`runpy.run_path("out/t1/Knapsack_solution.py")["object_model"]` (round trip checked: 19 objects again).
Only `.py` is saved: the JSON converter is missing from the installed besser wheel.

For example, create `solver_config.py` for the four-item editor example:

```python
from models.solver_configs import make_config

object_model = make_config(
    "editor_example", iterations=3, shots=1024, adder="RIPPLE_CARRY",
    expression_bit_width=6, expression_encoding="TWOS_COMPLEMENT",
)
```

In Python, `transform(problem_model, configuration_model)` returns
`(solution_model, trace)`. The configuration input must contain exactly one
`SolverConfig` object. T1 copies every setting and records the source config
in the trace; it never calculates Grover rounds from the problem.
The trace `{created object: source object}` is kept in memory for the backward mapping.

## Solver configuration through T2 and T3

The solution model must link exactly one config to its constraint system:

| Model property | Consumer |
|---|---|
| `iterations` (integer >= 0) | T2 emits exactly this many oracle/diffuser rounds; 0 means no amplification |
| `shots` (integer >= 1) | Demo/self-check pass this to BESSER's T3 Qiskit generator |
| `adder` (`AdderKind`) | T2 supports `RIPPLE_CARRY`; `QFT` raises `NotImplementedError` |
| `expressionBitWidth` (integer >= 1) | Width of both shared expression/temp registers; T2 checks each atom's signed bounds and rejects overflow |
| `expressionEncoding` (`ExpressionEncoding`) | Explicit `TWOS_COMPLEMENT` arithmetic |
| `Unknown.bitWidth` (integer >= 1) | Number of search qubits for that unknown, LSB first |

`t2(solution_model)` has no round override and no missing-config fallback.
The instance configurations in [solver_configs.py](../models/solver_configs.py)
are shared by T1 CLI, T2 self-check and demo. The self-check does not replace
their rounds with an internally computed optimum. The classical baseline is
only used to validate the selected values.

For T1's 0/1 knapsack mapping, one bit per item is a semantic requirement:
increasing it would allow packing an item multiple times. General solution-DSL
models may still use wider unknowns, and T2 reads those widths unchanged.

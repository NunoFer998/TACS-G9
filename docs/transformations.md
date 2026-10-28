# Transformations

## Run T1

```bash
python -m transformations.t1 problem_dsl/problem_objectmodel.py
```

Output:

```
problem_dsl/problem_objectmodel.py: 19 objects -> out/t1\Knapsack_solution.py
```

It loads `object_model` from the editor-exported `.py`, runs T1 and saves the solution model (metamodel + objects)
to `out/t1/<problem name>_solution.py`. T2 can load it back with
`runpy.run_path("out/t1/Knapsack_solution.py")["object_model"]` (round trip checked: 19 objects again).
Only `.py` is saved: the JSON converter is missing from the installed besser wheel.

In Python, `transform(om, SolverSettings(iterations=..., shots=..., adder=...))` returns `(solution_model, trace)`;
the trace `{created object: source object}` is kept in memory for the backward mapping.

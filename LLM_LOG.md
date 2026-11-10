## 2026-11-10 - Review: Explicit solver configuration models

- Tool: GitHub Copilot in VS Code.
- Request: Review explicit modeling of solver choices replacing hard-coded configurations in T1/T2.
- Output: Validated required configuration-model inputs in T1: explicit Grover rounds, 
	shots, adder, signed expression encoding, and register width; confirmed clear separation between instance configurations and problem data; verified that T2 consumes settings directly without relying on defaults or round overrides, correctly rejecting register widths that would lead to overflow; approved keeping single-bit item unknowns (appropriate for 0/1 knapsack).
- Verification: **Configuration regression tests:** Passed; **baseline & Oracle checks:** 	
	T1 baseline checks and T2 oracle checks passed across all 6 instances; **full demonstration:** Successful end-to-end run via generated Qiskit/Aer for the 5 instances under 20 qubits. Modeled rounds matched the baseline in every case; **simulation exception:** The 25-qubit f7_sub5 instance oracle was verified classically, omitting Aer simulation.
- Scope: AI-assisted implementation review and documentation for group review.

## 2026-10-20 - Hand-built example object models

- Tool: GitHub Copilot in VS Code.
- Request: document a small knapsack problem object model and the corresponding
	solution object model expected from T1, using objects, attribute values, and
	links; check the metamodel invariants and expected answer.
- Input: the user's illustrative three-item instance, the current problem and
	solution B-UML metamodels, the concept list, and the benchmark instance list.
- Output: [example object models](docs/example_object_models.md), including
	object and link tables, the expected T1 mapping, manual invariant checks,
	optional solver configuration, and the eight possible selections. Updated
	the hand-built models row in the README.
- Verification: an independent PowerShell enumeration checked all eight
	assignments, equivalence of the normalized inequalities, and the unique
	feasible selection {a, b} (weight 5, value 7). Documentation links were checked.
	No OCL engine or quantum simulator was run.
- Scope: AI-assisted example documentation, not the hand-written Part I report.
	The group should review the models before submission.

## 2026-10-17 - Problem and solution DSL metamodels

- Tool: Claude (LLM assistant).
- Request: review the group's concept tables against Part I, and help draft the
	problem and solution DSL metamodels in B-UML with OCL constraints.
- Input: the assignment, the group's concept tables, and the BESSER course fork.
- Output: drafts of [problem_metamodel.py](problem_dsl/problem_metamodel.py) and
	[solution_metamodel.py](solution_dsl/solution_metamodel.py), later edited in
	the BESSER web editor. Changes from the first draft: removed the suggested
	`Item.quantity` attribute (out of scope), set the `problem` end of the
	KnapsackProblem-Item association to 0..1, kept the OCL constraints (5 in the
	problem DSL, 9 in the solution DSL), and removed helper functions from the
	solution DSL so the BESSER web importer accepts it. The LLM also suggested
	diagram layout changes (and layout JSON files) to avoid crossing lines.
- Verification: both metamodels were imported into the BESSER web editor and
	the diagrams were checked against the code. OCL constraints were reviewed by
	hand.
- Scope: AI-assisted drafts; the final metamodels and diagrams were adjusted
	and reviewed by the group.

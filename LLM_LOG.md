## 2026-11-07 to 2026-11-10 - Setup fix, demo, validation 

- Tool: Claude
- Request: find why `python -m transformations.t2` failed with `TemplateNotFound`;
	save the generated Qiskit code; write the single-command demo with the
	validation table.
- Input: the assignment (§7, Annex A), the repository (T1, T2, baseline,
	instances) and the course BESSER fork.
- Output: `requirements.txt` installs BESSER in editable mode (the fork's pip
	package leaves out `besser/generators/qiskit/templates/`, which has no
	`__init__.py`); T2 saves the generated script to `out/t3/<instance>/`;
	[`demo.py`](demo.py) (baseline → T1 → T2 → generator → Aer → items →
	`out/validation.md`); the Grover rounds computed from the baseline's M (later
	moved into the explicit solver configuration models, see the next entry); drafts of the validation and limitations.
- What was wrong and how we found it:
	- The qubit estimate the LLM proposed for the test instances (11 to 20
	  qubits) was too low: the real T2 circuits have 4 to 5 more qubits (adder
	  temporary register, carry, flags, phase). Found by comparing with the
	  qubit counts printed by T2; the report table now shows both.
	- T1 kept the Grover rounds at 1, and T2's self-check hid it because it
	  computed its own rounds. Running the chain without the self-check gave 46%
	  on f4 instead of 96%. The demo now flags any difference between the rounds
	  in the model and the optimum.
	- T2 turned 0 rounds into a default of 3 (f4_none). Found by checking the
	  size of the generated circuit (10 operations expected).

## 2026-11-11 - Backward mapping (bonus)

- Tool: GitHub Copilot in VS Code.
- Request: map measured bitstrings back to the problem model, using the T1 trace.
- Output: [backward.py](transformations/backward.py); `demo.py` uses it for the "Most frequent answer" column and requires the answer to be a solution on the original problem.
- Verification: `python -m transformations.backward` tries all 2^n assignments on the 6
	instances and matches brute force; `python -m demo toy f4_multi` still shows valid answers.
- What was wrong: before this, `decode_items` recovered item names by stripping the `y_`
	prefix, so it relied on a naming convention and never used the trace, and the demo's
	check compared names against the baseline, not the problem model. Found by reading
	`decode_items`; fixed by going unknown -> trace -> `Item` and checking weight and value
	on the problem. The full demo (6 instances) was not rerun after the change.

## 2026-11-10 - Review: Explicit solver configuration models

- Tool: GitHub Copilot in VS Code.
- Request: Review explicit modeling of solver choices replacing hard-coded configurations in T1/T2.
- Output: Validated required configuration-model inputs in T1: explicit Grover rounds, 
	shots, adder, signed expression encoding, and register width; confirmed clear separation between instance configurations and problem data; verified that T2 consumes settings directly without relying on defaults or round overrides, correctly rejecting register widths that would lead to overflow; approved keeping single-bit item unknowns (appropriate for 0/1 knapsack).
- Verification: **Configuration regression tests:** Passed; **baseline & Oracle checks:** 	
	T1 baseline checks and T2 oracle checks passed across all 6 instances; **full demonstration:** Successful end-to-end run via generated Qiskit/Aer for the 5 instances under 20 qubits. Modeled rounds matched the baseline in every case; **simulation exception:** The 25-qubit f7_sub5 instance oracle was verified classically, omitting Aer simulation.
- What was wrong: before this change T1 fell back to a default `SolverSettings(iterations=1)`, so every circuit ran one Grover round whatever M was. The T2 self-check hid it by computing the rounds itself (`default_iterations`) instead of reading them from the model. For `tiny` and `f4` (M=1) one round gives about 47% success instead of the 96% of the optimal 3 rounds, and the same happened with the other instances whose optimum is not 1.
- How it was detected and fixed: the demo table compares "Rounds (model)" with "Rounds (optimal)" computed from the baseline's M and marks mismatches with `(!)`; the measured success probability (about 47%) also disagreed with the theory for the optimal rounds. Fixed by making the configuration a required input model (no defaults, no overrides in T2), one per instance in `models/solver_configs.py`; `validation/test_solver_config.py` fails if the configured rounds differ from `grover_rounds(n, M)` of the baseline.
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

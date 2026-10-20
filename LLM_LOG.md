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

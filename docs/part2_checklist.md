# TACS Part II checklist (deadline: **11 Nov**)

Source: assignment §7 (7.1–7.4), §8 (LLMs), §9 (evaluation weights).

## 7.1 M2M transformations (25%)
- [ ] **T1**: problem model → solution model (Python over BESSER models)
- [ ] **T2**: solution model → BESSER quantum circuit model
- [ ] Every rule cites its reference in a comment next to the rule
- [ ] Every rule cites its reference in the report
- [ ] Solver config (Grover rounds, adder encoding, bit widths…) modelled explicitly, not hard-coded in T1/T2
- [ ] Decoding of measured bitstrings → domain terms (items chosen) derived from the models, not added by hand
- [ ] Bonus: map solutions back to the problem DSL

## 7.2 M2T generation (10%, with demo)
- [ ] Qiskit Python generated with the BESSER generator (from quantum model + problem/config models where needed)
- [ ] Script builds the circuit, runs it on Aer, prints the result in domain terms
- [ ] Generated code never edited by hand (fix models/transformations instead)
- [ ] Using the course BESSER fork

## 7.3 Validation (10%)
- [x] ≥ 3 test instances in the problem DSL (`models/instances.py`), incl. several-solutions and no-solution cases
- [x] Classical baseline: brute force + DP (`validation/baseline.py`)
- [x] DP stated as solving weakly NP-complete knapsack efficiently
- [ ] Instances ≤ ~20 qubits (check once T2 gives real qubit counts)
- [ ] Quantum result vs baseline for each instance
- [ ] Metric for class C: oracle calls + success probability of Grover
- [ ] Validation catches typical LLM errors (qubit order little-endian, wrong oracle marks, wrong rounds)

## 7.4 Deliverables
- [ ] T1 and T2 implemented
- [ ] M2T generator used for Qiskit
- [ ] Working demo: ≥ 3 DSL specs → generated code → run → domain results, **one documented command**
- [ ] Validation results vs classical baseline
- [ ] Report (~2 pages, written by you, short and personal) covering:
  - [x] test instances (written)
  - [x] classical baseline (written)
  - [ ] transformations + references
  - [ ] validation results
  - [ ] limitations
- [ ] LLM usage log for Part II (tool/model, goal, prompt summary, accepted, **what was wrong + how detected/fixed**)

## Housekeeping
- [ ] Update the README Part II table as items are finished
- [ ] Commits spread across all 4 members (contribution is assessed from commits)
- [ ] Everyone can explain every part (final discussion)

## Status summary
Done: test instances, classical baseline, partial report.
Missing: T1, T2, generated Qiskit code, demo command, quantum-vs-classical validation, rest of report, Part II LLM log.

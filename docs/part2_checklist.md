# TACS Part II checklist (deadline: **11 Nov**)

Source: assignment §7 (7.1–7.4), §8 (LLMs), §9 (evaluation weights).
Last updated: 11 Nov (state of `main` at b1ac39c, demo checked).

## 7.1 M2M transformations (25%)
- [x] **T1**: problem model → solution model (`transformations/t1.py`, self-check vs brute force on all 6 instances)
- [x] **T2**: solution model → BESSER quantum circuit model (`transformations/t2.py`, oracle checked classically on all 2^n inputs)
- [x] T1: every rule (R1–R6) cites its reference in a comment
- [x] T2: every rule (R1–R11) cites its reference in a comment
- [ ] Every rule cites its reference in the report
- [x] Solver config modelled explicitly: mandatory model input with rounds, shots, adder, signed encoding and expression width. Instance configs are selected against the baseline; T1/T2/demo/self-check use the same settings, without hidden defaults or round overrides.
- [x] Decoding of measured bitstrings → items, from the T2 layout (`decode_bitstring` / `decode_items`)
- [x] Bonus: map solutions back to the problem DSL (`transformations/backward.py`, via the T1 trace; `python -m transformations.backward` checks all 2^n assignments against brute force)

## 7.2 M2T generation (10%, with demo)
- [x] Qiskit Python generated with the BESSER generator, saved in `out/t3/<instance>/qiskit_circuit.py`
- [x] Using the course BESSER fork (editable install pinned to 9cf7a90, needed for the Qiskit template)
- [x] Generated code never edited by hand
- [x] Script builds the circuit and runs it on Aer
- [ ] Script prints the result in domain terms (the generated script prints raw `Counts`; `python -m demo` and the T2 self-check decode them to items)

## 7.3 Validation (10%)
- [x] ≥ 3 test instances in the problem DSL (`models/instances.py`), incl. several-solutions and no-solution cases
- [x] Classical baseline: brute force + DP (`validation/baseline.py`)
- [x] DP stated as solving weakly NP-complete knapsack efficiently
- [ ] Instances ≤ ~20 qubits: real T2 counts are toy 15, tiny 18, f4/f4_multi/f4_none 20, **f7_sub5 25** (not simulated)
- [x] Quantum result vs baseline for each instance, written down (`python -m demo` → `out/validation.md`; top result is a brute-force solution on toy, tiny, f4, f4_multi); also in the report (Validation results)
- [x] Metric for class C: oracle calls + success probability of Grover, measured vs theoretical (in `out/validation.md`)
- [x] f4_none run on Aer (demo: 0/1024 valid, "no solution")
- [x] Validation catches typical LLM errors: oracle marks and dirty ancillas (T2 check), wrong number of rounds (`(!)` in the demo table), invalid config and undersized signed widths (`python -m unittest validation.test_solver_config`).

## 7.4 Deliverables
- [x] T1 and T2 implemented
- [x] M2T generator used for Qiskit
- [x] Working demo: ≥ 3 DSL specs → generated code → run → domain results, **one documented command** (`python -m demo`, documented in the README)
- [x] Validation results vs classical baseline (`out/validation.md`)
- [ ] Report (~2 pages, written by you, short and personal) covering:
  - [x] test instances (written; the table shows the real T2 qubit counts)
  - [x] classical baseline (written)
  - [ ] transformations + references
  - [x] validation results
  - [x] limitations (incl. M taken from the baseline, f7_sub5 over 20 qubits)
- [ ] LLM usage log for Part II (tool/model, goal, prompt summary, accepted, **what was wrong + how detected/fixed**)

## Housekeeping
- [x] Update the README Part II table
- [ ] Commits spread across all 4 members (contribution is assessed from commits)
- [ ] Everyone can explain every part (final discussion)
- [x] Setup fixed: after pulling, run `pip uninstall -y besser && pip install -r requirements.txt`

## Status summary
Done: instances, baseline, T1, T2, generated Qiskit code (`out/t3`), demo command, validation table, setup fix, solver configuration with Grover rounds (Inês), T2 rule references, validation results and limitations in the report.
In progress: report, Part II LLM log.
Missing: Transformations section with rule references in the report, domain-terms output in the generated script.

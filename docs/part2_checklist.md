# TACS Part II checklist (deadline: **11 Nov**)

Source: assignment §7 (7.1–7.4), §8 (LLMs), §9 (evaluation weights).
Last updated: 8 Nov (state of `main` at 0619bc4).

## 7.1 M2M transformations (25%)
- [x] **T1**: problem model → solution model (`transformations/t1.py`, self-check vs brute force on all 6 instances)
- [x] **T2**: solution model → BESSER quantum circuit model (`transformations/t2.py`, oracle checked classically on all 2^n inputs)
- [x] T1: every rule (R1–R6) cites its reference in a comment
- [ ] T2: every rule cites its reference in a comment (today only CDKM04/Cuccaro in the header)
- [ ] Every rule cites its reference in the report
- [ ] Solver config modelled explicitly: `SolverConfig` exists, but `iterations` is always 1 (T1 default). Grover rounds must come from `grover_rounds(n, M)` of the baseline. The T2 self-check hides this by computing rounds itself; the plain chain gives ~47% on f4 instead of ~96%
- [x] Decoding of measured bitstrings → items, from the T2 layout (`decode_bitstring` / `decode_items`)
- [ ] Bonus: map solutions back to the problem DSL

## 7.2 M2T generation (10%, with demo)
- [x] Qiskit Python generated with the BESSER generator, saved in `out/t3/<instance>/qiskit_circuit.py`
- [x] Using the course BESSER fork (editable install pinned to 9cf7a90, needed for the Qiskit template)
- [x] Generated code never edited by hand
- [x] Script builds the circuit and runs it on Aer
- [ ] Script prints the result in domain terms (today it prints raw `Counts`; translation to items only happens in the T2 self-check)

## 7.3 Validation (10%)
- [x] ≥ 3 test instances in the problem DSL (`models/instances.py`), incl. several-solutions and no-solution cases
- [x] Classical baseline: brute force + DP (`validation/baseline.py`)
- [x] DP stated as solving weakly NP-complete knapsack efficiently
- [ ] Instances ≤ ~20 qubits: real T2 counts are toy 15, tiny 18, f4/f4_multi/f4_none 20, **f7_sub5 25** (not simulated)
- [ ] Quantum result vs baseline for each instance, written down (T2 self-check already gets 95–96% valid on toy, tiny, f4, f4_multi, top result = brute-force solution)
- [ ] Metric for class C: oracle calls + success probability of Grover, measured vs theoretical
- [ ] f4_none run on Aer (no-solution behaviour shown, not only the oracle check)
- [ ] Validation catches typical LLM errors: oracle marks and dirty ancillas are checked; wrong number of rounds is not

## 7.4 Deliverables
- [x] T1 and T2 implemented
- [x] M2T generator used for Qiskit
- [ ] Working demo: ≥ 3 DSL specs → generated code → run → domain results, **one documented command**
- [ ] Validation results vs classical baseline
- [ ] Report (~2 pages, written by you, short and personal) covering:
  - [x] test instances (written; qubit table must be updated to the real T2 counts)
  - [x] classical baseline (written)
  - [ ] transformations + references
  - [ ] validation results
  - [ ] limitations (incl. M taken from the baseline, f7_sub5 over 20 qubits)
- [ ] LLM usage log for Part II (tool/model, goal, prompt summary, accepted, **what was wrong + how detected/fixed**)

## Housekeeping
- [ ] Update the README Part II table (still says T2 "To do")
- [ ] Commits spread across all 4 members (contribution is assessed from commits)
- [ ] Everyone can explain every part (final discussion)
- [x] Setup fixed: after pulling, run `pip uninstall -y besser && pip install -r requirements.txt`

## Status summary
Done: instances, baseline, T1, T2, generated Qiskit code (`out/t3`), setup fix.
In progress: Grover rounds from the baseline (Inês).
Missing: demo command, written validation results, T2 rule references, domain-terms output, rest of the report, Part II LLM log.

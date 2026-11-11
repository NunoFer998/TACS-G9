"""Part II demo: the whole chain, one command.

    python -m demo                 # all instances in models/instances.py
    python -m demo f4 f4_multi     # some instances

For each instance (a problem DSL model):
  1. classical baseline  -> feasible solutions and their number M   (validation/baseline.py)
  2. T1 (M2M)            -> solution model, incl. SolverConfig       (transformations/t1.py)
  3. T2 (M2M)            -> BESSER quantum circuit model, saved to out/t2/<instance>.py
  4. T3 (M2T)            -> Qiskit script with the BESSER generator, out/t3/<instance>/qiskit_circuit.py
  5. run the generated script on Aer (only up to MAX_QUBITS)
  6. decode the counts into items (names from the solution model, qubit order from the T2 layout)
  7. compare with the baseline and write out/validation.md

The number of Grover rounds is read from the solution model (SolverConfig.iterations),
never chosen here. Input configuration models live in models/solver_configs.py.
"""
import ast
import os
import subprocess
import sys

from besser.generators.qiskit import QiskitGenerator
from besser.utilities.buml_code_builder.quantum_model_builder import quantum_model_to_code

from models.instances import INSTANCES
from models.solver_configs import CONFIGS
from transformations import backward, t1, t2
from validation.baseline import (read_problem, brute_force, grover_rounds,
                                 grover_success_probability)

MAX_QUBITS = 20          # assignment 7.3: "small enough to simulate, roughly up to 20 qubits"
OUT = "out"


def run_generated(script):
    """Run a generated Qiskit script and return its Aer counts {bitstring: shots}."""
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")   # qc.draw() is non-ASCII
    res = subprocess.run([sys.executable, script], capture_output=True, text=True,
                         encoding="utf-8", errors="replace", env=env)
    lines = [l for l in res.stdout.splitlines() if l.startswith("Counts:")]
    if not lines:
        raise RuntimeError(f"{script} printed no counts (exit {res.returncode}):\n{res.stderr[-1500:]}")
    return ast.literal_eval(lines[0].split("Counts:", 1)[1].strip())   # first Counts = Aer


def run_instance(name):
    model = INSTANCES[name]
    _, capacity, min_value, items = read_problem(model)
    n = len(items)

    # 1. baseline
    solutions = brute_force(capacity, min_value, items)            # tuples in item-name order
    m = len(solutions)
    best_rounds = grover_rounds(n, m)

    # 2-3. T1, T2
    sol_model, trace = t1.transform(model, CONFIGS[name])
    circ, layout = t2.t2(sol_model)
    rounds = t2.extract_spec(sol_model).iterations
    os.makedirs(f"{OUT}/t2", exist_ok=True)
    quantum_model_to_code(circ, f"{OUT}/t2/{name}.py")

    # 4. T3
    out_dir = f"{OUT}/t3/{name}"
    os.makedirs(out_dir, exist_ok=True)
    shots = t2.extract_spec(sol_model).shots
    QiskitGenerator(circ, output_dir=out_dir, shots=shots).generate()

    row = {"name": name, "n": n, "qubits": layout.total, "M": m, "rounds": rounds,
           "best_rounds": best_rounds, "p_theory": grover_success_probability(n, m, rounds),
           "shots": shots, "valid": None, "top": None, "top_ok": None}
    if layout.total > MAX_QUBITS:
        return row

    # 5-6. run on Aer, decode with the T2 layout (unknown y_<item>, sorted by name = baseline order)
    counts = run_generated(f"{out_dir}/qiskit_circuit.py")
    def choice(bits):
        values = t2.decode_bitstring(bits, layout)
        return tuple(values[u] for u in layout.unknown_names)
    valid = sum(c for b, c in counts.items() if choice(b) in solutions)
    top = max(counts, key=counts.get)
    # backward mapping: bitstring -> problem-model Items via the T1 trace, checked on the problem itself
    packed = backward.back(top, layout, sol_model, trace)
    problem = next(o for o in model.objects if o.classifier.name == "KnapsackProblem")
    row.update(valid=valid, top="{" + ", ".join(sorted(t1._slot(i, "name") for i in packed)) + "}",
               top_ok=choice(top) in solutions and backward.is_solution(packed, problem))
    return row


def table(rows):
    head = ("| Instance | n | Qubits | M | Rounds (model) | Rounds (optimal) | Oracle calls per shot "
            "| P theory | P measured | Most frequent answer | Is a solution? |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|\n")
    lines = []
    for r in rows:
        if r["valid"] is None:
            measured, top, ok = f"not run (> {MAX_QUBITS} qubits)", "-", "-"
        else:
            measured = f"{r['valid'] / r['shots']:.1%} ({r['valid']}/{r['shots']})"
            top = r["top"] if r["top"] != "{}" else "{} (empty)"
            ok = "yes" if r["top_ok"] else ("no (there is none)" if r["M"] == 0 else "NO")
        flag = "" if r["rounds"] == r["best_rounds"] else " (!)"
        lines.append(f"| {r['name']} | {r['n']} | {r['qubits']} | {r['M']} | {r['rounds']}{flag} "
                     f"| {r['best_rounds']} | {r['rounds']} | {r['p_theory']:.1%} | {measured} | {top} | {ok} |")
    return head + "\n".join(lines) + "\n"


def main(names):
    rows = []
    for name in names or INSTANCES:
        print(f"{name}: T1 -> T2 -> T3 -> Aer ...", flush=True)
        rows.append(run_instance(name))
    md = table(rows)
    note = ("\n(!) rounds in the solution model differ from floor(pi/4*sqrt(2^n/M)) "
            "computed from the baseline's M.\n") if any(r["rounds"] != r["best_rounds"] for r in rows) else ""
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/validation.md", "w", encoding="utf-8") as f:
        f.write("# Validation: Aer vs classical baseline\n\nGenerated by `python -m demo`.\n\n" + md + note)
    print("\n" + md + note + f"\nSaved: {OUT}/validation.md, {OUT}/t2/<instance>.py, {OUT}/t3/<instance>/qiskit_circuit.py")


if __name__ == "__main__":
    main(sys.argv[1:])

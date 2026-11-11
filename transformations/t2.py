"""T2 (M2M): linear-constraint solution model -> BESSER QuantumCircuit (Grover search).

Pipeline position:  Problem DSL --T1--> Solution DSL --T2--> Quantum DSL --T3--> Qiskit code

Rules (traceable to docs/concept_list.md section 4 and the references there):
  R1  ConstraintSystem -> QuantumCircuit (one quantum register q, classical register c of n bits)   Annex A class C
  R2  Unknown y_k, w bits -> w search qubits (LSB first), put in uniform superposition with H        [Gro96]
  R3  LinearExpression a0 + sum(a_i y_i) -> expression register of B bits, two's complement;
      a0 loaded with X gates                                                                         [NC10]; Annex A class C
  R4  Term a_i*y_i -> y_i-controlled addition of a_i into the expression register,
      ripple-carry adder (CDKM; QFT adder not implemented)                                           [CDKM04]; [VBE96]; [Dra00]
  R5  Atom LE / EQ -> comparator (sign bit and zero test) that sets one flag qubit per atom          [NC10]; Annex A class C
  R6  root And -> multi-controlled X from all flags onto the phase qubit in |->  (Or: not supported) [BBC+95]; [CEMM98]
  R7  compute flags, mark, then run the compute blocks backwards (uncompute: all gates self-inverse)   [Ben73]
  R8  Grover diffuser H X (multi-controlled Z) X H on the search register                            [Gro96]
  R9  SolverConfig.iterations -> exact number of rounds R (including zero);
      shots / backend are used by T3                                                                 [Gro96]; [BBHT98]; Annex B
  R10 Measure the search qubits; decode_bitstring / decode_items map them back to Unknown.name
      and item names                                                                                 traceability choice
  R11 The circuit goes to BESSER's QiskitGenerator (T3); the self-check saves the generated script
      to out/t3/<instance>/qiskit_circuit.py and runs it on the Aer simulator                         Annex B

Design
------
* The oracle is built ONLY from primitive BESSER gates (PauliXGate / HadamardGate /
  PauliZGate, each optionally with control qubits -> CX, Toffoli, multi-controlled X/Z).
  No ArithmeticGate / ComparisonGate, so the Qiskit generator never emits placeholders.
  (PhaseGateZ and CXGate are avoided on purpose: BESSER's Qiskit generator only maps
  PauliZGate / PauliXGate-with-controls reliably.)
* The expression / temporary / carry registers are shared by all atoms: each atom is
  computed, compared into its own flag qubit and uncomputed before the next one is needed.
* A controlled constant addition "e += a_i if y_i" is done as: controlled-load a_i into a
  temp register t (CX y_i -> t_j), e += t, controlled-unload.  The CDKM adder is modular
  and needs one carry ancilla.
* Phase kickback: the phase qubit is prepared in |-> and the flags are the controls of
  an MCX onto it (a multi-controlled Z on |-> would NOT kick back a phase).

Qubit layout (indices in the single register "q")
    [0, n)                 search register  (unknown k, bit j  ->  offset_k + j, LSB first)
    [n, n+B)               expression register e
    [n+B, n+2B)            temp register t
    n+2B                   carry ancilla
    n+2B+1 ... +m          one flag per atom
    last                   phase qubit (|->)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence, Tuple

from besser.BUML.metamodel.quantum import (
    ClassicalRegister, ControlState, HadamardGate, Measurement, PauliXGate,
    PauliZGate, QuantumCircuit,
)
from solution_dsl.solver_config import SolverSettings, read_config

# --------------------------------------------------------------------------- #
# DSL-independent intermediate form
# --------------------------------------------------------------------------- #

@dataclass
class AtomSpec:
    """Normalised atom:  const + sum(coeffs[q] * search_bit[q])  (<= 0 | == 0)."""
    const: int
    coeffs: Dict[int, int]          # search-qubit index -> integer coefficient
    kind: str = "LE"                # "LE" (value <= 0) or "EQ" (value == 0)

    def bounds(self) -> Tuple[int, int]:
        lo = self.const + sum(c for c in self.coeffs.values() if c < 0)
        hi = self.const + sum(c for c in self.coeffs.values() if c > 0)
        return lo, hi


@dataclass
class SystemSpec:
    unknown_names: List[str]
    unknown_widths: List[int]
    atoms: List[AtomSpec]
    iterations: int
    shots: int
    adder: str
    expression_bit_width: int
    expression_encoding: str

    def __post_init__(self):
        SolverSettings(self.iterations, self.shots, self.adder,
                       self.expression_bit_width, self.expression_encoding)
        if not self.unknown_widths or len(self.unknown_names) != len(self.unknown_widths):
            raise ValueError("Each unknown must have a name and a bit width")
        if any(type(w) is not int or w < 1 for w in self.unknown_widths):
            raise ValueError("Unknown bit widths must be positive integers")

    @property
    def n(self) -> int:
        return sum(self.unknown_widths)

    def offsets(self) -> List[int]:
        out, o = [], 0
        for w in self.unknown_widths:
            out.append(o)
            o += w
        return out


@dataclass
class Layout:
    n: int
    B: int
    e: List[int]
    t: List[int]
    carry: int
    flags: List[int]
    phase: int
    total: int
    unknown_names: List[str] = field(default_factory=list)
    unknown_widths: List[int] = field(default_factory=list)


Op = Tuple[str, int, Tuple[int, ...]]   # (gate, target, controls)  gate in {"X","Z","H"}


# --------------------------------------------------------------------------- #
# Reading the ConstraintSystem (BESSER ObjectModel produced by T1)   [R1, R2, R3 inputs]
# --------------------------------------------------------------------------- #

def _slot(obj, name):
    return next(s.value.value for s in obj.slots if s.attribute.name == name)


def _linked(obj, end):
    """Objects linked to `obj` through the association end called `end`."""
    return [c.object for l in obj.links for c in l.connections
            if c.name == end and c.object is not obj]


def _enum_name(x) -> str:
    return str(getattr(x, "name", x)).split(".")[-1].upper()


def _flatten_and(node) -> list:
    """Atoms of an And-tree.  Or is not supported by T2."""
    cls = node.classifier.name
    if cls == "Atom":
        return [node]
    if cls == "And":
        return [a for child in _linked(node, "operands") for a in _flatten_and(child)]
    raise NotImplementedError(f"T2 supports only And / Atom formulas, got {cls}")


def extract_spec(solution_model) -> SystemSpec:
    """Solution ObjectModel -> SystemSpec (plain data).

    Unknowns are ordered by their `name` slot, exactly like t1.solutions_of and the
    classical baseline, so search qubit k always belongs to the k-th unknown by name.
    """
    system = next(o for o in solution_model.objects if o.classifier.name == "ConstraintSystem")
    unknowns = sorted(_linked(system, "unknowns"), key=lambda u: _slot(u, "name"))
    names = [_slot(u, "name") for u in unknowns]
    widths = [_slot(u, "bitWidth") for u in unknowns]
    if any(type(w) is not int or w < 1 for w in widths):
        raise ValueError("Unknown bit widths must be positive integers")
    index = {id(u): k for k, u in enumerate(unknowns)}
    offsets, o = [], 0
    for w in widths:
        offsets.append(o)
        o += w

    atoms: List[AtomSpec] = []
    for atom in _flatten_and(_linked(system, "root")[0]):
        rel = _enum_name(_slot(atom, "relation"))
        expr = _linked(atom, "expression")[0]
        const = int(_slot(expr, "constant"))
        coeffs: Dict[int, int] = {}
        for term in _linked(expr, "terms"):
            c = int(_slot(term, "coefficient"))
            k = index[id(_linked(term, "unknown")[0])]
            for j in range(widths[k]):                 # y = sum_j 2^j * bit_j
                q = offsets[k] + j
                coeffs[q] = coeffs.get(q, 0) + c * (1 << j)
        if rel == "LE":
            kind = "LE"
        elif rel == "EQ":
            kind = "EQ"
        else:
            raise NotImplementedError(f"Unsupported relation {rel}")
        atoms.append(AtomSpec(const, {q: c for q, c in coeffs.items() if c}, kind))

    cfg = _linked(system, "config")
    if len(cfg) != 1:
        raise ValueError("ConstraintSystem must link exactly one SolverConfig")
    settings = read_config(cfg[0])
    return SystemSpec(names, widths, atoms, settings.iterations, settings.shots,
                      settings.adder, settings.expression_bit_width, settings.expression_encoding)


# --------------------------------------------------------------------------- #
# Gate-list construction (pure Python, classically simulable)   [R2-R8]
# --------------------------------------------------------------------------- #

def make_layout(spec: SystemSpec) -> Layout:
    """R1-R3, R5, R6: assign qubit indices (search, expression, temp, carry, flags, phase)."""
    n, m = spec.n, len(spec.atoms)
    B = spec.expression_bit_width
    for atom in spec.atoms:
        lo, hi = atom.bounds()
        if not (-(1 << (B - 1)) <= lo and hi < (1 << (B - 1))):
            raise ValueError(f"Configured expressionBitWidth={B} cannot hold atom range [{lo}, {hi}]")
    e = list(range(n, n + B))
    t = list(range(n + B, n + 2 * B))
    carry = n + 2 * B
    flags = list(range(carry + 1, carry + 1 + m))
    phase = carry + 1 + m
    return Layout(n, B, e, t, carry, flags, phase, phase + 1,
                  list(spec.unknown_names), list(spec.unknown_widths))


def _maj(x: int, y: int, z: int) -> List[Op]:
    return [("X", y, (z,)), ("X", x, (z,)), ("X", z, (x, y))]


def _uma(x: int, y: int, z: int) -> List[Op]:
    return [("X", z, (x, y)), ("X", x, (z,)), ("X", y, (x,))]


def cdkm_adder(a: List[int], b: List[int], c0: int) -> List[Op]:
    """R4: b <- (a + b) mod 2^len(b); a and c0 restored.  MAJ/UMA ripple-carry adder [CDKM04]
    (same family as the Vedral et al. adder [VBE96], with one carry ancilla)."""
    n = len(b)
    ops: List[Op] = []
    chain = [c0] + a[:-1]
    for i in range(n):
        ops += _maj(chain[i], b[i], a[i])
    for i in reversed(range(n)):
        ops += _uma(chain[i], b[i], a[i])
    return ops


def compute_expression(atom: AtomSpec, L: Layout) -> List[Op]:
    """R3 + R4: load a0, then e += a_i * y_i for every term  (all gates self-inverse)."""
    mod = 1 << L.B
    ops: List[Op] = []
    for j, q in enumerate(L.e):
        if (atom.const % mod) >> j & 1:
            ops.append(("X", q, ()))
    for y, c in sorted(atom.coeffs.items()):
        cm = c % mod
        load = [("X", L.t[j], (y,)) for j in range(L.B) if cm >> j & 1]
        ops += load + cdkm_adder(L.t, L.e, L.carry) + load
    return ops


def comparator(atom: AtomSpec, L: Layout, flag: int) -> List[Op]:
    """R5: flag ^= [e <= 0]  (sign bit XOR zero; mutually exclusive) or [e == 0]  [NC10]."""
    ops: List[Op] = []
    if atom.kind == "LE":
        ops.append(("X", flag, (L.e[-1],)))
    ops += [("X", q, ()) for q in L.e]
    ops.append(("X", flag, tuple(L.e)))
    ops += [("X", q, ()) for q in L.e]
    return ops


def atom_flag_block(atom: AtomSpec, L: Layout, flag: int) -> List[Op]:
    """R3-R5, R7: compute e, set the flag, uncompute e (the block is its own mirror image) [Ben73]."""
    comp = compute_expression(atom, L)
    return comp + comparator(atom, L, flag) + list(reversed(comp))   # self-inverse


def build_oracle_ops(spec: SystemSpec, L: Layout) -> List[Op]:
    """R6 + R7: flag blocks, MCX of all flags onto the |-> phase qubit [BBC+95][CEMM98], blocks reversed [Ben73]."""
    blocks = [atom_flag_block(a, L, f) for a, f in zip(spec.atoms, L.flags)]
    mark = [("X", L.phase, tuple(L.flags))]
    ops: List[Op] = []
    for b in blocks:
        ops += b
    ops += mark
    for b in reversed(blocks):
        ops += b
    return ops


def build_diffuser_ops(n: int) -> List[Op]:
    """R8: inversion about the mean, H X (multi-controlled Z) X H on the search register [Gro96]."""
    S = list(range(n))
    ops: List[Op] = [("H", q, ()) for q in S] + [("X", q, ()) for q in S]
    ops.append(("Z", S[-1], tuple(S[:-1])))
    ops += [("X", q, ()) for q in S] + [("H", q, ()) for q in S]
    return ops


# --------------------------------------------------------------------------- #
# BESSER emission   [R1, R2, R9, R10]
# --------------------------------------------------------------------------- #

def _emit(circ: QuantumCircuit, op: Op) -> None:
    g, t, ctrl = op
    ctrl_l = list(ctrl)
    states = [ControlState.CONTROL] * len(ctrl_l)
    if g == "X":
        circ.add_operation(PauliXGate(t, ctrl_l or None, states or None))
    elif g == "Z":
        circ.add_operation(PauliZGate(t, ctrl_l or None, states or None))
    elif g == "H":
        circ.add_operation(HadamardGate(t))
    else:
        raise ValueError(g)


def build_circuit_from_spec(spec: SystemSpec, name: str = "KnapsackGrover") -> Tuple[QuantumCircuit, Layout]:
    if spec.adder != "RIPPLE_CARRY":
        raise NotImplementedError(f"Adder kind {spec.adder} not implemented (only ripple-carry)")
    if not spec.atoms:
        raise ValueError("ConstraintSystem has no atoms")
    L = make_layout(spec)
    R = spec.iterations

    circ = QuantumCircuit(name, L.total)
    circ.add_creg(ClassicalRegister("c", L.n))

    # R6: phase qubit -> |->
    _emit(circ, ("X", L.phase, ()))
    _emit(circ, ("H", L.phase, ()))
    # R2: uniform superposition on search register [Gro96]
    for q in range(L.n):
        _emit(circ, ("H", q, ()))
    oracle, diffuser = build_oracle_ops(spec, L), build_diffuser_ops(L.n)
    for _ in range(R):                       # R9: R rounds of oracle + diffuser
        for op in oracle:
            _emit(circ, op)
        for op in diffuser:
            _emit(circ, op)
    for q in range(L.n):                     # R10: measure the search register
        circ.add_operation(Measurement(q, output_bit=q))
    return circ, L


def t2(constraint_system: Any, name: str = "KnapsackGrover") -> Tuple[QuantumCircuit, Layout]:
    """M2M transformation T2: ConstraintSystem -> (BESSER QuantumCircuit, Layout)."""
    spec = extract_spec(constraint_system)
    return build_circuit_from_spec(spec, name)


# --------------------------------------------------------------------------- #
# Classical decoding   [R10]
# --------------------------------------------------------------------------- #

def decode_bitstring(bitstring: str, layout_or_spec: Any) -> Dict[str, int]:
    """Qiskit count key (rightmost char = clbit 0 = search qubit 0)  ->  {unknown: value}.

    '1110' with unknowns [a,b,c,d] (1 bit each) -> {a:0, b:1, c:1, d:1}.
    """
    names, widths = layout_or_spec.unknown_names, layout_or_spec.unknown_widths
    bits = bitstring.replace(" ", "")[::-1]
    if len(bits) < sum(widths):
        raise ValueError(f"bitstring '{bitstring}' shorter than {sum(widths)} search qubits")
    out, o = {}, 0
    for nm, w in zip(names, widths):
        out[nm] = sum(int(bits[o + j]) << j for j in range(w))
        o += w
    return out


# --------------------------------------------------------------------------- #
# Self-check:  python -m transformations.t2
# --------------------------------------------------------------------------- #

def classical_run(ops: Sequence[Op], state: List[int]) -> List[int]:
    for g, t, ctrl in ops:
        if g == "X" and all(state[c] for c in ctrl):
            state[t] ^= 1
    return state


def decode_items(bitstring: str, layout: Layout) -> List[str]:
    """Domain item names packed by a measured bitstring (unknown 'y_<item>' -> '<item>')."""
    vals = decode_bitstring(bitstring, layout)
    return [nm[2:] if nm.startswith("y_") else nm for nm, v in vals.items() if v]


def _self_check(names=None, max_aer_qubits: int = 20) -> None:
    """For each instance: T1 -> T2, check the oracle classically, run on Aer, compare."""
    import itertools
    import os
    import subprocess
    import sys

    from besser.generators.qiskit import QiskitGenerator
    from models.instances import INSTANCES
    from models.solver_configs import CONFIGS
    from transformations import t1

    for name in names or INSTANCES:
        sol = t1.transform(INSTANCES[name], CONFIGS[name])[0]
        truth = set(t1.solutions_of(sol))                     # tuples in unknown-name order
        spec = extract_spec(sol)
        L = make_layout(spec)
        oracle = build_oracle_ops(spec, L)
        for bits in itertools.product([0, 1], repeat=L.n):
            st = [0] * L.total
            st[:L.n] = bits
            out = classical_run(oracle, st)
            assert out[L.phase] == (1 if bits in truth else 0), (name, bits)
            assert out[L.n:L.phase] == [0] * (L.phase - L.n), f"{name}: dirty ancillas {bits}"
        msg = f"{name:8s} n={L.n} qubits={L.total} B={L.B} solutions={len(truth)} oracle OK"
        if L.total <= max_aer_qubits and 0 < len(truth) < (1 << L.n):
            circ, L = build_circuit_from_spec(spec)
            d = os.path.join("out", "t3", name)                 # R11: keep the generated Qiskit script
            os.makedirs(d, exist_ok=True)
            QiskitGenerator(circ, output_dir=d, shots=spec.shots).generate()
            env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")   # Windows: qc.draw() is non-ASCII
            res = subprocess.run([sys.executable, f"{d}/qiskit_circuit.py"], capture_output=True,
                                 text=True, encoding="utf-8", errors="replace", env=env)
            lines = [l for l in res.stdout.splitlines() if l.startswith("Counts:")]
            if not lines:
                raise RuntimeError(f"generated script {d}/qiskit_circuit.py gave no counts "
                                   f"(exit {res.returncode}). stderr tail:\n{res.stderr[-1500:]}")
            counts = eval(lines[-1].split("Counts:")[1])
            good = sum(c for k, c in counts.items()
                       if tuple(decode_bitstring(k, L)[nm] for nm in L.unknown_names) in truth)
            top = max(counts, key=counts.get)
            msg += f" | Aer {good}/{sum(counts.values())} valid, top={decode_items(top, L)}"
            assert good / sum(counts.values()) > 0.7, msg
        print(msg)


if __name__ == "__main__":
    import sys
    _self_check(sys.argv[1:] or None)

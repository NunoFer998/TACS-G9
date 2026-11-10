# Part I concept lists

The concept lists are the result of the domain analysis, so they keep every domain concept.
The **In metamodel** column says what each concept becomes in the metamodel.

## 1. Problem DSL (knapsack feasibility)

| Concept | Description | Attributes | Connections | In metamodel | Reference |
|---|---|---|---|---|---|
| Knapsack Problem | The question: is there a choice of items that fits in the knapsack and is worth enough? | name: String | contains 1 Knapsack, 1..* Item, 1 Weight Constraint, 1 Value Constraint, 1 Objective Function | **class** `KnapsackProblem` (name, capacity, minValue) | [GJ79] MP9; Annex A class C, problem 2 |
| Knapsack | The container the items are packed into. | — | has 1 Target Weight; holds the selected Items | **attribute**: merged into `KnapsackProblem` (only carries the capacity) | [KPP04] |
| Item | Something that can be packed, with a weight and a value; it is packed at most once (0/1). | name: String (unique); weight: Integer (> 0); value: Integer (≥ 0) | belongs to 1 Knapsack Problem; counted in Total Weight and Total Value | **class** `Item` | [GJ79] MP9 (0/1 items) |
| Target Weight | The most weight the knapsack can carry (capacity C). | amount: Integer (≥ 0) | belongs to 1 Knapsack; used by Weight Constraint | **attribute** `KnapsackProblem.capacity` | [GJ79] MP9 (bound B) |
| Target Value | The least total value the packing must reach (V). | amount: Integer (≥ 0) | used by Value Constraint | **attribute** `KnapsackProblem.minValue` | [GJ79] MP9 (bound K) |
| Total Weight | Combined weight of the packed items, Σ wᵢ·yᵢ. | amount: Integer (derived) | sums over 1..* Item; checked by Weight Constraint | **derived** (becomes a LinearExpression in T1) | [KPP04] |
| Total Value | Combined value of the packed items, Σ vᵢ·yᵢ. | amount: Integer (derived) | sums over 1..* Item; checked by Value Constraint | **derived** (becomes a LinearExpression in T1) | [KPP04] |
| Weight Constraint | The packing must not be too heavy: Total Weight ≤ Target Weight. | — | compares Total Weight with Target Weight | **implicit** (T1 creates an Atom) | [GJ79] MP9 |
| Value Constraint | The packing must be worth enough: Total Value ≥ Target Value. | — | compares Total Value with Target Value | **implicit** (T1 creates an Atom) | [GJ79] MP9 |
| Objective Function | What is asked: find a packing that satisfies both constraints, or report that none exists (feasibility). | goal: FEASIBILITY | requires Weight Constraint and Value Constraint | **implicit** (T1 creates the root And) | Annex A class C ("Question") |
| Selection | What items are packed (the answer). | isSelected: Boolean | one per Item | **output** | Annex A class C |

### OCL constraints (problem DSL)

| Context | Name | OCL | Guarantees |
|---|---|---|---|
| KnapsackProblem | capacityNonNegative | `self.capacity >= 0` | capacity makes sense |
| KnapsackProblem | minValueNonNegative | `self.minValue >= 0` | target value makes sense |
| KnapsackProblem | uniqueItemNames | `self.items->forAll(i1, i2 \| i1 <> i2 implies i1.name <> i2.name)` | items can be told apart when decoding |
| Item | weightPositive | `self.weight > 0` | no weightless items |
| Item | valueNonNegative | `self.value >= 0` | no negative values |


## 2. Solution DSL (linear integer constraints)

| Concept | Description | Attributes | Connections | In metamodel | Reference |
|---|---|---|---|---|---|
| Constraint System | A system of linear integer constraints over bounded unknowns. | name: String | contains 1..* Unknown, 1 root Formula, 1 Solver Config | **class** `ConstraintSystem` | Annex A class C ("Instance") |
| Unknown | Integer variable yᵢ; with w bits it takes the values 0 … 2ʷ − 1. | name: String (unique); bitWidth: Integer (≥ 1) | used by 0..* Term | **class** `Unknown` | Annex A class C |
| Formula | Something that is true or false for a choice of the unknowns. | — | root of 1 Constraint System, or operand of 1 And/Or | **abstract class** `Formula` | Annex A class C (∧, ∨) |
| Atom | Compares one linear expression with zero. | relation: Relation | is a Formula; contains 1 Linear Expression | **class** `Atom` | Annex A class C |
| Relation | The comparison an atom makes. | EQ (= 0), LE (≤ 0) | used by Atom | **enum** `Relation` | Annex A class C |
| And / Or | True when all / at least one of the operands is true. | — | is a Formula; contains 2..* Formula | **classes** `And`, `Or` under abstract `Junction` | Annex A class C |
| Linear Expression | a₀ + a₁y₁ + … + aₙyₙ. | constant: Integer (a₀) | contains 0..* Term; belongs to 1 Atom | **class** `LinearExpression` | Annex A class C |
| Term | One coefficient times one unknown, aᵢ·yᵢ. | coefficient: Integer (≠ 0) | refers to 1 Unknown | **class** `Term` | Annex A class C |
| Solver Config | Explicit model input describing how the search runs. | iterations: Integer (≥ 0); shots: Integer (≥ 1); adder: AdderKind; expressionBitWidth: Integer (≥ 1); expressionEncoding: ExpressionEncoding | standalone input or owned by 1 Constraint System | **class** `SolverConfig` | Annex B [Gro96, BBHT98] |
| Adder Kind | Which reversible adder T2 builds. | RIPPLE_CARRY, QFT | used by Solver Config | **enum** `AdderKind` | [VBE96, CDKM04]; [Dra00] |
| Expression Encoding | Signed arithmetic representation. | TWOS_COMPLEMENT | used by Solver Config | **enum** `ExpressionEncoding` | [NC10] |
| Expression Register | Register of B bits that holds an expression's value in the oracle. | B = SolverConfig.expressionBitWidth | shared by all atoms; temp register has the same width | **configured** (T2 validates expression min/max fit, never resizes) | Annex A class C (implementation notes); [NC10] |


### OCL constraints (solution DSL)

| Context | Name | OCL | Guarantees |
|---|---|---|---|
| Unknown | bitWidthPositive | `self.bitWidth >= 1` | every unknown has at least one qubit |
| ConstraintSystem | uniqueUnknownNames | `self.unknowns->forAll(u1, u2 \| u1 <> u2 implies u1.name <> u2.name)` | unknowns can be told apart |
| ConstraintSystem | searchSpaceSimulable | `self.unknowns->collect(u \| u.bitWidth)->sum() <= 20` | search register fits the ~20-qubit limit |
| Term | coefficientNonZero | `self.coefficient <> 0` | no useless terms |
| LinearExpression | oneTermPerUnknown | `self.terms->forAll(t1, t2 \| t1 <> t2 implies t1.unknown <> t2.unknown)` | each unknown appears at most once per expression |
| Formula | singleParent | `self.rootOf->size() + self.parent->size() = 1` | the formulas form a tree with one root |
| Junction | noSelfOperand | `self.operands->excludes(self)` | no formula contains itself |
| SolverConfig | iterationsNonNegative | `self.iterations >= 0` | zero rounds are valid |
| SolverConfig | shotsPositive | `self.shots >= 1` | at least one shot |
| SolverConfig | expressionBitWidthPositive | `self.expressionBitWidth >= 1` | nonempty signed register |

## 3. Mapping problem → solution (seed of T1)

| Problem concept | Solution element | Reference |
|---|---|---|
| Knapsack Problem | 1 Constraint System | Annex A class C |
| Objective Function | root And of the weight atom and the value atom | Annex A class C (∧); [GJ79] MP9 (both conditions) |
| Item | 1 Unknown yᵢ, bitWidth = 1 (0 = left out, 1 = packed) | Annex A class C; [GJ79] MP9 (0/1 items) |
| Total Weight | Linear Expression with Terms wᵢ·yᵢ | [KPP04] capacity constraint |
| Target Weight / Knapsack | constant −C of the weight expression | Annex A class C (atom form "… ≤ 0") |
| Weight Constraint | Atom LE: Σ wᵢyᵢ − C ≤ 0 | Annex A class C |
| Total Value | Linear Expression with Terms −vᵢ·yᵢ (coefficients negated) | Annex A class C variants ("y₁ + y₂ ≥ 3 becomes 3 − y₁ − y₂ ≤ 0") |
| Target Value | constant +V of the value expression | same as above |
| Value Constraint | Atom LE: V − Σ vᵢyᵢ ≤ 0 | same as above |
| Item.name | Unknown.name (e.g. y_a), used to decode the answer | traceability choice |
| Selection | (not mapped: read back from the measured bits of yᵢ in Part II) | — |
| Solver configuration model | Copy of SolverConfig, preserving rounds, shots, adder, expression width and encoding | assignment section 2 |

## 4. Mapping solution → quantum circuit (seed of T2)

T2 builds the oracle only from primitive gates (X, Z, H with optional controls), so the BESSER Qiskit generator
never emits placeholders for high-level arithmetic or comparison gates.

| Solution element | Quantum circuit element | Reference |
|---|---|---|
| Constraint System | 1 `QuantumCircuit`: one quantum register `q`, one classical register `c` with n bits | Annex A class C |
| Unknown yₖ (w bits) | w search qubits (LSB first), each put in superposition with H; bits are read back by `Unknown.name` | [Gro96]; traceability choice |
| Linear Expression | Expression register of configured B bits (validated against every atom's min/max), temp register of B qubits, 1 carry ancilla; shared by all atoms | [NC10]; Annex A class C (implementation notes) |
| constant a₀ | X gates that load a₀ mod 2ᴮ into the expression register | [NC10] |
| Term aᵢ·yᵢ | yᵢ-controlled addition of aᵢ mod 2ᴮ: CX yᵢ → temp bits, adder, CX again (controlled load / unload) | [CDKM04]; [VBE96] |
| Adder Kind = RIPPLE_CARRY | MAJ/UMA ripple-carry adder with one carry ancilla (Adder Kind = QFT: not implemented) | [CDKM04]; [Dra00] |
| Atom LE | comparator: flag ⊕= [e < 0] ⊕ [e = 0] (sign bit, and zero test with X gates and one multi-controlled X); 1 flag qubit per atom | [NC10]; Annex A class C |
| Atom EQ | zero test only | [NC10] |
| root And | multi-controlled X from all flag qubits onto the phase qubit, which is in \|−⟩ (phase kickback) | [BBC+95]; [CEMM98] |
| Or | not supported by T2 (T1 never creates it) | — |
| (compute, mark, uncompute) | the flag blocks are run backwards after marking, so expression, temp, carry and flag qubits return to \|0⟩ | [Ben73] |
| (diffuser) | H, X, multi-controlled Z, X, H on the search register | [Gro96] |
| Solver Config.iterations | Exactly R repetitions of oracle + diffuser, including R = 0; no transformation default or override | [Gro96]; [BBHT98]; Annex B |
| Solver Config.shots, backend | shots of the Qiskit script generated in T3 (Aer simulator); the script is saved as `out/t3/<instance>/qiskit_circuit.py` | Annex B |
| Selection | measurement of the n search qubits; `decode_bitstring` / `decode_items` map the bits to Unknowns and item names | Annex A class C; traceability choice |

Qubit layout (single register `q`, indices in order):

| Qubits | Content |
|---|---|
| 0 … n−1 | search register (unknown k, bit j at offset_k + j) |
| n … n+B−1 | expression register e |
| n+B … n+2B−1 | temp register t (holds aᵢ while it is added) |
| n+2B | carry ancilla |
| next m | one flag per atom |
| last | phase qubit in \|−⟩ |

## References

- [GJ79] M. R. Garey, D. S. Johnson. *Computers and Intractability: A Guide to the Theory of NP-Completeness.* W. H. Freeman, 1979 (appendix, problem MP9 "Knapsack").
- [KPP04] H. Kellerer, U. Pferschy, D. Pisinger. *Knapsack Problems.* Springer, 2004.
- [Gro96] L. Grover. "A fast quantum mechanical algorithm for database search." STOC, 1996.
- [BBHT98] M. Boyer, G. Brassard, P. Høyer, A. Tapp. "Tight bounds on quantum searching." Fortschritte der Physik, 1998.
- [VBE96] V. Vedral, A. Barenco, A. Ekert. "Quantum networks for elementary arithmetic operations." Physical Review A, 1996.
- [CDKM04] S. Cuccaro et al. "A new quantum ripple-carry addition circuit." arXiv:quant-ph/0410184, 2004.
- [Dra00] T. Draper. "Addition on a quantum computer." arXiv:quant-ph/0008033, 2000.
- [BBC+95] A. Barenco, C. H. Bennett, R. Cleve, D. P. DiVincenzo, N. Margolus, P. Shor, T. Sleator, J. Smolin, H. Weinfurter. "Elementary gates for quantum computation." Physical Review A, 1995.
- [CEMM98] R. Cleve, A. Ekert, C. Macchiavello, M. Mosca. "Quantum algorithms revisited." Proceedings of the Royal Society A, 1998.
- [Ben73] C. H. Bennett. "Logical reversibility of computation." IBM Journal of Research and Development, 1973.
- [NC10] M. A. Nielsen, I. L. Chuang. *Quantum Computation and Quantum Information.* Cambridge University Press, 10th anniversary edition, 2010.
- Assignment: "TACS 2627 Assignment, QMDE"

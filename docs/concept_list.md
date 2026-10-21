# Part I concept lists

The concept lists are the result of the domain analysis, so they keep every domain concept.
The **In metamodel** column says what each concept becomes in the metamodel.

## 1. Problem DSL (knapsack feasibility)

| Concept | Description | Attributes | Connections | In metamodel | Reference |
|---|---|---|---|---|---|
| Knapsack Problem | The question: is there a choice of items that fits in the knapsack and is worth enough? | name: String | contains 1 Knapsack, 1..* Item, 1 Weight Constraint, 1 Value Constraint, 1 Objective Function | **class** `KnapsackProblem` (name, capacity, minValue) | [GJ79] MP9; Annex A class C, problem 2 |
| Knapsack | The container the items are packed into. | — | has 1 Target Weight; holds the selected Items | **attribute**: merged into `KnapsackProblem` (only carries the capacity) | [KPP04] |
| Item | Something that can be packed, with a weight, a value and a number of available copies. | name: String (unique); weight: Integer (> 0); value: Integer (≥ 0); quantity: Integer (≥ 1, default 1) | belongs to 1 Knapsack Problem; counted in Total Weight and Total Value | **class** `Item` | [GJ79] MP9 (0/1 items); [KPP04] bounded knapsack (quantity) |
| Target Weight | The most weight the knapsack can carry (capacity C). | amount: Integer (≥ 0) | belongs to 1 Knapsack; used by Weight Constraint | **attribute** `KnapsackProblem.capacity` | [GJ79] MP9 (bound B) |
| Target Value | The least total value the packing must reach (V). | amount: Integer (≥ 0) | used by Value Constraint | **attribute** `KnapsackProblem.minValue` | [GJ79] MP9 (bound K) |
| Total Weight | Combined weight of the packed items, Σ wᵢ·yᵢ. | amount: Integer (derived) | sums over 1..* Item; checked by Weight Constraint | **derived** (becomes a LinearExpression in T1) | [KPP04] |
| Total Value | Combined value of the packed items, Σ vᵢ·yᵢ. | amount: Integer (derived) | sums over 1..* Item; checked by Value Constraint | **derived** (becomes a LinearExpression in T1) | [KPP04] |
| Weight Constraint | The packing must not be too heavy: Total Weight ≤ Target Weight. | — | compares Total Weight with Target Weight | **implicit** (T1 creates an Atom) | [GJ79] MP9 |
| Value Constraint | The packing must be worth enough: Total Value ≥ Target Value. | — | compares Total Value with Target Value | **implicit** (T1 creates an Atom) | [GJ79] MP9 |
| Objective Function | What is asked: find a packing that satisfies both constraints, or report that none exists (feasibility). | goal: FEASIBILITY | requires Weight Constraint and Value Constraint | **implicit** (T1 creates the root And) | Annex A class C ("Question") |
| Selection | What items are packed (the answer). | isSelected: Boolen | one per Item | **output** | Annex A class C |

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
| Constraint System | A system of linear integer constraints over bounded unknowns. | name: String | contains 1..* Unknown, 1 root Formula, | **class** `ConstraintSystem` | Annex A class C ("Instance") |
| Unknown | Integer variable yᵢ; with w bits it takes the values 0 … 2ʷ − 1. | name: String (unique); bitWidth: Integer (≥ 1) | used by 0..* Term | **class** `Unknown` | Annex A class C |
| Formula | Something that is true or false for a choice of the unknowns. | — | root of 1 Constraint System, or operand of 1 And/Or | **abstract class** `Formula` | Annex A class C (∧, ∨) |
| Atom | Compares one linear expression with zero. | relation: Relation | is a Formula; contains 1 Linear Expression | **class** `Atom` | Annex A class C |
| Relation | The comparison an atom makes. | EQ (= 0), LE (≤ 0) | used by Atom | **enum** `Relation` | Annex A class C |
| And / Or | True when all / at least one of the operands is true. | — | is a Formula; contains 2..* Formula | **classes** `And`, `Or` under abstract `Junction` | Annex A class C |
| Linear Expression | a₀ + a₁y₁ + … + aₙyₙ. | constant: Integer (a₀) | contains 0..* Term; belongs to 1 Atom | **class** `LinearExpression` | Annex A class C |
| Term | One coefficient times one unknown, aᵢ·yᵢ. | coefficient: Integer (≠ 0) | refers to 1 Unknown | **class** `Term` | Annex A class C | 
Solver Config | How the search runs; kept out of the transformations. | iterations: Integer (≥ 0); shots: Integer (≥ 1); adder: AdderKind | belongs to 1 Constraint System | **class** `SolverConfig` | Annex B [Gro96, BBHT98] |
| Adder Kind | Which reversible adder T2 builds. | RIPPLE_CARRY, QFT | used by Solver Config | **enum** `AdderKind` | [VBE96, CDKM04]; [Dra00] |
| Expression Register | Two's-complement register of B bits that holds an expression's value in the oracle. | B: Integer (derived from the expression's min/max) | one per Linear Expression | **derived** (computed by T2, not stored) | Annex A class C (implementation notes) |


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

## 3. Mapping problem → solution (seed of T1)

| Problem concept | Solution element | Reference |
|---|---|---|
| Knapsack Problem | 1 Constraint System | Annex A class C |
| Objective Function | root And of the weight atom, the value atom and any quantity atoms | Annex A class C (∧); [GJ79] MP9 (both conditions) |
| Item | 1 Unknown yᵢ, bitWidth = ⌈log₂(quantity + 1)⌉ (1 bit when quantity = 1) | Annex A class C; [KPP04] bounded knapsack |
| Item.quantity (when quantity + 1 is not a power of 2) | extra Atom LE: yᵢ − quantity ≤ 0 | Annex A class C variants ("y₁ ≤ 10 becomes y₁ − 10 ≤ 0") |
| Total Weight | Linear Expression with Terms wᵢ·yᵢ | [KPP04] capacity constraint |
| Target Weight / Knapsack | constant −C of the weight expression | Annex A class C (atom form "… ≤ 0") |
| Weight Constraint | Atom LE: Σ wᵢyᵢ − C ≤ 0 | Annex A class C |
| Total Value | Linear Expression with Terms −vᵢ·yᵢ (coefficients negated) | Annex A class C variants ("y₁ + y₂ ≥ 3 becomes 3 − y₁ − y₂ ≤ 0") |
| Target Value | constant +V of the value expression | same as above |
| Value Constraint | Atom LE: V − Σ vᵢyᵢ ≤ 0 | same as above |
| Item.name | Unknown.name (e.g. y_a), used to decode the answer | traceability choice |
| Selection | (not mapped: read back from the measured bits of yᵢ in Part II) | — |

## References

- [GJ79] M. R. Garey, D. S. Johnson. *Computers and Intractability: A Guide to the Theory of NP-Completeness.* W. H. Freeman, 1979 (appendix, problem MP9 "Knapsack").
- [KPP04] H. Kellerer, U. Pferschy, D. Pisinger. *Knapsack Problems.* Springer, 2004.
- [Gro96] L. Grover. "A fast quantum mechanical algorithm for database search." STOC, 1996.
- [BBHT98] M. Boyer, G. Brassard, P. Høyer, A. Tapp. "Tight bounds on quantum searching." Fortschritte der Physik, 1998.
- [VBE96] V. Vedral, A. Barenco, A. Ekert. "Quantum networks for elementary arithmetic operations." Physical Review A, 1996.
- [CDKM04] S. Cuccaro et al. "A new quantum ripple-carry addition circuit." arXiv:quant-ph/0410184, 2004.
- [Dra00] T. Draper. "Addition on a quantum computer." arXiv:quant-ph/0008033, 2000.
- Assignment: "TACS 2627 Assignment, QMDE"


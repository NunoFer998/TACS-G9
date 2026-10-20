# Hand-built example object models

These tables specify one problem object model and its expected T1 solution
object model by hand. They instantiate the existing B-UML metamodels; they are
not generated models or an implementation of T1. Tables are used as the object
model representation permitted by the deliverable description.

## Example instance

This is an illustrative 0/1 knapsack instance, not one of the named benchmarks
in [the instance list](../instances/instances.md), which does not include item
data. Each item can be selected at most once.

| Item | Weight | Value |
|---|---:|---:|
| a | 2 | 3 |
| b | 3 | 4 |
| c | 4 | 5 |

Capacity is 5 and minimum required value is 7. No `quantity` or selection
attribute is added: neither belongs to the current problem metamodel.

## Problem object model

Metamodel: [problem_metamodel.py](../problem_dsl/problem_metamodel.py).

### Objects and attribute values

| Object ID | Class | Attributes |
|---|---|---|
| p | KnapsackProblem | name = "toy", capacity = 5, minValue = 7 |
| i1 | Item | name = "a", weight = 2, value = 3 |
| i2 | Item | name = "b", weight = 3, value = 4 |
| i3 | Item | name = "c", weight = 4, value = 5 |

### Links

Each row lists one association instance from both navigation directions; the
two directions describe the same link, not two separate links.

| Association | Forward navigation | Inverse navigation |
|---|---|---|
| problem_items | p.items contains i1 | i1.problem = p |
| problem_items | p.items contains i2 | i2.problem = p |
| problem_items | p.items contains i3 | i3.problem = p |

The problem contains three items (satisfying `1..*`); each item has one owner
(allowed by the current `0..1` inverse multiplicity). All items are composition
parts of p.

### OCL checks

| Invariant | Check |
|---|---|
| capacityNonNegative | 5 >= 0 |
| minValueNonNegative | 7 >= 0 |
| uniqueItemNames | "a", "b", and "c" are distinct within p.items |
| weightPositive | 2, 3, and 4 are all > 0 |
| valueNonNegative | 3, 4, and 5 are all >= 0 |

## Solution object model

Metamodel: [solution_metamodel.py](../solution_dsl/solution_metamodel.py).

### Objects and attribute values

Unknown object IDs y1, y2, and y3 correspond to items i1, i2, and i3. Their
`name` attributes preserve the concept-list naming convention `y_<item name>`.
Each unknown has domain {0, 1}: 0 means omitted and 1 means selected.

| Object ID | Concrete class | Attributes |
|---|---|---|
| s | ConstraintSystem | name = "toy" |
| y1 | Unknown | name = "y_a", bitWidth = 1 |
| y2 | Unknown | name = "y_b", bitWidth = 1 |
| y3 | Unknown | name = "y_c", bitWidth = 1 |
| root | And | None |
| atomW | Atom | relation = Relation::LE |
| atomV | Atom | relation = Relation::LE |
| expressionW | LinearExpression | constant = -5 |
| expressionV | LinearExpression | constant = 7 |
| tW1 | Term | coefficient = 2 |
| tW2 | Term | coefficient = 3 |
| tW3 | Term | coefficient = 4 |
| tV1 | Term | coefficient = -3 |
| tV2 | Term | coefficient = -4 |
| tV3 | Term | coefficient = -5 |

`And` inherits from `Junction`, which inherits from `Formula`. Both atoms also
inherit from `Formula`. There are no instances of the abstract classes and
enumeration literals are attribute values, not additional objects.

### Links

| Association | Forward navigation | Inverse navigation |
|---|---|---|
| system_unknowns | s.unknowns contains y1 | y1.system = s |
| system_unknowns | s.unknowns contains y2 | y2.system = s |
| system_unknowns | s.unknowns contains y3 | y3.system = s |
| system_root | s.root = root | root.rootOf = s |
| junction_operands | root.operands contains atomW | atomW.parent = root |
| junction_operands | root.operands contains atomV | atomV.parent = root |
| atom_expression | atomW.expression = expressionW | expressionW.atom = atomW |
| atom_expression | atomV.expression = expressionV | expressionV.atom = atomV |
| expression_terms | expressionW.terms contains tW1 | tW1.expr = expressionW |
| expression_terms | expressionW.terms contains tW2 | tW2.expr = expressionW |
| expression_terms | expressionW.terms contains tW3 | tW3.expr = expressionW |
| expression_terms | expressionV.terms contains tV1 | tV1.expr = expressionV |
| expression_terms | expressionV.terms contains tV2 | tV2.expr = expressionV |
| expression_terms | expressionV.terms contains tV3 | tV3.expr = expressionV |
| term_unknown | tW1.unknown = y1 | y1.usedBy contains tW1 |
| term_unknown | tW2.unknown = y2 | y2.usedBy contains tW2 |
| term_unknown | tW3.unknown = y3 | y3.usedBy contains tW3 |
| term_unknown | tV1.unknown = y1 | y1.usedBy contains tV1 |
| term_unknown | tV2.unknown = y2 | y2.usedBy contains tV2 |
| term_unknown | tV3.unknown = y3 | y3.usedBy contains tV3 |

Unlisted optional links are absent: root has no parent, and neither atom has
a rootOf link. Collection-valued roles contain only the objects listed above.
All composite parts have a single owner. The root has exactly two operands,
each atom has one expression, and each term refers to one unknown.

### Optional solver configuration

The mathematical model above is the expected output of T1. The metamodel also
allows an optional configuration; for a configured example, add this object
and link. These are execution choices, not values inferred from the items by T1.

| Object ID | Class | Attributes |
|---|---|---|
| cfg | SolverConfig | iterations = 1, shots = 1024, adder = AdderKind::RIPPLE_CARRY |

| Association | Forward navigation | Inverse navigation |
|---|---|---|
| system_config | s.config = cfg | cfg.configOf = s |

Without this optional extension, s.config is absent and no cfg object exists.

### Expected T1 mapping

| Source | Target |
|---|---|
| p | s, preserving the problem name |
| i1, i2, i3 | y1, y2, y3 respectively, each with bitWidth = 1 |
| p.capacity = 5 | expressionW.constant = -5 |
| Item weights 2, 3, 4 | tW1, tW2, tW3 coefficients 2, 3, 4 |
| p.minValue = 7 | expressionV.constant = 7 |
| Item values 3, 4, 5 | tV1, tV2, tV3 coefficients -3, -4, -5 |
| Both knapsack conditions | root, an And over the two LE atoms |

Writing y1, y2, and y3 for the unknown values, the atoms encode:

$$
2y_1 + 3y_2 + 4y_3 - 5 \leq 0
$$

$$
7 - 3y_1 - 4y_2 - 5y_3 \leq 0
$$

The root requires both atoms to hold. The second inequality is exactly the
minimum-value requirement, not an upper bound on value. No quantity atoms are
needed for this 0/1 instance.

### OCL checks

| Invariant | Check |
|---|---|
| bitWidthPositive | Every unknown has bitWidth = 1 >= 1 |
| uniqueUnknownNames | "y_a", "y_b", and "y_c" are distinct |
| searchSpaceSimulable | 1 + 1 + 1 = 3 <= 20 search bits |
| coefficientNonZero | 2, 3, 4, -3, -4, and -5 are all nonzero |
| oneTermPerUnknown | Each expression has exactly one term for each of y1, y2, y3 |
| singleParent | root has one rootOf and no parent; each atom has one parent and no rootOf |
| noSelfOperand | root.operands = {atomW, atomV}, which excludes root |
| iterationsNonNegative | If cfg is included, 1 >= 0 |
| shotsPositive | If cfg is included, 1024 >= 1 |

## Expected answer

All eight possible selections are listed by hand below. This is a semantic
check of the example, not an executed OCL validation or a quantum simulation.

| (y1, y2, y3) | Selected items | Total weight | Total value | Feasible? |
|---|---|---:|---:|---|
| (0, 0, 0) | None | 0 | 0 | No: value < 7 |
| (1, 0, 0) | a | 2 | 3 | No: value < 7 |
| (0, 1, 0) | b | 3 | 4 | No: value < 7 |
| (0, 0, 1) | c | 4 | 5 | No: value < 7 |
| (1, 1, 0) | a, b | 5 | 7 | Yes |
| (1, 0, 1) | a, c | 6 | 8 | No: weight > 5 |
| (0, 1, 1) | b, c | 7 | 9 | No: weight > 5 |
| (1, 1, 1) | a, b, c | 9 | 12 | No: weight > 5 |

The unique satisfying assignment is (y1, y2, y3) = (1, 1, 0). It makes both
linear expressions zero, selecting a and b with weight 5 and value 7. This is
the expected marked assignment for a future Grover oracle, not a guarantee
that every quantum measurement returns it. Measured bitstring ordering must
be specified when the quantum encoding is implemented in Part II.
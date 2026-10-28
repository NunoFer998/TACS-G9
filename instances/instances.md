# Instances:

|            | Instance           | n   | W   | Opt | Qubits |
| ---------- | ------------------ | --- | --- | --- | ------ |
| Small      | `f4_l-d_kp_4_11`   | 4   | 11  | 23  | 15 (4+5+6)   |
| Medium     | `f7_l-d_kp_7_50`   | 7   | 50  | 107 | 22 (7+7+8)   |
| Large      | `f1_l-d_kp_10_269` | 10  | 269 | 295 | 30 (10+10+10) |
| Infeasible | `f7_l-d_kp_7_50`   | 7   | 50  | 108 | 22 (7+7+8)   |

Qubits = n + bits(Σw·y − W − 1) + bits(V − Σv·y − 1), with V = Opt; bits = smallest two's complement width for the range
(see `docs/report_part2.md`). Lower bound: the T2 adder may add ancillas. Σw/Σv: f4 19/41, f7 93/188, f1 539/412.

# Simulated instances (≤ ~20 qubits, as in `models/instances.py`)

| Instance   | Role                     | n | C  | V  | M | Qubits |
| ---------- | ------------------------ | - | -- | -- | - | ------ |
| `toy`      | tiny, checkable by hand  | 3 | 5  | 7  | 1 | 11     |
| `tiny`     | Annex A example          | 4 | 10 | 15 | 1 | 14     |
| `f4`       | small, known optimum     | 4 | 11 | 23 | 1 | 15     |
| `f4_multi` | several solutions        | 4 | 11 | 16 | 5 | 15     |
| `f4_none`  | no solution              | 4 | 11 | 24 | 0 | 15     |
| `f7_sub5`  | near the 20-qubit limit  | 5 | 25 | 46 | 1 | 20     |

f7 (22) and f1 (30) above exceed the simulation limit, so they are not run.

# Ref : 
https://github.com/dnlfm/knapsack-01-instances/blob/main/pisinger_instances_01_KP/low-dimensional/f1_l-d_kp_10_269
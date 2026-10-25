"""Problem object models for the Part II test instances.

Each instance is a KnapsackProblem object model (problem DSL). Item data for the
Pisinger instances comes from
https://github.com/dnlfm/knapsack-01-instances/tree/main/pisinger_instances_01_KP/low-dimensional
(file format: "n C" then one "value weight" line per item).

| Name        | Source                          | Role                          |
|-------------|---------------------------------|-------------------------------|
| toy         | docs/example_object_models.md   | tiny, checkable by hand       |
| tiny        | Annex A example (class D)       | unique solution               
| f4          | Pisinger f4_l-d_kp_4_11, V=opt  | unique solution (optimum)     |
| f4_multi    | f4 with V=16                    | several solutions             |
| f4_none     | f4 with V=opt+1                 | no solution                   |
| f7_sub5     | first 5 items of f7, C=25, V=46 | medium, close to ~20 qubits   |
"""
from besser.BUML.metamodel.object import ObjectModel
from problem_dsl.problem_metamodel import KnapsackProblem, Item


def make_problem(name, capacity, min_value, items):
    """Build a problem object model. items = [(item_name, weight, value), ...]."""
    item_objs = [Item(f"{name}_{n}").attributes(name=n, weight=w, value=v).build()
                 for n, w, v in items]
    problem = (KnapsackProblem(name)
               .attributes(name=name, capacity=capacity, minValue=min_value)
               .link(set(item_objs), "items").build())
    return ObjectModel(name=name, objects={problem, *item_objs})


# Pisinger f4_l-d_kp_4_11 (value weight): 6 2 / 10 4 / 12 6 / 13 7, C=11, opt=23
F4 = [("i1", 2, 6), ("i2", 4, 10), ("i3", 6, 12), ("i4", 7, 13)]
# Pisinger f7_l-d_kp_7_50, first 5 items (value weight): 70 31 / 20 10 / 39 20 / 37 19 / 7 4
F7_SUB5 = [("i1", 31, 70), ("i2", 10, 20), ("i3", 20, 39), ("i4", 19, 37), ("i5", 4, 7)]

INSTANCES = {
    "toy": make_problem("toy", 5, 7, [("a", 2, 3), ("b", 3, 4), ("c", 4, 5)]),
    "tiny": make_problem("tiny", 10, 15, [("a", 2, 3), ("b", 3, 4), ("c", 5, 8), ("d", 7, 9)]),
    "f4": make_problem("f4", 11, 23, F4),
    "f4_multi": make_problem("f4_multi", 11, 16, F4),
    "f4_none": make_problem("f4_none", 11, 24, F4),
    "f7_sub5": make_problem("f7_sub5", 25, 46, F7_SUB5),
}

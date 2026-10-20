"""Problem DSL: knapsack feasibility (class C, problem 2), 0/1 version.

Question: is there a choice of items (each taken at most once) whose total
weight is <= capacity and whose total value is >= minValue?
"""
from besser.BUML.metamodel.structural import (
    DomainModel, Class, Property, BinaryAssociation, Multiplicity,
    Constraint, StringType, IntegerType,
)

# --- Classes ---------------------------------------------------------------

problem_name = Property(name="name", type=StringType)
capacity = Property(name="capacity", type=IntegerType)      # C
min_value = Property(name="minValue", type=IntegerType)     # V
KnapsackProblem = Class(name="KnapsackProblem",
                        attributes={problem_name, capacity, min_value})

item_name = Property(name="name", type=StringType)
weight = Property(name="weight", type=IntegerType)
value = Property(name="value", type=IntegerType)
Item = Class(name="Item", attributes={item_name, weight, value})

# --- Associations ----------------------------------------------------------

# "problem" is 0..1 rather than 1 so that neither class needs the other to be
# created first; the composition already guarantees every Item has one owner.
problem_items = BinaryAssociation(
    name="problem_items",
    ends={
        Property(name="problem", type=KnapsackProblem, multiplicity=Multiplicity(0, 1)),
        Property(name="items", type=Item, multiplicity=Multiplicity(1, "*"),
                 is_composite=True),
    },
)

# --- OCL constraints -------------------------------------------------------

constraints = {
    Constraint(name="capacityNonNegative", context=KnapsackProblem, language="OCL",
               expression="context KnapsackProblem inv capacityNonNegative: self.capacity >= 0"),
    Constraint(name="minValueNonNegative", context=KnapsackProblem, language="OCL",
               expression="context KnapsackProblem inv minValueNonNegative: self.minValue >= 0"),
    Constraint(name="uniqueItemNames", context=KnapsackProblem, language="OCL",
               expression="context KnapsackProblem inv uniqueItemNames: "
                          "self.items->forAll(i1, i2 | i1 <> i2 implies i1.name <> i2.name)"),
    Constraint(name="weightPositive", context=Item, language="OCL",
               expression="context Item inv weightPositive: self.weight > 0"),
    Constraint(name="valueNonNegative", context=Item, language="OCL",
               expression="context Item inv valueNonNegative: self.value >= 0"),
}

problem_metamodel = DomainModel(
    name="KnapsackProblemDSL",
    types={KnapsackProblem, Item},
    associations={problem_items},
    constraints=constraints,
)

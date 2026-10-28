####################
# STRUCTURAL MODEL #
####################

from besser.BUML.metamodel.structural import (
    Class, Property, Method, Parameter,
    BinaryAssociation, Generalization, DomainModel,
    Enumeration, EnumerationLiteral, Multiplicity,
    StringType, IntegerType, FloatType, BooleanType,
    TimeType, DateType, DateTimeType, TimeDeltaType,
    AnyType, Constraint, AssociationClass, Metadata, MethodImplementationType
)
from besser.BUML.metamodel.object import ObjectModel
import datetime

# Enumerations
Relation: Enumeration = Enumeration(
    name="Relation",
    literals={
            EnumerationLiteral(name="EQ"),
			EnumerationLiteral(name="LE")
    }
)

AdderKind: Enumeration = Enumeration(
    name="AdderKind",
    literals={
            EnumerationLiteral(name="RIPPLE_CARRY"),
			EnumerationLiteral(name="QFT")
    }
)

# Classes
ConstraintSystem = Class(name="ConstraintSystem")
Unknown = Class(name="Unknown")
Formula = Class(name="Formula", is_abstract=True)
Atom = Class(name="Atom")
Junction = Class(name="Junction", is_abstract=True)
And = Class(name="And")
Or = Class(name="Or")
LinearExpression = Class(name="LinearExpression")
Term = Class(name="Term")
SolverConfig = Class(name="SolverConfig")

# ConstraintSystem class attributes and methods
ConstraintSystem_name: Property = Property(name="name", type=StringType)
ConstraintSystem.attributes={ConstraintSystem_name}

# Unknown class attributes and methods
Unknown_name: Property = Property(name="name", type=StringType)
Unknown_bitWidth: Property = Property(name="bitWidth", type=IntegerType)
Unknown.attributes={Unknown_bitWidth, Unknown_name}

# Formula class attributes and methods

# Atom class attributes and methods
Atom_relation: Property = Property(name="relation", type=Relation)
Atom.attributes={Atom_relation}

# Junction class attributes and methods

# And class attributes and methods

# Or class attributes and methods

# LinearExpression class attributes and methods
LinearExpression_constant: Property = Property(name="constant", type=IntegerType)
LinearExpression.attributes={LinearExpression_constant}

# Term class attributes and methods
Term_coefficient: Property = Property(name="coefficient", type=IntegerType)
Term.attributes={Term_coefficient}

# SolverConfig class attributes and methods
SolverConfig_iterations: Property = Property(name="iterations", type=IntegerType)
SolverConfig_shots: Property = Property(name="shots", type=IntegerType)
SolverConfig_adder: Property = Property(name="adder", type=AdderKind)
SolverConfig.attributes={SolverConfig_adder, SolverConfig_iterations, SolverConfig_shots}

# Relationships
term_unknown: BinaryAssociation = BinaryAssociation(
    name="term_unknown",
    ends={
        Property(name="usedBy", type=Term, multiplicity=Multiplicity(0, 9999)),
        Property(name="unknown", type=Unknown, multiplicity=Multiplicity(1, 1))
    }
)
system_config: BinaryAssociation = BinaryAssociation(
    name="system_config",
    ends={
        Property(name="configOf", type=ConstraintSystem, multiplicity=Multiplicity(1, 1)),
        Property(name="config", type=SolverConfig, multiplicity=Multiplicity(0, 1), is_composite=True)
    }
)
system_unknowns: BinaryAssociation = BinaryAssociation(
    name="system_unknowns",
    ends={
        Property(name="system", type=ConstraintSystem, multiplicity=Multiplicity(0, 1)),
        Property(name="unknowns", type=Unknown, multiplicity=Multiplicity(1, 9999), is_composite=True)
    }
)
system_root: BinaryAssociation = BinaryAssociation(
    name="system_root",
    ends={
        Property(name="rootOf", type=ConstraintSystem, multiplicity=Multiplicity(0, 1)),
        Property(name="root", type=Formula, multiplicity=Multiplicity(1, 1), is_composite=True)
    }
)
junction_operands: BinaryAssociation = BinaryAssociation(
    name="junction_operands",
    ends={
        Property(name="parent", type=Junction, multiplicity=Multiplicity(0, 1)),
        Property(name="operands", type=Formula, multiplicity=Multiplicity(2, 9999), is_composite=True)
    }
)
atom_expression: BinaryAssociation = BinaryAssociation(
    name="atom_expression",
    ends={
        Property(name="atom", type=Atom, multiplicity=Multiplicity(0, 1)),
        Property(name="expression", type=LinearExpression, multiplicity=Multiplicity(1, 1), is_composite=True)
    }
)
expression_terms: BinaryAssociation = BinaryAssociation(
    name="expression_terms",
    ends={
        Property(name="expr", type=LinearExpression, multiplicity=Multiplicity(1, 1)),
        Property(name="terms", type=Term, multiplicity=Multiplicity(0, 9999), is_composite=True)
    }
)

# Generalizations
gen_Atom_Formula = Generalization(general=Formula, specific=Atom)
gen_Junction_Formula = Generalization(general=Formula, specific=Junction)
gen_And_Junction = Generalization(general=Junction, specific=And)
gen_Or_Junction = Generalization(general=Junction, specific=Or)


# OCL Constraints
bitWidthPositive: Constraint = Constraint(
    name="bitWidthPositive",
    context=Unknown,
    expression="context Unknown inv bitWidthPositive: self.bitWidth >= 1",
    language="OCL"
)
uniqueUnknownNames: Constraint = Constraint(
    name="uniqueUnknownNames",
    context=ConstraintSystem,
    expression="context ConstraintSystem inv uniqueUnknownNames: self.unknowns->forAll(u1, u2 | u1 <> u2 implies u1.name <> u2.name)",
    language="OCL"
)
searchSpaceSimulable: Constraint = Constraint(
    name="searchSpaceSimulable",
    context=ConstraintSystem,
    expression="context ConstraintSystem inv searchSpaceSimulable: self.unknowns->collect(u | u.bitWidth)->sum() <= 20",
    language="OCL"
)
coefficientNonZero: Constraint = Constraint(
    name="coefficientNonZero",
    context=Term,
    expression="context Term inv coefficientNonZero: self.coefficient <> 0",
    language="OCL"
)
oneTermPerUnknown: Constraint = Constraint(
    name="oneTermPerUnknown",
    context=LinearExpression,
    expression="context LinearExpression inv oneTermPerUnknown: self.terms->forAll(t1, t2 | t1 <> t2 implies t1.unknown <> t2.unknown)",
    language="OCL"
)
singleParent: Constraint = Constraint(
    name="singleParent",
    context=Formula,
    expression="context Formula inv singleParent: self.rootOf->size() + self.parent->size() = 1",
    language="OCL"
)
noSelfOperand: Constraint = Constraint(
    name="noSelfOperand",
    context=Junction,
    expression="context Junction inv noSelfOperand: self.operands->excludes(self)",
    language="OCL"
)
iterationsNonNegative: Constraint = Constraint(
    name="iterationsNonNegative",
    context=SolverConfig,
    expression="context SolverConfig inv iterationsNonNegative: self.iterations >= 0",
    language="OCL"
)
shotsPositive: Constraint = Constraint(
    name="shotsPositive",
    context=SolverConfig,
    expression="context SolverConfig inv shotsPositive: self.shots >= 1",
    language="OCL"
)

# Domain Model
domain_model = DomainModel(
    name="LinearConstraintsDSL",
    types={ConstraintSystem, Unknown, Formula, Atom, Junction, And, Or, LinearExpression, Term, SolverConfig, Relation, AdderKind},
    associations={term_unknown, system_config, system_unknowns, system_root, junction_operands, atom_expression, expression_terms},
    constraints={bitWidthPositive, uniqueUnknownNames, searchSpaceSimulable, coefficientNonZero, oneTermPerUnknown, singleParent, noSelfOperand, iterationsNonNegative, shotsPositive},
    generalizations={gen_Atom_Formula, gen_Junction_Formula, gen_And_Junction, gen_Or_Junction},
    metadata=None
)

################
# OBJECT MODEL #
################
knapsack_obj = ConstraintSystem("Knapsack").attributes(name="Knapsack").build()
knapsack_config_obj = SolverConfig("Knapsack_config").attributes(iterations=1, shots=1024, adder=AdderKind.RIPPLE_CARRY).build()
knapsack_root_obj = And("Knapsack_root").build()
knapsack_v_e_obj = LinearExpression("Knapsack_v_e").attributes(constant=23).build()
knapsack_v_t_item_1_obj = Term("Knapsack_v_t_Item_1").attributes(coefficient=-6).build()
knapsack_v_t_item_2_obj = Term("Knapsack_v_t_Item_2").attributes(coefficient=-10).build()
knapsack_v_t_item_3_obj = Term("Knapsack_v_t_Item_3").attributes(coefficient=-12).build()
knapsack_v_t_item_4_obj = Term("Knapsack_v_t_Item_4").attributes(coefficient=-13).build()
knapsack_value_atom_obj = Atom("Knapsack_value_atom").attributes(relation=Relation.LE).build()
knapsack_w_e_obj = LinearExpression("Knapsack_w_e").attributes(constant=-11).build()
knapsack_w_t_item_1_obj = Term("Knapsack_w_t_Item_1").attributes(coefficient=2).build()
knapsack_w_t_item_2_obj = Term("Knapsack_w_t_Item_2").attributes(coefficient=4).build()
knapsack_w_t_item_3_obj = Term("Knapsack_w_t_Item_3").attributes(coefficient=6).build()
knapsack_w_t_item_4_obj = Term("Knapsack_w_t_Item_4").attributes(coefficient=7).build()
knapsack_weight_atom_obj = Atom("Knapsack_weight_atom").attributes(relation=Relation.LE).build()
knapsack_y_item_1_obj = Unknown("Knapsack_y_Item_1").attributes(name="y_Item_1", bitWidth=1).build()
knapsack_y_item_2_obj = Unknown("Knapsack_y_Item_2").attributes(name="y_Item_2", bitWidth=1).build()
knapsack_y_item_3_obj = Unknown("Knapsack_y_Item_3").attributes(name="y_Item_3", bitWidth=1).build()
knapsack_y_item_4_obj = Unknown("Knapsack_y_Item_4").attributes(name="y_Item_4", bitWidth=1).build()

knapsack_value_atom_obj.expression = knapsack_v_e_obj
knapsack_w_e_obj.terms = {knapsack_w_t_item_1_obj, knapsack_w_t_item_2_obj, knapsack_w_t_item_3_obj, knapsack_w_t_item_4_obj}
knapsack_weight_atom_obj.expression = knapsack_w_e_obj
knapsack_obj.config = knapsack_config_obj
knapsack_w_t_item_2_obj.unknown = knapsack_y_item_2_obj
knapsack_v_t_item_2_obj.unknown = knapsack_y_item_2_obj
knapsack_v_t_item_4_obj.unknown = knapsack_y_item_4_obj
knapsack_v_e_obj.terms = {knapsack_v_t_item_1_obj, knapsack_v_t_item_2_obj, knapsack_v_t_item_3_obj, knapsack_v_t_item_4_obj}
knapsack_obj.unknowns = {knapsack_y_item_1_obj, knapsack_y_item_2_obj, knapsack_y_item_3_obj, knapsack_y_item_4_obj}
knapsack_w_t_item_4_obj.unknown = knapsack_y_item_4_obj
knapsack_root_obj.operands = {knapsack_value_atom_obj, knapsack_weight_atom_obj}
knapsack_w_t_item_1_obj.unknown = knapsack_y_item_1_obj
knapsack_v_t_item_1_obj.unknown = knapsack_y_item_1_obj
knapsack_v_t_item_3_obj.unknown = knapsack_y_item_3_obj
knapsack_w_t_item_3_obj.unknown = knapsack_y_item_3_obj
knapsack_obj.root = knapsack_root_obj

# Object Model instance
object_model: ObjectModel = ObjectModel(
    name="Knapsack_solution",
    objects={knapsack_obj, knapsack_config_obj, knapsack_root_obj, knapsack_v_e_obj, knapsack_v_t_item_1_obj, knapsack_v_t_item_2_obj, knapsack_v_t_item_3_obj, knapsack_v_t_item_4_obj, knapsack_value_atom_obj, knapsack_w_e_obj, knapsack_w_t_item_1_obj, knapsack_w_t_item_2_obj, knapsack_w_t_item_3_obj, knapsack_w_t_item_4_obj, knapsack_weight_atom_obj, knapsack_y_item_1_obj, knapsack_y_item_2_obj, knapsack_y_item_3_obj, knapsack_y_item_4_obj}
)


######################
# PROJECT DEFINITION #
######################

from besser.BUML.metamodel.project import Project
from besser.BUML.metamodel.structural.structural import Metadata

metadata = Metadata(description="T1 output")
project = Project(
    name="Knapsack_solution",
    models=[domain_model, object_model],
    owner="",
    metadata=metadata
)

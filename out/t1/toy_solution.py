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
Junction = Class(name="Junction", is_abstract=True)
And = Class(name="And")
Or = Class(name="Or")
LinearExpression = Class(name="LinearExpression")
ConstraintSystem = Class(name="ConstraintSystem")
Unknown = Class(name="Unknown")
Formula = Class(name="Formula", is_abstract=True)
Atom = Class(name="Atom")
Term = Class(name="Term")
SolverConfig = Class(name="SolverConfig")

# Junction class attributes and methods

# And class attributes and methods

# Or class attributes and methods

# LinearExpression class attributes and methods
LinearExpression_constant: Property = Property(name="constant", type=IntegerType)
LinearExpression.attributes={LinearExpression_constant}

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

# Term class attributes and methods
Term_coefficient: Property = Property(name="coefficient", type=IntegerType)
Term.attributes={Term_coefficient}

# SolverConfig class attributes and methods
SolverConfig_iterations: Property = Property(name="iterations", type=IntegerType)
SolverConfig_shots: Property = Property(name="shots", type=IntegerType)
SolverConfig_adder: Property = Property(name="adder", type=AdderKind)
SolverConfig.attributes={SolverConfig_adder, SolverConfig_iterations, SolverConfig_shots}

# Relationships
atom_expression: BinaryAssociation = BinaryAssociation(
    name="atom_expression",
    ends={
        Property(name="expression", type=LinearExpression, multiplicity=Multiplicity(1, 1), is_composite=True),
        Property(name="atom", type=Atom, multiplicity=Multiplicity(0, 1))
    }
)
expression_terms: BinaryAssociation = BinaryAssociation(
    name="expression_terms",
    ends={
        Property(name="expr", type=LinearExpression, multiplicity=Multiplicity(1, 1)),
        Property(name="terms", type=Term, multiplicity=Multiplicity(0, 9999), is_composite=True)
    }
)
term_unknown: BinaryAssociation = BinaryAssociation(
    name="term_unknown",
    ends={
        Property(name="usedBy", type=Term, multiplicity=Multiplicity(0, 9999)),
        Property(name="unknown", type=Unknown, multiplicity=Multiplicity(1, 1))
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
system_config: BinaryAssociation = BinaryAssociation(
    name="system_config",
    ends={
        Property(name="configOf", type=ConstraintSystem, multiplicity=Multiplicity(1, 1)),
        Property(name="config", type=SolverConfig, multiplicity=Multiplicity(0, 1), is_composite=True)
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
    types={Junction, And, Or, LinearExpression, ConstraintSystem, Unknown, Formula, Atom, Term, SolverConfig, Relation, AdderKind},
    associations={atom_expression, expression_terms, term_unknown, system_unknowns, system_root, junction_operands, system_config},
    constraints={bitWidthPositive, uniqueUnknownNames, searchSpaceSimulable, coefficientNonZero, oneTermPerUnknown, singleParent, noSelfOperand, iterationsNonNegative, shotsPositive},
    generalizations={gen_Atom_Formula, gen_Junction_Formula, gen_And_Junction, gen_Or_Junction},
    metadata=None
)

################
# OBJECT MODEL #
################
toy_obj = ConstraintSystem("toy").attributes(name="toy").build()
toy_config_obj = SolverConfig("toy_config").attributes(iterations=1, shots=1024, adder=AdderKind.RIPPLE_CARRY).build()
toy_root_obj = And("toy_root").build()
toy_v_e_obj = LinearExpression("toy_v_e").attributes(constant=7).build()
toy_v_t_a_obj = Term("toy_v_t_a").attributes(coefficient=-3).build()
toy_v_t_b_obj = Term("toy_v_t_b").attributes(coefficient=-4).build()
toy_v_t_c_obj = Term("toy_v_t_c").attributes(coefficient=-5).build()
toy_value_atom_obj = Atom("toy_value_atom").attributes(relation=Relation.LE).build()
toy_w_e_obj = LinearExpression("toy_w_e").attributes(constant=-5).build()
toy_w_t_a_obj = Term("toy_w_t_a").attributes(coefficient=2).build()
toy_w_t_b_obj = Term("toy_w_t_b").attributes(coefficient=3).build()
toy_w_t_c_obj = Term("toy_w_t_c").attributes(coefficient=4).build()
toy_weight_atom_obj = Atom("toy_weight_atom").attributes(relation=Relation.LE).build()
toy_y_a_obj = Unknown("toy_y_a").attributes(name="y_a", bitWidth=1).build()
toy_y_b_obj = Unknown("toy_y_b").attributes(name="y_b", bitWidth=1).build()
toy_y_c_obj = Unknown("toy_y_c").attributes(name="y_c", bitWidth=1).build()

toy_v_t_b_obj.unknown = toy_y_b_obj
toy_v_t_a_obj.unknown = toy_y_a_obj
toy_w_t_b_obj.unknown = toy_y_b_obj
toy_v_e_obj.terms = {toy_v_t_a_obj, toy_v_t_b_obj, toy_v_t_c_obj}
toy_w_e_obj.terms = {toy_w_t_a_obj, toy_w_t_b_obj, toy_w_t_c_obj}
toy_obj.root = toy_root_obj
toy_root_obj.operands = {toy_value_atom_obj, toy_weight_atom_obj}
toy_obj.unknowns = {toy_y_a_obj, toy_y_b_obj, toy_y_c_obj}
toy_weight_atom_obj.expression = toy_w_e_obj
toy_value_atom_obj.expression = toy_v_e_obj
toy_w_t_a_obj.unknown = toy_y_a_obj
toy_w_t_c_obj.unknown = toy_y_c_obj
toy_obj.config = toy_config_obj
toy_v_t_c_obj.unknown = toy_y_c_obj

# Object Model instance
object_model: ObjectModel = ObjectModel(
    name="toy_solution",
    objects={toy_obj, toy_config_obj, toy_root_obj, toy_v_e_obj, toy_v_t_a_obj, toy_v_t_b_obj, toy_v_t_c_obj, toy_value_atom_obj, toy_w_e_obj, toy_w_t_a_obj, toy_w_t_b_obj, toy_w_t_c_obj, toy_weight_atom_obj, toy_y_a_obj, toy_y_b_obj, toy_y_c_obj}
)


######################
# PROJECT DEFINITION #
######################

from besser.BUML.metamodel.project import Project
from besser.BUML.metamodel.structural.structural import Metadata

metadata = Metadata(description="T1 output")
project = Project(
    name="toy_solution",
    models=[domain_model, object_model],
    owner="",
    metadata=metadata
)

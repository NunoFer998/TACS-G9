"""Solution DSL: a system of linear integer constraints (class C intermediate model).

Meaning (Annex A, class C): unknowns y1..yn, each with w_i bits (0 .. 2^w_i - 1);
atoms  a0 + a1*y1 + ... + an*yn = 0  or  <= 0,  combined with and / or.
Question: find values of the unknowns that make the root formula true, or report none.
"""
from besser.BUML.metamodel.structural import (
    DomainModel, Class, Property, BinaryAssociation, Multiplicity, Generalization,
    Enumeration, EnumerationLiteral, Constraint, StringType, IntegerType,
)

# --- Enumerations ----------------------------------------------------------

Relation = Enumeration(name="Relation", literals={
    EnumerationLiteral(name="EQ"),   # expression = 0
    EnumerationLiteral(name="LE"),   # expression <= 0
})

AdderKind = Enumeration(name="AdderKind", literals={
    EnumerationLiteral(name="RIPPLE_CARRY"),   # Cuccaro et al. 2004 / Vedral et al. 1996
    EnumerationLiteral(name="QFT"),            # Draper 2000
})

# --- Classes ---------------------------------------------------------------

ConstraintSystem = Class(name="ConstraintSystem", attributes={
    Property(name="name", type=StringType),
})

Unknown = Class(name="Unknown", attributes={
    Property(name="name", type=StringType),
    Property(name="bitWidth", type=IntegerType),
})

Formula = Class(name="Formula", is_abstract=True)
Atom = Class(name="Atom", attributes={
    Property(name="relation", type=Relation),
})
Junction = Class(name="Junction", is_abstract=True)
And = Class(name="And")
Or = Class(name="Or")

LinearExpression = Class(name="LinearExpression", attributes={
    Property(name="constant", type=IntegerType),      # a0
})
Term = Class(name="Term", attributes={
    Property(name="coefficient", type=IntegerType),   # ai
})

# Solver choices, kept out of the transformations (assignment, section 2).
SolverConfig = Class(name="SolverConfig", attributes={
    Property(name="iterations", type=IntegerType),    # Grover rounds
    Property(name="shots", type=IntegerType),
    Property(name="adder", type=AdderKind),
})

# --- Generalizations -------------------------------------------------------

gen_atom = Generalization(general=Formula, specific=Atom)
gen_junction = Generalization(general=Formula, specific=Junction)
gen_and = Generalization(general=Junction, specific=And)
gen_or = Generalization(general=Junction, specific=Or)

# --- Associations ----------------------------------------------------------
# Back-ends to the container are 0..1 so BESSER has no mandatory creation cycle;
# composition already guarantees each part has its owner.

system_unknowns = BinaryAssociation(name="system_unknowns", ends={
    Property(name="system", type=ConstraintSystem, multiplicity=Multiplicity(0, 1)),
    Property(name="unknowns", type=Unknown, multiplicity=Multiplicity(1, "*"), is_composite=True),
})

system_root = BinaryAssociation(name="system_root", ends={
    Property(name="rootOf", type=ConstraintSystem, multiplicity=Multiplicity(0, 1)),
    Property(name="root", type=Formula, multiplicity=Multiplicity(1, 1), is_composite=True),
})

junction_operands = BinaryAssociation(name="junction_operands", ends={
    Property(name="parent", type=Junction, multiplicity=Multiplicity(0, 1)),
    Property(name="operands", type=Formula, multiplicity=Multiplicity(2, "*"), is_composite=True),
})

atom_expression = BinaryAssociation(name="atom_expression", ends={
    Property(name="atom", type=Atom, multiplicity=Multiplicity(0, 1)),
    Property(name="expression", type=LinearExpression, multiplicity=Multiplicity(1, 1), is_composite=True),
})

expression_terms = BinaryAssociation(name="expression_terms", ends={
    Property(name="expr", type=LinearExpression, multiplicity=Multiplicity(1, 1)),
    Property(name="terms", type=Term, multiplicity=Multiplicity(0, "*"), is_composite=True),
})

term_unknown = BinaryAssociation(name="term_unknown", ends={
    Property(name="usedBy", type=Term, multiplicity=Multiplicity(0, "*")),
    Property(name="unknown", type=Unknown, multiplicity=Multiplicity(1, 1)),
})

system_config = BinaryAssociation(name="system_config", ends={
    Property(name="configOf", type=ConstraintSystem, multiplicity=Multiplicity(1, 1)),
    Property(name="config", type=SolverConfig, multiplicity=Multiplicity(0, 1), is_composite=True),
})

# --- OCL constraints -------------------------------------------------------

constraints = {
    Constraint(name="bitWidthPositive", context=Unknown, language="OCL",
               expression="context Unknown inv bitWidthPositive: self.bitWidth >= 1"),
    Constraint(name="uniqueUnknownNames", context=ConstraintSystem, language="OCL",
               expression="context ConstraintSystem inv uniqueUnknownNames: "
                          "self.unknowns->forAll(u1, u2 | u1 <> u2 implies u1.name <> u2.name)"),
    # Search register only; ancillas and expression registers are added by T2.
    Constraint(name="searchSpaceSimulable", context=ConstraintSystem, language="OCL",
               expression="context ConstraintSystem inv searchSpaceSimulable: "
                          "self.unknowns->collect(u | u.bitWidth)->sum() <= 20"),
    Constraint(name="coefficientNonZero", context=Term, language="OCL",
               expression="context Term inv coefficientNonZero: self.coefficient <> 0"),
    Constraint(name="oneTermPerUnknown", context=LinearExpression, language="OCL",
               expression="context LinearExpression inv oneTermPerUnknown: "
                          "self.terms->forAll(t1, t2 | t1 <> t2 implies t1.unknown <> t2.unknown)"),
    # A formula is either the root of the system or an operand of exactly one junction.
    Constraint(name="singleParent", context=Formula, language="OCL",
               expression="context Formula inv singleParent: "
                          "self.rootOf->size() + self.parent->size() = 1"),
    Constraint(name="noSelfOperand", context=Junction, language="OCL",
               expression="context Junction inv noSelfOperand: self.operands->excludes(self)"),
    Constraint(name="iterationsNonNegative", context=SolverConfig, language="OCL",
               expression="context SolverConfig inv iterationsNonNegative: self.iterations >= 0"),
    Constraint(name="shotsPositive", context=SolverConfig, language="OCL",
               expression="context SolverConfig inv shotsPositive: self.shots >= 1"),
}

solution_metamodel = DomainModel(
    name="LinearConstraintsDSL",
    types={Relation, AdderKind, ConstraintSystem, Unknown, Formula, Atom, Junction,
           And, Or, LinearExpression, Term, SolverConfig},
    associations={system_unknowns, system_root, junction_operands, atom_expression,
                  expression_terms, term_unknown, system_config},
    generalizations={gen_atom, gen_junction, gen_and, gen_or},
    constraints=constraints,
)

"""T1 (M2M): knapsack problem model -> linear-constraint solution model.

Rules (traceable to docs/concept_list.md section 3 and the references there):
  R1  KnapsackProblem -> ConstraintSystem                     Annex A class C
  R2  Item -> Unknown y_i, 1 bit (0 = left out, 1 = packed)   [GJ79] MP9 (0/1 items)
  R3  weight constraint -> Atom LE: sum(w_i y_i) - C <= 0     [KPP04]; Annex A class C
  R4  value constraint  -> Atom LE: V - sum(v_i y_i) <= 0     Annex A class C variants
                           ("y1 + y2 >= 3 becomes 3 - y1 - y2 <= 0")
  R5  objective (feasibility) -> root And(weight atom, value atom)   [GJ79] MP9 (bounds B, K)
  R6  SolverConfig -> given as input, never hard-coded in the rules  assignment section 2

The trace maps every created object to its source, used by the backward mapping (bonus).
"""
from dataclasses import dataclass

from besser.BUML.metamodel.object import ObjectModel

from solution_dsl.solution_metamodel import (
    ConstraintSystem, Unknown, Atom, And, LinearExpression, Term, SolverConfig,
    Relation, AdderKind,
)


@dataclass
class SolverSettings:
    """Solver configuration model (input of T1): Grover rounds, shots, adder choice."""
    iterations: int = 1
    shots: int = 1024
    adder: str = "RIPPLE_CARRY"      # AdderKind literal name


def _literal(enum, name):
    return next(l for l in enum.literals if l.name == name)


def _objects_of(model, class_name):
    return sorted((o for o in model.objects if o.classifier.name == class_name),
                  key=lambda o: o.name_)


def _slot(obj, name):
    return next(s.value.value for s in obj.slots if s.attribute.name == name)


def _id(text):
    """BESSER object/link names cannot contain spaces; free-text names can."""
    return text.replace(" ", "_")


def _expression(prefix, constant, terms, target, trace, src):
    """Build a LinearExpression a0 + sum(a_i * y_i); terms = [(coefficient, unknown, item)]."""
    term_objs = []
    for coef, unknown, item in terms:
        t = Term(f"{prefix}_t_{_id(_slot(item, 'name'))}").attributes(coefficient=coef) \
            .link(unknown, "unknown").build()
        trace[t] = item
        term_objs.append(t)
    e = LinearExpression(f"{prefix}_e").attributes(constant=constant)
    if term_objs:
        e = e.link(set(term_objs), "terms")
    e = e.build()
    trace[e] = src
    target.update(term_objs + [e])
    return e


def _atom(name, expression, target, trace, src):
    a = Atom(name).attributes(relation=_literal(Relation, "LE")) \
        .link(expression, "expression").build()
    trace[a] = src
    target.add(a)
    return a


def r2_unknowns(items, pname, objs, trace):
    """R2: one 1-bit unknown per item (name kept for decoding). Returns {item: unknown}."""
    unknown_of = {}
    for it in items:
        u = Unknown(f"{pname}_y_{_id(_slot(it, 'name'))}")             .attributes(name=f"y_{_id(_slot(it, 'name'))}", bitWidth=1).build()
        unknown_of[it] = u
        trace[u] = it
        objs.add(u)
    return unknown_of


def r3_weight_atom(problem, items, unknown_of, pname, objs, trace):
    """R3: sum(w_i y_i) - C <= 0."""
    expr = _expression(f"{pname}_w", -_slot(problem, "capacity"),
                       [(_slot(i, "weight"), unknown_of[i], i) for i in items],
                       objs, trace, problem)
    return _atom(f"{pname}_weight_atom", expr, objs, trace, problem)


def r4_value_atom(problem, items, unknown_of, pname, objs, trace):
    """R4: V - sum(v_i y_i) <= 0 ; zero-value items give no term (coefficientNonZero)."""
    expr = _expression(f"{pname}_v", _slot(problem, "minValue"),
                       [(-_slot(i, "value"), unknown_of[i], i) for i in items
                        if _slot(i, "value") != 0],
                       objs, trace, problem)
    return _atom(f"{pname}_value_atom", expr, objs, trace, problem)


def r5_root(w_atom, v_atom, problem, pname, objs, trace):
    """R5: root And(weight atom, value atom)."""
    root = And(f"{pname}_root").link({w_atom, v_atom}, "operands").build()
    trace[root] = problem
    objs.add(root)
    return root


def r6_config(settings, pname, objs):
    """R6: solver config comes from the input settings."""
    config = SolverConfig(f"{pname}_config").attributes(
        iterations=settings.iterations, shots=settings.shots,
        adder=_literal(AdderKind, settings.adder)).build()
    objs.add(config)
    return config


def r1_system(problem, unknown_of, root, config, pname, objs, trace):
    """R1: constraint system owning everything."""
    system = ConstraintSystem(pname).attributes(name=pname)         .link(set(unknown_of.values()), "unknowns").link(root, "root")         .link(config, "config").build()
    trace[system] = problem
    objs.add(system)
    return system


def transform(source: ObjectModel, settings: SolverSettings = None):
    """Return (solution ObjectModel, trace {target object: source object})."""
    settings = settings or SolverSettings()
    problem = _objects_of(source, "KnapsackProblem")[0]
    pname = _id(_slot(problem, "name"))
    items = _objects_of(source, "Item")
    objs, trace = set(), {}

    unknown_of = r2_unknowns(items, pname, objs, trace)
    w_atom = r3_weight_atom(problem, items, unknown_of, pname, objs, trace)
    v_atom = r4_value_atom(problem, items, unknown_of, pname, objs, trace)
    root = r5_root(w_atom, v_atom, problem, pname, objs, trace)
    config = r6_config(settings, pname, objs)
    r1_system(problem, unknown_of, root, config, pname, objs, trace)

    return ObjectModel(name=f"{pname}_solution", objects=objs), trace


def run_file(path, out_dir="out/t1"):
    """Run T1 on the object model of an editor-exported .py and save the solution model."""
    import os
    import runpy
    from besser.BUML.metamodel.project import Project
    from besser.BUML.metamodel.structural.structural import Metadata
    from besser.utilities.buml_code_builder.project_builder import project_to_code
    from solution_dsl.solution_metamodel import solution_metamodel

    source = runpy.run_path(path)["object_model"]
    model, _ = transform(source)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{model.name}.py")
    project_to_code(Project(name=model.name, models=[solution_metamodel, model],
                                 metadata=Metadata(description="T1 output")), out)
    print(f"{path}: {len(model.objects)} objects -> {out}")
    # ponytail: no .json export, the converter is missing from the installed besser wheel
    return model


if __name__ == "__main__":
    import sys
    run_file(sys.argv[1])

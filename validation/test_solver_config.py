"""Regression tests for configuration as model input, not transformation policy."""
import itertools
import runpy
import tempfile
import unittest
from dataclasses import replace
from unittest.mock import patch

from besser.BUML.metamodel.object import ObjectModel

from models.instances import INSTANCES
from models.solver_configs import CONFIGS
from solution_dsl.solution_metamodel import (
    Atom, ConstraintSystem, LinearExpression, Relation, Term, Unknown,
)
from solution_dsl.solver_config import SolverSettings, config_object, read_config
from transformations import t1, t2
from validation.baseline import brute_force, grover_rounds, read_problem


class SolverConfigTests(unittest.TestCase):
    def test_instance_configs_and_semantics(self):
        for name, problem in INSTANCES.items():
            with self.subTest(name=name):
                source_config = config_object(CONFIGS[name])
                settings = read_config(source_config)
                solution, trace = t1.transform(problem, CONFIGS[name])
                config = config_object(solution)
                self.assertIsNot(config, source_config)
                self.assertIs(trace[config], source_config)
                self.assertEqual(read_config(config), settings)
                _, capacity, min_value, items = read_problem(problem)
                truth = brute_force(capacity, min_value, items)
                self.assertEqual(settings.iterations, grover_rounds(len(items), len(truth)))
                self.assertEqual(sorted(t1.solutions_of(solution)), sorted(truth))
                spec = t2.extract_spec(solution)
                layout = t2.make_layout(spec)
                self.assertEqual(layout.B, settings.expression_bit_width)
                self.assertEqual(spec.iterations, settings.iterations)
                oracle = t2.build_oracle_ops(spec, layout)
                for bits in itertools.product((0, 1), repeat=spec.n):
                    state = list(bits) + [0] * (layout.total - spec.n)
                    result = t2.classical_run(oracle, state)
                    self.assertEqual(result[layout.phase], int(bits in truth))
                    self.assertEqual(result[spec.n:layout.phase], [0] * (layout.phase - spec.n))

    def test_configured_rounds_zero_and_nonzero(self):
        base = read_config(config_object(CONFIGS["toy"]))
        for rounds in (0, 1, 4):
            with self.subTest(rounds=rounds):
                settings = replace(base, iterations=rounds, shots=37, expression_bit_width=5)
                configuration = ObjectModel(name="custom", objects={settings.to_object("cfg")})
                solution, _ = t1.transform(INSTANCES["toy"], configuration)
                spec = t2.extract_spec(solution)
                self.assertEqual(spec.shots, 37)
                self.assertEqual(spec.iterations, rounds)
                layout = t2.make_layout(spec)
                emitted = []
                with patch.object(t2, "_emit", side_effect=lambda circuit, op: emitted.append(op)):
                    t2.t2(solution)
                per_round = len(t2.build_oracle_ops(spec, layout)) + len(t2.build_diffuser_ops(spec.n))
                self.assertEqual(len(emitted), 2 + spec.n + rounds * per_round)
                self.assertEqual(layout.B, 5)

    def test_config_round_trip(self):
        solution, _ = t1.transform(INSTANCES["f4_none"], CONFIGS["f4_none"])
        with tempfile.TemporaryDirectory() as directory:
            path = t1.save(solution, directory)
            restored = runpy.run_path(path)["object_model"]
        expected, actual = t2.extract_spec(solution), t2.extract_spec(restored)
        self.assertCountEqual(actual.atoms, expected.atoms)
        self.assertEqual(replace(actual, atoms=[]), replace(expected, atoms=[]))
        self.assertEqual(actual.iterations, 0)

    def test_missing_and_multiple_configs_fail(self):
        empty = ObjectModel(name="empty", objects=set())
        with self.assertRaisesRegex(ValueError, "exactly one"):
            t1.transform(INSTANCES["toy"], empty)
        settings = read_config(config_object(CONFIGS["toy"]))
        multiple = ObjectModel(name="multiple", objects={
            settings.to_object("one"), settings.to_object("two"),
        })
        with self.assertRaisesRegex(ValueError, "exactly one"):
            t1.transform(INSTANCES["toy"], multiple)
        solution, _ = t1.transform(INSTANCES["toy"], CONFIGS["toy"])
        real_linked = t2._linked
        with patch.object(t2, "_linked", side_effect=lambda obj, end:
                          [] if end == "config" else real_linked(obj, end)):
            with self.assertRaisesRegex(ValueError, "exactly one"):
                t2.extract_spec(solution)

    def test_missing_slots_fail(self):
        from solution_dsl.solution_metamodel import SolverConfig
        config = SolverConfig("incomplete").build()
        with self.assertRaisesRegex(ValueError, "missing settings"):
            read_config(config)

    def test_invalid_settings_fail(self):
        base = read_config(config_object(CONFIGS["toy"]))
        for changes in ({"iterations": -1}, {"iterations": True}, {"iterations": 1.5},
                        {"shots": 0}, {"expression_bit_width": 0},
                        {"adder": "invalid"}, {"expression_encoding": "UNSIGNED"}):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    replace(base, **changes)

    def test_undersized_width_and_unsupported_adder_fail(self):
        solution, _ = t1.transform(INSTANCES["toy"], CONFIGS["toy"])
        spec = t2.extract_spec(solution)
        with self.assertRaisesRegex(ValueError, "cannot hold"):
            t2.build_circuit_from_spec(replace(spec, expression_bit_width=3))
        with self.assertRaisesRegex(NotImplementedError, "QFT"):
            t2.build_circuit_from_spec(replace(spec, adder="QFT"))

    def test_signed_width_boundaries(self):
        base = t2.SystemSpec(["y"], [1], [], 0, 16, "RIPPLE_CARRY", 2, "TWOS_COMPLEMENT")
        for width, constant, coefficient in ((1, -1, 1), (2, -2, 3)):
            with self.subTest(width=width):
                spec = replace(base, atoms=[t2.AtomSpec(constant, {0: coefficient})],
                               expression_bit_width=width)
                self.assertEqual(t2.make_layout(spec).B, width)
                for outside in (t2.AtomSpec(constant - 1, {0: coefficient}),
                                t2.AtomSpec(constant, {0: coefficient + 1})):
                    with self.assertRaisesRegex(ValueError, "cannot hold"):
                        t2.make_layout(replace(spec, atoms=[outside]))

    def test_general_integer_unknown_width_is_preserved(self):
        unknown = Unknown("y").attributes(name="y", bitWidth=2).build()
        term = Term("t").attributes(coefficient=1).link(unknown, "unknown").build()
        expression = LinearExpression("e").attributes(constant=-2).link({term}, "terms").build()
        atom = Atom("a").attributes(relation=Relation.LE).link(expression, "expression").build()
        config = SolverSettings(0, 16, "RIPPLE_CARRY", 2, "TWOS_COMPLEMENT").to_object("cfg")
        system = (ConstraintSystem("s").attributes(name="s").link({unknown}, "unknowns")
                  .link(atom, "root").link(config, "config").build())
        model = ObjectModel(name="integer", objects={unknown, term, expression, atom, config, system})
        spec = t2.extract_spec(model)
        self.assertEqual(spec.unknown_widths, [2])
        layout = t2.make_layout(spec)
        for value in range(4):
            bits = [(value >> j) & 1 for j in range(2)]
            state = bits + [0] * (layout.total - 2)
            result = t2.classical_run(t2.build_oracle_ops(spec, layout), state)
            self.assertEqual(result[layout.phase], int(value <= 2))
            self.assertEqual(result[2:layout.phase], [0] * (layout.phase - 2))
        self.assertEqual(t2.decode_bitstring("11", layout), {"y": 3})


if __name__ == "__main__":
    unittest.main()

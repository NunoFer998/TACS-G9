"""Solver input models, separate from the mathematical problem instances.

Rounds are selected using the validation baseline's solution counts, not by T1/T2.
Widths hold the full range of both atoms in two's complement.
"""
from besser.BUML.metamodel.object import ObjectModel

from solution_dsl.solver_config import SolverSettings


def make_config(name, *, iterations, shots, adder, expression_bit_width, expression_encoding):
    settings = SolverSettings(iterations, shots, adder, expression_bit_width, expression_encoding)
    return ObjectModel(name=f"{name}_solver", objects={settings.to_object(f"{name}_config")})


CONFIGS = {
    "toy": make_config("toy", iterations=2, shots=1024, adder="RIPPLE_CARRY",
                       expression_bit_width=4, expression_encoding="TWOS_COMPLEMENT"),
    "tiny": make_config("tiny", iterations=3, shots=1024, adder="RIPPLE_CARRY",
                        expression_bit_width=5, expression_encoding="TWOS_COMPLEMENT"),
    "f4": make_config("f4", iterations=3, shots=1024, adder="RIPPLE_CARRY",
                      expression_bit_width=6, expression_encoding="TWOS_COMPLEMENT"),
    "f4_multi": make_config("f4_multi", iterations=1, shots=1024, adder="RIPPLE_CARRY",
                            expression_bit_width=6, expression_encoding="TWOS_COMPLEMENT"),
    "f4_none": make_config("f4_none", iterations=0, shots=1024, adder="RIPPLE_CARRY",
                           expression_bit_width=6, expression_encoding="TWOS_COMPLEMENT"),
    "f7_sub5": make_config("f7_sub5", iterations=4, shots=1024, adder="RIPPLE_CARRY",
                           expression_bit_width=8, expression_encoding="TWOS_COMPLEMENT"),
}

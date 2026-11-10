"""Read and build explicit SolverConfig model objects; no execution defaults."""
from dataclasses import dataclass

from besser.BUML.metamodel.object import ObjectModel

from solution_dsl.solution_metamodel import AdderKind, ExpressionEncoding, SolverConfig


@dataclass(frozen=True)
class SolverSettings:
    iterations: int
    shots: int
    adder: str
    expression_bit_width: int
    expression_encoding: str

    def __post_init__(self):
        for name, minimum in (("iterations", 0), ("shots", 1), ("expression_bit_width", 1)):
            value = getattr(self, name)
            if type(value) is not int or value < minimum:
                raise ValueError(f"SolverConfig.{name} must be an integer >= {minimum}")
        if self.adder not in {literal.name for literal in AdderKind.literals}:
            raise ValueError(f"Unknown adder kind: {self.adder}")
        if self.expression_encoding not in {literal.name for literal in ExpressionEncoding.literals}:
            raise ValueError(f"Unknown expression encoding: {self.expression_encoding}")

    def to_object(self, name):
        return SolverConfig(name).attributes(
            iterations=self.iterations, shots=self.shots,
            adder=next(l for l in AdderKind.literals if l.name == self.adder),
            expressionBitWidth=self.expression_bit_width,
            expressionEncoding=next(l for l in ExpressionEncoding.literals
                                    if l.name == self.expression_encoding),
        ).build()


def read_config(config):
    if config.classifier.name != "SolverConfig":
        raise ValueError("Expected a SolverConfig object")
    slots = {s.attribute.name: s.value.value for s in config.slots}
    required = {"iterations", "shots", "adder", "expressionBitWidth", "expressionEncoding"}
    missing = required - slots.keys()
    if missing:
        raise ValueError(f"SolverConfig is missing settings: {', '.join(sorted(missing))}")
    return SolverSettings(
        iterations=slots["iterations"], shots=slots["shots"],
        adder=getattr(slots["adder"], "name", slots["adder"]),
        expression_bit_width=slots["expressionBitWidth"],
        expression_encoding=getattr(slots["expressionEncoding"], "name", slots["expressionEncoding"]),
    )


def config_object(model: ObjectModel):
    configs = [o for o in model.objects if o.classifier.name == "SolverConfig"]
    if len(configs) != 1:
        raise ValueError("Configuration model must contain exactly one SolverConfig")
    read_config(configs[0])
    return configs[0]

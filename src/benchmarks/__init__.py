"""Standard benchmark integrations."""

from .mmlu_benchmark import MMLUBenchmark
from .humaneval_benchmark import HumanEvalBenchmark

__all__ = ["MMLUBenchmark", "HumanEvalBenchmark"]

"""Pipeline utilities that chain lifecycle stages together."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from .arena import ArenaEvaluationSuite
from .benchmarks import BenchmarkEvaluationSuite
from .foundational import FoundationalEvaluationSuite
from .models import (
    ArenaRunConfig,
    BenchmarkRunConfig,
    FoundationalRunConfig,
    LifecycleStageResult,
)


@dataclass
class EvaluationLifecycleReport:
    """Aggregated output from running the lifecycle pipeline."""

    stages: Dict[str, LifecycleStageResult] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, dict]:
        """Convert the report into a JSON-serializable dictionary."""
        return {
            stage: {
                "metrics": result.metrics,
                "artifacts": result.artifacts,
            }
            for stage, result in self.stages.items()
        }


class EvaluationLifecyclePipeline:
    """High-level coordinator for the three-stage evaluation journey."""

    def __init__(
        self,
        foundational_suite: FoundationalEvaluationSuite,
        benchmark_suite: Optional[BenchmarkEvaluationSuite] = None,
        arena_suite: Optional[ArenaEvaluationSuite] = None,
    ):
        self.foundational_suite = foundational_suite
        self.benchmark_suite = benchmark_suite
        self.arena_suite = arena_suite

    async def run(
        self,
        foundational_config: Optional[FoundationalRunConfig] = None,
        benchmark_config: Optional[BenchmarkRunConfig] = None,
        arena_config: Optional[ArenaRunConfig] = None,
        *,
        run_foundational: bool = True,
        run_benchmarks: bool = True,
        run_arena: bool = True,
    ) -> EvaluationLifecycleReport:
        """Execute the configured stages and collect their outputs."""
        report = EvaluationLifecycleReport()

        if run_foundational:
            result = await self.foundational_suite.run(foundational_config)
            report.stages[result.stage] = result

        if run_benchmarks and self.benchmark_suite:
            result = await self.benchmark_suite.run(benchmark_config)
            report.stages[result.stage] = result

        if run_arena and self.arena_suite and arena_config:
            result = await self.arena_suite.run(arena_config)
            report.stages[result.stage] = result

        return report

"""Stage 2 orchestration: standardized benchmark execution."""

from __future__ import annotations

from typing import Dict, Optional

from ..benchmarks import HumanEvalBenchmark, MMLUBenchmark
from ..providers.base_client import BaseClient
from .models import BenchmarkRunConfig, LifecycleStageResult

BENCHMARK_REGISTRY = {
    "mmlu": MMLUBenchmark,
    "humaneval": HumanEvalBenchmark,
}


class BenchmarkEvaluationSuite:
    """Runs configured benchmarks and aggregates the results."""

    def __init__(self, client: BaseClient, model: str):
        self.client = client
        self.model = model

    async def run(
        self,
        config: Optional[BenchmarkRunConfig] = None
    ) -> LifecycleStageResult:
        """Execute selected benchmarks sequentially."""
        config = config or BenchmarkRunConfig()
        metrics: Dict[str, Dict] = {}
        artifacts: Dict[str, Dict] = {}
        raw_results = []

        for benchmark_name in config.benchmark_names:
            key = benchmark_name.lower()
            benchmark_cls = BENCHMARK_REGISTRY.get(key)
            if not benchmark_cls:
                raise ValueError(f"Unsupported benchmark: {benchmark_name}")

            benchmark = benchmark_cls(
                client=self.client,
                model=self.model
            )
            kwargs = config.benchmark_kwargs.get(key, {})
            result = await benchmark.evaluate(**kwargs)
            raw_results.append(result)
            metrics[key] = result.metrics
            artifacts[f"{key}_metadata"] = result.metadata

        return LifecycleStageResult(
            stage="task_benchmarks",
            metrics=metrics,
            artifacts=artifacts,
            raw_results=raw_results,
        )

"""Stage 1 orchestration: foundational metric evaluations."""

from __future__ import annotations

from typing import Optional

from ..evaluators.cost import CostAnalyzer
from ..evaluators.performance import AccuracyEvaluator
from ..evaluators.quality import TextQualityEvaluator
from ..evaluators.speed import LatencyBenchmark
from ..providers.base_client import BaseClient
from .models import FoundationalRunConfig, LifecycleStageResult


class FoundationalEvaluationSuite:
    """Runs Stage 1 evaluations and aggregates their outputs."""

    def __init__(self, client: BaseClient, model: str):
        self.client = client
        self.model = model

    async def run(
        self,
        config: Optional[FoundationalRunConfig] = None
    ) -> LifecycleStageResult:
        """Execute foundational checks for a model."""
        config = config or FoundationalRunConfig()
        metrics = {}
        artifacts = {}
        raw_results = []

        if config.accuracy_dataset:
            accuracy_evaluator = AccuracyEvaluator(
                client=self.client,
                model=self.model
            )
            accuracy_result = await accuracy_evaluator.evaluate(
                list(config.accuracy_dataset)
            )
            raw_results.append(accuracy_result)
            metrics["accuracy"] = accuracy_result.metrics
            artifacts["accuracy_metadata"] = accuracy_result.metadata

        if config.quality_dataset:
            quality_evaluator = TextQualityEvaluator(
                client=self.client,
                model=self.model
            )
            quality_result = await quality_evaluator.evaluate(
                list(config.quality_dataset),
                compute_bert_score=config.compute_bert_score
            )
            raw_results.append(quality_result)
            metrics["quality"] = quality_result.metrics
            artifacts["quality_examples"] = quality_result.metadata.get("examples", [])

        latency_evaluator = LatencyBenchmark(
            client=self.client,
            model=self.model
        )
        latency_result = await latency_evaluator.evaluate(
            num_requests=config.latency_requests,
            prompt=config.latency_prompt,
            max_tokens=config.latency_max_tokens,
            concurrent_requests=config.latency_concurrency
        )
        raw_results.append(latency_result)
        metrics["latency"] = latency_result.metrics

        if config.cost_model_ids:
            analyzer = CostAnalyzer()
            cost_df = analyzer.compare_models(
                list(config.cost_model_ids),
                config.cost_input_tokens,
                config.cost_output_tokens,
                config.cost_requests_per_day
            )
            artifacts["cost_comparison"] = cost_df.to_dict(orient="records")

        return LifecycleStageResult(
            stage="foundational_metrics",
            metrics=metrics,
            artifacts=artifacts,
            raw_results=raw_results,
        )

    async def run_with_defaults(self) -> LifecycleStageResult:
        """Convenience wrapper using default smoke-test settings."""
        return await self.run(FoundationalRunConfig())

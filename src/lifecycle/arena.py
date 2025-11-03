"""Stage 3 orchestration: arena mode evaluations."""

from __future__ import annotations

from typing import Optional

from ..evaluators.arena import ArenaPrompt, LMArenaClient, LMArenaEvaluator
from ..providers.base_client import BaseClient
from .models import ArenaRunConfig, LifecycleStageResult


class ArenaEvaluationSuite:
    """Coordinates LMArena-style tournaments between two models."""

    def __init__(
        self,
        candidate_client: BaseClient,
        candidate_model: str,
        baseline_client: BaseClient,
        baseline_model: str,
        arena_client: Optional[LMArenaClient] = None,
        judge_client: Optional[BaseClient] = None,
        judge_model: Optional[str] = None,
    ):
        self.candidate_client = candidate_client
        self.candidate_model = candidate_model
        self.baseline_client = baseline_client
        self.baseline_model = baseline_model
        self.arena_client = arena_client
        self.judge_client = judge_client
        self.judge_model = judge_model

    async def run(
        self,
        config: ArenaRunConfig
    ) -> LifecycleStageResult:
        """Execute arena matches and aggregate scores."""
        evaluator = LMArenaEvaluator(
            client=self.candidate_client,
            model=self.candidate_model,
            baseline_client=self.baseline_client,
            baseline_model=self.baseline_model,
            arena_client=self.arena_client,
            judge_client=self.judge_client,
            judge_model=self.judge_model,
        )

        result = await evaluator.evaluate(
            dataset=config.prompts,
            judge_temperature=config.judge_temperature,
            judge_max_tokens=config.judge_max_tokens,
        )

        artifacts = {
            "match_metadata": result.metadata.get("matches", []),
            "arena_metadata": config.arena_metadata,
        }

        return LifecycleStageResult(
            stage="arena_evaluations",
            metrics=result.metrics,
            artifacts=artifacts,
            raw_results=[result],
        )

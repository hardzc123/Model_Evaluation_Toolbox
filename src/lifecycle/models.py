"""Shared dataclasses used by lifecycle orchestration modules."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence


@dataclass
class LifecycleStageResult:
    """Container for high-level stage output."""

    stage: str
    metrics: Dict[str, Any]
    artifacts: Dict[str, Any] = field(default_factory=dict)
    raw_results: List[Any] = field(default_factory=list)


@dataclass
class FoundationalRunConfig:
    """Configuration for Stage 1 evaluations."""

    accuracy_dataset: Optional[Sequence[Any]] = None
    quality_dataset: Optional[Sequence[Any]] = None
    compute_bert_score: bool = False
    latency_requests: int = 50
    latency_prompt: str = "Provide a concise summary of the 2024 AI safety landscape."
    latency_max_tokens: int = 256
    latency_concurrency: int = 1
    cost_model_ids: Optional[Sequence[str]] = None
    cost_input_tokens: int = 1000
    cost_output_tokens: int = 200
    cost_requests_per_day: Optional[int] = None


@dataclass
class BenchmarkRunConfig:
    """Configuration for Stage 2 benchmark execution."""

    benchmark_names: Sequence[str] = field(default_factory=lambda: ("mmlu",))
    benchmark_kwargs: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class ArenaRunConfig:
    """Configuration for Stage 3 arena matches."""

    prompts: Sequence[Any]
    baseline_model: str
    judge_model: Optional[str] = None
    judge_temperature: float = 0.0
    judge_max_tokens: int = 256
    arena_metadata: Dict[str, Any] = field(default_factory=dict)

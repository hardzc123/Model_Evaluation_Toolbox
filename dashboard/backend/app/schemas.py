"""Pydantic schemas for API."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class EvaluationRunCreate(BaseModel):
    """Schema for creating an evaluation run."""

    model_id: str
    model_name: str
    provider: str
    evaluator_type: str
    metrics: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    duration_seconds: Optional[float] = None
    num_samples: Optional[int] = None
    notes: Optional[str] = None


class EvaluationRunResponse(BaseModel):
    """Schema for evaluation run response."""

    id: int
    model_id: str
    model_name: str
    provider: str
    evaluator_type: str
    metrics: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]
    accuracy: Optional[float]
    latency_ms: Optional[float]
    cost_per_request: Optional[float]
    quality_score: Optional[float]
    duration_seconds: Optional[float]
    num_samples: Optional[int]
    timestamp: datetime
    notes: Optional[str]
    status: str

    class Config:
        from_attributes = True


class ModelInfo(BaseModel):
    """Schema for model information."""

    model_id: str
    model_name: str
    provider: str
    context_window: Optional[int]
    max_output_tokens: Optional[int]
    capabilities: Optional[List[str]]
    input_price_per_1k: Optional[float]
    output_price_per_1k: Optional[float]
    latest_accuracy: Optional[float]
    latest_latency_ms: Optional[float]
    latest_quality_score: Optional[float]

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    """Schema for leaderboard entry."""

    model_id: str
    model_name: str
    provider: str
    accuracy: Optional[float]
    latency_ms: Optional[float]
    cost_per_request: Optional[float]
    quality_score: Optional[float]
    cost_efficiency: Optional[float]  # quality / cost
    capabilities: Optional[List[str]]
    last_evaluated: Optional[datetime]


class BenchmarkCreate(BaseModel):
    """Schema for creating a benchmark result."""

    model_id: str
    benchmark_name: str
    score: float
    details: Optional[Dict[str, Any]]
    num_samples: Optional[int]
    duration_seconds: Optional[float]


class BenchmarkResponse(BaseModel):
    """Schema for benchmark response."""

    id: int
    model_id: str
    benchmark_name: str
    score: float
    details: Optional[Dict[str, Any]]
    timestamp: datetime
    num_samples: Optional[int]
    duration_seconds: Optional[float]

    class Config:
        from_attributes = True


class ComparisonRequest(BaseModel):
    """Schema for model comparison request."""

    model_ids: List[str]
    metrics: Optional[List[str]] = ["accuracy", "latency_ms", "cost_per_request"]


class ComparisonResponse(BaseModel):
    """Schema for model comparison response."""

    models: List[Dict[str, Any]]
    comparison_matrix: Dict[str, List[float]]

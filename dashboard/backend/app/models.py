"""Database models."""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, Index
from sqlalchemy.sql import func
from datetime import datetime

from .database import Base


class EvaluationRun(Base):
    """Model for evaluation run results."""

    __tablename__ = "evaluation_runs"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String(255), index=True, nullable=False)
    model_name = Column(String(255), nullable=False)
    provider = Column(String(100), index=True, nullable=False)
    evaluator_type = Column(String(100), index=True, nullable=False)

    # Metrics (stored as JSON for flexibility)
    metrics = Column(JSON, nullable=False)
    metadata = Column(JSON)

    # Aggregate metrics for quick access
    accuracy = Column(Float)
    latency_ms = Column(Float)
    cost_per_request = Column(Float)
    quality_score = Column(Float)

    # Run details
    duration_seconds = Column(Float)
    num_samples = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Additional info
    notes = Column(Text)
    status = Column(String(50), default="completed")  # completed, failed, running

    # Indexes for common queries
    __table_args__ = (
        Index('idx_model_provider', 'model_id', 'provider'),
        Index('idx_timestamp_model', 'timestamp', 'model_id'),
    )


class ModelRegistry(Base):
    """Model registry for storing model information."""

    __tablename__ = "model_registry"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String(255), unique=True, index=True, nullable=False)
    model_name = Column(String(255), nullable=False)
    provider = Column(String(100), index=True, nullable=False)

    # Model specifications
    context_window = Column(Integer)
    max_output_tokens = Column(Integer)
    capabilities = Column(JSON)  # List of capabilities

    # Pricing
    input_price_per_1k = Column(Float)
    output_price_per_1k = Column(Float)
    currency = Column(String(10), default="USD")

    # Latest metrics (cached for quick access)
    latest_accuracy = Column(Float)
    latest_latency_ms = Column(Float)
    latest_quality_score = Column(Float)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive


class Benchmark(Base):
    """Standard benchmark results."""

    __tablename__ = "benchmarks"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String(255), index=True, nullable=False)
    benchmark_name = Column(String(100), index=True, nullable=False)  # MMLU, HumanEval, etc.

    # Results
    score = Column(Float, nullable=False)
    details = Column(JSON)  # Detailed results

    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    num_samples = Column(Integer)
    duration_seconds = Column(Float)

    __table_args__ = (
        Index('idx_benchmark_model', 'benchmark_name', 'model_id'),
    )

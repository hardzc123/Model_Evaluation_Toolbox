"""Tests for evaluators."""

import pytest
from src.evaluators.base_evaluator import EvaluationResult
from src.evaluators.cost import CostAnalyzer


def test_cost_analyzer_initialization():
    """Test cost analyzer initialization."""
    analyzer = CostAnalyzer()
    assert analyzer is not None
    assert analyzer.models_registry is not None


def test_cost_estimate():
    """Test cost estimation."""
    analyzer = CostAnalyzer()

    estimate = analyzer.estimate_cost(
        model_id="gpt-3.5-turbo",
        input_tokens=1000,
        output_tokens=500
    )

    assert estimate.model == "GPT-3.5 Turbo"
    assert estimate.provider == "openai"
    assert estimate.total_cost > 0
    assert estimate.input_cost + estimate.output_cost == estimate.total_cost


def test_cost_comparison():
    """Test comparing costs across models."""
    analyzer = CostAnalyzer()

    models = ["gpt-3.5-turbo", "gpt-4"]
    df = analyzer.compare_models(
        model_ids=models,
        input_tokens=1000,
        output_tokens=500
    )

    assert len(df) == 2
    assert "Model" in df.columns
    assert "Cost per Request" in df.columns


def test_cost_efficiency():
    """Test cost efficiency calculation."""
    analyzer = CostAnalyzer()

    efficiency = analyzer.calculate_cost_efficiency(
        model_id="gpt-3.5-turbo",
        quality_score=0.85,
        input_tokens=1000,
        output_tokens=500
    )

    assert efficiency > 0
    assert isinstance(efficiency, float)


def test_evaluation_result_creation():
    """Test creating an evaluation result."""
    result = EvaluationResult(
        model="test-model",
        provider="test-provider",
        evaluator_type="AccuracyEvaluator",
        metrics={"accuracy": 0.85},
        metadata={"temperature": 0.7}
    )

    assert result.model == "test-model"
    assert result.metrics["accuracy"] == 0.85
    assert result.metadata["temperature"] == 0.7

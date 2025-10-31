"""CRUD operations for database."""

from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List, Optional
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app import models, schemas
from src.config import get_config


def create_evaluation_run(
    db: Session,
    evaluation: schemas.EvaluationRunCreate
) -> models.EvaluationRun:
    """Create a new evaluation run.

    Args:
        db: Database session
        evaluation: Evaluation data

    Returns:
        Created evaluation run
    """
    # Extract specific metrics for quick access
    metrics = evaluation.metrics
    accuracy = metrics.get("accuracy")
    latency_ms = metrics.get("mean_latency_ms") or metrics.get("latency_ms")
    quality_score = (
        metrics.get("mean_bleu") or
        metrics.get("quality_score") or
        metrics.get("mean_rouge1")
    )
    cost_per_request = metrics.get("cost_per_request")

    db_evaluation = models.EvaluationRun(
        model_id=evaluation.model_id,
        model_name=evaluation.model_name,
        provider=evaluation.provider,
        evaluator_type=evaluation.evaluator_type,
        metrics=evaluation.metrics,
        metadata=evaluation.metadata,
        accuracy=accuracy,
        latency_ms=latency_ms,
        cost_per_request=cost_per_request,
        quality_score=quality_score,
        duration_seconds=evaluation.duration_seconds,
        num_samples=evaluation.num_samples,
        notes=evaluation.notes,
    )

    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)

    # Update model registry with latest metrics
    update_model_metrics(db, evaluation.model_id)

    return db_evaluation


def get_evaluation_runs(
    db: Session,
    model_id: Optional[str] = None,
    provider: Optional[str] = None,
    evaluator_type: Optional[str] = None,
    limit: int = 100,
    skip: int = 0
) -> List[models.EvaluationRun]:
    """Get evaluation runs with filtering.

    Args:
        db: Database session
        model_id: Filter by model ID
        provider: Filter by provider
        evaluator_type: Filter by evaluator type
        limit: Maximum results
        skip: Number to skip

    Returns:
        List of evaluation runs
    """
    query = db.query(models.EvaluationRun)

    if model_id:
        query = query.filter(models.EvaluationRun.model_id == model_id)
    if provider:
        query = query.filter(models.EvaluationRun.provider == provider)
    if evaluator_type:
        query = query.filter(models.EvaluationRun.evaluator_type == evaluator_type)

    return query.order_by(
        desc(models.EvaluationRun.timestamp)
    ).offset(skip).limit(limit).all()


def get_leaderboard(
    db: Session,
    sort_by: str = "accuracy",
    order: str = "desc",
    provider: Optional[str] = None,
    limit: int = 50
) -> List[schemas.LeaderboardEntry]:
    """Get model leaderboard.

    Args:
        db: Database session
        sort_by: Metric to sort by
        order: Sort order (asc/desc)
        provider: Filter by provider
        limit: Maximum results

    Returns:
        List of leaderboard entries
    """
    query = db.query(models.ModelRegistry).filter(models.ModelRegistry.is_active == 1)

    if provider:
        query = query.filter(models.ModelRegistry.provider == provider)

    # Sort
    if sort_by == "accuracy":
        sort_col = models.ModelRegistry.latest_accuracy
    elif sort_by == "latency_ms":
        sort_col = models.ModelRegistry.latest_latency_ms
    elif sort_by == "quality_score":
        sort_col = models.ModelRegistry.latest_quality_score
    else:
        sort_col = models.ModelRegistry.latest_accuracy

    if order == "asc":
        query = query.order_by(asc(sort_col))
    else:
        query = query.order_by(desc(sort_col))

    models_list = query.limit(limit).all()

    # Convert to leaderboard entries
    entries = []
    for model in models_list:
        # Calculate cost efficiency if we have both quality and cost
        cost_efficiency = None
        if model.latest_quality_score and model.input_price_per_1k and model.output_price_per_1k:
            avg_cost = (model.input_price_per_1k + model.output_price_per_1k) / 2
            if avg_cost > 0:
                cost_efficiency = model.latest_quality_score / avg_cost

        # Get latest evaluation time
        latest_eval = db.query(models.EvaluationRun).filter(
            models.EvaluationRun.model_id == model.model_id
        ).order_by(desc(models.EvaluationRun.timestamp)).first()

        entries.append(schemas.LeaderboardEntry(
            model_id=model.model_id,
            model_name=model.model_name,
            provider=model.provider,
            accuracy=model.latest_accuracy,
            latency_ms=model.latest_latency_ms,
            cost_per_request=(model.input_price_per_1k + model.output_price_per_1k) / 2 if model.input_price_per_1k else None,
            quality_score=model.latest_quality_score,
            cost_efficiency=cost_efficiency,
            capabilities=model.capabilities,
            last_evaluated=latest_eval.timestamp if latest_eval else None
        ))

    return entries


def get_model_comparison(
    db: Session,
    model_ids: List[str],
    metrics: List[str]
) -> schemas.ComparisonResponse:
    """Compare models across metrics.

    Args:
        db: Database session
        model_ids: List of model IDs to compare
        metrics: List of metrics to compare

    Returns:
        Comparison response with model data
    """
    models_list = db.query(models.ModelRegistry).filter(
        models.ModelRegistry.model_id.in_(model_ids)
    ).all()

    models_data = []
    comparison_matrix = {metric: [] for metric in metrics}

    for model in models_list:
        model_dict = {
            "model_id": model.model_id,
            "model_name": model.model_name,
            "provider": model.provider,
        }

        # Add metrics
        for metric in metrics:
            if metric == "accuracy":
                value = model.latest_accuracy
            elif metric == "latency_ms":
                value = model.latest_latency_ms
            elif metric == "cost_per_request":
                value = (model.input_price_per_1k + model.output_price_per_1k) / 2 if model.input_price_per_1k else None
            elif metric == "quality_score":
                value = model.latest_quality_score
            else:
                value = None

            model_dict[metric] = value
            comparison_matrix[metric].append(value if value is not None else 0)

        models_data.append(model_dict)

    return schemas.ComparisonResponse(
        models=models_data,
        comparison_matrix=comparison_matrix
    )


def update_model_metrics(db: Session, model_id: str):
    """Update model with latest metrics from evaluations.

    Args:
        db: Database session
        model_id: Model ID to update
    """
    model = db.query(models.ModelRegistry).filter(
        models.ModelRegistry.model_id == model_id
    ).first()

    if not model:
        return

    # Get latest evaluations for each metric type
    latest_accuracy = db.query(models.EvaluationRun).filter(
        models.EvaluationRun.model_id == model_id,
        models.EvaluationRun.accuracy.isnot(None)
    ).order_by(desc(models.EvaluationRun.timestamp)).first()

    latest_latency = db.query(models.EvaluationRun).filter(
        models.EvaluationRun.model_id == model_id,
        models.EvaluationRun.latency_ms.isnot(None)
    ).order_by(desc(models.EvaluationRun.timestamp)).first()

    latest_quality = db.query(models.EvaluationRun).filter(
        models.EvaluationRun.model_id == model_id,
        models.EvaluationRun.quality_score.isnot(None)
    ).order_by(desc(models.EvaluationRun.timestamp)).first()

    # Update model
    if latest_accuracy:
        model.latest_accuracy = latest_accuracy.accuracy
    if latest_latency:
        model.latest_latency_ms = latest_latency.latency_ms
    if latest_quality:
        model.latest_quality_score = latest_quality.quality_score

    db.commit()


def sync_models_from_registry(db: Session):
    """Sync models from config registry to database.

    Args:
        db: Database session
    """
    config = get_config()
    models_registry = config.models_registry

    for provider_models in models_registry.models.values():
        for model_info in provider_models:
            # Check if model exists
            existing = db.query(models.ModelRegistry).filter(
                models.ModelRegistry.model_id == model_info.id
            ).first()

            if existing:
                # Update existing model
                existing.model_name = model_info.name
                existing.context_window = model_info.context_window
                existing.max_output_tokens = model_info.max_output_tokens
                existing.capabilities = model_info.capabilities
                existing.input_price_per_1k = model_info.pricing.get("input_per_1k_tokens")
                existing.output_price_per_1k = model_info.pricing.get("output_per_1k_tokens")
            else:
                # Create new model
                new_model = models.ModelRegistry(
                    model_id=model_info.id,
                    model_name=model_info.name,
                    provider=model_info.provider,
                    context_window=model_info.context_window,
                    max_output_tokens=model_info.max_output_tokens,
                    capabilities=model_info.capabilities,
                    input_price_per_1k=model_info.pricing.get("input_per_1k_tokens"),
                    output_price_per_1k=model_info.pricing.get("output_per_1k_tokens"),
                )
                db.add(new_model)

    db.commit()

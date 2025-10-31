"""Main FastAPI application."""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app import __version__
from app.database import get_db, init_db
from app import models, schemas
from app.crud import (
    create_evaluation_run,
    get_evaluation_runs,
    get_leaderboard,
    get_model_comparison,
    sync_models_from_registry,
)

# Initialize FastAPI app
app = FastAPI(
    title="Model Evaluation Dashboard API",
    description="API for AI model evaluation and benchmarking",
    version=__version__,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    # Sync models from registry
    db = next(get_db())
    try:
        sync_models_from_registry(db)
    finally:
        db.close()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Model Evaluation Dashboard API",
        "version": __version__,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Evaluation Runs Endpoints

@app.post("/evaluations", response_model=schemas.EvaluationRunResponse)
async def create_evaluation(
    evaluation: schemas.EvaluationRunCreate,
    db: Session = Depends(get_db)
):
    """Create a new evaluation run."""
    return create_evaluation_run(db, evaluation)


@app.get("/evaluations", response_model=List[schemas.EvaluationRunResponse])
async def list_evaluations(
    model_id: Optional[str] = None,
    provider: Optional[str] = None,
    evaluator_type: Optional[str] = None,
    limit: int = Query(100, le=1000),
    skip: int = 0,
    db: Session = Depends(get_db)
):
    """List evaluation runs with optional filtering."""
    return get_evaluation_runs(
        db,
        model_id=model_id,
        provider=provider,
        evaluator_type=evaluator_type,
        limit=limit,
        skip=skip
    )


@app.get("/evaluations/{evaluation_id}", response_model=schemas.EvaluationRunResponse)
async def get_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific evaluation run."""
    evaluation = db.query(models.EvaluationRun).filter(
        models.EvaluationRun.id == evaluation_id
    ).first()

    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    return evaluation


# Leaderboard Endpoints

@app.get("/leaderboard", response_model=List[schemas.LeaderboardEntry])
async def leaderboard(
    sort_by: str = Query("accuracy", regex="^(accuracy|latency_ms|cost_per_request|quality_score|cost_efficiency)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    provider: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db)
):
    """Get model leaderboard."""
    return get_leaderboard(
        db,
        sort_by=sort_by,
        order=order,
        provider=provider,
        limit=limit
    )


# Model Endpoints

@app.get("/models", response_model=List[schemas.ModelInfo])
async def list_models(
    provider: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all models."""
    query = db.query(models.ModelRegistry).filter(models.ModelRegistry.is_active == 1)

    if provider:
        query = query.filter(models.ModelRegistry.provider == provider)

    return query.all()


@app.get("/models/{model_id}", response_model=schemas.ModelInfo)
async def get_model(
    model_id: str,
    db: Session = Depends(get_db)
):
    """Get model information."""
    model = db.query(models.ModelRegistry).filter(
        models.ModelRegistry.model_id == model_id
    ).first()

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return model


@app.post("/models/compare", response_model=schemas.ComparisonResponse)
async def compare_models(
    request: schemas.ComparisonRequest,
    db: Session = Depends(get_db)
):
    """Compare multiple models."""
    return get_model_comparison(db, request.model_ids, request.metrics)


# Benchmark Endpoints

@app.post("/benchmarks", response_model=schemas.BenchmarkResponse)
async def create_benchmark(
    benchmark: schemas.BenchmarkCreate,
    db: Session = Depends(get_db)
):
    """Create a benchmark result."""
    db_benchmark = models.Benchmark(**benchmark.dict())
    db.add(db_benchmark)
    db.commit()
    db.refresh(db_benchmark)
    return db_benchmark


@app.get("/benchmarks", response_model=List[schemas.BenchmarkResponse])
async def list_benchmarks(
    benchmark_name: Optional[str] = None,
    model_id: Optional[str] = None,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    """List benchmark results."""
    query = db.query(models.Benchmark)

    if benchmark_name:
        query = query.filter(models.Benchmark.benchmark_name == benchmark_name)
    if model_id:
        query = query.filter(models.Benchmark.model_id == model_id)

    return query.order_by(models.Benchmark.timestamp.desc()).limit(limit).all()


# Statistics Endpoints

@app.get("/stats/overview")
async def get_overview_stats(db: Session = Depends(get_db)):
    """Get overview statistics."""
    total_models = db.query(models.ModelRegistry).filter(
        models.ModelRegistry.is_active == 1
    ).count()

    total_evaluations = db.query(models.EvaluationRun).count()

    providers = db.query(models.ModelRegistry.provider).distinct().all()
    num_providers = len(providers)

    return {
        "total_models": total_models,
        "total_evaluations": total_evaluations,
        "num_providers": num_providers,
        "providers": [p[0] for p in providers]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""Base evaluator class for all evaluation types."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from ..providers.base_client import BaseClient
from ..utils import get_logger

logger = get_logger(__name__)


class EvaluationResult(BaseModel):
    """Results from an evaluation run."""

    model: str
    provider: str
    evaluator_type: str
    metrics: Dict[str, Any]
    metadata: Dict[str, Any] = {}
    timestamp: datetime = datetime.now()
    duration_seconds: Optional[float] = None
    total_cost: Optional[float] = None
    num_samples: Optional[int] = None


class BaseEvaluator(ABC):
    """Abstract base class for all evaluators."""

    def __init__(
        self,
        client: BaseClient,
        model: str,
        **kwargs
    ):
        """Initialize evaluator.

        Args:
            client: API client for the model provider
            model: Model identifier to evaluate
            **kwargs: Additional evaluator-specific parameters
        """
        self.client = client
        self.model = model
        self.config = kwargs
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    async def evaluate(
        self,
        dataset: Any,
        **kwargs
    ) -> EvaluationResult:
        """Run evaluation on a dataset.

        Args:
            dataset: Dataset or data to evaluate on
            **kwargs: Additional evaluation parameters

        Returns:
            EvaluationResult with metrics and metadata
        """
        pass

    @abstractmethod
    def evaluate_sync(
        self,
        dataset: Any,
        **kwargs
    ) -> EvaluationResult:
        """Synchronous version of evaluate.

        Args:
            dataset: Dataset or data to evaluate on
            **kwargs: Additional evaluation parameters

        Returns:
            EvaluationResult with metrics and metadata
        """
        pass

    def _create_result(
        self,
        metrics: Dict[str, Any],
        metadata: Dict[str, Any],
        duration: Optional[float] = None,
        total_cost: Optional[float] = None,
        num_samples: Optional[int] = None
    ) -> EvaluationResult:
        """Create an evaluation result.

        Args:
            metrics: Dictionary of metric names to values
            metadata: Additional metadata
            duration: Duration of evaluation in seconds
            total_cost: Total cost in USD
            num_samples: Number of samples evaluated

        Returns:
            EvaluationResult instance
        """
        # Determine provider from client class
        provider = self.client.__class__.__name__.replace("Client", "").lower()

        return EvaluationResult(
            model=self.model,
            provider=provider,
            evaluator_type=self.__class__.__name__,
            metrics=metrics,
            metadata=metadata,
            duration_seconds=duration,
            total_cost=total_cost,
            num_samples=num_samples,
        )

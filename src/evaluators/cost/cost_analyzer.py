"""Cost analysis and comparison for different models."""

from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd

from ...config import get_config, ModelInfo
from ...utils import get_logger

logger = get_logger(__name__)


@dataclass
class CostEstimate:
    """Cost estimate for a model and workload."""

    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    requests_per_day: Optional[int] = None
    monthly_cost: Optional[float] = None


class CostAnalyzer:
    """Analyzes and compares costs across models."""

    def __init__(self):
        """Initialize cost analyzer."""
        self.config = get_config()
        self.models_registry = self.config.models_registry
        self.logger = logger

    def estimate_cost(
        self,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
        requests_per_day: Optional[int] = None
    ) -> CostEstimate:
        """Estimate cost for a specific model and workload.

        Args:
            model_id: Model identifier
            input_tokens: Number of input tokens per request
            output_tokens: Number of output tokens per request
            requests_per_day: Optional number of requests per day

        Returns:
            CostEstimate with detailed breakdown
        """
        model_info = self.models_registry.get_model(model_id)
        if not model_info:
            raise ValueError(f"Model {model_id} not found in registry")

        # Calculate costs
        input_cost = (input_tokens / 1000) * model_info.pricing["input_per_1k_tokens"]
        output_cost = (output_tokens / 1000) * model_info.pricing["output_per_1k_tokens"]
        total_cost = input_cost + output_cost

        # Calculate monthly cost if requests per day provided
        monthly_cost = None
        if requests_per_day:
            monthly_cost = total_cost * requests_per_day * 30

        return CostEstimate(
            model=model_info.name,
            provider=model_info.provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            requests_per_day=requests_per_day,
            monthly_cost=monthly_cost,
        )

    def compare_models(
        self,
        model_ids: List[str],
        input_tokens: int,
        output_tokens: int,
        requests_per_day: Optional[int] = None
    ) -> pd.DataFrame:
        """Compare costs across multiple models.

        Args:
            model_ids: List of model identifiers
            input_tokens: Number of input tokens per request
            output_tokens: Number of output tokens per request
            requests_per_day: Optional requests per day for monthly estimates

        Returns:
            DataFrame with cost comparison
        """
        estimates = []

        for model_id in model_ids:
            try:
                estimate = self.estimate_cost(
                    model_id,
                    input_tokens,
                    output_tokens,
                    requests_per_day
                )
                estimates.append({
                    "Model": estimate.model,
                    "Provider": estimate.provider,
                    "Cost per Request": f"${estimate.total_cost:.6f}",
                    "Input Cost": f"${estimate.input_cost:.6f}",
                    "Output Cost": f"${estimate.output_cost:.6f}",
                    "Monthly Cost": f"${estimate.monthly_cost:.2f}" if estimate.monthly_cost else "N/A",
                    "Cost (numeric)": estimate.total_cost,  # For sorting
                })
            except Exception as e:
                self.logger.error(f"Error estimating cost for {model_id}", error=str(e))

        df = pd.DataFrame(estimates)
        if not df.empty:
            df = df.sort_values("Cost (numeric)")

        return df

    def calculate_cost_efficiency(
        self,
        model_id: str,
        quality_score: float,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost efficiency ratio (quality per dollar).

        Args:
            model_id: Model identifier
            quality_score: Quality metric (0-1 scale, higher is better)
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost efficiency score (quality / cost)
        """
        estimate = self.estimate_cost(model_id, input_tokens, output_tokens)

        if estimate.total_cost == 0:
            return float('inf')

        # Cost efficiency: higher quality per dollar is better
        return quality_score / estimate.total_cost

    def find_best_value(
        self,
        model_ids: List[str],
        quality_scores: Dict[str, float],
        input_tokens: int,
        output_tokens: int
    ) -> pd.DataFrame:
        """Find the best value models based on quality and cost.

        Args:
            model_ids: List of model identifiers
            quality_scores: Dictionary of model_id to quality score (0-1)
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            DataFrame with models ranked by cost efficiency
        """
        results = []

        for model_id in model_ids:
            if model_id not in quality_scores:
                continue

            try:
                estimate = self.estimate_cost(model_id, input_tokens, output_tokens)
                efficiency = self.calculate_cost_efficiency(
                    model_id,
                    quality_scores[model_id],
                    input_tokens,
                    output_tokens
                )

                results.append({
                    "Model": estimate.model,
                    "Provider": estimate.provider,
                    "Quality Score": f"{quality_scores[model_id]:.3f}",
                    "Cost per Request": f"${estimate.total_cost:.6f}",
                    "Cost Efficiency": f"{efficiency:.2f}",
                    "Efficiency (numeric)": efficiency,
                })
            except Exception as e:
                self.logger.error(f"Error calculating efficiency for {model_id}", error=str(e))

        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values("Efficiency (numeric)", ascending=False)

        return df

    def get_pricing_info(self, model_id: str) -> Dict:
        """Get pricing information for a model.

        Args:
            model_id: Model identifier

        Returns:
            Dictionary with pricing details
        """
        model_info = self.models_registry.get_model(model_id)
        if not model_info:
            raise ValueError(f"Model {model_id} not found in registry")

        return {
            "model": model_info.name,
            "provider": model_info.provider,
            "pricing": model_info.pricing,
            "context_window": model_info.context_window,
            "max_output_tokens": model_info.max_output_tokens,
        }

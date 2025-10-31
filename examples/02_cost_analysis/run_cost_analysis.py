"""Cost analysis and comparison example."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.evaluators.cost import CostAnalyzer


def main():
    """Run cost analysis example."""
    print("=" * 70)
    print("Cost Analysis Example")
    print("=" * 70)

    # Initialize cost analyzer
    analyzer = CostAnalyzer()

    # Example workload parameters
    input_tokens = 1000  # Input tokens per request
    output_tokens = 500  # Output tokens per request
    requests_per_day = 1000  # Daily request volume

    # Models to compare
    models_to_compare = [
        "gpt-4-turbo-2024-04-09",
        "gpt-3.5-turbo",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "command-r-plus",
    ]

    print("\n1. Cost Comparison for Sample Workload")
    print("-" * 70)
    print(f"Input tokens per request: {input_tokens}")
    print(f"Output tokens per request: {output_tokens}")
    print(f"Requests per day: {requests_per_day}")
    print()

    # Compare costs
    comparison_df = analyzer.compare_models(
        model_ids=models_to_compare,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        requests_per_day=requests_per_day
    )

    print(comparison_df.to_string(index=False))

    # Calculate cost efficiency with hypothetical quality scores
    print("\n\n2. Cost Efficiency Analysis")
    print("-" * 70)
    print("Assuming hypothetical quality scores (0-1 scale):")
    print()

    # Example quality scores (these would come from actual evaluations)
    quality_scores = {
        "gpt-4-turbo-2024-04-09": 0.92,
        "gpt-3.5-turbo": 0.78,
        "claude-3-opus-20240229": 0.94,
        "claude-3-sonnet-20240229": 0.88,
        "claude-3-haiku-20240307": 0.82,
        "gemini-1.5-pro": 0.90,
        "gemini-1.5-flash": 0.84,
        "command-r-plus": 0.86,
    }

    efficiency_df = analyzer.find_best_value(
        model_ids=models_to_compare,
        quality_scores=quality_scores,
        input_tokens=input_tokens,
        output_tokens=output_tokens
    )

    print(efficiency_df.to_string(index=False))

    # Detailed cost estimate for top model
    print("\n\n3. Detailed Cost Estimate for Best Value Model")
    print("-" * 70)

    if not efficiency_df.empty:
        best_model = models_to_compare[0]  # First model as example
        estimate = analyzer.estimate_cost(
            model_id=best_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            requests_per_day=requests_per_day
        )

        print(f"\nModel: {estimate.model}")
        print(f"Provider: {estimate.provider}")
        print(f"\nPer Request:")
        print(f"  Input cost: ${estimate.input_cost:.6f}")
        print(f"  Output cost: ${estimate.output_cost:.6f}")
        print(f"  Total cost: ${estimate.total_cost:.6f}")

        if estimate.monthly_cost:
            print(f"\nMonthly Estimate:")
            print(f"  Total requests: {requests_per_day * 30:,}")
            print(f"  Monthly cost: ${estimate.monthly_cost:,.2f}")
            print(f"  Annual cost: ${estimate.monthly_cost * 12:,.2f}")

    # Pricing info
    print("\n\n4. Detailed Pricing Information")
    print("-" * 70)

    for model_id in models_to_compare[:3]:  # Show first 3
        try:
            pricing = analyzer.get_pricing_info(model_id)
            print(f"\n{pricing['model']} ({pricing['provider']}):")
            print(f"  Input: ${pricing['pricing']['input_per_1k_tokens']}/1K tokens")
            print(f"  Output: ${pricing['pricing']['output_per_1k_tokens']}/1K tokens")
            print(f"  Context window: {pricing['context_window']:,} tokens")
            print(f"  Max output: {pricing['max_output_tokens']:,} tokens")
        except Exception as e:
            print(f"\nError getting pricing for {model_id}: {e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

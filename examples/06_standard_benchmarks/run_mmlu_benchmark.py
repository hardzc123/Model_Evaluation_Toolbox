"""MMLU benchmark example."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.providers import get_client
from src.benchmarks import MMLUBenchmark
from src.utils import setup_logging


async def main():
    """Run MMLU benchmark."""
    setup_logging(level="INFO")

    print("=" * 70)
    print("MMLU Benchmark Example")
    print("=" * 70)

    # Initialize client
    print("\nInitializing client...")
    client = get_client("openai")

    # Create benchmark
    print("Creating MMLU benchmark...")
    benchmark = MMLUBenchmark(client=client, model="gpt-3.5-turbo")

    # Run on subset of subjects for demo
    subjects = [
        "abstract_algebra",
        "anatomy",
        "astronomy",
        "business_ethics",
        "college_mathematics"
    ]

    print(f"\nRunning MMLU on {len(subjects)} subjects...")
    print("(Using small sample size for demo - increase for full evaluation)")
    print()

    result = await benchmark.evaluate(
        subjects=subjects,
        num_samples_per_subject=10  # Small sample for demo
    )

    # Display results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    print(f"\nModel: {result.model}")
    print(f"Duration: {result.duration_seconds:.2f} seconds")
    print(f"\nOverall Accuracy: {result.metrics['overall_accuracy']:.2%}")
    print(f"Subjects Evaluated: {result.metrics['num_subjects']}")

    print("\nPer-Subject Scores:")
    for subject, score in result.metrics['subject_scores'].items():
        print(f"  {subject}: {score:.2%}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

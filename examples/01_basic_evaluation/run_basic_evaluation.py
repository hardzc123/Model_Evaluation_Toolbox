"""Basic accuracy evaluation example."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.providers import get_client
from src.evaluators.performance import AccuracyEvaluator
from src.evaluators.performance.accuracy_evaluator import QAExample
from src.utils import setup_logging


async def main():
    """Run basic evaluation example."""
    # Setup logging
    setup_logging(level="INFO")

    print("=" * 70)
    print("Basic Model Evaluation Example")
    print("=" * 70)

    # Create test dataset
    dataset = [
        QAExample(
            question="What is the capital of France?",
            correct_answer="Paris"
        ),
        QAExample(
            question="What is 2 + 2?",
            correct_answer="4"
        ),
        QAExample(
            question="Who wrote 'Romeo and Juliet'?",
            correct_answer="William Shakespeare"
        ),
        QAExample(
            question="What is the largest planet in our solar system?",
            correct_answer="Jupiter"
        ),
        QAExample(
            question="What is the chemical symbol for gold?",
            correct_answer="Au"
        ),
        QAExample(
            question="In what year did World War II end?",
            correct_answer="1945"
        ),
        QAExample(
            question="What is the speed of light in vacuum (in m/s)?",
            correct_answer="299792458"
        ),
        QAExample(
            question="Who painted the Mona Lisa?",
            correct_answer="Leonardo da Vinci"
        ),
    ]

    # Initialize client and evaluator
    print("\n1. Initializing OpenAI client...")
    client = get_client("openai")

    print("2. Creating accuracy evaluator...")
    evaluator = AccuracyEvaluator(
        client=client,
        model="gpt-3.5-turbo"
    )

    # Run evaluation
    print(f"3. Evaluating on {len(dataset)} questions...")
    print()

    result = await evaluator.evaluate(
        dataset=dataset,
        temperature=0.0,  # Use 0 for deterministic answers
        max_tokens=50
    )

    # Display results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    print(f"\nModel: {result.model}")
    print(f"Provider: {result.provider}")
    print(f"Duration: {result.duration_seconds:.2f} seconds")
    print(f"Samples Evaluated: {result.num_samples}")

    print("\nMetrics:")
    print(f"  Exact Match Accuracy: {result.metrics['accuracy']:.2%}")
    print(f"  Partial Match Accuracy: {result.metrics['partial_accuracy']:.2%}")
    print(f"  Exact Matches: {result.metrics['exact_matches']}/{result.metrics['total_samples']}")
    print(f"  Partial Matches: {result.metrics['partial_matches']}/{result.metrics['total_samples']}")

    if result.total_cost:
        print(f"\nCost: ${result.total_cost:.4f}")

    # Show example predictions
    print("\nSample Predictions:")
    for i, example in enumerate(result.metadata.get('examples', [])[:5]):
        print(f"\n{i+1}. Question: {example['question']}")
        print(f"   Predicted: {example['predicted']}")
        print(f"   Actual: {example['actual']}")
        print(f"   Match: {'✓' if example['predicted'] == example['actual'] else '✗'}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
